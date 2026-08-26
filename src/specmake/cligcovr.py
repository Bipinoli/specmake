# SPDX-License-Identifier: BSD-2-Clause
"""
Provides a command line interface to remove existing coverage files and run
gcovr using test output.
"""

# Copyright (C) 2025 embedded brains GmbH & Co. KG
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
import base64
import glob
import os
import re
import shutil
import subprocess

from .util import command_arguments

_GCOV_INFO = re.compile(r"\*\*\* BEGIN OF GCOV INFO BASE64 \*\*\*(.*)"
                        r"\*\*\* END OF GCOV INFO BASE64 \*\*\*")


def cligcovr(argv: list[str] | None = None) -> None:
    """ Removes existing coverage files and runs gcovr using test output. """
    parser = argparse.ArgumentParser()
    parser.add_argument("-o",
                        "--object-directory",
                        type=str,
                        default="build",
                        help="the path to the object directory")
    parser.add_argument(
        "-d",
        "--destination-directory",
        help="the path to the coverage report destination directory",
        default="coverage")
    parser.add_argument("-w",
                        "--working-directory",
                        help="the path to the working directory",
                        default=".")
    parser.add_argument("-r",
                        "--gcovr",
                        help="the path to the gcovr executable",
                        default="gcovr")
    parser.add_argument("-g",
                        "--gcov",
                        help="the path to the gcov executable",
                        default="gcov")
    parser.add_argument("-t",
                        "--gcov-tool",
                        help="the path to the gcov-tool executable",
                        default="gcov-tool")
    parser.add_argument("-v",
                        "--verbose",
                        action="store_true",
                        help="be verbose")
    parser.add_argument("outputs",
                        metavar="OUTPUTS",
                        nargs="+",
                        help="the test output files")
    args = parser.parse_args(command_arguments(argv))
    for gcda in glob.glob(os.path.join(args.object_directory, "**/*.gcda"),
                          recursive=True):
        print("remove:", gcda)
        os.unlink(gcda)
    for output in args.outputs:
        with open(output, "r", encoding="latin-1") as src:
            lines = src.readlines()
            mobj = _GCOV_INFO.search("".join(line.strip() for line in lines))
            if mobj:
                gcov_info = base64.b64decode(mobj.group(1))
                cmd = [args.gcov_tool, "merge-stream"]
                print(f"run in {args.working_directory}: {' '.join(cmd)}")
                subprocess.run(cmd,
                               check=True,
                               input=gcov_info,
                               cwd=args.working_directory)
    shutil.rmtree(args.destination_directory, ignore_errors=True)
    os.makedirs(args.destination_directory)
    cmd = [
        args.gcovr, "--include-internal-functions", "--json",
        f"{args.destination_directory}/report.json", "--json-summary",
        f"{args.destination_directory}/summary.json", "--json-summary-pretty",
        f"--gcov-executable={args.gcov}", "--html-details",
        f"{args.destination_directory}/index.html", "--html-medium-threshold",
        "80.0", "--html-high-threshold", "100.0", "--object-directory",
        args.object_directory, args.object_directory
    ]
    if args.verbose:
        cmd.insert(1, "--verbose")
    print(f"run in {args.working_directory}: {' '.join(cmd)}")
    subprocess.run(cmd, check=True, cwd=args.working_directory)
