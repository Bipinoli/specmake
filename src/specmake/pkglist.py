# SPDX-License-Identifier: BSD-2-Clause
""" Lists the files and the targets of a build configuration. """

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

import fnmatch
from typing import Iterable, Optional

from specitems import Item, ItemCache

from .pkgitems import PackageBuildDirector, PackageComponent
from .reposubset import RepositorySubset


class ListError(Exception):
    """ Indicates that a list report has nothing to report. """


def _match(uid: str, patterns: Optional[list[str]]) -> bool:
    return patterns is not None and any(
        fnmatch.fnmatch(uid, pattern) for pattern in patterns)


def _is_selected(uid: str, only: Optional[list[str]],
                 force: Optional[list[str]],
                 skip: Optional[list[str]]) -> bool:
    if only is not None and not _match(uid, only):
        return False
    return not _match(uid, skip) or _match(uid, force)


def _find_build_roots(item_cache: ItemCache) -> list[Item]:
    return sorted(
        (item for item in item_cache.values() if "build-uids" in item),
        key=lambda item: item.uid)


def _select_build_roots(item_cache: ItemCache, only: Optional[list[str]],
                        force: Optional[list[str]],
                        skip: Optional[list[str]]) -> list[Item]:
    roots = _find_build_roots(item_cache)
    if not roots:
        raise ListError("the configuration has no build root")
    selected = [
        root for root in roots if _is_selected(root.uid, only, force, skip)
    ]
    if not selected:
        raise ListError("no build root matches the filters")
    return selected


def _print_report(report: Iterable[tuple[str, Iterable[str]]]) -> None:
    for index, (uid, leaves) in enumerate(report):
        if index:
            print()
        print(uid)
        for leaf in sorted(set(leaves)):
            print(f"  {leaf}")


def _gather_files(director: PackageBuildDirector, root: Item) -> list[str]:
    """ The workspace item factory has no repository subset constructor. """
    with root.view["component"].scope():
        return RepositorySubset(director, root).gather_files()


def _gather_targets(item_cache: ItemCache,
                    enabled_set: list[str]) -> list[str]:
    return [
        item.uid.lstrip("/") for item in item_cache.values()
        if item.get("type") == "requirement"
        and item.get("non-functional-type") == "design-target"
        and item.is_enabled(enabled_set)
    ]


def list_files(director: PackageBuildDirector,
               only: Optional[list[str]] = None,
               force: Optional[list[str]] = None,
               skip: Optional[list[str]] = None) -> None:
    """ Print the files of each selected build root. """
    _print_report((root.uid, _gather_files(director, root)) for root in
                  _select_build_roots(director.item_cache, only, force, skip))


def list_targets(director: PackageBuildDirector) -> None:
    """ Print the available targets of each component which builds. """
    components: dict[str, PackageComponent] = {}
    for root in _select_build_roots(director.item_cache, None, None, None):
        component = root.view["component"]
        components.setdefault(component.uid, component)
    report = []
    for uid, component in sorted(components.items()):
        targets = _gather_targets(director.item_cache,
                                  list(component.selection.enabled_set))
        if targets:
            report.append((uid, targets))
    _print_report(report)
