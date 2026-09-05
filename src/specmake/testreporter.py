# SPDX-License-Identifier: BSD-2-Clause
""" Builds test report documents. """

# Copyright (C) 2022, 2026 embedded brains GmbH & Co. KG
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from contextlib import contextmanager
import functools
import os
import re
from typing import Any, Callable, Iterator, NamedTuple

from specitems import (EmptyItem, Item, ItemGetValueContext, SphinxContent,
                       base64_to_hex_text)

from .directorystate import DirectoryState
from .docbuilder import DocumentBuilder
from .pkgitems import PackageBuildDirector
from .perfimages import environment_order
from .testaggregator import TestAggregator
from .util import duration

_Failures = dict[str, dict[tuple[Item, str], dict[str, set[str]]]]

_NON_ORDINARY = re.compile(r"[^\x20-\x7e]")


def _escape_char(match: re.Match[str]) -> str:
    return f"\\x{ord(match.group(0)):02x}"


def _invisible_spaces(text: str) -> str:
    return "\u200b".join(iter(_NON_ORDINARY.sub(_escape_char, text)))


def _ok(good: bool) -> str:
    if good:
        return "OK"
    return "NOK"


def _check(expected: str, reported: str) -> str:
    if reported == "?":
        return "NOK"
    return _ok(expected == reported)


def _check_gt_zero(_expected: str, reported: str) -> str:
    try:
        if float(reported) > 0.0:
            return "OK"
    except ValueError:
        pass
    return "NOK"


def _check_eq_zero(_expected: str, reported: str) -> str:
    try:
        if int(reported) == 0:
            return "OK"
    except ValueError:
        pass
    return "NOK"


def _check_duration(_expected: str, reported: str) -> str:
    if reported == "?":
        return "NOK"
    return "OK"


def _listed(listed: bool) -> str:
    if listed:
        return "listed"
    return "not listed"


def _zero_one(value: bool) -> str:
    if value:
        return "1"
    return "0"


def _rtems_version_to_commit(version: str) -> str:
    return _invisible_spaces(version.split(".")[-1])


_RSB_COMMIT = re.compile(r"RSB ([^,]+),")


def _rsb_version_to_commit(version: str) -> str:
    match = _RSB_COMMIT.search(version)
    if match is None:
        return "?"
    return _invisible_spaces(match.group(1))


def _option(option: str, options: list[str]) -> str:
    return _listed(option in options)


def _target_hash(target_hash: str) -> str:
    if not target_hash:
        return "\u200b"
    return _invisible_spaces(target_hash)


_PROPERTY_TRANSFORM = {
    "rtems-source-builder-version": _rsb_version_to_commit,
    "rtems-version": _rtems_version_to_commit
}

_HEADER = ["Property", "Line", "Reported", "Expected", "Status"]

_WIDTHS = [42, 8, 20, 20, 10]

_ERRORS = {
    "no-begin-of-test-message":
    "The test output contains no begin of test message.",
    "no-end-of-test-message":
    "The test output contains no end of test message.",
    "unexpected-bsp":
    "The BSP has not the expected name.",
    "unexpected-build":
    "At least one build configuration option has not the expected value "
    "or the build configuration information is not present.",
    "unexpected-build-label":
    "The build label has not the expected value.",
    "unexpected-compiler":
    "The compiler version has not the expected value.",
    "unexpected-duration":
    "The test duration has not the expected value.",
    "unexpected-failed-steps-count":
    "The failed test steps count value is not zero.",
    "unexpected-report-hash":
    "The report hash has not the expected value.",
    "unexpected-rtems-debug":
    "The RTEMS_DEBUG build configuration option has not the expected value.",
    "unexpected-rtems-multiprocessing":
    "The RTEMS_MULTIPROCESSING build configuration option "
    "has not the expected value.",
    "unexpected-rtems-posix-api":
    "The RTEMS_POSIX_API build configuration option "
    "has not the expected value.",
    "unexpected-rtems-profiling":
    "The RTEMS_PROFILING build configuration option "
    "has not the expected value.",
    "unexpected-rtems-smp":
    "The RTEMS_SMP build configuration option has not the expected value.",
    "unexpected-runtime-maximum":
    "A maximum runtime value is greater than expected.",
    "unexpected-runtime-median":
    "A median runtime value is not in the expected interval.",
    "unexpected-runtime-minimum":
    "A minimum runtime value is less than expected.",
    "unexpected-step-count":
    "The test step count value is not positive.",
    "unexpected-target-hash":
    "The target hash has not the expected value.",
    "unexpected-tools":
    "The tools version has not the expected value.",
    "unexpected-version":
    "The RTEMS Git commit has not the expected value.",
}


