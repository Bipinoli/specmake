# SPDX-License-Identifier: BSD-2-Clause
""" Aggregates test results. """

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

import copy
import hashlib
import itertools
import logging
import os
from typing import Any

from specitems import (Item, ROW_SPAN, SphinxContent, TextContent,
                       link_is_enabled, make_label, to_collection)
from specware import CodeMapper

from .directorystate import DirectoryState
from .notruncoverage import (add_coverage_across_targets, add_not_run_section,
                             is_complete_evidence, not_run_by_scope_of,
                             not_run_issues, not_run_spots)
from .pkgitems import BuildItem, BuildItemMapper, PackageBuildDirector
from .rtems import RTEMSItemCache
from .sphinxbuilder import spacify

_Configs = dict[BuildItem, dict[str, list[DirectoryState]]]
_Results = dict[BuildItem, _Configs]
_Data = dict[str, Any]
_SpotToJustification = dict[str, tuple[str, str]]
_FileToSpotJustification = dict[str, _SpotToJustification]


def _add_link(some_data: _Data, report_data: _Data, label: str) -> None:
    some_data["link"] = f"{report_data['report-file']}.html#{label.lower()}"


def _set_limits_and_target_hash(target_data: dict, target: Item) -> None:
    try:
        limits = target.parent("performance-runtime-limits-provider")
    except IndexError as err:
        raise ValueError(
            f"target item {target.uid} has no performance runtime limits"
        ) from err
    assert limits.type == "performance-runtime-limits-provider"
    limits_by_req = {}
    for link in limits.links_to_parents("performance-runtime-limits"):
        limits_by_req[link.item.uid] = link["limits"]
    target_data["limits-by-requirement"] = limits_by_req
    target_data["limits-uid"] = limits.uid
    target_data["target-hash"] = to_collection(target["target-hash"])


def _test_status(target_data: dict, target: Item, info: dict,
                 verifications: dict[str, str]) -> str:
    link = target_data["link"]
    if info["failed-steps-count"] == 0:
        status = "P"
    elif info.get("uid", None) in verifications:
        status = "X"
    else:
        target.view["no-unexpected-test-failures"] = False
        target.view["validation-status"] = (
            "at least one unexpected test failure", link)
        return "F"
    target.view.setdefault("no-unexpected-test-failures", True)
    target.view.setdefault("validation-status",
                           ("no unexpected test failures", link))
    return status


def get_test_result_status(item: Item,
                           mapper: BuildItemMapper,
                           prefix: str = "(",
                           postfix: str = ")") -> str:
    """ Gets the test result status of the item. """
    results: list[str] = []
    for test_results in item.view.get("test-results", {}).values():
        for data in test_results:
            results.append(mapper.format_link(data["status"], data["link"]))
    if not results:
        return "**no test results**"
    return f"{prefix}{', '.join(results)}{postfix}"


def _update_measurement_status(measurement_data: _Data, env_data: _Data,
                               limits: _Data) -> None:
    if limits["min-lower-bound"] <= env_data[
            "min"] and limits["median-lower-bound"] <= env_data[
                "q2"] <= limits["median-upper-bound"] and env_data[
                    "max"] <= limits["max-upper-bound"]:
        return
    measurement_data["status"] = "F"


def _gather_test_error_verifications(item: Item,
                                     verifications: dict[str, str]) -> None:
    for item_2 in itertools.chain(item.children("verification-member"),
                                  item.parents("verification-provider")):
        _gather_test_error_verifications(item_2, verifications)
    for item_2 in item.parents("verification",
                               is_link_enabled=link_is_enabled):
        assert item_2.uid not in verifications
        verifications[item_2.uid] = item.uid


def _gather_coverage_gap_verifications(
        uid: str, target: Item,
        verifications: dict[str, _FileToSpotJustification]) -> None:
    for child in itertools.chain(target.parents("verification-by"),
                                 target.children("verification")):
        if not child.type.startswith("verification/code-coverage-gap"):
            continue
        for scope_name, scope in child["areas"].items():
            for file_path, file in scope.items():
                logging.info(
                    "%s: for target %s gather code coverage gap "
                    "verifications from %s for file: %s", uid, target.uid,
                    child.uid, file_path)
                gaps: _SpotToJustification = {}
                for line in file["lines"]:
                    line_number = line["line"]
                    logging.info(
                        "%s: add line coverage gap justification at %s", uid,
                        line_number)
                    gaps[f"line/{line_number}"] = child.uid, line["md5"]
                for branches in file["branches"]:
                    line_number = branches["line"]
                    for branch in branches["branches"]:
                        line_branch = f"{line_number}/{branch}"
                        logging.info(
                            "%s: add branch coverage gap justification at %s",
                            uid, line_branch)
                        gaps[f"branch/{line_branch}"] = child.uid, branches[
                            "md5"]
                for function_name in file["functions"]:
                    logging.info(
                        "%s: add function coverage gap justification for %s()",
                        uid, function_name)
                    gaps[f"function/{function_name}"] = child.uid, ""
                verifications.setdefault(scope_name, {})[file_path] = gaps


