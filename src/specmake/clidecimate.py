# SPDX-License-Identifier: BSD-2-Clause
"""
Provides a command line interface to recursively delete all files in the
deployment directory which do not belong to a specified set of directory
states.
"""

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
import os
import stat

from specitems import (ItemCache, ItemCacheConfig, JSONItemCache,
                       get_item_cache_arguments)

from .directorystate import DirectoryState
from .pkgfactory import create_build_item_factory
from .pkgitems import BuildItemTypeProvider, PackageBuildDirector
from .util import command_arguments

_ITEM_CACHE = {
    "JSON": JSONItemCache,
    "YAML": ItemCache,
}


def _decimate(path: str, keep: set[str]) -> None:
    for name in os.listdir(path):
        path_2 = os.path.join(path, name)
        if stat.S_ISDIR(os.lstat(path_2).st_mode):
            _decimate(path_2, keep)
            try:
                os.rmdir(path_2)
            except OSError:
                pass
            else:
                logging.debug("removed empty directory: %s", path_2)
        elif path_2 not in keep:
            logging.debug("unlink: %s", path_2)
            os.unlink(path_2)
        else:
            logging.debug("keep: %s", path_2)


def clidecimate(argv: list[str] | None = None) -> None:
    """
    Recursively delete all files in the deployment directory which do not
    belong to the specified set of directory states.

    WARNING: This is a destructive command which likely requires a full package
    rebuild to undo.  The command is intended to prepare a deployment directory
    for efficient CI caching.
    """

    def _add_arguments(parser):
        parser.add_argument(
            "--item-format",
            choices=["JSON", "YAML"],
            type=str.upper,
            default="JSON",
            help="the specification item format (default: JSON)")
        parser.add_argument(
            "--package-uid",
            help="the package component UID (default: /pkg/component)",
            default="/pkg/component")
        parser.add_argument(
            "uids",
            metavar="UID",
            nargs="+",
            help="the UID of a directory state item containing "
            "files which shall remain in the deployment directory")

    args = get_item_cache_arguments(command_arguments(argv),
                                    description=clidecimate.__doc__,
                                    add_arguments=(_add_arguments, ))
    cache_config = ItemCacheConfig(paths=args.spec_directories,
                                   cache_directory=args.cache_directory)
    type_provider = BuildItemTypeProvider({})
    package_uid = args.package_uid
    logging.info("%s: load item cache", package_uid)
    item_cache = _ITEM_CACHE[args.item_format](cache_config,
                                               type_provider=type_provider)
    logging.info("%s: loading done", package_uid)
    factory = create_build_item_factory()
    director = PackageBuildDirector(item_cache, package_uid, factory)
    keep: set[str] = set()
    for uid in args.uids:
        directory_state = director.create_with_dependencies(uid)
        assert isinstance(directory_state, DirectoryState)
        with directory_state.component.scope():
            keep.update(directory_state.files())
    _decimate(director.package["deployment-directory"], keep)
