# SPDX-License-Identifier: BSD-2-Clause
""" Runs test executables using a test runner specification item. """

# Copyright (C) 2026 embedded brains GmbH & Co. KG
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

import argparse
import functools
import hashlib
import json
import logging
import os
from pathlib import Path
import re
import sys
import time
from typing import Any

from specitems import hash_file, is_enabled, load_data

from .ctrf import (CTRF_FAILED, convert_test_log, ctrf_markdown_summary,
                   get_ctrf_tool_version)
from .runtests import (RunnerExecutable, RunnerReport, run_subprocess_tests,
                       run_tests_with_retries, select_command)
from .testoutputparser import augment_report
from .util import command_arguments, command_name, now_utc, write_json

_UID = "run-tests"

_VARIABLE = re.compile(r"\$\{[^}]*\}")

_TEST_EXECUTABLE = "${.:/test-executable}"

_EPILOG = """\
example:
  The command of a subprocess test runner item uses substitution variables:

      command:
      - ${/pkg/deployment/qemu:/directory}/bin/qemu-system-arm
      - -machine
      - ${.:/component/machine}
      - enabled-by: RTEMS_SMP
        value:
        - -RTEMS_SMP
        - '4'
      - -kernel
      - ${.:/test-executable}

  Outside a package build directory there are no items to substitute, so
  every variable except the test executable needs a value.  The
  substitutions file provides them without the ${ and }:

      /pkg/deployment/qemu:/directory: /opt/qemu
      .:/component/machine: xilinx-zynq-a9

  The command uses an argument with a condition only if the enabled set
  fulfils the condition.  The -E option adds a name to the enabled set,
  which is empty by default.

  Run the test programs of two directories with a machine of the command
  line and with the arguments enabled by RTEMS_SMP:

      specruntests --substitutions substitutions.yml \\
          -D '.:/component/machine=virt' -E RTEMS_SMP \\
          --ctrf report.ctrf.json runner.yml tests more-tests
"""

_Data = dict[str, Any]


class RunTestsError(Exception):
    """ Indicates an invalid usage of the command. """


def _get_arguments(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=cliruntests.__doc__,
        epilog=_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--substitutions",
                        help="the path to a YAML file which maps substitution "
                        "variables to values; give the key without the ${ and "
                        "}, for example "
                        "\"/pkg/deployment/qemu:/directory: /opt/qemu\"")
    parser.add_argument("-D",
                        "--define",
                        action="append",
                        default=[],
                        metavar="KEY=VALUE",
                        help="map a substitution variable to a value; give "
                        "the key without the ${ and }, for example "
                        "-D '/pkg/deployment/qemu:/directory=/opt/qemu'; "
                        "overrides the substitutions file")
    parser.add_argument("-E",
                        "--enable",
                        action="append",
                        default=[],
                        metavar="NAME",
                        help="add the name to the enabled set, which "
                        "decides the command arguments with a condition")
    parser.add_argument("--test-timeouts",
                        help="the path to a YAML file which provides the "
                        "measured test durations")
    parser.add_argument("--timeout-key",
                        default="default",
                        help="the key of the test timeouts to use "
                        "(default: default)")
    parser.add_argument("-o",
                        "--output",
                        default="test-log.json",
                        help="the path to the test log file "
                        "(default: test-log.json)")
    parser.add_argument("--reuse",
                        help="the path to a test log file; the report of an "
                        "executable with an unchanged hash is reused")
    parser.add_argument("--ctrf",
                        help="the path to a test report file in the Common "
                        "Test Report Format")
    parser.add_argument("--summary",
                        action="store_true",
                        help="print a short summary in CommonMark to "
                        "standard output")
    parser.add_argument("--app-name", default="", help="the CTRF application")
    parser.add_argument("--build-name", default="", help="the CTRF build")
    parser.add_argument("-v",
                        "--verbose",
                        action="store_true",
                        help="be verbose")
    parser.add_argument("runner",
                        metavar="RUNNER",
                        help="the path to a subprocess test runner "
                        "specification item")
    parser.add_argument("directories",
                        metavar="DIRECTORY",
                        nargs="+",
                        help="the paths to the directories with test "
                        "executables")
    return parser.parse_args(argv)


def _check_key(key: str) -> str:
    """
    Check that the key is a substitution variable without the delimiters.

    An empty key or a key which keeps the delimiters would form a variable no
    command contains, so it would silently substitute nothing.
    """
    if not key:
        raise RunTestsError("a substitution key must not be empty")
    if "${" in key or "}" in key:
        raise RunTestsError(f"the substitution key '{key}' must not contain "
                            "the ${ and } of the variable")
    return key