def _add_coverage_table(content: SphinxContent, mapper: BuildItemMapper,
                        none: str, some: str,
                        stats_of_files: list[dict]) -> None:
    if not stats_of_files:
        content.add(none)
        return
    content.add(some)
    rows = [[
        "File", "Functions", "Status", "Lines", "Status", "Branches", "Status"
    ]]
    for stats in stats_of_files:
        row = [
            mapper.format_link(spacify(stats["file-path"]), stats["file-link"])
        ]
        for kind in _COVERAGE_KINDS:
            row.append(stats[f"{kind}-info"])
            row.append(stats[f"{kind}-status"])
        rows.append(row)
    content.add_grid_table(rows, [34, 13, 7, 13, 7, 13, 7], font_size=-3)


_COVERAGE_KINDS = ("function", "line", "branch")


class _CoverageSummary:
    # pylint: disable=too-many-instance-attributes

    def __init__(self, test_aggregator: "TestAggregator",
                 mapper: BuildItemMapper, coverage: dict) -> None:
        self.test_aggregator = test_aggregator
        self.scope = coverage["scope"]
        self.verifications = copy.deepcopy(coverage["verifications"])
        self.html_directory = coverage["html-directory"]
        self.limits_by_area = coverage["limits-by-area"]
        self.not_run_groups = coverage.get("not-run-groups", [])
        self.not_run_spots = not_run_spots(self.not_run_groups)
        self.not_run_counts = [{
            "function": 0,
            "line": 0,
            "branch": 0
        } for _ in self.not_run_groups]
        self.good_files: list[dict] = []
        self.justified_files: list[dict] = []
        self.not_run_files: list[dict] = []
        self.bad_files: list[dict] = []
        self.overall: dict = {}
        self.issues: dict[str, set[str]] = {}
        self._spots_of_file: dict[str, int] = {}
        for kind in _COVERAGE_KINDS:
            self.overall[f"{kind}-covered"] = 0
            self.overall[f"{kind}-justified"] = 0
            self.overall[f"{kind}-not-run"] = 0
            self.overall[f"{kind}-total"] = 0
            self.overall[f"per-file-{kind}-covered"] = 0
            self.overall[f"per-file-{kind}-justified"] = 0
            self.overall[f"per-file-{kind}-not-run"] = 0
            self.overall[f"per-file-{kind}-total"] = 0
        for file_coverage in coverage["files"]:
            self._add_coverage_of_file(mapper, file_coverage)
        limits = self.limits_by_area["overall"]
        for kind in _COVERAGE_KINDS:
            self.overall[f"{kind}-justified-covered"] = self.overall[
                f"{kind}-covered"]
            self._add_coverage_status(mapper, self.overall,
                                      limits[f"{kind}-min-percent"], True,
                                      kind)
        self._add_not_run_issues()
        if self.verifications:
            unused: list[str] = sorted(
                set(justification[0]
                    for spot_to_justification in self.verifications.values()
                    for justification in spot_to_justification.values()))
            logging.warning(
                "%s: for %s there are unused code coverage justifications: %s",
                self.test_aggregator.uid, coverage["target-uid"], unused)
            self.issues.setdefault("Unused code coverage justifications",
                                   set()).update(f"spec:{spacify(uid)}"
                                                 for uid in unused)

    def _add_not_run_issues(self) -> None:
        """ Add the issues of the excluded tests. """
        for key, names in not_run_issues(self.not_run_groups).items():
            self.issues.setdefault(key, set()).update(names)

    def add_not_run_section(self, content: SphinxContent) -> None:
        """ Add the section which states the excluded tests of the target. """
        add_not_run_section(content, self.scope, self.not_run_groups,
                            self.not_run_counts)

    def get_issues(self, issues: dict[str, set[str]]) -> None:
        """ Get the detected coverage issues. """
        for key, items in self.issues.items():
            issues.setdefault(key, set()).update(items)

    def add_coverage_section(self, content: SphinxContent,
                             mapper: BuildItemMapper) -> None:
        """ Add a coverage section to the content. """
        with content.section(f"Scope - {self.scope}"):
            if any((self.good_files, self.justified_files, self.not_run_files,
                    self.bad_files)):
                _add_coverage_table(
                    content, mapper,
                    "There are no files with unjustified coverage issues.",
                    "The following table lists files "
                    "with unjustified coverage issues.", self.bad_files)
                _add_coverage_table(
                    content, mapper,
                    "There are no files with justified coverage issues.",
                    "The following table lists files "
                    "with justified coverage issues.", self.justified_files)
                _add_coverage_table(
                    content, mapper,
                    "There are no files with coverage issues justified by an "
                    "excluded test.",
                    "The following table lists files with coverage issues "
                    "justified by an excluded test.", self.not_run_files)
                _add_coverage_table(
                    content, mapper,
                    "There are no files without coverage issues.",
                    "The following table lists files "
                    "having the expected coverage.", self.good_files)
            else:
                content.add("There is no coverage information available.")

    def _add_no_coverage_data(self, stats: dict, overall: bool, kind: str,
                              per_file_total: int) -> None:
        if overall:
            stats[f"{kind}-status"] = "**NOK**"
            stats[f"{kind}-error"] = True
            stats["error"] = True
            if per_file_total:
                info = f"No general {kind} information in coverage data"
            else:
                info = f"No {kind} information in coverage data"
            self.issues.setdefault(info, set()).add(f"Scope - {self.scope}")
        else:
            stats[f"{kind}-status"] = "OK"

    def _add_coverage_status(self, mapper: BuildItemMapper, stats: dict,
                             limit: float, overall: bool, kind: str) -> None:
        # pylint: disable=too-many-arguments
        # pylint: disable=too-many-positional-arguments
        # pylint: disable=too-many-locals
        total = stats[f"{kind}-total"]
        per_file_total = stats.get(f"per-file-{kind}-total", 0)
        if total + per_file_total == 0:
            stats[f"{kind}-info"] = "N/A"
            self._add_no_coverage_data(stats, overall, kind, per_file_total)
            return

        per_file_info = ""
        if per_file_total:
            per_file_covered = stats.get(f"per-file-{kind}-covered", 0)
            per_file_justified = stats.get(f"per-file-{kind}-justified", 0)
            per_file_info = f"{per_file_info} [{per_file_covered}"
            if per_file_justified:
                per_file_info = f"{per_file_info}+{per_file_justified}"
            per_file_info = f"{per_file_info}/{per_file_total}]"

        covered = stats[f"{kind}-covered"]
        info = str(covered)
        justified = stats[f"{kind}-justified"]
        if justified != 0:
            info = f"{info}+{justified}"
        info = f"{info}/{total}"
        both = covered + justified
        if both == total:
            if total:
                stats[f"{kind}-info"] = f"{info} (100%){per_file_info}"
                stats[f"{kind}-status"] = "OK"
            else:
                stats[f"{kind}-info"] = f"{info} (N/A){per_file_info}"
                self._add_no_coverage_data(stats, overall, kind,
                                           per_file_total)
            return

        # Make sure we never display 100.0% if not everything is covered
        percent = float((1000 * both) // total) / 10.0

        if percent >= limit:
            status = "OK"
        else:
            status = "**NOK**"
            stats[f"{kind}-error"] = True
            stats["error"] = True
            if overall:
                self.overall[f"{kind}-error"] = True
                self.issues.setdefault(f"Insufficient overall {kind} coverage",
                                       set()).add(f"Scope - {self.scope}")
            else:
                self.issues.setdefault(
                    f"Insufficient file-specific {kind} coverage", set()).add(
                        mapper.format_link(spacify(stats["file-path"]),
                                           stats["file-link"]))
        stats[f"{kind}-info"] = f"{info} ({percent:.1f}%){per_file_info}"
        stats[f"{kind}-status"] = status

    def _add_file_stats(self, mapper: BuildItemMapper,
                        stats: dict[str, int | str], file_path: str,
                        spot_to_justification: _SpotToJustification) -> None:
        # Files with explicit coverage limits are excluded from the general
        # overall coverage accounting and shown separately in [...] brackets.
        limits = self.limits_by_area.get(f"file-{file_path}")
        if limits is None:
            limits = self.limits_by_area["per-file"]
            overall_scope = ""
        else:
            overall_scope = "per-file-"
        for kind in _COVERAGE_KINDS:
            for what in ("covered", "justified", "not-run", "total"):
                key = f"{kind}-{what}"
                self.overall[f"{overall_scope}{key}"] += stats[key]
            self._add_coverage_status(mapper, stats,
                                      limits[f"{kind}-min-percent"], False,
                                      kind)
        if spot_to_justification:
            unrelated: list[str] = sorted(
                set(justification[0]
                    for justification in spot_to_justification.values()))
            logging.warning(
                "%s: for file %s there are unrelated "
                "code coverage justifications: %s", self.test_aggregator.uid,
                file_path, unrelated)
            self.issues.setdefault("Unrelated code coverage justifications",
                                   set()).update(f"spec:{spacify(uid)}"
                                                 for uid in unrelated)
        if "error" in stats:
            self.bad_files.append(stats)
        elif "not-run" in stats:
            self.not_run_files.append(stats)
        elif "justified" in stats:
            self.justified_files.append(stats)
        else:
            self.good_files.append(stats)

    def _take_not_run_spot(self, stats: dict, spot: str, kind: str) -> bool:
        """
        Take the spot as reached by an excluded test.

        Return True if an excluded test of this target reaches the spot on
        another target.
        """
        index = self._spots_of_file.get(spot, None)
        if index is None:
            return False
        stats["not-run"] = True
        stats[f"{kind}-justified"] += 1
        stats[f"{kind}-not-run"] += 1
        self.not_run_counts[index][kind] += 1
        return True

    def _add_line_stats(self, stats: dict, line: dict,
                        spot_to_justification: _SpotToJustification) -> None:
        if line["count"] > 0:
            stats["line-covered"] += 1
        else:
            file_path = stats["file-path"]
            line_no = line["line_number"]
            justification = spot_to_justification.pop(f"line/{line_no}", None)
            if justification is None:
                if self._take_not_run_spot(stats, f"line/{line_no}", "line"):
                    return
                logging.info(
                    "%s: no line coverage gap justification for %s:%s",
                    self.test_aggregator.uid, file_path, line_no)
            else:
                uid = justification[0]
                logging.info(
                    "%s: use line coverage gap "
                    "justification %s for %s:%s", self.test_aggregator.uid,
                    uid, file_path, line_no)
                if line["gcovr/md5"] == justification[1]:
                    stats["justified"] = True
                    stats["line-justified"] += 1
                else:
                    logging.warning(
                        "%s: out of date line coverage gap "
                        "justification %s for %s:%s", self.test_aggregator.uid,
                        uid, file_path, line_no)
                    self.issues.setdefault(
                        "Out of date line coverage gap justifications",
                        set()).add(f"spec:{spacify(uid)}")

    def _add_branch_stats(self, stats: dict, line: dict, branch: dict,
                          spot_to_justification: _SpotToJustification) -> None:
        stats["branch-total"] += 1
        if branch["count"] > 0:
            stats["branch-covered"] += 1
        else:
            file_path = stats["file-path"]

            # Since GCC 14, the JSON gcov output is used by gcovr.  In this
            # case, branches are identified by a "source_block_id" and
            # "destination_block_id" pair.  The "source_block_id" is the same
            # for all branches of a line.  In GCC 13 or earlier, a "branchno"
            # is used.  This means that the branch identification depends on
            # the target GCC version.
            branchno = branch.get("destination_block_id",
                                  branch.get("branchno", -1))

            line_branch = f"{line['line_number']}/{branchno}"
            justification = spot_to_justification.pop(f"branch/{line_branch}",
                                                      None)
            if justification is None:
                if self._take_not_run_spot(stats, f"branch/{line_branch}",
                                           "branch"):
                    return
                logging.info(
                    "%s: no branch coverage gap justification for %s:%s",
                    self.test_aggregator.uid, file_path, line_branch)
            else:
                uid = justification[0]
                logging.info(
                    "%s: use branch coverage gap "
                    "justification %s for %s:%s", self.test_aggregator.uid,
                    uid, file_path, line_branch)
                if line["gcovr/md5"] == justification[1]:
                    stats["justified"] = True
                    stats["branch-justified"] += 1
                else:
                    logging.warning(
                        "%s: out of date branch coverage gap "
                        "justification %s for %s:%s", self.test_aggregator.uid,
                        uid, file_path, line_branch)
                    self.issues.setdefault(
                        "Out of date branch coverage gap justifications",
                        set()).add(f"spec:{spacify(uid)}")

    def _add_function_stats(
            self, stats: dict, function: dict,
            spot_to_justification: _SpotToJustification) -> None:
        execution_count = function.get("execution_count", None)
        if execution_count is None:
            # Sometimes gcov is unable to find an associated name for some
            # function code blocks.  This results in function data with a name
            # of "<unknown function N>" and no execution count.  The code
            # blocks still have line and branch coverage data.
            return
        stats["function-total"] += 1
        if execution_count > 0:
            stats["function-covered"] += 1
        else:
            file_path = stats["file-path"]
            function_name = function["name"]
            justification = spot_to_justification.pop(
                f"function/{function_name}", None)
            if justification is None:
                if self._take_not_run_spot(stats, f"function/{function_name}",
                                           "function"):
                    return
                logging.info(
                    "%s: no function coverage gap "
                    "justification for %s() in %s", self.test_aggregator.uid,
                    function_name, file_path)
            else:
                uid = justification[0]
                logging.info(
                    "%s: use function coverage gap "
                    "justification %s for %s() in %s",
                    self.test_aggregator.uid, uid, function_name, file_path)
                stats["justified"] = True
                stats["function-justified"] += 1

    def _add_coverage_of_file(self, mapper: BuildItemMapper,
                              file_coverage: dict) -> None:
        file_path = file_coverage["file"]
        digest = hashlib.md5(file_path.encode("utf-8"),
                             usedforsecurity=False).hexdigest()
        file_link = f"{os.path.basename(file_path)}.{digest}"
        file_link = f"{self.html_directory}/index.{file_link}.html"
        spot_to_justification = self.verifications.pop(file_path, {})
        self._spots_of_file = self.not_run_spots.get(file_path, {})
        stats = {
            "file-path": file_path,
            "file-link": file_link,
            "branch-covered": 0,
            "branch-justified": 0,
            "branch-not-run": 0,
            "branch-total": 0,
            "function-covered": 0,
            "function-justified": 0,
            "function-not-run": 0,
            "function-total": 0,
            "line-covered": 0,
            "line-justified": 0,
            "line-not-run": 0,
            "line-total": 0
        }
        for line in file_coverage["lines"]:
            stats["line-total"] += 1
            self._add_line_stats(stats, line, spot_to_justification)
            for branch in line["branches"]:
                self._add_branch_stats(stats, line, branch,
                                       spot_to_justification)
        for function in file_coverage["functions"]:
            self._add_function_stats(stats, function, spot_to_justification)
        self._add_file_stats(mapper, stats, file_path, spot_to_justification)


def _limits_order(area_and_limits: tuple) -> str:
    area = area_and_limits[0]
    if area == "overall":
        return "a"
    if area == "per-file":
        return "b"
    return f"c{area}"


class TestAggregator(BuildItem):
    """ Aggregates test results. """

    def __init__(self, director: PackageBuildDirector, item: Item):
        super().__init__(director, item)
        self.report_file: str = self["report-file"]
        self.report_directory = os.path.dirname(self.report_file)
        self.targets: dict[str, dict] = {}
        self.runtime_measurements: list[_Data] = []
        self._summaries: None | dict[str, list] = None
        spec = self.input("spec")
        assert isinstance(spec, RTEMSItemCache)
        self.spec = spec
        for target, configs in sorted(self._gather_results().items()):
            target_key = target["key"]
            label = self._make_label({}, target_key)
            test_error_verifications: dict[str, str] = {}
            _gather_test_error_verifications(target.item,
                                             test_error_verifications)
            coverage_gap_verifications: dict[str,
                                             _FileToSpotJustification] = {}
            _gather_coverage_gap_verifications(self.uid, target.item,
                                               coverage_gap_verifications)
            target_data = {
                "configs": [],
                "key": target_key,
                "label": label,
                "link": self._make_report_link(label),
                "name": CodeMapper(target.item).substitute(target["name"]),
                "uid": target.uid,
                "test-error-verifications": test_error_verifications,
                "coverage-gap-verifications": coverage_gap_verifications
            }
            _set_limits_and_target_hash(target_data, target.item)
            logging.debug("%s: add target %s with hash %s", self.uid,
                          target_data["uid"], target_data["target-hash"])
            self._add_configs_to_target(spec, configs, target_data, target_key)
            self.targets[target.uid] = target_data
        spec.validate_using_test_results()

    def run(self) -> None:
        self.description.add("Aggregate test results.")

    def _add_configs_to_target(self, spec: RTEMSItemCache, configs: _Configs,
                               target_data: dict, target_key: str) -> None:
        for config, results in sorted(configs.items()):
            config_key = config["config-key"]
            label = self._make_label(target_data, config_key)
            config_data = {
                "build-label": config["build-label"],
                "config-key": config_key,
                "description": config["description"],
                "label": label,
                "link": self._make_report_link(label),
                "name": config["name"],
                "other-programs": {},
                "report-file-base": f"{target_key}-{config_key}",
                "target": target_data,
                "test-programs": {},
                "test-suites": {},
            }
            logging.debug("%s: add configuration %s to target %s", self.uid,
                          config_key, target_data["uid"])
            for test_log in results.get("test-log", []):
                self._add_test_reports(spec, test_log, config_data)
            not_run_by_scope = not_run_by_scope_of(results)
            for coverage in results.get("test-coverage", []):
                coverage_data = coverage.json_load()
                scope = coverage["scope"]
                coverage_data["scope"] = scope
                coverage_data["target-uid"] = target_data["uid"]
                coverage_data["limits-by-area"] = coverage["limits"]
                coverage_data["html-directory"] = coverage.output(
                    "html")["directory"]
                coverage_data["verifications"] = target_data[
                    "coverage-gap-verifications"].get(scope, {})
                coverage_data["not-run-groups"] = not_run_by_scope.get(
                    scope, [])
                config_data.setdefault("coverage", []).append(coverage_data)
            target_data["configs"].append(config_data)

    def _make_label(self, data: dict, name: str) -> str:
        return f"{data.get('label', '')}{make_label(name)}"

    def _make_report_link(self, label: str) -> str:
        return f"{self.report_file}#{label.lower()}"

    def _make_report_file(self, config_data: _Data, uid: str) -> str:
        base = config_data["report-file-base"]
        name = uid.replace("/", "-")
        return f"{self.report_directory}/{base}{name}"

    def _gather_results(self) -> _Results:
        results: _Results = {}
        for link, file_state in itertools.chain(
                self.input_links("test-log"),
                self.input_links("test-coverage"),
                self.input_links("not-run-coverage")):
            assert isinstance(file_state, DirectoryState)
            target = file_state.input("target")
            build_config = file_state.input("build-configuration")
            results.setdefault(target,
                               {}).setdefault(build_config, {}).setdefault(
                                   link["name"], []).append(file_state)
        return results

    def _add_test_reports(self, spec: RTEMSItemCache, test_log: DirectoryState,
                          config_data: _Data) -> None:
        logging.debug("%s: process %s", self.uid, test_log.file)
        test_log_data = test_log.json_load()
        description = test_log_data.get("test-runner-description", "")
        target_data = config_data["target"]
        if "test-runner-description" in target_data:
            assert not description or target_data[
                "test-runner-description"] == description
        else:
            target_data["test-runner-description"] = description
        for report in test_log_data["reports"]:
            try:
                test_suite = report["test-suite"]
                test_suite_item = spec.name_to_item[test_suite["name"]]
            except KeyError:
                executable = os.path.basename(report["executable"])
                name = f"file/{executable}"
                try:
                    uid = spec.name_to_item[name].uid
                except KeyError:
                    logging.debug("%s: add other program %s", self.uid,
                                  executable)
                    assert executable not in config_data["other-programs"]
                    report["report-file"] = self._make_report_file(
                        config_data, f"-{executable}")
                    config_data["other-programs"][executable] = report
                else:
                    logging.debug("%s: add test program %s", self.uid, uid)
                    assert uid not in config_data["test-programs"]
                    report["report-file"] = self._make_report_file(
                        config_data, uid)
                    config_data["test-programs"][uid] = report
            else:
                self._process_test_suite(spec, report, config_data, test_suite,
                                         test_suite_item)

    def _process_runtime_measurements(self, spec: RTEMSItemCache,
                                      runtime_measurements: _Data,
                                      config_data: _Data, test_suite: _Data,
                                      test_case: _Data) -> None:
        # pylint: disable=too-many-arguments
        # pylint: disable=too-many-positional-arguments
        # pylint: disable=too-many-locals
        target_data = config_data["target"]
        target_uid = target_data["uid"]
        limits_by_req = target_data["limits-by-requirement"]
        for env_data in test_case["runtime-measurements"]:
            req = spec.name_to_item[env_data["name"]]
            env_data["requirement-uid"] = req.uid
            env_data["test-case"] = test_case
            measurement_data = runtime_measurements.get(req.uid, None)
            if measurement_data is None:
                label = self._make_label(test_suite, req.uid)
                measurement_data = {
                    "config": config_data,
                    "label": label,
                    "requirement-uid": req.uid,
                    "status": "P",
                    "test-case": test_case,
                    "test-suite": test_suite,
                    "variants": {}
                }
                _add_link(measurement_data, test_suite, label)
                runtime_measurements[req.uid] = measurement_data
                req.view.setdefault("test-results",
                                    {}).setdefault(target_uid,
                                                   []).append(measurement_data)
            else:
                test_case_2 = measurement_data["test-case"]
                assert test_case_2["name"] == test_case["name"]
                assert test_case_2["test-suite"]["name"] == test_suite["name"]
            env_name = env_data["variant"]
            measurement_data["variants"][env_name] = env_data
            label = self._make_label(measurement_data, env_name)
            env_data["label"] = label
            _add_link(env_data, test_suite, label)
            _update_measurement_status(measurement_data, env_data,
                                       limits_by_req[req.uid][env_name])
            self.runtime_measurements.append(measurement_data)

    def _process_test_suite(self, spec: RTEMSItemCache, report: Any,
                            config_data: _Data, test_suite: dict[str, Any],
                            test_suite_item: Item) -> None:
        # pylint: disable=too-many-arguments
        # pylint: disable=too-many-positional-arguments
        # pylint: disable=too-many-locals
        logging.debug("%s: process test suite %s", self.uid,
                      test_suite_item.uid)
        target_data = config_data["target"]
        target_uid = target_data["uid"]
        target_item = self.item.cache[target_uid]
        verifications = target_data["test-error-verifications"]
        test_suite["uid"] = test_suite_item.uid
        runtime_measurements: _Data = {}
        test_cases: dict = {}
        unspec_test_cases: list = []
        assert test_suite_item.uid not in config_data["test-suites"]
        label = self._make_label(config_data, test_suite["name"])
        report_file = self._make_report_file(config_data, test_suite_item.uid)
        test_suite_data = {
            "config":
            config_data,
            "label":
            label,
            "report-file":
            report_file,
            "report":
            report,
            "status":
            _test_status(target_data, target_item, test_suite, verifications),
            "runtime-measurements":
            runtime_measurements,
            "test-cases":
            test_cases,
            "unspecified-test-cases":
            unspec_test_cases
        }
        _add_link(test_suite_data, test_suite_data, label)
        config_data["test-suites"][test_suite_item.uid] = test_suite_data
        test_suite_item.view.setdefault("test-results", {}).setdefault(
            target_uid, []).append(test_suite_data)
        test_suite["config"] = config_data
        test_suite["label"] = label
        test_suite["report-file"] = report_file
        _add_link(test_suite, test_suite_data, label)
        for test_case in test_suite["test-cases"]:
            test_case_name = test_case["name"]
            label = self._make_label(test_suite, test_case_name)
            test_case["config"] = config_data
            test_case["label"] = label
            test_case["test-suite"] = test_suite
            _add_link(test_case, test_suite, label)
            no_spec_for_test_case = False
            try:
                test_case_item = spec.name_to_item[test_case_name]
            except KeyError:
                logging.debug("%s: test case without specification %s",
                              self.uid, test_case_name)
                no_spec_for_test_case = True
            else:
                test_case["uid"] = test_case_item.uid
                test_cases[test_case_item.uid] = test_case
                test_case_item.view.setdefault("test-results", {}).setdefault(
                    target_uid, []).append(test_case)
                self._process_runtime_measurements(spec, runtime_measurements,
                                                   config_data, test_suite,
                                                   test_case)
            test_case["status"] = _test_status(target_data, target_item,
                                               test_case, verifications)
            for remark in test_case["remarks"]:
                try:
                    remark_item = spec.name_to_item[remark["remark"]]
                except KeyError:
                    no_spec_for_test_case = True
                else:
                    remark["uid"] = remark_item.uid
                    remark_item.view.setdefault("test-results", {}).setdefault(
                        target_uid, []).append(test_case)
            if no_spec_for_test_case:
                unspec_test_cases.append(test_case)

    def add_coverage_achievement(self, content: TextContent,
                                 mapper: BuildItemMapper) -> None:
        """ Add the code/branch coverage achievement to the content. """
        rows: list[list[str | int]] = [[
            "Target", "Configuration", "Scope", "Functions", "Status", "Lines",
            "Status", "Branches", "Status"
        ]]
        for target_data in self.targets.values():
            target: str | int = mapper.format_link(target_data["name"],
                                                   target_data["link"])
            for config_data in target_data["configs"]:
                key = config_data["config-key"]
                config: str | int = mapper.format_link(key,
                                                       config_data["link"])
                for coverage in config_data.get("coverage", []):
                    summary = _CoverageSummary(self, mapper, coverage)
                    row = [target, config, coverage["scope"]]
                    for kind in _COVERAGE_KINDS:
                        row.append(summary.overall[f"{kind}-info"])
                        row.append(summary.overall[f"{kind}-status"])
                    rows.append(row)
                    config = ROW_SPAN
                    target = ROW_SPAN
        content.add_grid_table(rows, [18, 8, 8, 13, 7, 13, 7, 13, 7],
                               font_size=-3)

    def add_simple_coverage_achievement(self, content: TextContent,
                                        mapper: BuildItemMapper) -> None:
        """
        Add the code/branch coverage achievement to the content as a simple
        table.
        """
        rows: list[list[str]] = [[
            "Target", "Configuration", "Scope", "Functions", "Status", "Lines",
            "Status", "Branches", "Status"
        ]]
        for target_data in self.targets.values():
            target = target_data["name"]
            for config_data in target_data["configs"]:
                key = config_data["config-key"]
                for coverage in config_data.get("coverage", []):
                    summary = _CoverageSummary(self, mapper, coverage)
                    row = [target, key, coverage["scope"]]
                    for kind in _COVERAGE_KINDS:
                        row.append(summary.overall[f"{kind}-info"])
                        row.append(summary.overall[f"{kind}-status"])
                    rows.append(row)
        content.add_simple_table(rows)

    def add_coverage_limits(self, content: TextContent,
                            mapper: BuildItemMapper) -> None:
        """ Add the code/branch coverage limits to the content. """
        rows: list[list[str | int]] = [[
            "Target", "Configuration", "Scope", "Area", "Functions", "Lines",
            "Branches"
        ]]
        for target_data in self.targets.values():
            target: str | int = mapper.format_link(target_data["name"],
                                                   target_data["link"])
            for config_data in target_data["configs"]:
                key = config_data["config-key"]
                config: str | int = mapper.format_link(key,
                                                       config_data["link"])
                for coverage in config_data.get("coverage", []):
                    for area, limits in sorted(
                            coverage["limits-by-area"].items(),
                            key=_limits_order):
                        rows.append([
                            target, config, coverage["scope"],
                            area.removeprefix("file-")
                        ] + [
                            f"{limits[f'{kind}-min-percent']:.1f}%"
                            for kind in _COVERAGE_KINDS
                        ])
                        config = ROW_SPAN
                        target = ROW_SPAN
        content.add_grid_table(rows, [22, 12, 10, 17, 13, 13, 13],
                               font_size=-3)

    def _summaries_of_target(self, mapper: BuildItemMapper) -> dict[str, list]:
        """ Get the coverage summaries of each target. """
        if self._summaries is None:
            self._summaries = dict((uid, [
                _CoverageSummary(self, mapper, coverage)
                for config_data in target_data["configs"]
                for coverage in config_data.get("coverage", [])
            ]) for uid, target_data in self.targets.items())
        return self._summaries

    def anchor_target_uids(self, mapper: BuildItemMapper) -> list[str]:
        """
        Get the targets which carry complete code coverage evidence.

        A target carries complete evidence if it has no unjustified coverage
        issue and if no gap of it rests on an excluded test.  The
        pre-qualification of the variant needs at least one such target.
        """
        return [
            uid
            for uid, summaries in self._summaries_of_target(mapper).items()
            if summaries and all(
                is_complete_evidence(summary) for summary in summaries)
        ]

    def add_coverage_across_targets(self, content: SphinxContent,
                                    mapper: BuildItemMapper) -> None:
        """ Add the code coverage statement over all targets. """
        add_coverage_across_targets(content, mapper, self.targets,
                                    self._summaries_of_target(mapper),
                                    self.anchor_target_uids(mapper))

    def add_coverage_of_config(self, content: SphinxContent,
                               mapper: BuildItemMapper, config_data: _Data,
                               issues: dict[str, set[str]]) -> None:
        """
        Add the code/branch coverage data associated with the configuration
        data to the content.

        Get the detected code coverage issues.
        """
        summaries: list[_CoverageSummary] = []
        with content.section("Overview"):
            rows = [[
                "Scope", "Functions", "Status", "Lines", "Status", "Branches",
                "Status"
            ]]
            for coverage in config_data.get("coverage", []):
                summary = _CoverageSummary(self, mapper, coverage)
                summaries.append(summary)
                summary.get_issues(issues)
                row = [summary.scope]
                for kind in _COVERAGE_KINDS:
                    row.append(summary.overall[f"{kind}-info"])
                    row.append(summary.overall[f"{kind}-status"])
                rows.append(row)
            content.add_grid_table(rows, [34, 13, 7, 13, 7, 13, 7],
                                   font_size=-3)
        for summary in summaries:
            summary.add_coverage_section(content, mapper)
        for summary in summaries:
            summary.add_not_run_section(content)
