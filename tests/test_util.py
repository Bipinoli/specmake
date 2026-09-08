# SPDX-License-Identifier: BSD-2-Clause
""" Unit tests for the util module. """

# Copyright (C) 2020, 2026 embedded brains GmbH & Co. KG
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
import logging
from pathlib import Path
import re
import sys

from specitems import load_data, save_data
from specware import load_config, run_command

from specmake import (command_arguments, command_name, duration,
                      get_build_arguments, copy_file, copy_files, now_utc,
                      write_json)
from specmake.cliaddpatches import cliaddpatches

from .util import get_and_clear_log


def test_copy_files(caplog, tmpdir):
    caplog.set_level(logging.INFO)
    src_dir = os.path.dirname(__file__)
    copy_files(src_dir, tmpdir, [], "uid")
    filename = "config/c/d.yml"
    dst_dir = os.path.join(tmpdir, "1")
    assert not os.path.exists(os.path.join(dst_dir, filename))
    copy_files(src_dir, dst_dir, [filename], "uid")
    assert os.path.exists(os.path.join(dst_dir, filename))
    assert get_and_clear_log(caplog) == (
        f"INFO uid: copy '{src_dir}"
        f"/config/c/d.yml' to '{dst_dir}/config/c/d.yml'")
    src_file = os.path.join(src_dir, filename)
    dst_file = os.path.join(tmpdir, "2", filename)
    assert not os.path.exists(dst_file)
    copy_file(src_file, dst_file, "uid")
    assert os.path.exists(dst_file)
    assert get_and_clear_log(
        caplog) == f"INFO uid: copy '{src_file}' to '{dst_file}'"


def test_load_config():
    filename = os.path.join(os.path.dirname(__file__), "config", "a.yml")
    config = load_config(filename)
    assert config["a"] == "b"
    assert config["c"] == "d"


def test_run(caplog):
    caplog.set_level(logging.DEBUG)
    status = run_command(["echo", "A"])
    assert status == 0
    assert get_and_clear_log(caplog) == """INFO run in '.': 'echo' 'A'
DEBUG A"""
    stdout = []
    status = run_command(["echo", "A"], stdout=stdout)
    assert status == 0
    assert stdout[0].strip() == "A"
    status = run_command(["sleep", "0.1"])
    assert status == 0


def test_get_build_arguments_default():
    args = get_build_arguments([])
    assert args.log_level == "INFO"
    assert args.log_file is None
    assert args.only is None
    assert args.force is None
    assert not args.no_spec_verify


def test_get_build_arguments_explicit(tmpdir):
    log_file = os.path.join(tmpdir, "log.txt")
    args = get_build_arguments([
        "--log-level=DEBUG", f"--log-file={log_file}", "--only", "abc",
        "--force", "def", "--no-spec-verify"
    ])
    assert args.log_level == "DEBUG"
    assert args.log_file == log_file
    assert args.only == ["abc"]
    assert args.force == ["def"]
    assert args.no_spec_verify


def test_duration():
    assert duration("foobar") == "foobar"
    assert duration(0.0) == "0s"
    assert duration(1e-7) == "100.000ns"
    assert duration(1e-4) == "100.000μs"
    assert duration(1e-1) == "100.000ms"
    assert duration(123.456) == "123.456s"


def test_now_utc():
    now = now_utc()
    assert re.match(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:"
        r"[0-9]{2}\.[0-9]{6}\+00:00$", now) is not None


def test_write_json_makes_the_directory(tmpdir):
    path = Path(tmpdir) / "sub" / "data.json"
    write_json(str(path), {"a": 1})
    with open(path, "r", encoding="utf-8") as src:
        assert json.load(src) == {"a": 1}


def test_write_json_without_a_directory(tmpdir, monkeypatch):
    monkeypatch.chdir(tmpdir)
    write_json("data.json", {"b": 2})
    with open(Path(tmpdir) / "data.json", "r", encoding="utf-8") as src:
        assert json.load(src) == {"b": 2}


def test_an_entry_point_reads_the_argument_vector_at_the_call(
        tmpdir, monkeypatch):
    # A default argument binds at import, so an entry point which
    # defaults to sys.argv keeps the vector of the import.  A caller
    # which rebinds sys.argv still got that original vector.
    item_file = Path(tmpdir) / "item.yml"
    patch_file = Path(tmpdir) / "a.patch"
    save_data(str(item_file), {"type": "spec"})
    patch_file.write_text("--- a\n+++ b\n", encoding="utf-8")
    monkeypatch.setattr(
        sys, "argv",
        ["specaddpatches", str(item_file),
         str(patch_file)])
    cliaddpatches()
    assert load_data(str(item_file))["archive-patches"][0]["patch"] == \
        "--- a\n+++ b\n"


def test_add_patches_appends_only_on_request(tmpdir):
    # A call without --append drops the patches which the item holds.
    # An item collects the patches of more than one call only through
    # that option.
    item_file = Path(tmpdir) / "item.yml"
    patch_file = Path(tmpdir) / "b.patch"
    save_data(
        str(item_file), {
            "type":
            "spec",
            "archive-patches": [{
                "enabled-by": True,
                "patch": "--- a\n",
                "type": "inline"
            }],
        })
    patch_file.write_text("--- b\n", encoding="utf-8")
    cliaddpatches(
        ["specaddpatches", "--append",
         str(item_file),
         str(patch_file)])
    patches = load_data(str(item_file))["archive-patches"]
    assert [patch["patch"] for patch in patches] == ["--- a\n", "--- b\n"]
    cliaddpatches(["specaddpatches", str(item_file), str(patch_file)])
    patches = load_data(str(item_file))["archive-patches"]
    assert [patch["patch"] for patch in patches] == ["--- b\n"]


def test_the_command_vector_falls_back_to_the_process(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["specmake", "--verbose"])
    assert command_arguments(None) == ["--verbose"]
    assert command_name(None) == "specmake"
    assert command_arguments(["other", "-x"]) == ["-x"]
    assert command_name(["/usr/bin/other", "-x"]) == "other"
