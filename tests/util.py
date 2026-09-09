# SPDX-License-Identifier: BSD-2-Clause
""" Provides methods used by tests. """

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

import logging
import os
from pathlib import Path
import re
import shutil
from typing import Any

from specitems import (EmptyItemCache, ItemCache, ItemCacheConfig,
                       ItemGetValueContext, load_data, pickle_load_data_by_uid,
                       verify_specification_format)

from specmake import (BuildItemFactory, BuildItemTypeProvider,
                      BuildPerformanceImages, BuildRTEMSTestsImages,
                      BuildspaceConfig, PackageBuildDirector, PackageComponent,
                      WorkspaceConfig, create_workspace, export_to_buildspace)


class _DummyPerformanceImages(BuildPerformanceImages):

    def run(self) -> None:
        pass


class _DummyRTEMSTestsImages(BuildRTEMSTestsImages):

    def run(self) -> None:
        pass


def create_item_cache(tmp_dir: str, spec_dir: str) -> dict[str, str]:
    test_dir = os.path.dirname(__file__)
    config = ItemCacheConfig(
        paths=[os.path.normpath(os.path.join(test_dir, spec_dir))],
        cache_directory=os.path.normpath(os.path.join(tmp_dir, "cache")))
    return ItemCache(config, type_provider=BuildItemTypeProvider({}))


def get_and_clear_log(the_caplog) -> str:
    log = "\n".join(f"{rec.levelname} {rec.message}"
                    for rec in the_caplog.records)
    the_caplog.clear()
    return log


def create_package(caplog: Any,
                   tmp_dir: Path,
                   spec_dir: Path,
                   enabled_set: list[str] | None = None,
                   workspace_dir: str = "test-files") -> PackageComponent:
    if enabled_set is None:
        enabled_set = []
    test_dir = Path(__file__).parent
    workspace_config = WorkspaceConfig(
        spec_directories=[str(test_dir / spec_dir)],
        workspace_directory=str(test_dir / workspace_dir),
        cache_directory=str(tmp_dir / "cache-workspace"),
        enabled_set=enabled_set,
        extra_type_data_by_uid=pickle_load_data_by_uid(
            str(test_dir / "spec.pickle")))
    workspace = create_workspace(workspace_config)

    caplog.set_level(logging.WARN)
    status = verify_specification_format(workspace.cache)
    assert status.critical == 0
    assert status.error == 0
    caplog.set_level(logging.DEBUG)

    workspace.director.package.item["tmpdir"] = str(tmp_dir)
    buildspace_config = BuildspaceConfig(spec_directory=str(tmp_dir / "spec"),
                                         cache_directory=str(
                                             tmp_dir / "cache-buildspace"))
    buildspace = export_to_buildspace(workspace, buildspace_config)
    director = buildspace.director
    if "/pkg/source/test-files" in director:
        test_files = director["/pkg/source/test-files"]
        test_files.build()
    director.factory.add_constructor(
        "pkg/directory-state/performance-images-dummy",
        _DummyPerformanceImages)
    director.factory.add_constructor(
        "pkg/directory-state/rtems-tests-images-dummy", _DummyRTEMSTestsImages)
    return director.package


_TABLE_BEGIN = re.compile(r"( +)\+[+-]+$")
_TABLE_CHARS = re.compile(r"[ =-]+")
_TABLE_SPACE = re.compile(r"[ ]+")


def _only_one(match: re.Match[str]) -> str:
    return match.group(0)[0]


def get_document_text(tmpdir: Any, path: Path) -> str:
    with open(path, "r", encoding="utf-8") as src:
        text = src.read()
    text = text.replace(str(tmpdir), "")
    indent = ""
    lines: list[str] = []
    for line in text.splitlines():
        match = _TABLE_BEGIN.match(line)
        if match:
            indent = match.group(1)
        if indent:
            start = len(indent) + 1
            if line.startswith(f"{indent}+"):
                line = f"{indent}+{_TABLE_CHARS.sub(_only_one, line[start:])}"
            elif line.startswith(f"{indent}|"):
                line = f"{indent}|{_TABLE_SPACE.sub(_only_one, line[start:])}"
            else:
                indent = ""
        lines.append(line)
    return "\n".join(lines)


def build_document(caplog: Any, tmpdir: Any, document: str,
                   enabled_set: list[str]) -> tuple[PackageComponent, str]:
    package = create_package(caplog, Path(tmpdir), Path("spec-packagebuild"),
                             enabled_set)
    director = package.director
    director.build_package(only=[f"/pkg/deployment/{document}"])
    dir_build = Path(director[f"/pkg/build/{document}"].directory)
    index_rst = dir_build / "source" / "index.rst"
    return package, get_document_text(tmpdir, index_rst)


def create_test_director() -> PackageBuildDirector:
    item_cache = EmptyItemCache(type_provider=BuildItemTypeProvider({}))
    item_cache.add_item(
        "/component", {
            "SPDX-License-Identifier": "CC-BY-SA-4.0 OR BSD-2-Clause",
            "component-type": "generic",
            "copyrights": ["Copyright (C) 2026 embedded brains GmbH & Co. KG"],
            "enabled-by": True,
            "enabled-set": [],
            "links": [],
            "name": "Name",
            "pkg-type": "component",
            "type": "pkg",
        })
    factory = BuildItemFactory()
    factory.add_constructor("pkg/component/generic", PackageComponent)
    return PackageBuildDirector(item_cache, "/component", factory)