class _TestProperty(NamedTuple):
    name: str
    type: str
    expected: str


class _TestContext:
    # pylint: disable=too-many-instance-attributes
    def __init__(self, reporter: "TestReporter"):
        self.content = SphinxContent()
        self.enabled_set = reporter.enabled_set
        self.expected_failures: _Failures = {}
        self.unexpected_failures: _Failures = {}
        self.limits_uid = ""
        self.limits_by_req: dict[str, dict] = {}
        self.target_hashes: tuple[str, ...] = tuple()
        self.target_hashes_display = ""
        self.target_uid = ""
        self.build_label = ""
        self.bsp: str = reporter.component["bsp"]
        self.properties: dict[str, _TestProperty] = {}
        for link, _ in reporter.input_links("test-property"):
            data = reporter.substitute(link.data)
            self.properties[data["key"]] = _TestProperty(
                data["property-name"], data["type"],
                _invisible_spaces(data["expected"]))
        self.item = EmptyItem()
        self.verifications: dict[str, str] = {}
        self.output_label = ""
        self.config_data: dict[str, Any] = {}

    def begin_report(self, report: dict) -> None:
        """ Begins the report. """
        self.output_label = f"{self.content.get_label()}Output"
        executable = os.path.basename(report["executable"])
        self.content.add(f"""This report was produced by the
:file:`{executable}`
executable.  The executable file had an SHA512 digest of
{base64_to_hex_text(report['executable-sha512'])}.""")
        error = report.get("error")
        if error:
            with self.content.directive("error", value="Test runner error"):
                self.content.add(error)
        else:
            self.content.gap = False

    def output_line_ref(self, line: int | str) -> str:
        """ Gets the output line reference for the line. """
        if isinstance(line, str):
            return line
        return (f":ref:`{line + 1} <"
                f"{self.output_label}{line - line % 100}>`")

    def add_error(self, error: str, add_to_content: bool = False) -> None:
        """
        Add the error with the reason.

        Optionally, add the reason to the content.
        """
        text = _ERRORS[error]
        if add_to_content:
            self.content.wrap(text)
        key = self.config_data["config-key"]
        config = f":ref:`Configuration - {key} <{self.content.get_label()}>`"
        uid = self.verifications.get(self.item.uid, None)
        failures = self.unexpected_failures
        verification_text = ""
        if uid is not None:
            verification = self.item.cache[uid]
            if error in verification["acceptable-test-errors"]:
                failures = self.expected_failures
                verification_text = verification["text"]
        failures.setdefault(self.target_uid, {}).setdefault(
            (self.item, verification_text), {}).setdefault(config,
                                                           set()).add(text)

    def add_failures(self, which: str, failures: _Failures,
                     test_aggregator: TestAggregator) -> None:
        """ Add the test failures to the content. """
        with self.content.section(f"List of {which} test failures"):
            if not failures:
                self.content.add(f"There were no {which} test errors "
                                 "found in the test outputs.")
                return
            for target_uid, by_test in failures.items():
                target_data = test_aggregator.targets[target_uid]
                target_section = f"Target - {target_data['name']}"
                with self.content.section(target_section):
                    for item_text, by_config in sorted(by_test.items()):
                        with self.content.section(item_text[0].spec_2):
                            self.content.add(item_text[1])
                            for config, errors in sorted(by_config.items()):
                                self.content.add_list_item(f"{config}:")
                                self.content.add_blank_line()
                                with self.content.indent("  "):
                                    self.content.add_list(sorted(errors))

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-positional-arguments
    def check(self,
              rows: list[list[str]],
              info: dict,
              name: str,
              key: str,
              expected: str,
              transform: Callable[[Any], str],
              check=_check) -> None:
        """ Check the test property. """
        try:
            line = self.output_line_ref(info[f"line-{key}"])
        except KeyError:
            line = "?"
            reported = "?"
        else:
            reported = transform(info[key])
        status = check(expected, reported)
        if status != "OK":
            self.add_error(f"unexpected-{key}")
        rows.append([name, line, reported, expected, status])

    def check_property(self, rows: list[list[str]], info: dict, key: str,
                       property_key: str) -> None:
        """ Check the property. """
        prop = self.properties[property_key]
        self.check(rows, info, prop.name, key, prop.expected,
                   _PROPERTY_TRANSFORM.get(prop.type, _invisible_spaces))

    def check_rtems_commit(self, rows: list[list[str]], info: dict) -> None:
        """ Check the RTEMS Git commit. """
        self.check_property(rows, info, "version", "rtems-commit")

    def check_compiler(self, rows: list[list[str]], info: dict,
                       key: str) -> None:
        """ Check the compiler version. """
        self.check_property(rows, info, key, "compiler-version")

    def _check_build_info(self, rows: list[list[str]], info: dict) -> None:
        for option in [
                "RTEMS_DEBUG", "RTEMS_MULTIPROCESSING", "RTEMS_PARAVIRT",
                "RTEMS_POSIX_API", "RTEMS_PROFILING", "RTEMS_SMP"
        ]:
            self.check(rows, info, option, "build",
                       _listed(option in self.enabled_set),
                       functools.partial(_option, option))

    def check_build_options(self, rows: list[list[str]], info: dict) -> None:
        """ Check the test suite build options. """
        for option in [
                "debug", "multiprocessing", "posix-api", "profiling", "smp"
        ]:
            key = f"rtems-{option}"
            name = key.replace("-", "_").upper()
            self.check(rows, info, name, key,
                       _zero_one(name in self.enabled_set), _zero_one)

    def check_target_hash(self, _expected: str, reported: str) -> str:
        """ Check the target hash. """
        return _ok(reported in self.target_hashes)

    def check_validations_by_test(self, test_aggregator: TestAggregator,
                                  target_uid: str) -> None:
        """
        Check that each validation by test has a test result for the target.
        """
        for item in test_aggregator.spec.related_validations_by_test:
            if target_uid not in item.view.get("test-results", {}):
                text = "There are no test results available for this target."
                verification_uid = self.verifications.get(item.uid, None)
                failures = self.unexpected_failures
                if verification_uid is not None:
                    verification = self.item.cache[verification_uid]
                    if "no-test-results" in verification[
                            "acceptable-test-errors"]:
                        failures = self.expected_failures
                        text = verification["text"]
                failures.setdefault(self.target_uid, {}).setdefault(
                    (item, text), {})

    def add_table(self, rows: list[list[str]], widths: list[int]) -> None:
        """ Add a table to the content with the rows and widths. """
        self.content.add_grid_table(rows, widths, font_size=-3)

    def add_test_info(self, info: dict) -> None:
        """ Add the test information to the content. """
        rows = [_HEADER]
        try:
            begin = self.output_line_ref(info["line-begin-of-test"])
            self.content.wrap(
                f"There is a valid begin of test message at line {begin}.")
        except KeyError:
            self.add_error("no-begin-of-test-message", True)
        self.content.gap = False
        try:
            end = self.output_line_ref(info["line-end-of-test"])
            self.content.wrap(f"""There is a valid end of test message at line
{end}.  This indicates that the test program executed without a detected
error.""")
        except KeyError:
            self.add_error("no-end-of-test-message", True)
        self.content.gap = False
        self.content.wrap("""The following table lists an evaluation of the
reported test information.""")
        self.check_rtems_commit(rows, info)
        self._check_build_info(rows, info)
        self.check_compiler(rows, info, "tools")
        self.add_table(rows, _WIDTHS)

    def add_limits(self, env_name: str, env_data: dict, limits: dict) -> None:
        """ Add the runtime performance limits to the content. """
        rows = [["Limit Kind", "Specified Limits", "Actual Value", "Status"]]
        value = env_data["min"]
        lower_bound = limits[env_name]["min-lower-bound"]
        status = _ok(lower_bound <= value)
        if status != "OK":
            self.add_error("unexpected-runtime-minimum")
        rows.append([
            "Minimum", f"{duration(lower_bound)} :math:`\\leq` Minimum",
            duration(value), status
        ])
        value = env_data["q2"]
        lower_bound = limits[env_name]["median-lower-bound"]
        upper_bound = limits[env_name]["median-upper-bound"]
        status = _ok(lower_bound <= value <= upper_bound)
        if status != "OK":
            self.add_error("unexpected-runtime-median")
        rows.append([
            "Median", f"{duration(lower_bound)} :math:`\\leq` Median "
            f":math:`\\leq` {duration(upper_bound)}",
            duration(value), status
        ])
        value = env_data["max"]
        upper_bound = limits[env_name]["max-upper-bound"]
        status = _ok(value <= upper_bound)
        if status != "OK":
            self.add_error("unexpected-runtime-maximum")
        rows.append([
            "Maximum", f"Maximum :math:`\\leq` {duration(upper_bound)}",
            duration(value), status
        ])
        self.add_table(rows, [15, 45, 25, 15])

    @contextmanager
    def file_scope(self, file_path: str, data: dict) -> Iterator[str]:
        """ Opens a file scope. """
        file_name = os.path.basename(data["report-file"])
        self.content.add(file_name)
        content = self.content
        self.content = SphinxContent()
        yield file_name
        self.content.write(
            os.path.join(os.path.dirname(file_path), f"{file_name}.rst"))
        self.content = content


