# SPDX-License-Identifier: BSD-2-Clause
""" Tests for the notruncoverage module. """

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
from pathlib import Path

import specmake
from specitems import SphinxContent

from specmake.notruncoverage import (add_coverage_across_targets,
                                     add_not_run_section, count_spots,
                                     covered_spots)
from specmake.testaggregator import _CoverageSummary
from specmake.testrunner import do_not_run_names, gather_do_not_run

from .util import create_package, get_and_clear_log

_LIMITS = {
    "overall": {
        "branch-min-percent": 100.0,
        "function-min-percent": 100.0,
        "line-min-percent": 100.0
    },
    "per-file": {
        "branch-min-percent": 100.0,
        "function-min-percent": 100.0,
        "line-min-percent": 100.0
    }
}


class _Mapper:

    def format_link(self, name, _target):
        return name


class _Aggregator:
    uid = "/pkg/steps/aggregate-test-results"


def _file_coverage(line_count, branch_count, function_count):
    """ Build a gcovr file coverage entry of one line and one function. """
    return {
        "file":
        "a.c",
        "lines": [{
            "line_number":
            10,
            "count":
            line_count,
            "gcovr/md5":
            "d0",
            "branches": [{
                "count": branch_count,
                "destination_block_id": 3
            }]
        }],
        "functions": [{
            "name": "f",
            "execution_count": function_count
        }]
    }


def _summary(not_run_groups):
    return _CoverageSummary(
        _Aggregator(), _Mapper(), {
            "files": [_file_coverage(0, 0, 0)],
            "html-directory": "html",
            "limits-by-area": _LIMITS,
            "not-run-groups": not_run_groups,
            "scope": "Third-Party",
            "target-uid": "/target/simulator",
            "verifications": {}
        })


def test_covered_spots():
    spots = covered_spots({"files": [_file_coverage(7, 7, 7)]})
    assert spots == {"a.c": ["branch/10/3", "function/f", "line/10"]}
    assert count_spots(spots) == {"branch": 1, "function": 1, "line": 1}
    assert covered_spots({"files": [_file_coverage(0, 0, 0)]}) == {}


def test_gap_is_justified_by_a_test_which_does_not_run():
    """ A gap which only a test that does not run reaches is justified. """
    covered = covered_spots({"files": [_file_coverage(7, 7, 7)]})
    summary = _summary([{
        "executables": ["xilinx-canps.exe"],
        "justification": "The test needs the test peer.",
        "source-uid": "/pkg/test-runner/simulator",
        "covered": covered,
        "measured-on": {
            "xilinx-canps.exe": "/target/board-0"
        },
        "not-measured": []
    }])
    assert not summary.bad_files
    assert not summary.justified_files
    assert len(summary.not_run_files) == 1
    assert summary.not_run_counts == [{"branch": 1, "function": 1, "line": 1}]
    for kind in ("branch", "function", "line"):
        assert summary.overall[f"{kind}-not-run"] == 1
        assert summary.overall[f"{kind}-covered"] == 0
        assert summary.overall[f"{kind}-status"] == "OK"
    assert not summary.issues


def test_a_group_without_a_reason_justifies_nothing():
    covered = covered_spots({"files": [_file_coverage(7, 7, 7)]})
    summary = _summary([{
        "executables": ["xilinx-default.exe"],
        "justification": None,
        "source-uid": "/pkg/test-runner/simulator",
        "covered": covered,
        "measured-on": {},
        "not-measured": ["xilinx-default.exe"]
    }])
    assert len(summary.bad_files) == 1
    assert not summary.not_run_files
    assert summary.overall["line-not-run"] == 0
    assert "Excluded tests without a reason" in summary.issues


