# SPDX-License-Identifier: BSD-2-Clause
""" Run tests. """

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

import functools
import json
import logging
import os
from pathlib import Path
import tarfile
import time
from typing import Any

from specitems import data_digest, is_enabled, Item, ItemGetValueContext

from .directorystate import DirectoryState
from .pkgitems import BuildItem, PackageBuildDirector
from .runtests import (RunnerExecutable, RunnerReport, run_subprocess_tests,
                       run_tests_with_retries, select_command)
from .testoutputparser import augment_report
from .util import now_utc


def gather_do_not_run(item: Item) -> list[dict[str, Any]]:
    """
    Gather the do not run entries of the test runner item and of the items
    which link to it.

    Each entry of the result names the test executables of one group, the
    reason why they do not run, and the item which excludes them.  A plain
    name in the specification item states no reason, so the reason of its
    group is None.

    The groups of the test runner item come first in the order of the item.
    The groups of the items which link to it follow in the order of their
    unique identifier, so the result does not depend on the order of the
    links.
    """
    groups: list[dict[str, Any]] = []

    def add(entries: Any, source_uid: str) -> None:
        for entry in entries:
            if isinstance(entry, str):
                executables = [entry]
                justification = None
            else:
                executables = list(entry["executables"])
                justification = entry["justification"]
            groups.append({
                "executables": sorted(executables),
                "justification": justification,
                "source-uid": source_uid
            })

    add(item["do-not-run"], item.uid)
    own = len(groups)
    for link in item.links_to_children("test-runner-do-not-run"):
        add(link["do-not-run"], link.item.uid)
    groups[own:] = sorted(groups[own:],
                          key=lambda group:
                          (group["source-uid"], group["executables"]))
    return groups


def do_not_run_names(groups: list[dict[str, Any]]) -> set[str]:
    """ Get the names of the test executables which do not run. """
    return set(name for group in groups for name in group["executables"])


class TestLog(DirectoryState):
    """ Maintains a test log. """

    def get_reports_by_hash(self) -> tuple[dict[str, RunnerReport], str, str]:
        """
        Get the reports by executable hash and the test runner description.
        """
        reports_by_hash: dict[str, RunnerReport] = {}
        description = "There is no description available."
        runner_hash = ""
        try:
            with open(self.file, "r", encoding="utf-8") as src:
                data = json.load(src)
                description = data.get("test-runner-description", description)
                runner_hash = data.get("test-runner-hash", runner_hash)
                for report in data["reports"]:
                    digest = report["executable-sha512"]
                    assert digest not in reports_by_hash
                    assert isinstance(digest, str)
                    reports_by_hash[digest] = report
        except FileNotFoundError:
            pass
        return reports_by_hash, description, runner_hash


