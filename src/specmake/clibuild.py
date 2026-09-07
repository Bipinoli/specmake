# SPDX-License-Identifier: BSD-2-Clause
"""
Provides a command line interface to create a package workspace directory
according to the configuration file.
"""

# Copyright (C) 2020, 2025 embedded brains GmbH & Co. KG
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
import logging
import os
import sys

from specware import run_command

from .pkgitems import BuildItem
from .pkglist import ListError, list_files, list_targets
from .pkgworkspace import (BuildspaceConfig, WorkspaceConfig, create_workspace,
                           export_to_buildspace)
from .util import command_arguments, command_name, get_build_arguments


def _get_arguments(argv: list[str]) -> argparse.Namespace:

    def _add_arguments(parser):
        parser.add_argument(
            "--do-not-use-git",
            help="do not use git to track changes in the workspace",
            action="store_true")
        parser.add_argument("--config-directory",
                            help="the configuration directory",
                            default=".")
        parser.add_argument("--enabled-set",
                            help="the enabled set to configure the package",
                            default="")
        parser.add_argument("--name", help="the package name", default="pkg")
        parser.add_argument("--cache-directory",
                            help="the configuration cache directory",
                            default="config-cache")
        group = parser.add_mutually_exclusive_group()
        group.add_argument("--list-files",
                           action="store_true",
                           help="list the files included in the build")
        group.add_argument("--list-targets",
                           action="store_true",
                           help="list the targets included in the build")
        parser.add_argument('config_files', nargs='+')

    return get_build_arguments(argv, add_arguments=(_add_arguments, ))


def _make_deployment_directory(workspace_package: BuildItem) -> str:
    deployment_directory = workspace_package["deployment-directory"]
    if os.path.exists(os.path.join(deployment_directory, ".git")):
        assert os.path.isdir(deployment_directory)
    else:
        logging.info("build: create deployment directory: %s",
                     deployment_directory)
        os.makedirs(deployment_directory, exist_ok=True)
        status = run_command(["git", "init"], deployment_directory)
        assert status == 0
    return deployment_directory


def clibuild(argv: list[str] | None = None) -> None:
    """
    Create a package workspace directory according to the configuration files.
    """

    args = _get_arguments(command_arguments(argv))
    workspace_directory = os.path.abspath(args.config_directory)
    os.chdir(workspace_directory)

    logging.info("build: create workspace in: %s", workspace_directory)
    workspace_config = WorkspaceConfig(
        spec_directories=args.config_files,
        workspace_directory=workspace_directory,
        cache_directory=os.path.abspath(args.cache_directory),
        verify_specification_format=not args.no_spec_verify)
    workspace = create_workspace(workspace_config)

    if args.list_files or args.list_targets:
        try:
            if args.list_files:
                list_files(workspace.director, args.only, args.force,
                           args.skip)
            else:
                list_targets(workspace.director)
        except ListError as err:
            sys.exit(f"{command_name(argv)}: error: {err}")
        return

    deployment_directory = _make_deployment_directory(
        workspace.director.package)
    buildspace_config = BuildspaceConfig(
        spec_directory=os.path.join(deployment_directory, "build", "spec"),
        cache_directory=os.path.join(deployment_directory, "build", "cache"),
        git_directory=None if args.do_not_use_git else deployment_directory)
    buildspace = export_to_buildspace(workspace, buildspace_config)
    buildspace.director.build_package(args.only, args.force, args.skip)
