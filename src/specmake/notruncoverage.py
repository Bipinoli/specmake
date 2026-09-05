# SPDX-License-Identifier: BSD-2-Clause
""" Measures the code coverage of test executables which do not run. """

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

import json
import logging
import os
from subprocess import run as subprocess_run
import tempfile
from typing import Any

from specitems import SphinxContent

from .directorystate import DirectoryState
from .gcdaproducer import gcov_stream, merge_gcov_stream, remove_gcda
from .sphinxbuilder import spacify

_Data = dict[str, Any]


def covered_spots(report: _Data) -> dict[str, list[str]]:
    """
    Get the covered spots of a gcovr JSON report by file.

    A spot is a line, a branch or a function.  The keys are those of the
    coverage gap justifications, so a caller compares them directly with the
    gaps of another report.
    """
    spots_by_file: dict[str, list[str]] = {}
    for file_coverage in report.get("files", []):
        spots: set[str] = set()
        for line in file_coverage["lines"]:
            line_number = line["line_number"]
            if line["count"] > 0:
                spots.add(f"line/{line_number}")
            for branch in line["branches"]:
                if branch["count"] > 0:
                    branchno = branch.get("destination_block_id",
                                          branch.get("branchno", -1))
                    spots.add(f"branch/{line_number}/{branchno}")
        for function in file_coverage["functions"]:
            if function.get("execution_count", 0) > 0:
                spots.add(f"function/{function['name']}")
        if spots:
            spots_by_file[file_coverage["file"]] = sorted(spots)
    return spots_by_file


def count_spots(spots_by_file: dict[str, list[str]]) -> dict[str, int]:
    """ Count the spots by kind. """
    counts = {"function": 0, "line": 0, "branch": 0}
    for spots in spots_by_file.values():
        for spot in spots:
            counts[spot.split("/", 1)[0]] += 1
    return counts