def test_a_duplicate_exclusion_keeps_its_reason():
    """ A test which two items exclude keeps the reason of either of them. """
    covered = covered_spots({"files": [_file_coverage(7, 7, 7)]})
    summary = _summary([{
        "executables": ["test-peer-uart-ping.exe"],
        "justification": "The test needs the test peer.",
        "source-uid": "/pkg/test-runner/simulator",
        "covered": covered,
        "measured-on": {
            "test-peer-uart-ping.exe": "/target/board-0"
        },
        "not-measured": []
    }, {
        "executables": ["test-peer-uart-ping.exe"],
        "justification": None,
        "source-uid": "/pkg/source/eb-test-support",
        "covered": {},
        "measured-on": {},
        "not-measured": ["test-peer-uart-ping.exe"]
    }])
    assert not summary.issues
    assert len(summary.not_run_files) == 1
    assert summary.not_run_counts[0] == {"branch": 1, "function": 1, "line": 1}


def test_a_test_which_ran_nowhere_is_reported():
    summary = _summary([{
        "executables": ["xilinx-canps.exe"],
        "justification": "The test needs the test peer.",
        "source-uid": "/pkg/test-runner/simulator",
        "covered": {},
        "measured-on": {},
        "not-measured": ["xilinx-canps.exe"]
    }])
    assert len(summary.bad_files) == 1
    assert ("Excluded tests which no other target ran" in summary.issues)


class _Link:

    def __init__(self, uid, entries):
        self.item = type("I", (), {"uid": uid})()
        self._entries = entries

    def __getitem__(self, key):
        assert key == "do-not-run"
        return self._entries


class _Item:

    uid = "/pkg/test-runner/simulator"

    def __init__(self, entries, link_entries):
        self._entries = entries
        self._link_entries = link_entries

    def __getitem__(self, key):
        assert key == "do-not-run"
        return self._entries

    def links_to_children(self, role):
        assert role == "test-runner-do-not-run"
        return [_Link("/pkg/source/zephyr", self._link_entries)]


def test_gather_do_not_run_takes_both_forms():
    groups = gather_do_not_run(
        _Item([{
            "executables": ["b.exe", "a.exe"],
            "justification": "A reason."
        }], ["z.exe"]))
    assert groups == [{
        "executables": ["a.exe", "b.exe"],
        "justification": "A reason.",
        "source-uid": "/pkg/test-runner/simulator"
    }, {
        "executables": ["z.exe"],
        "justification": None,
        "source-uid": "/pkg/source/zephyr"
    }]
    assert do_not_run_names(groups) == {"a.exe", "b.exe", "z.exe"}


def _gcov_tool(command, check, cwd, input):
    """ Merge a gcov information stream into the object directory. """
    assert command == ["my-gcov-tool", "merge-stream"]
    assert check
    assert input == b"gcfnB04R\x00\x00\x00\x95/opt"
    (Path(cwd) / "merged.gcda").touch()


def _gcovr(command, check, cwd):
    """ Write the report of one covered line, branch and function. """
    assert check
    assert command[0] == "my-gcovr"
    assert "--gcov-executable=my-gcov" in command
    json_file = command[command.index("--json") + 1]
    with open(json_file, "w", encoding="utf-8") as dst:
        json.dump({"files": [_file_coverage(1, 1, 1)]}, dst)