class TestRunner(BuildItem):
    """ Runs tests. """

    def __init__(self, director: PackageBuildDirector, item: Item):
        super().__init__(director, item)
        self._executable = "/dev/null"
        self._executables: list[RunnerExecutable] = []
        self._do_not_run_groups: list[dict[str, Any]] = []
        self.mapper.add_get_value(f"{self.item.type}:/test-executable",
                                  self._get_test_executable)

    def _get_test_executable(self, _ctx: ItemGetValueContext) -> str:
        return self._executable

    def describe(self) -> str:
        """ Return a description of the test runner. """
        return "This test procedure cannot run tests."

    def get_runner_hash(self) -> str:
        """
        Get a hash of the test runner.

        The runner hash is stored in the test log.  If the current runner hash
        differs from the hash in the test log, the test reports are not reused
        and all tests are run again.
        """
        return data_digest({
            "digest": self.digest(),
            "do-not-run": gather_do_not_run(self.item)
        })

    def run_tests(self,
                  executables: list[RunnerExecutable]) -> list[RunnerReport]:
        """
        Run the test executables and returns a list of test reports.
        """
        start_time = now_utc()
        return [{
            "executable": executable.path,
            "executable-sha512": executable.digest,
            "command-line": "",
            "start-time": start_time,
            "output": ["This executable did not run."],
            "duration": 0.0
        } for executable in executables]

    def get_run_command(self, _executable: str) -> None | list[str]:
        """ Get the command to run an executable. """
        return None

    def _get_config_and_timeout_keys(self) -> tuple[str, str]:
        config = self.input("build-configuration")

        # Get timeout key for the enabled set
        for timeout_key in config["test-timeout-key"]:
            if is_enabled(self.enabled_set, timeout_key["enabled-by"]):
                return config["config-key"], timeout_key["key"]

        raise ValueError(
            f"{self.uid}: for enabled set {list(self.enabled_set)} "
            f"and build configuration {config.uid}, there is no timeout key "
            f"in {config['test-timeout-key']}")

    def _get_reports_and_executables(
            self, target: Item, previous_reports_by_hash: dict[str,
                                                               RunnerReport],
            report_runner_hash: str, timeout_key: str
    ) -> tuple[list[RunnerReport], list[RunnerExecutable]]:
        # pylint: disable=too-many-locals
        timeouts = target.parent("test-timeouts")["timeouts"]
        source = self.input("source")
        assert isinstance(source, DirectoryState)
        reports: list[RunnerReport] = []
        executables: list[RunnerExecutable] = []
        do_not_run = do_not_run_names(self._do_not_run_groups)
        default_timeout = self["default-timeout-in-seconds"]
        min_timeout = self["min-timeout-in-seconds"]
        timeout_scaler = self["timeout-scaler"]
        cannot_reuse_reports = self.get_runner_hash() != report_runner_hash
        if cannot_reuse_reports:
            logging.info(
                "%s: cannot reuse reports with "
                "runner hash %s and report hash %s", self.uid,
                self.get_runner_hash(), report_runner_hash)
        for path, digest in source.files_and_hashes():
            if not path.endswith(".exe") or path.endswith(".norun.exe"):
                continue
            assert digest
            name = Path(path).name

            # Use previous report if the executable hash did not change.  Reuse
            # also reports which contain an "error" attribute to avoid running
            # them in CI jobs.  Resolving failed tests is a manual activity.
            report = previous_reports_by_hash.get(digest, None)
            if report is None or cannot_reuse_reports:
                if name in do_not_run:
                    logging.info("%s: do not run: %s", self.uid, path)
                    report = TestRunner.run_tests(
                        self, [RunnerExecutable(path, digest, 0.0)])[0]
                    report["do-not-run"] = True
                    augment_report(report, report["output"])
                    reports.append(report)
                else:
                    try:
                        timeout = max(timeouts[timeout_key][name])
                    except KeyError:
                        timeout = default_timeout
                    timeout = timeout_scaler * max(timeout, min_timeout)
                    logging.debug("%s: run with %.1fs timeout: %s", self.uid,
                                  timeout, path)
                    executables.append(RunnerExecutable(path, digest, timeout))
            else:
                logging.info("%s: use previous report for: %s", self.uid, path)
                report["executable"] = path
                reports.append(report)
        return reports, executables

    def run(self) -> None:
        start_time = now_utc()
        begin = time.monotonic()
        log = self.output("log")
        assert isinstance(log, TestLog)
        target = self.item.parent("target")
        assert target.uid == self.input("target").uid
        config_key, timeout_key = self._get_config_and_timeout_keys()
        self._do_not_run_groups = gather_do_not_run(self.item)
        (reports_by_hash, description,
         report_runner_hash) = log.get_reports_by_hash()
        reports, executables = self._get_reports_and_executables(
            target, reports_by_hash, report_runner_hash, timeout_key)

        # Run the tests with changed executable hashes
        if executables:
            description = self.describe()
            reports.extend(self._run_tests(executables))

        # Save the reports
        os.makedirs(os.path.dirname(log.file), exist_ok=True)
        with open(log.file, "w", encoding="utf-8") as dst:
            data = {
                "build-configuration": config_key,
                "do-not-run": self._do_not_run_groups,
                "timeout-key": timeout_key,
                "duration": time.monotonic() - begin,
                "end-time": now_utc(),
                "reports": sorted(reports, key=lambda x: x["executable"]),
                "start-time": start_time,
                "test-runner-description": description,
                "test-runner-hash": self.get_runner_hash(),
                "target": target.uid
            }
            json.dump(data, dst, sort_keys=True, indent=2)

        self.description.add(f"""Run tests and produce test result file
{self.description.path(log.file)}""")

    def _run_tests_of_attempt(
            self, executables: list[RunnerExecutable]) -> list[RunnerReport]:
        self._executables = executables
        return self.run_tests(executables)

    def _run_tests(self,
                   executables: list[RunnerExecutable]) -> list[RunnerReport]:
        return run_tests_with_retries(
            executables, self._run_tests_of_attempt,
            self["max-retry-count-per-executable"] + 1, self.uid)


