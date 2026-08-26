# SPDX-License-Identifier: BSD-2-Clause
""" Provides utility functions. """

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

import argparse
import datetime
import itertools
import json
import logging
import os
import shutil
import sys
from typing import Callable, Iterable, Optional

from specitems import ItemMapper, get_arguments


def _command_argv(argv: list[str] | None) -> list[str]:
    return sys.argv if argv is None else argv


def command_arguments(argv: list[str] | None) -> list[str]:
    """
    Is the argument vector of a command without the program name.

    A default argument binds its value at import, so an entry point
    which defaults to sys.argv keeps the vector of that moment for the
    life of the process.  A caller which rebinds sys.argv before the
    call still gets the original vector.  Take None for the vector of
    the process and read sys.argv here instead.
    """
    return _command_argv(argv)[1:]


def command_name(argv: list[str] | None) -> str:
    """ Is the name of the command which runs. """
    return os.path.basename(_command_argv(argv)[0])


def write_json(path: str, data: dict) -> None:
    """ Write the data as JSON to the path and make the directory of it. """
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8") as dst:
        json.dump(data, dst, sort_keys=True, indent=2)


def now_utc() -> str:
    """ Return the current UTC time in ISO 8601 format. """
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def duration(value: float | str) -> str:
    """ Convert a duration in seconds into a value with unit string. """
    if isinstance(value, str):
        return value
    assert value >= 0.0
    if value == 0.0:
        return "0s"
    if value < 1e-6:
        return f"{value * 1e9:.3f}ns"
    if value < 1e-3:
        return f"{value * 1e6:.3f}μs"
    if value < 1.0:
        return f"{value * 1e3:.3f}ms"
    return f"{value:.3f}s"


def copy_file(src_file: str, dst_file: str, log_context: str) -> None:
    """ Copy the source file to the destination file. """
    os.makedirs(os.path.dirname(dst_file), exist_ok=True)
    logging.info("%s: copy '%s' to '%s'", log_context, src_file, dst_file)
    shutil.copy2(src_file, dst_file)


def copy_files(src_dir: str, dst_dir: str, files: list[str],
               log_context: str) -> None:
    """
    Copy a list of files in the source directory to the destination directory
    preserving the directory of the files relative to the source directory.
    """
    for a_file in files:
        src_file = os.path.join(src_dir, a_file)
        dst_file = os.path.join(dst_dir, a_file)
        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
        logging.info("%s: copy '%s' to '%s'", log_context, src_file, dst_file)
        shutil.copy2(src_file, dst_file)


def copy_and_substitute(src_file: str, dst_file: str, mapper: ItemMapper,
                        log_context: str) -> None:
    """
    Copy the file from the source to the destination path and performs a
    variable substitution on the file content using the item mapper.
    """
    logging.info("%s: read: %s", log_context, src_file)
    with open(src_file, "r", encoding="utf-8") as src:
        logging.info("%s: substitute using mapper of item %s", log_context,
                     mapper.item.uid)
        content = mapper.substitute(src.read())
        logging.info("%s: write: %s", log_context, dst_file)
        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
        with open(dst_file, "w+", encoding="utf-8") as dst:
            dst.write(content)


def remove_empty_directories(scope: str, base: str) -> None:
    """
    Recursively remove all empty subdirectories of base and base itself if it
    gets empty.

    The scope is used for log messages.
    """
    removed: set[str] = set()
    for root, subdirs, files in os.walk(base, topdown=False):
        if files:
            continue
        if any(subdir for subdir in subdirs
               if os.path.join(root, subdir) not in removed):
            continue
        logging.info("%s: remove empty directory: %s", scope, root)
        os.rmdir(root)
        removed.add(root)


def get_build_arguments(
    argv: list[str],
    default_log_level: str = "INFO",
    description: Optional[str] = None,
    add_arguments: Iterable[Callable[[argparse.ArgumentParser],
                                     None]] = tuple(),
    post_process_arguments: Iterable[Callable[[argparse.Namespace],
                                              None]] = tuple()
) -> argparse.Namespace:
    """
    Create an argument parser with default logging and build options,
    optionally add arguments to the parser, parse the argument vector,
    initialize logging, optionally post process the parsed arguments, and
    return the parsed arguments.
    """

    def _add_arguments(parser):
        parser.add_argument("--only",
                            type=str,
                            action="append",
                            default=None,
                            help="build only these steps")
        parser.add_argument("--force",
                            type=str,
                            action="append",
                            default=None,
                            help="force to build these steps")
        parser.add_argument("--skip",
                            type=str,
                            action="append",
                            default=None,
                            help="skip these steps")
        parser.add_argument("--no-spec-verify",
                            action="store_true",
                            help="do not verify the specification")

    return get_arguments(argv, default_log_level, description,
                         itertools.chain((_add_arguments, ), add_arguments),
                         post_process_arguments)