class NotRunCoverage(DirectoryState):
    """
    Measures what the test executables which one target excludes cover on the
    other targets of the variant.

    The test log of the target states which test executables it excludes and
    why.  The test logs of the other targets carry the gcov information of
    these test executables.  One measurement per group of test executables
    which share a reason gives the spots which that reason accounts for.
    """

    def _gcovr(self, object_directory: str, json_file: str) -> None:
        command = [
            self["gcovr"], "--include-internal-functions",
            "--gcov-ignore-parse-errors", "--json", json_file,
            f"--gcov-executable={self['gcov']}", "--object-directory",
            object_directory, object_directory
        ]
        logging.info("%s: run in %s: %s", self.uid,
                     self["gcovr-working-directory"], " ".join(command))
        subprocess_run(command,
                       check=True,
                       cwd=self["gcovr-working-directory"])

    def _streams_by_executable(
            self, names: set[str]) -> dict[str, tuple[str, bytes]]:
        """
        Get the gcov information stream of each named test executable.

        A test executable which ran on more than one target contributes the
        stream of the first target which carries it.
        """
        streams: dict[str, tuple[str, bytes]] = {}
        for log in self.inputs("other-log"):
            assert isinstance(log, DirectoryState)
            data = log.json_load()
            target_uid = data.get("target", log.uid)
            for report in data["reports"]:
                name = os.path.basename(report["executable"])
                if name not in names or name in streams:
                    continue
                if report.get("do-not-run", False):
                    continue
                stream = gcov_stream(report, self.uid)
                if stream is not None:
                    logging.info("%s: take the coverage data of %s from %s",
                                 self.uid, name, target_uid)
                    streams[name] = (target_uid, stream)
        return streams

    def _measure(self, group: _Data, object_directory: str,
                 streams: dict[str, tuple[str, bytes]]) -> None:
        """ Measure what one group of test executables covers. """
        build = self.input("build")
        assert isinstance(build, DirectoryState)
        gcov_tool = self["gcov-tool"]
        working_directory = self["gcov-tool-working-directory"]
        measured: dict[str, str] = {}
        remove_gcda(build.directory, self.uid, expected=True)
        for name in group["executables"]:
            entry = streams.get(name, None)
            if entry is None:
                continue
            measured[name] = entry[0]
            merge_gcov_stream(entry[1], gcov_tool, working_directory)
        group["measured-on"] = measured
        group["not-measured"] = sorted(
            set(group["executables"]) - set(measured))
        if not measured:
            logging.warning(
                "%s: no other target ran any test executable of the group %s",
                self.uid, group["executables"])
            group["covered"] = {}
            group["counts"] = count_spots({})
            return
        with tempfile.TemporaryDirectory() as tmp:
            json_file = os.path.join(tmp, "report.json")
            self._gcovr(object_directory, json_file)
            with open(json_file, "r", encoding="utf-8") as src:
                report = json.load(src)
        remove_gcda(build.directory, self.uid, expected=True)
        group["covered"] = covered_spots(report)
        group["counts"] = count_spots(group["covered"])

    def run(self) -> None:
        super().run()
        build = self.input("build")
        assert isinstance(build, DirectoryState)
        log = self.input("log")
        assert isinstance(log, DirectoryState)
        log_data = log.json_load()
        of_suite = set(
            os.path.basename(report["executable"])
            for report in log_data["reports"])
        groups = []
        for group in log_data.get("do-not-run", []):
            executables = [
                name for name in group["executables"] if name in of_suite
            ]
            if not executables:
                logging.info(
                    "%s: no test of the group %s belongs to this test suite",
                    self.uid, group["executables"])
                continue
            groups.append(dict(group, executables=executables))
        justified = [
            group for group in groups
            if group.get("justification", None) is not None
        ]
        names = set(name for group in justified
                    for name in group["executables"])
        streams = self._streams_by_executable(names)
        object_directory = os.path.join(build.directory,
                                        self["gcda-sub-directory"])
        for group in groups:
            if group.get("justification", None) is None:
                logging.info(
                    "%s: the group %s states no reason, so it justifies no "
                    "coverage gap", self.uid, group["executables"])
                group["measured-on"] = {}
                group["not-measured"] = sorted(group["executables"])
                group["covered"] = {}
                group["counts"] = count_spots({})
                continue
            self._measure(group, object_directory, streams)
        file_path = os.path.join(self["directory"],
                                 self.item["files"][0]["file"])
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as dst:
            json.dump(
                {
                    "groups": groups,
                    "scope": self["scope"],
                    "target-uid": log_data.get("target", "")
                },
                dst,
                sort_keys=True,
                indent=2)
        self.description.add(f"""Measure the code coverage of the excluded
tests and produce {self.description.path(file_path)}""")
        self.run_post_actions()


def not_run_spots(groups: list[dict]) -> dict[str, dict[str, int]]:
    """
    Get the index of the group which reaches each spot, by file and spot.

    A group which states no reason justifies nothing, so it contributes no
    spot.  A spot which more than one group reaches belongs to the first of
    them, so the counts of the groups sum to the count of the spots.
    """
    group_of_spot: dict[str, dict[str, int]] = {}
    for index, group in enumerate(groups):
        if group.get("justification", None) is None:
            continue
        for file_path, spots in group.get("covered", {}).items():
            spot_to_group = group_of_spot.setdefault(file_path, {})
            for spot in spots:
                spot_to_group.setdefault(spot, index)
    return group_of_spot


def do_not_run_names_of_groups(groups: list[dict]) -> set[str]:
    """ Get the names of the tests of the groups. """
    return set(name for group in groups for name in group["executables"])


