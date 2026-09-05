# SPDX-License-Identifier: BSD-2-Clause
""" Tests the command to run test executables. """

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
import os
from pathlib import Path
import sys

import pytest
import yaml

from specmake.cliruntests import cliruntests

from .ctrf import validate_ctrf_report

_TESTS = Path(__file__).parent
_RUNNER = str(_TESTS / "simulator-runner.yml")
_SIMULATOR = str(_TESTS / "simulator.py")

# The substitution keys of the runner item without the ${ and }
_PYTHON_KEY = "/pkg/deployment/python:/executable"
_SIMULATOR_KEY = "/pkg/deployment/simulator:/executable"

_EXECUTABLES = [
    "ts-pass.exe",
    "ts-fail.exe",
    "hello.exe",
    "crash.exe",
    "discarded.exe",
    "do-not-run.exe",
    "no-reason.exe",
    "skipped.norun.exe",
]


def _make_executables(directory):
    directory.mkdir(parents=True, exist_ok=True)
    nested = directory / "nested"
    nested.mkdir(exist_ok=True)
    for index, name in enumerate(_EXECUTABLES):
        # Put one executable into a subdirectory to check the recursive scan
        base = nested if name == "hello.exe" else directory
        (base / name).write_text(f"executable {index}\n", encoding="utf-8")
    (directory / "not-an-executable.txt").write_text("x", encoding="utf-8")


def _substitutions(path):
    path.write_text(yaml.safe_dump({
        _PYTHON_KEY: sys.executable,
        _SIMULATOR_KEY: "wrong",
    }),
                    encoding="utf-8")
    return str(path)


def _run(tmp_path, *extra):
    argv = [
        "specruntests",
        "--substitutions",
        _substitutions(tmp_path / "substitutions.yml"),
        "--define",
        f"{_SIMULATOR_KEY}={_SIMULATOR}",
        "--output",
        str(tmp_path / "test-log.json"),
        "--ctrf",
        str(tmp_path / "report.ctrf.json"),
        *extra,
        _RUNNER,
        str(tmp_path / "tests"),
    ]
    return cliruntests(argv)


def _load(path):
    with open(path, "r", encoding="utf-8") as src:
        return json.load(src)


def test_run(tmp_path, capsys):
    _make_executables(tmp_path / "tests")
    status = _run(tmp_path, "--summary", "--app-name", "app", "--build-name",
                  "build")

    # There are failing tests
    assert status == 1

    test_log = _load(tmp_path / "test-log.json")
    reports = {
        os.path.basename(report["executable"]): report
        for report in test_log["reports"]
    }

    # The scan is recursive, skips *.norun.exe and non executables
    assert sorted(reports.keys()) == [
        "crash.exe", "discarded.exe", "do-not-run.exe", "hello.exe",
        "no-reason.exe", "ts-fail.exe", "ts-pass.exe"
    ]

    # The command is fully substituted and drops the disabled argument
    assert reports["hello.exe"]["command-line"][:2] == [
        sys.executable, _SIMULATOR
    ]
    assert "--verbose" not in reports["hello.exe"]["command-line"]

    # The description keeps the test executable placeholder
    description = test_log["test-runner-description"]
    assert _SIMULATOR in description
    assert "${test_program}" in description

    # A do-not-run executable has no command line, whether its entry is a
    # group with a reason or a plain name
    assert reports["do-not-run.exe"]["command-line"] == ""
    assert reports["no-reason.exe"]["command-line"] == ""

    # A discard pattern turns a run into an error
    assert "lost the connection" in reports["discarded.exe"]["error"]

    # The reports are augmented, so the test suite structure is present
    assert reports["ts-pass.exe"]["test-suite"]["failed-steps-count"] == 0
    suite = reports["ts-pass.exe"]["test-suite"]
    assert suite["report-hash"] == suite["report-hash-calculated"]

    report = _load(tmp_path / "report.ctrf.json")
    results = report["results"]
    assert results["environment"] == {"appName": "app", "buildName": "build"}
    tests = {test["name"]: test for test in results["tests"]}
    assert tests["CasePassOne"]["status"] == "passed"
    assert tests["CasePassOne"]["suite"] == ["TestsuitesPass"]
    assert tests["CaseFail"]["status"] == "failed"
    assert tests["hello.exe"]["status"] == "passed"
    assert tests["crash.exe"]["status"] == "failed"
    assert tests["crash.exe"]["message"] == "no end of test message"
    assert tests["discarded.exe"]["status"] == "failed"
    assert tests["do-not-run.exe"]["status"] == "skipped"
    assert tests["no-reason.exe"]["status"] == "skipped"

    # The test suite ran to its end, so its failed test case reports the
    # failure and there is no test for the executable
    assert "ts-fail.exe" not in tests

    summary = results["summary"]
    assert summary["tests"] == len(results["tests"])
    assert summary["skipped"] == 2

    # The report satisfies the schema of the Common Test Report Format
    validate_ctrf_report(report)

    out = capsys.readouterr().out
    assert "# Test results" in out
    assert "## Failures" in out
    assert "CaseFail" in out