def test_not_run_coverage(caplog, tmpdir, monkeypatch):
    tmp_dir = Path(tmpdir)
    package = create_package(caplog, tmp_dir, Path("spec-packagebuild"),
                             ["not-run-coverage"])
    monkeypatch.setattr(specmake.gcdaproducer, "subprocess_run", _gcov_tool)
    monkeypatch.setattr(specmake.notruncoverage, "subprocess_run", _gcovr)
    director = package.director
    director.build_package()
    state = director["/pkg/build/not-run-coverage"]
    with open(Path(state.directory) / "not-run-coverage.json",
              "r",
              encoding="utf-8") as src:
        data = json.load(src)

    assert data["scope"] == "Scope"
    assert data["target-uid"] == "/rtems/target-a"
    groups = data["groups"]

    # A group whose tests belong to another test suite is dropped
    assert len(groups) == 3

    # The other target ran the test, so its coverage justifies the gaps
    assert groups[0]["executables"] == ["excluded-ethernet.exe"]
    assert groups[0]["measured-on"] == {
        "excluded-ethernet.exe": "/rtems/target-b"
    }
    assert groups[0]["not-measured"] == []
    assert groups[0]["counts"] == {"branch": 1, "function": 1, "line": 1}
    assert groups[0]["covered"] == {
        "a.c": ["branch/10/3", "function/f", "line/10"]
    }

    # The other target does not run the test either, so nothing is measured
    assert groups[1]["executables"] == ["excluded-nowhere.exe"]
    assert groups[1]["measured-on"] == {}
    assert groups[1]["not-measured"] == ["excluded-nowhere.exe"]
    assert groups[1]["counts"] == {"branch": 0, "function": 0, "line": 0}

    # A group without a reason justifies nothing, so it is not measured
    assert groups[2]["executables"] == ["excluded-silent.exe"]
    assert groups[2]["measured-on"] == {}
    assert groups[2]["covered"] == {}

    log = get_and_clear_log(caplog)
    assert ("/pkg/build/not-run-coverage: no test of the group "
            "['of-another-suite.exe'] belongs to this test suite") in log
    assert ("/pkg/build/not-run-coverage: the group ['excluded-silent.exe'] "
            "states no reason, so it justifies no coverage gap") in log
    assert ("/pkg/build/not-run-coverage: take the coverage data of "
            "excluded-ethernet.exe from /rtems/target-b") in log
    assert ("/pkg/build/not-run-coverage: no other target ran any test "
            "executable of the group ['excluded-nowhere.exe']") in log


def test_a_section_without_a_measured_group():
    content = SphinxContent()
    add_not_run_section(content, "Scope", [{
        "executables": ["a.exe"],
        "justification": "The target has no device for it.\n",
        "measured-on": {},
        "not-measured": ["a.exe"]
    }], [{
        "function": 0,
        "line": 0,
        "branch": 0
    }])
    text = content.join()
    assert "Excluded tests - Scope" in text
    assert "The coverage of these tests comes from" not in text


def test_a_file_of_mixed_gaps_belongs_to_the_excluded_tests():
    """
    A gap which only an excluded test reaches is weaker evidence than a
    justification of the specification.
    """
    summary = _CoverageSummary(
        _Aggregator(), _Mapper(), {
            "files": [_file_coverage(0, 0, 0)],
            "html-directory":
            "html",
            "limits-by-area":
            _LIMITS,
            "not-run-groups": [{
                "executables": ["a.exe"],
                "justification": "The target has no device for it.\n",
                "covered": {
                    "a.c": ["branch/10/3", "function/f"]
                }
            }],
            "scope":
            "Third-Party",
            "target-uid":
            "/target/simulator",
            "verifications": {
                "a.c": {
                    "line/10": ("/spec/gap", "d0")
                }
            }
        })
    assert not summary.bad_files
    assert not summary.justified_files
    assert len(summary.not_run_files) == 1
    stats = summary.not_run_files[0]
    assert stats["line-justified"] == 1
    assert stats["line-not-run"] == 0
    assert stats["branch-not-run"] == 1
    assert stats["function-not-run"] == 1


def test_an_excluded_test_of_two_scopes_counts_once():
    """ More than one scope of a target may exclude the same test. """
    groups = [{
        "executables": ["a.exe", "b.exe"],
        "justification": "The target has no device for it.\n"
    }]
    content = SphinxContent()
    add_coverage_across_targets(
        content, _Mapper(),
        {"/target/simulator": {
            "name": "Simulator",
            "link": "l"
        }}, {"/target/simulator": [_summary(groups),
                                   _summary(groups)]}, [])
    row = [line for line in content.join().splitlines() if "Simulator" in line]
    assert [" ".join(line.split())
            for line in row] == ["| Simulator | 2 | 2 | no |"]
