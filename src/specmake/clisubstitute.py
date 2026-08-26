# SPDX-License-Identifier: BSD-2-Clause
"""
Provides a command line interface to substitute text using a package
specification.
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
import sys

from specitems import (ItemCache, ItemCacheConfig, JSONItemCache,
                       get_item_cache_arguments)

from .pkgfactory import create_build_item_factory
from .pkgitems import BuildItemTypeProvider, PackageBuildDirector
from .util import command_arguments

_ITEM_CACHE = {
    "JSON": JSONItemCache,
    "YAML": ItemCache,
}


def clisubstitute(argv: list[str] | None = None) -> None:
    """ Substitute text using a package specification. """

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
        parser.add_argument("uid",
                            metavar="UID",
                            help="the UID of the build item used to "
                            "perform the substitution")

    args = get_item_cache_arguments(command_arguments(argv),
                                    description=clisubstitute.__doc__,
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
    build_item = director.create_with_dependencies(args.uid)
    with build_item.scope():
        for line in sys.stdin:
            sys.stdout.write(build_item.substitute(line))
