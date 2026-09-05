# SPDX-License-Identifier: BSD-2-Clause
""" Produces GCDA files from a test log. """

# Copyright (C) 2022 embedded brains GmbH & Co. KG
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

import base64
import glob
import json
import logging
import os
import shutil
from subprocess import run as subprocess_run

from typing import Iterable

from .directorystate import DirectoryState


def gcov_stream(report: dict, uid: str) -> None | bytes:
    """
    Get the gcov information stream of the test report.

    Return None if the test did not end, if the report carries no gcov
    information, or if the gcov information is corrupt.
    """
    executable = report["executable"]
    if "line-end-of-test" not in report["info"]:
        logging.info("%s: discard coverage data of failed test: %s", uid,
                     executable)
        return None
    begin = report.get("line-gcov-info-base64-begin", None)
    if begin is None:
        logging.info("%s: discard due to missing gcov info begin: %s", uid,
                     executable)
        return None
    end = report.get("line-gcov-info-base64-end", None)
    if end is None:
        logging.info("%s: discard due to missing gcov info end: %s", uid,
                     executable)
        return None
    if report.get("gcov-info-hash",
                  "") != report.get("gcov-info-hash-calculated", ""):
        logging.info("%s: discard corrupt report: %s", uid, executable)
        return None
    return base64.b64decode("".join(report["output"][begin + 1:end]))


def copy_gcno(source_directory: str, files: Iterable[str],
              destination: str) -> None:
    """ Copy the GCNO files of the source directory to the destination. """
    for file in files:
        if file.endswith(".gcno"):
            file_dest = file.replace(source_directory, destination)
            os.makedirs(os.path.dirname(file_dest), exist_ok=True)
            shutil.copy2(file, file_dest)


def remove_gcda(directory: str, uid: str) -> None:
    """ Remove the GCDA files of the directory. """
    for file in glob.glob(f"{directory}/**/*.gcda", recursive=True):
        logging.warning(
            "%s: remove unexpected *.gcda file in build directory: '%s'", uid,
            file)
        os.remove(file)


def merge_gcov_stream(stream: bytes, gcov_tool: str,
                      working_directory: str) -> None:
    """ Merge the gcov information stream into the GCDA files. """
    subprocess_run([gcov_tool, "merge-stream"],
                   check=True,
                   cwd=working_directory,
                   input=stream)


def move_gcda(source_directory: str, destination: str) -> None:
    """ Move the GCDA files of the source directory to the destination. """
    for file in glob.glob(f"{source_directory}/**/*.gcda", recursive=True):
        file_dest = file.replace(source_directory, destination)
        os.makedirs(os.path.dirname(file_dest), exist_ok=True)
        os.replace(file, file_dest)


class GCDAProducer(DirectoryState):
    """ Runs the gcov-tool to produce GCDA files from a test log. """

    def run(self):
        super().run()
        self.discard_and_clear()

        build = self.input("build")
        assert isinstance(build, DirectoryState)

        logging.info("%s: copy *.gcno files from '%s' to '%s'", self.uid,
                     build.directory, self.directory)
        copy_gcno(build.directory, build.files(), self.directory)
        remove_gcda(build.directory, self.uid)

        log = self.input("log")
        assert isinstance(log, DirectoryState)

        gcov_tool = self["gcov-tool"]
        cwd = self["working-directory"]

        logging.debug("%s: load file: %s", self.uid, log.file)
        with open(log.file, "r", encoding="utf-8") as src:
            data = json.load(src)

        for report in data["reports"]:
            logging.debug("%s: consider: %s", self.uid, report["executable"])
            stream = gcov_stream(report, self.uid)
            if stream is None:
                continue
            logging.debug("%s: process: %s", self.uid, report["executable"])
            merge_gcov_stream(stream, gcov_tool, cwd)

        logging.info("%s: move *.gcda files from '%s' to '%s'", self.uid,
                     build.directory, self.directory)
        move_gcda(build.directory, self.directory)

        self.create_symbolic_links(self["symbolic-links"])
        self.description.add(f"""Produce GCDA files in directory
{self.description.path(self.directory)}""")
        self.run_post_actions()