class GRMONManualTestRunner(TestRunner):
    """ Provides scripts to run the tests using GRMON. """

    def __init__(self, director: PackageBuildDirector, item: Item):
        super().__init__(director, item)
        self.mapper.add_get_value(f"{self.item.type}:/test-executables-grmon",
                                  self._get_test_executables_grmon)

    def _get_test_executables_grmon(self, _ctx: ItemGetValueContext) -> str:
        return " \\\n".join(
            os.path.basename(executable.path)
            for executable in self._executables)

    def describe(self) -> str:
        return """This test procedure creates an archive with test programs, a
GRMON test script, and a shell script to run the tests manually."""

    def run_tests(self,
                  executables: list[RunnerExecutable]) -> list[RunnerReport]:
        base = self["script-base-path"]
        dir_name = os.path.basename(base)
        grmon_name = f"{base}.grmon"
        shell_name = f"{base}.sh"
        tar_name = f"{base}.tar.xz"
        os.makedirs(os.path.dirname(base), exist_ok=True)
        with tarfile.open(tar_name, "w:xz") as tar_file:
            with open(grmon_name, "w", encoding="utf-8") as grmon_file:
                grmon_file.write(self["grmon-script"])
            tar_file.add(grmon_name, os.path.join(dir_name, "run.grmon"))
            with open(shell_name, "w", encoding="utf-8") as shell_file:
                shell_file.write(self["shell-script"])
            tar_file.add(shell_name, os.path.join(dir_name, "run.sh"))
            for executable in executables:
                tar_file.add(
                    executable.path,
                    os.path.join(dir_name, os.path.basename(executable.path)))
        raise IOError(f"Run the tests provided by {tar_name}")


class SubprocessTestRunner(TestRunner):
    """ Runs tests in subprocesses. """

    def _is_enabled_item_condition(self, condition: Any) -> bool:
        return is_enabled(self.enabled_set, self.substitute(condition))

    def _resolve_command(self) -> list[str]:
        return self.mapper.substitute_flexible_list(
            self.item["command"],
            functools.partial(is_enabled, self.enabled_set), self.item)

    def get_runner_hash(self) -> str:
        # The arguments keep their variables.  A substituted argument carries
        # the workspace path, so a relocated build directory discards every
        # test report.
        return data_digest({
            "runner":
            super().get_runner_hash(),
            "command":
            select_command(self.item["command"],
                           self._is_enabled_item_condition)
        })

    def describe(self) -> str:
        executable = "${test_program}"
        self._executable = executable
        command = " ".join(f"'{part}'" if " " in part else part
                           for part in self._resolve_command())
        return f"""For each test program (indicated by ``{executable}``),
this test procedure runs the following command as a subprocess on the machine
building the package and captures the output:

.. code-block:: none

    {command}"""

    def _get_command(self, executable: RunnerExecutable) -> list[str]:
        self._executable = executable.path
        return self._resolve_command()

    def run_tests(self,
                  executables: list[RunnerExecutable]) -> list[RunnerReport]:
        return run_subprocess_tests(executables, self._get_command,
                                    self.item["discard-patterns"],
                                    self["max-process-count"], self.uid)

    def get_run_command(self, executable: str) -> None | list[str]:
        self._executable = executable
        return self._resolve_command()