def _add_output(ctx: _TestContext, report: dict) -> None:
    ctx.content.add_program_output(report["output"], report["data-ranges"],
                                   ctx.output_label)


def _add_test_output(ctx: _TestContext, report: dict) -> None:
    with ctx.content.section("Test output"):
        ctx.content.add(
            "The test report was generated from the following test output.")
        _add_output(ctx, report)


def _save_unexpected_failures(destination: DirectoryState,
                              failures: _Failures) -> None:
    target_to_failures: dict[str, list[str]] = {}
    for target_uid, by_test in sorted(failures.items()):
        target_to_failures[target_uid] = [
            item_text[0].uid for item_text in sorted(by_test.keys())
        ]
    destination["unexpected-test-failures"] = target_to_failures


class TestReporter(DocumentBuilder):
    """ Builds a test report. """

    def __init__(self, director: PackageBuildDirector, item: Item):
        super().__init__(director, item)
        self.mapper.add_get_value(f"{self.item.type}:/reports", self._reports)

    def _add_runtime_measurements(self, ctx: _TestContext,
                                  suite_data: dict) -> dict[str, str]:
        uid_to_label: dict[str, str] = {}
        for req_uid, measurement_data in sorted(
                suite_data["runtime-measurements"].items()):
            req = self.item.cache[req_uid]
            with ctx.content.section(f"Runtime measurement - {req.spec_2}",
                                     label=measurement_data["label"]):
                ctx.content.wrap(f"""For the runtime performance requirement
{self.mapper.get_link(req, 'test-plan')}, the following runtime values were
measured on this target and configuration in the listed measurement
environments.""")
                ctx.content.add_image(
                    os.path.relpath(f"{measurement_data['boxplot']}.*",
                                    os.path.dirname(self.file_path)), "50%")
                uid_to_label[req_uid] = ctx.content.get_label()
                limits = ctx.limits_by_req[req.uid]
                for env_name, env_data in sorted(
                        measurement_data["variants"].items(),
                        key=environment_order):
                    ctx.content.add_label(env_data["label"])
                    ctx.content.add_rubric(
                        f"Measurement environment - {env_name}")
                    begin = ctx.output_line_ref(env_data["line-begin"])
                    end = ctx.output_line_ref(env_data["line-end"])
                    ctx.content.add(f"""The runtime measurement report for this
measurement environment was generated from lines {begin} up to and including
{end} of the test output.""")
                    ctx.content.add_image(
                        os.path.relpath(f"{env_data['histogram']}.*",
                                        os.path.dirname(self.file_path)),
                        "50%")
                    ctx.add_limits(env_name, env_data, limits)
        return uid_to_label

    def _add_remarks(self, ctx: _TestContext, remarks: list) -> None:
        if not remarks:
            return
        test_cases: list[tuple[str, str]] = []
        for remark in remarks:
            try:
                uid = remark["uid"]
            except KeyError:
                pass
            else:
                link = self.mapper.get_link(self.item.cache[uid], "test-plan")
                line = ctx.output_line_ref(remark["line"])
                test_cases.append((link, line))
        if len(test_cases) == 1:
            test_case = test_cases[0]
            ctx.content.append(f"""It runs the parameterized test case
{test_case[0]} reported in line {test_case[1]}.""")
            return
        ctx.content.append("It runs the following parameterized test cases:")
        for test_case in test_cases:
            ctx.content.add_list_item(
                f"{test_case[0]} reported in line {test_case[1]}")

    def _add_test_cases(self, ctx: _TestContext, suite_data: dict,
                        uid_to_label: dict[str, str]) -> None:
        for case_uid, case_data in sorted(suite_data["test-cases"].items()):
            case_item = self.item.cache[case_uid]
            ctx.item = case_item
            with ctx.content.section(f"Test case - {case_item.spec_2}",
                                     label=case_data["label"]):
                ctx.content.add(f"""This test case is specified by
{self.mapper.get_link(case_item, 'test-plan')}.""")
                self._add_remarks(ctx, case_data["remarks"])
                begin = ctx.output_line_ref(case_data["line-begin"])
                end = ctx.output_line_ref(case_data["line-end"])
                ctx.content.add(f"""The following table lists an evaluation of
the test case information reported in lines {begin} up to and including {end}
of the test output.""")
                rows = [_HEADER]
                ctx.check(rows, case_data, "Step Count", "step-count", "> 0",
                          str, _check_gt_zero)
                ctx.check(rows, case_data, "Failed Steps Count",
                          "failed-steps-count", "0", str, _check_eq_zero)
                ctx.check(rows, case_data, "Duration", "duration",
                          ":math:`\\geq` 0", duration, _check_duration)
                ctx.add_table(rows, _WIDTHS)
                uids = set(
                    measurement_data["requirement-uid"]
                    for measurement_data in case_data["runtime-measurements"])
                if uids:
                    ctx.content.wrap("""This test case contains the
following runtime measurements presented in the preceeding sections:""")
                    for uid in sorted(uids):
                        item = self.item.cache[uid]
                        ctx.content.add_list_item(
                            f":ref:`{item.spec_2} <{uid_to_label[uid]}>`")

    def _add_one_test_suite(self, ctx: _TestContext, suite_uid: str,
                            suite_data: dict) -> None:
        suite_item = self.item.cache[suite_uid]
        ctx.item = suite_item
        suite_section = f"Test suite - {suite_item.spec_2}"
        with ctx.content.section(suite_section, label=suite_data["label"]):
            report = suite_data["report"]
            ctx.begin_report(report)
            ctx.content.wrap(f"""This test suite is specified by
{self.mapper.get_link(suite_item)}.""")
            ctx.content.gap = False
            ctx.add_test_info(report["info"])
            begin = ctx.output_line_ref(report["test-suite"]["line-begin"])
            end = ctx.output_line_ref(report["test-suite"]["line-end"])
            ctx.content.wrap(f"""The following table lists an evaluation of the
test suite information reported in lines {begin} up to and including {end} of
the test output.""")
            if suite_data["runtime-measurements"]:
                ctx.content.gap = False
                ctx.content.wrap("""The runtime measurements and test cases
of this test suite are presented in the following sections.""")
            else:
                ctx.content.gap = False
                ctx.content.wrap("""The test cases of this test suite are
presented in the following sections.""")
            rows = [_HEADER]
            info = report["test-suite"]
            ctx.check_compiler(rows, info, "compiler")
            ctx.check_rtems_commit(rows, info)
            ctx.check(rows, info, "BSP", "bsp", _invisible_spaces(ctx.bsp),
                      _invisible_spaces)
            ctx.check(rows, info, "Build Label", "build-label",
                      ctx.build_label, _invisible_spaces)
            ctx.check(rows, info, "Target Hash", "target-hash",
                      ctx.target_hashes_display, _target_hash,
                      ctx.check_target_hash)
            ctx.check_build_options(rows, info)
            ctx.check(rows, info, "Step Count", "step-count", "> 0", str,
                      _check_gt_zero)
            ctx.check(rows, info, "Failed Steps Count", "failed-steps-count",
                      "0", str, _check_eq_zero)
            ctx.check(rows, info, "Duration", "duration", ":math:`\\geq` 0",
                      duration, _check_duration)
            ctx.check(rows, info, "Report Hash", "report-hash",
                      _invisible_spaces(info["report-hash-calculated"]),
                      _invisible_spaces)
            ctx.add_table(rows, _WIDTHS)
            uid_to_label = self._add_runtime_measurements(ctx, suite_data)
            self._add_test_cases(ctx, suite_data, uid_to_label)
            _add_test_output(ctx, report)

    def _add_test_suites(self, ctx: _TestContext) -> None:
        for suite_uid, suite_data in sorted(
                ctx.config_data["test-suites"].items()):
            with ctx.file_scope(self.file_path, suite_data):
                self._add_one_test_suite(ctx, suite_uid, suite_data)

    def _add_test_programs(self, ctx: _TestContext) -> None:
        for uid, report in sorted(ctx.config_data["test-programs"].items()):
            with ctx.file_scope(self.file_path, report) as file_name:
                program_item = self.item.cache[uid]
                ctx.item = program_item
                program_section = f"Test program - {program_item.spec_2}"
                with ctx.content.section(program_section, label=file_name):
                    ctx.begin_report(report)
                    ctx.add_test_info(report["info"])
                    for image in report.get("images", []):
                        ctx.content.add_image(
                            os.path.relpath(f"{image}.*",
                                            os.path.dirname(self.file_path)),
                            "50%")
                    _add_test_output(ctx, report)

    def _add_other_programs(self, ctx: _TestContext) -> None:
        for executable, report in sorted(
                ctx.config_data["other-programs"].items()):
            with ctx.file_scope(self.file_path, report) as file_name:
                program_section = f"Other program - {executable}"
                with ctx.content.section(program_section, label=file_name):
                    ctx.begin_report(report)
                    _add_output(ctx, report)

    def _add_coverage(self, ctx: _TestContext,
                      test_aggregator: TestAggregator) -> None:
        with ctx.content.section("Coverage data"):
            coverage_count = 0
            anchors = test_aggregator.anchor_target_uids(self.mapper)
            with ctx.content.directive("toctree"):
                report = {"report-file": "coverage"}
                with ctx.file_scope(self.file_path, report):
                    with ctx.content.label_scope("Coverage"):
                        for target_data in test_aggregator.targets.values():
                            ctx.verifications = target_data[
                                "test-error-verifications"]
                            target_uid = target_data["uid"]
                            target_item = self.item.cache[target_uid]
                            target_section = f"Target - {target_data['name']}"
                            failure_key = (
                                target_item,
                                "For this target, the following code "
                                "coverage issues were present.")
                            issues: dict[
                                str, set[str]] = ctx.unexpected_failures.get(
                                    target_uid, {}).get(failure_key, {})
                            not_run_scopes: set[str] = set()
                            with ctx.content.section(target_section):
                                for config_data in target_data["configs"]:
                                    if "coverage" not in config_data:
                                        continue
                                    coverage_count += 1
                                    not_run_scopes.update(
                                        f"Scope - {coverage['scope']}"
                                        for coverage in config_data["coverage"]
                                        if coverage.get("not-run-groups", []))
                                    test_aggregator.add_coverage_of_config(
                                        ctx.content, self.mapper, config_data,
                                        issues)
                            if not_run_scopes and not anchors:
                                issues.setdefault(
                                    "Coverage limits met only with an "
                                    "excluded test, and no target gives "
                                    "complete evidence",
                                    set()).update(not_run_scopes)
                            if issues:
                                ctx.unexpected_failures.setdefault(
                                    target_uid, {})[failure_key] = issues
                        if coverage_count:
                            test_aggregator.add_coverage_across_targets(
                                ctx.content, self.mapper)
            if coverage_count == 0:
                ctx.content.add("There is no coverage data available.")

    def _reports(self, _unused: ItemGetValueContext) -> str:
        test_aggregator = self.input("test-aggregation")
        assert isinstance(test_aggregator, TestAggregator)
        ctx = _TestContext(self)
        for target_uid, target_data in test_aggregator.targets.items():
            ctx.limits_uid = target_data["limits-uid"]
            ctx.limits_by_req = target_data["limits-by-requirement"]
            ctx.target_hashes = ("\u200b", ) + tuple(
                _invisible_spaces(text) for text in target_data["target-hash"])
            ctx.target_hashes_display = ", ".join(ctx.target_hashes[1:])
            ctx.target_uid = target_uid
            ctx.verifications = target_data["test-error-verifications"]
            with ctx.content.section(f"Target - {target_data['name']}",
                                     label=target_data["label"]):
                with ctx.content.section("Test procedure description"):
                    ctx.content.add(target_data["test-runner-description"])
                for config_data in target_data["configs"]:
                    ctx.config_data = config_data
                    config_key = config_data["config-key"]
                    config_section = f"Configuration - {config_key}"
                    ctx.build_label = _invisible_spaces(
                        config_data["build-label"])
                    with ctx.content.section(config_section,
                                             label=config_data["label"]):
                        with ctx.content.directive("toctree"):
                            self._add_test_suites(ctx)
                            self._add_test_programs(ctx)
                            self._add_other_programs(ctx)
            ctx.check_validations_by_test(test_aggregator, target_uid)
        self._add_coverage(ctx, test_aggregator)
        ctx.add_failures("expected", ctx.expected_failures, test_aggregator)
        ctx.add_failures("unexpected", ctx.unexpected_failures,
                         test_aggregator)
        _save_unexpected_failures(self, ctx.unexpected_failures)
        return ctx.content.join()