def add_not_run_section(content: SphinxContent, scope: str, groups: list[dict],
                        counts_of_groups: list[dict]) -> None:
    """
    Add the section which states the tests which the target does not run.

    The section carries the same heading whether the target excludes a test
    or not, so every report of the variant has the same layout.
    """
    with content.section(f"Excluded tests - {scope}"):
        if not groups:
            content.add("No test is excluded from this target.")
            return
        content.add("""The following table lists the excluded tests of
this target.  The counts state how many coverage gaps the reason of the row
justifies.  A row without a reason justifies no gap.""")
        with_reason = set(name for group in groups
                          if group.get("justification", None) is not None
                          for name in group["executables"])
        rows: list[list[str]] = [[
            "Tests", "Functions", "Lines", "Branches", "Reason"
        ]]
        for group, counts in zip(groups, counts_of_groups):
            justification = group.get("justification", None)
            if justification is None:
                if set(group["executables"]).issubset(with_reason):
                    reason = ("**This item states no reason.**  Another "
                              "item states one.")
                else:
                    reason = "**No item states a reason.**"
            else:
                reason = " ".join(justification.split())
                not_measured = group.get("not-measured", [])
                if not_measured:
                    names = ", ".join(spacify(name) for name in not_measured)
                    reason = (f"{reason}  **No other target ran "
                              f"{names}.**")
            rows.append([
                ", ".join(spacify(name) for name in group["executables"]),
                str(counts["function"]),
                str(counts["line"]),
                str(counts["branch"]), reason
            ])
        content.add_grid_table(rows, [24, 8, 8, 8, 52], font_size=-3)
        measured_on = sorted(
            set(target for group in groups
                for target in group.get("measured-on", {}).values()))
        if measured_on:
            names = ", ".join(f"spec:{spacify(uid)}" for uid in measured_on)
            content.add(f"""The coverage of these tests comes from the
following targets: {names}.""")


def is_complete_evidence(summary: Any) -> bool:
    """
    Tell whether the coverage of the summary stands on its own.

    It stands on its own if no file carries an unjustified issue, if the
    overall coverage meets its limits, and if no gap rests on an excluded
    test.
    """
    if summary.bad_files or "error" in summary.overall:
        return False
    return not any(value for key, value in summary.overall.items()
                   if key.endswith("-not-run"))


def add_coverage_across_targets(content: SphinxContent, mapper: Any,
                                targets: dict[str, dict],
                                summaries_of_target: dict[str, list],
                                anchors: list[str]) -> None:
    """ Add the code coverage statement over all targets. """
    with content.section("Coverage across the targets"):
        rows: list[list[str]] = [[
            "Target", "Excluded tests", "Unjustified issues",
            "Complete evidence"
        ]]
        for uid, target_data in targets.items():
            summaries = summaries_of_target.get(uid, [])
            not_run = len(
                do_not_run_names_of_groups([
                    group for summary in summaries
                    for group in summary.not_run_groups
                ]))
            bad = sum(len(summary.bad_files) for summary in summaries)
            rows.append([
                mapper.format_link(target_data["name"], target_data["link"]),
                str(not_run),
                str(bad), "yes" if uid in anchors else "no"
            ])
        content.add_grid_table(rows, [40, 20, 20, 20], font_size=-3)
        if anchors:
            names = ", ".join(targets[uid]["name"] for uid in anchors)
            content.add(f"""The coverage evidence of this variant rests on
the following targets: {names}.  Each of them meets its coverage limits with
the tests it runs.""")
        else:
            content.add("""**No target meets its coverage limits with the
tests it runs.**  The coverage evidence of this variant is incomplete.""")


def not_run_by_scope_of(results: dict) -> dict[str, list[dict]]:
    """ Get the not run coverage groups of each scope. """
    by_scope: dict[str, list[dict]] = {}
    for not_run in results.get("not-run-coverage", []):
        data = not_run.json_load()
        by_scope[data["scope"]] = data["groups"]
    return by_scope


def not_run_issues(groups: list[dict]) -> dict[str, set[str]]:
    """
    Get the issues of the excluded tests.

    More than one item may exclude the same test executable.  A group with a
    reason justifies its test executables, whatever the other groups say.
    """
    with_reason: set[str] = set()
    measured: set[str] = set()
    for group in groups:
        if group.get("justification", None) is not None:
            with_reason.update(group["executables"])
        measured.update(group.get("measured-on", {}))
    without_reason: set[str] = set()
    never_run: set[str] = set()
    for group in groups:
        if group.get("justification", None) is None:
            without_reason.update(name for name in group["executables"]
                                  if name not in with_reason)
        else:
            never_run.update(name for name in group.get("not-measured", [])
                             if name not in measured)
    issues: dict[str, set[str]] = {}
    if without_reason:
        issues["Excluded tests without a reason"] = set(
            spacify(name) for name in without_reason)
    if never_run:
        issues["Excluded tests which no other target ran"] = set(
            spacify(name) for name in never_run)
    return issues