def test_enable(tmp_path):
    _make_executables(tmp_path / "tests")
    _run(tmp_path)
    without = _load(tmp_path / "test-log.json")

    # The name of the enabled set fulfils the condition of the argument, so
    # the argument is part of the command and of the description
    assert _run(tmp_path, "-E", "verbose") == 1
    with_verbose = _load(tmp_path / "test-log.json")
    reports = {
        os.path.basename(report["executable"]): report
        for report in with_verbose["reports"]
    }
    assert reports["hello.exe"]["command-line"] == [
        sys.executable, _SIMULATOR, "--verbose",
        str(tmp_path / "tests" / "nested" / "hello.exe")
    ]
    assert "--verbose" in with_verbose["test-runner-description"]

    # The command decides the test runner hash, so a report of the run
    # without the argument is not reusable
    assert with_verbose["test-runner-hash"] != without["test-runner-hash"]


def test_timeout(tmp_path):
    directory = tmp_path / "tests"
    directory.mkdir(parents=True)
    (directory / "hang.exe").write_text("hang", encoding="utf-8")
    assert _run(tmp_path) == 1
    reports = _load(tmp_path / "test-log.json")["reports"]
    assert reports[0]["error"] == "timeout"


def test_test_timeouts(tmp_path):
    directory = tmp_path / "tests"
    directory.mkdir(parents=True)
    (directory / "hello.exe").write_text("hello", encoding="utf-8")
    timeouts = tmp_path / "test-timeouts.yml"
    timeouts.write_text(yaml.safe_dump(
        {"timeouts": {
            "default": {
                "hello.exe": [2.5]
            }
        }}),
                        encoding="utf-8")
    assert _run(tmp_path, "--test-timeouts", str(timeouts)) == 0


def test_unknown_timeout_key(tmp_path, capsys):
    _make_executables(tmp_path / "tests")
    timeouts = tmp_path / "test-timeouts.yml"
    timeouts.write_text(yaml.safe_dump({"timeouts": {}}), encoding="utf-8")
    assert _run(tmp_path, "--test-timeouts", str(timeouts)) == 2
    assert "no timeouts for the key 'default'" in capsys.readouterr().err


def test_a_missing_directory_is_an_error(tmp_path, capsys):
    # A mistyped directory must not report that the tests passed
    assert _run(tmp_path) == 2
    assert "is not a directory with test executables" in capsys.readouterr(
    ).err


def test_a_directory_without_executables_is_an_error(tmp_path, capsys):
    directory = tmp_path / "tests"
    directory.mkdir(parents=True)
    (directory / "skipped.norun.exe").write_text("x", encoding="utf-8")
    assert _run(tmp_path) == 2
    assert "there is no test executable in" in capsys.readouterr().err


def _run_directories(tmp_path, *directories):
    """ Run the tests of the directories and return the exit status. """
    argv = [
        "specruntests",
        "--define",
        f"{_PYTHON_KEY}={sys.executable}",
        "--define",
        f"{_SIMULATOR_KEY}={_SIMULATOR}",
        "--output",
        str(tmp_path / "test-log.json"),
        _RUNNER,
        *directories,
    ]
    return cliruntests(argv)


def test_several_directories(tmp_path):
    first = tmp_path / "first"
    first.mkdir()
    (first / "hello.exe").write_text("one", encoding="utf-8")
    second = tmp_path / "second"
    second.mkdir()
    (second / "hello.exe").write_text("two", encoding="utf-8")

    assert _run_directories(tmp_path, str(first), str(second)) == 0
    reports = _load(tmp_path / "test-log.json")["reports"]

    # The executables of both directories run, even with an equal name
    assert [report["executable"] for report in reports
            ] == [str(first / "hello.exe"),
                  str(second / "hello.exe")]


def test_a_nested_directory_runs_its_executables_once(tmp_path):
    directory = tmp_path / "tests"
    nested = directory / "nested"
    nested.mkdir(parents=True)
    (nested / "hello.exe").write_text("hello", encoding="utf-8")

    # The scan is recursive, so the nested directory is covered twice.  A
    # second run of an executable would become a failed attempt of the first.
    assert _run_directories(tmp_path, str(directory), str(nested)) == 0
    reports = _load(tmp_path / "test-log.json")["reports"]
    assert len(reports) == 1
    assert "failed-attempts" not in reports[0]


def test_a_missing_second_directory_is_an_error(tmp_path, capsys):
    directory = tmp_path / "tests"
    directory.mkdir(parents=True)
    (directory / "hello.exe").write_text("hello", encoding="utf-8")
    assert _run_directories(tmp_path, str(directory),
                            str(tmp_path / "nope")) == 2
    assert "is not a directory with test executables" in capsys.readouterr(
    ).err


def _run_and_keep(tmp_path):
    """ Run the tests and return the path of the produced test log. """
    _make_executables(tmp_path / "tests")
    assert _run(tmp_path) == 1
    previous = tmp_path / "previous.json"
    os.replace(tmp_path / "test-log.json", previous)
    return previous