def _get_substitutions(args: argparse.Namespace) -> dict[str, str]:
    substitutions: dict[str, str] = {}
    if args.substitutions:
        data = load_data(args.substitutions)
        substitutions.update({
            _check_key(key): str(value)
            for key, value in data.items()
        })
    for define in args.define:
        key, separator, value = define.partition("=")
        if not separator:
            raise RunTestsError(
                f"the definition '{define}' is not a KEY=VALUE pair")
        substitutions[_check_key(key)] = value
    return substitutions


def _substitute(command: list[str],
                substitutions: dict[str, str],
                executable: str,
                check: bool = True) -> list[str]:
    """
    Substitute the variables of the command.

    Only the test executable variable and the variables of the substitutions
    are known.  Raise an error if a variable remains, so that a wrong command
    is not executed.  The description of the test procedure keeps a placeholder
    for the test executable, so it is not checked.
    """
    parts: list[str] = []
    for part in command:
        part = part.replace(_TEST_EXECUTABLE, executable)
        for key, value in substitutions.items():
            part = part.replace(f"${{{key}}}", value)
        match = _VARIABLE.search(part)
        if check and match:
            variable = match.group(0)
            raise RunTestsError(
                f"there is no substitution for {variable} in the command part "
                f"'{part}'; define it with -D '{variable[2:-1]}=VALUE'")
        parts.append(part)
    return parts


def _get_timeouts(args: argparse.Namespace) -> dict[str, list[float]]:
    if not args.test_timeouts:
        return {}
    data = load_data(args.test_timeouts)
    try:
        return data["timeouts"][args.timeout_key]
    except KeyError as err:
        raise RunTestsError(
            f"the test timeouts file '{args.test_timeouts}' has no timeouts "
            f"for the key '{args.timeout_key}'") from err


def _get_timeout(runner: _Data, timeouts: dict[str, list[float]],
                 name: str) -> float:
    try:
        timeout = max(timeouts[name])
    except (KeyError, ValueError):
        timeout = runner["default-timeout-in-seconds"]
    return runner["timeout-scaler"] * max(timeout,
                                          runner["min-timeout-in-seconds"])


def _get_do_not_run(runner: _Data) -> set[str]:
    """
    Get the names of the test executables which do not run.

    An entry of the list is either a plain name or a group which names its
    test executables and the reason why they do not run.
    """
    names: set[str] = set()
    for entry in runner.get("do-not-run", []):
        if isinstance(entry, str):
            names.add(entry)
        else:
            names.update(entry["executables"])
    return names


def _did_not_run(path: str, digest: str) -> RunnerReport:
    report: RunnerReport = {
        "executable": path,
        "executable-sha512": digest,
        "command-line": "",
        "start-time": now_utc(),
        "output": ["This executable did not run."],
        "duration": 0.0,
        "do-not-run": True
    }
    augment_report(report, report["output"])
    return report


def _get_previous_reports(path: str,
                          runner_hash: str) -> dict[str, RunnerReport]:
    """
    Get the reusable reports of a previous test log by executable hash.

    Reports of a test log produced by a different test runner are not reusable,
    otherwise a changed command would silently yield the results of the
    previous command.
    """
    if not path:
        return {}
    reports_by_hash: dict[str, RunnerReport] = {}
    try:
        with open(path, "r", encoding="utf-8") as src:
            test_log = json.load(src)
    except FileNotFoundError:
        logging.warning("%s: no test log to reuse: %s", _UID, path)
        return reports_by_hash
    except json.JSONDecodeError as err:
        raise RunTestsError(
            f"the test log '{path}' to reuse is not valid JSON: {err}"
        ) from err
    previous_hash = test_log.get("test-runner-hash", "")
    if previous_hash != runner_hash:
        logging.warning(
            "%s: cannot reuse the reports of '%s', it used the test runner "
            "%s and this is the test runner %s", _UID, path, previous_hash[:16]
            or "?", runner_hash[:16])
        return reports_by_hash
    for report in test_log["reports"]:
        reports_by_hash[report["executable-sha512"]] = report
    return reports_by_hash


