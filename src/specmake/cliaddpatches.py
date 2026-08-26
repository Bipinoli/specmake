# SPDX-License-Identifier: BSD-2-Clause
""" Provides a command line interface to add patches to an item. """

# Copyright (C) 2023, 2026 embedded brains GmbH & Co. KG
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

import argparse

from specitems import load_data, save_data

from .util import command_arguments


def cliaddpatches(argv: list[str] | None = None) -> None:
    """ Add patches to an item. """
    parser = argparse.ArgumentParser(description=cliaddpatches.__doc__)
    parser.add_argument(
        "--append",
        action="store_true",
        help="append the patches to the existing list of patches")
    parser.add_argument("item_file", metavar="ITEM_FILE", help="the item file")
    parser.add_argument("patches",
                        metavar="PATCH",
                        nargs="+",
                        help="a patch file")
    args = parser.parse_args(command_arguments(argv))
    data = load_data(args.item_file)
    data.pop("_file", None)
    if not args.append:
        data["archive-patches"] = []
    for patch in args.patches:
        with open(patch, "r", encoding="utf-8") as f:
            data["archive-patches"].append({
                "enabled-by": True,
                "patch": f.read(),
                "type": "inline"
            })
    save_data(args.item_file, data)