def test_reuse(tmp_path):
    previous = _run_and_keep(tmp_path)
    expected = _load(previous)["reports"]

    # The test runner is unchanged, so every report is reused.  A report which
    # ran again would have a new start time and duration, so the reports are
    # identical only if nothing ran.
    assert _run(tmp_path, "--reuse", str(previous)) == 1
    reports = _load(tmp_path / "test-log.json")["reports"]
    assert len(reports) == 7
    assert reports == expected


def test_reuse_of_another_test_runner(tmp_path, caplog):
    previous = _run_and_keep(tmp_path)
    previous_hash = _load(previous)["test-runner-hash"]

    # Changed substitution data changes the test runner hash, so the reports
    # of the previous test log are not reusable.  The command is unchanged, so
    # the tests run again and produce the same results.
    assert _run(tmp_path, "--reuse", str(previous), "--define",
                "unused=x") == 1
    test_log = _load(tmp_path / "test-log.json")
    assert test_log["test-runner-hash"] != previous_hash
    assert "cannot reuse the reports" in caplog.text
    assert len(test_log["reports"]) == 7


def test_reuse_of_invalid_json(tmp_path, capsys):
    _make_executables(tmp_path / "tests")
    previous = tmp_path / "previous.json"
    previous.write_text("{not json", encoding="utf-8")
    assert _run(tmp_path, "--reuse", str(previous)) == 2
    assert "is not valid JSON" in capsys.readouterr().err


def test_missing_reuse_file(tmp_path, caplog):
    directory = tmp_path / "tests"
    directory.mkdir(parents=True)
    (directory / "hello.exe").write_text("hello", encoding="utf-8")
    assert _run(tmp_path, "--reuse", str(tmp_path / "nope.json")) == 0
    assert "no test log to reuse" in caplog.text


def test_unresolved_variable(tmp_path, capsys):
    _make_executables(tmp_path / "tests")
    argv = [
        "specruntests", "--output",
        str(tmp_path / "test-log.json"), "--define",
        f"{_PYTHON_KEY}={sys.executable}", _RUNNER,
        str(tmp_path / "tests")
    ]
    assert cliruntests(argv) == 2
    error = capsys.readouterr().err
    assert f"there is no substitution for ${{{_SIMULATOR_KEY}}}" in error

    # The error names the definition which resolves the variable
    assert f"-D '{_SIMULATOR_KEY}=VALUE'" in error


def test_bad_define(tmp_path, capsys):
    _make_executables(tmp_path / "tests")
    argv = [
        "specruntests", "--define", "nonsense", _RUNNER,
        str(tmp_path / "tests")
    ]
    assert cliruntests(argv) == 2
    assert "is not a KEY=VALUE pair" in capsys.readouterr().err


@pytest.mark.parametrize("key", ["${" + _PYTHON_KEY + "}", _PYTHON_KEY + "}"])
def test_a_key_with_the_variable_delimiters_is_rejected(tmp_path, capsys, key):
    _make_executables(tmp_path / "tests")
    argv = [
        "specruntests", "--define", f"{key}={sys.executable}", _RUNNER,
        str(tmp_path / "tests")
    ]
    assert cliruntests(argv) == 2
    assert "must not contain the ${ and }" in capsys.readouterr().err


def test_an_empty_key_is_rejected(tmp_path, capsys):
    _make_executables(tmp_path / "tests")
    argv = ["specruntests", "--define", "=x", _RUNNER, str(tmp_path / "tests")]
    assert cliruntests(argv) == 2
    assert "must not be empty" in capsys.readouterr().err


def test_a_substitutions_file_key_with_the_delimiters_is_rejected(
        tmp_path, capsys):
    _make_executables(tmp_path / "tests")
    path = tmp_path / "bad.yml"
    path.write_text(yaml.safe_dump({"${" + _PYTHON_KEY + "}": "x"}),
                    encoding="utf-8")
    argv = [
        "specruntests", "--substitutions",
        str(path), _RUNNER,
        str(tmp_path / "tests")
    ]
    assert cliruntests(argv) == 2
    assert "must not contain the ${ and }" in capsys.readouterr().err


def test_not_a_subprocess_runner(tmp_path, capsys):
    runner = tmp_path / "runner.yml"
    runner.write_text(yaml.safe_dump({"test-runner-type": "grpc"}),
                      encoding="utf-8")
    argv = ["specruntests", str(runner), str(tmp_path)]
    assert cliruntests(argv) == 2
    assert "is not a subprocess test runner" in capsys.readouterr().err


def test_verbose_and_no_ctrf(tmp_path):
    directory = tmp_path / "tests"
    directory.mkdir(parents=True)
    (directory / "hello.exe").write_text("hello", encoding="utf-8")
    argv = [
        "specruntests", "--verbose", "--define",
        f"{_PYTHON_KEY}={sys.executable}", "--define",
        f"{_SIMULATOR_KEY}={_SIMULATOR}", "--output",
        str(tmp_path / "sub" / "test-log.json"), _RUNNER,
        str(directory)
    ]
    assert cliruntests(argv) == 0
    assert (tmp_path / "sub" / "test-log.json").exists()