def _find_executables(directories: list[str]) -> list[str]:
    """
    Get the test executables of the directories.

    A directory may contain another one of the list, so normalize the paths and
    yield each executable once.  Running one executable twice would turn the
    second run into a failed attempt of the first.
    """
    paths: set[str] = set()
    for directory in directories:
        if not os.path.isdir(directory):
            raise RunTestsError(
                f"'{directory}' is not a directory with test executables")
        paths.update(
            os.path.normpath(str(found))
            for found in Path(directory).rglob("*.exe")
            if not found.name.endswith(".norun.exe"))
    return sorted(paths)


def _gather(
        args: argparse.Namespace, runner: _Data, timeouts: dict[str,
                                                                list[float]],
        runner_hash: str) -> tuple[list[RunnerReport], list[RunnerExecutable]]:
    """ Gather the reusable reports and the executables to run. """
    do_not_run = _get_do_not_run(runner)
    previous_reports = _get_previous_reports(args.reuse, runner_hash)
    reports: list[RunnerReport] = []
    executables: list[RunnerExecutable] = []
    for path in _find_executables(args.directories):
        name = os.path.basename(path)
        digest = hash_file(path)
        report = previous_reports.get(digest, None)
        if report is not None:
            logging.info("%s: use previous report for: %s", _UID, path)
            report["executable"] = path
            reports.append(report)
        elif name in do_not_run:
            logging.info("%s: do not run: %s", _UID, path)
            reports.append(_did_not_run(path, digest))
        else:
            executables.append(
                RunnerExecutable(path, digest,
                                 _get_timeout(runner, timeouts, name)))
    if not reports and not executables:
        directories = ", ".join(f"'{path}'" for path in args.directories)
        raise RunTestsError(
            f"there is no test executable in {directories}; a report of no "
            "test at all would say that the tests passed")
    return reports, executables


def _runner_hash(command: list[str], substitutions: dict[str, str]) -> str:
    state = hashlib.sha512()
    state.update(
        json.dumps({
            "command": command,
            "substitutions": substitutions
        },
                   sort_keys=True).encode("utf-8"))
    return state.hexdigest()


def _describe(command: list[str]) -> str:
    parts = " ".join(f"'{part}'" if " " in part else part for part in command)
    return f"""For each test program, this test procedure runs the following
command as a subprocess and captures the output:

.. code-block:: none

    {parts}"""


def _run(args: argparse.Namespace) -> _Data:
    runner = load_data(args.runner)
    if runner.get("test-runner-type", "") != "subprocess":
        raise RunTestsError(
            f"the item '{args.runner}' is not a subprocess test runner")
    substitutions = _get_substitutions(args)
    timeouts = _get_timeouts(args)
    enabled_set = set(args.enable)
    command = select_command(runner["command"],
                             functools.partial(is_enabled, enabled_set))

    def get_command(executable: RunnerExecutable) -> list[str]:
        return _substitute(command, substitutions, executable.path)

    def run_tests(executables: list[RunnerExecutable]) -> list[RunnerReport]:
        return run_subprocess_tests(executables, get_command,
                                    runner.get("discard-patterns", []),
                                    runner["max-process-count"], _UID)

    runner_hash = _runner_hash(command, substitutions)
    start_time = now_utc()
    begin = time.monotonic()
    reports, executables = _gather(args, runner, timeouts, runner_hash)
    reports.extend(
        run_tests_with_retries(executables, run_tests,
                               runner["max-retry-count-per-executable"] + 1,
                               _UID))
    return {
        "duration":
        time.monotonic() - begin,
        "end-time":
        now_utc(),
        "reports":
        sorted(reports, key=lambda report: report["executable"]),
        "start-time":
        start_time,
        "test-runner-description":
        _describe(_substitute(command, substitutions, "${test_program}",
                              False)),
        "test-runner-hash":
        runner_hash
    }


def _write_outputs(args: argparse.Namespace, test_log: _Data) -> int:
    write_json(args.output, test_log)
    report = convert_test_log(test_log, get_ctrf_tool_version(), {
        "appName": args.app_name,
        "buildName": args.build_name
    })
    if args.ctrf:
        write_json(args.ctrf, report)
    if args.summary:
        print(ctrf_markdown_summary(report))
    return 1 if report["results"]["summary"][CTRF_FAILED] else 0


def cliruntests(argv: list[str] | None = None) -> int:
    """ Run test executables using a subprocess test runner item. """
    args = _get_arguments(command_arguments(argv))
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(message)s")
    try:
        return _write_outputs(args, _run(args))
    except RunTestsError as err:
        print(f"{command_name(argv)}: error: {err}", file=sys.stderr)
        return 2
