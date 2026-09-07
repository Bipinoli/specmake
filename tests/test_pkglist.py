# SPDX-License-Identifier: BSD-2-Clause
""" Tests the file and target listing. """

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

import logging
from pathlib import Path

import pytest

from specitems import pickle_load_data_by_uid
from specmake import (ListError, WorkspaceConfig, create_workspace, list_files,
                      list_targets)

from .util import create_test_director

_SUB_REPO = "/pkg/source/sub-repo"
_SUB_REPO_2 = "/pkg/source/sub-repo-2"
_FILES = ("  bsp.c\n"
          "  extra.c\n"
          "  tests/tr-test-case.h\n")


def _director(caplog, tmp_path):
    """ The workspace director, the one clibuild reports on. """
    test_dir = Path(__file__).parent
    caplog.set_level(logging.WARN)
    workspace = create_workspace(
        WorkspaceConfig(spec_directories=[str(test_dir / "spec-packagebuild")],
                        workspace_directory=str(test_dir / "test-files"),
                        cache_directory=str(tmp_path / "cache-workspace"),
                        enabled_set=["repository-subset"],
                        extra_type_data_by_uid=pickle_load_data_by_uid(
                            str(test_dir / "spec.pickle"))))
    workspace.director.package.item["tmpdir"] = str(tmp_path)
    return workspace.director


def test_list_files(caplog, tmp_path, capsys):
    list_files(_director(caplog, tmp_path))
    assert capsys.readouterr().out == (f"{_SUB_REPO}\n{_FILES}"
                                       "\n"
                                       f"{_SUB_REPO_2}\n{_FILES}")


def test_list_files_only(caplog, tmp_path, capsys):
    list_files(_director(caplog, tmp_path), only=["*sub-repo-2"])
    assert capsys.readouterr().out == f"{_SUB_REPO_2}\n{_FILES}"


def test_list_files_skip(caplog, tmp_path, capsys):
    list_files(_director(caplog, tmp_path), skip=["*sub-repo-2"])
    assert capsys.readouterr().out == f"{_SUB_REPO}\n{_FILES}"


def test_list_files_force_beats_skip(caplog, tmp_path, capsys):
    list_files(_director(caplog, tmp_path),
               skip=["*sub-repo*"],
               force=["*sub-repo-2"])
    assert capsys.readouterr().out == f"{_SUB_REPO_2}\n{_FILES}"


def test_list_files_no_match(caplog, tmp_path):
    with pytest.raises(ListError, match="no build root matches"):
        list_files(_director(caplog, tmp_path), only=["*no-such-root*"])


def test_list_files_no_root():
    with pytest.raises(ListError, match="no build root"):
        list_files(create_test_director())


def test_list_targets(caplog, tmp_path, capsys):
    list_targets(_director(caplog, tmp_path))
    assert capsys.readouterr().out == "/pkg/component\n  rtems/target-a\n"


def test_list_targets_no_root():
    with pytest.raises(ListError, match="no build root"):
        list_targets(create_test_director())
