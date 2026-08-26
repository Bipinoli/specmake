# SPDX-License-Identifier: BSD-2-Clause
"""
Provides a command line interface to update the test timeouts using the
specified test reports.
"""

# Copyright (C) 2024, 2026 embedded brains GmbH & Co. KG
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
import dataclasses
import datetime
import json
import logging
from pathlib import Path

from specitems import (Item, ItemCache, ItemCacheConfig,
                       get_item_cache_arguments)

from .util import command_arguments


@dataclasses.dataclass
class _LastUpdate:
    old: datetime.datetime
    new: datetime.datetime


def _update_timeouts(args: argparse.Namespace, report_path: str,
                     last_update: _LastUpdate, timeouts: dict[str, list[int]],
                     reports: list) -> None:
    error_factor = args.error_factor
    warning_factor = args.warning_factor
    minimum_timeout = args.minimum_timeout
    for report in reports:
        name = Path(report["executable"]).name
        new_duration = report.get("execution-duration-in-seconds",
                                  report.get("duration"))
        if not new_duration:
            logging.debug("%s: %s: has no execution duration", report_path,
                          name)
            continue
        update_time: str | None = report.get("start-time")
        if update_time is not None:
            update_datetime = datetime.datetime.fromisoformat(update_time)
            if update_datetime <= last_update.old:
                logging.debug("%s: %s: skip out of date result", report_path,
                              name)
                continue
            last_update.new = max(last_update.new, update_datetime)
        durations = timeouts.setdefault(name, [])
        try:
            maximum = max(durations)
        except ValueError:
            pass
        else:
            if new_duration > error_factor * maximum + minimum_timeout:
                logging.error(
                    "%s: %s: duration %s is greater than %s * %s + %s",
                    report_path, name, new_duration, error_factor, maximum,
                    minimum_timeout)
                continue
            if new_duration > warning_factor * maximum + minimum_timeout:
                logging.warning(
                    "%s: %s: duration %s is greater than %s * %s + %s",
                    report_path, name, new_duration, warning_factor, maximum,
                    minimum_timeout)
        logging.debug("%s: %s: add duration: %s", report_path, name,
                      new_duration)
        durations.append(new_duration)


def _prepare_timeouts(item: Item, report_path: str, data: dict, reset: bool,
                      reset_done: set[str]) -> dict[str, list[int]]:
    timeout_key = data["timeout-key"]
    logging.info("%s: timeout key: %s", report_path, timeout_key)
    reset_key = f"{item.uid} {timeout_key}"
    if reset and reset_key not in reset_done:
        reset_done.add(reset_key)
        timeouts = {}
    else:
        timeouts = item["timeouts"].get(timeout_key, {})
    item["timeouts"][timeout_key] = timeouts
    return timeouts


def _get_arguments(argv: list[str]) -> argparse.Namespace:

    def _add_arguments(parser):
        parser.add_argument('--dry-run',
                            action="store_true",
                            default=False,
                            help="do not save timeout items")
        parser.add_argument('--reset',
                            action="store_true",
                            help="reset the timeouts")
        parser.add_argument(
            '--test-timeouts',
            type=str,
            default="test-timeouts",
            help="the test timeouts item UID basename (default: test-timeouts)"
        )
        parser.add_argument(
            '--minimum-timeout',
            type=float,
            default=10.0,
            help="the minimum timeout used by the test runner (default: 10.0)")
        parser.add_argument(
            '--warning-factor',
            type=float,
            default=1.2,
            help="a new duration greater than the factor times the current "
            "maximum duration plus the minimum timeout "
            "is a warning (default: 1.2)")
        parser.add_argument(
            '--error-factor',
            type=float,
            default=1.9,
            help="a new duration greater than the factor times the current "
            "maximum duration plus the minimum timeout "
            "is an error (default: 1.9)")
        parser.add_argument("reports",
                            metavar="REPORT",
                            nargs="+",
                            help="a test report JSON file")

    return get_item_cache_arguments(argv,
                                    description=cliupdatetimeouts.__doc__,
                                    add_arguments=(_add_arguments, ))


def cliupdatetimeouts(argv: list[str] | None = None) -> None:
    """
    Update the test timeouts using the specified test reports.

    The target UID and the timeout key are obtained from the test report.
    """
    args = _get_arguments(command_arguments(argv))
    cache_config = ItemCacheConfig(paths=args.spec_directories,
                                   cache_directory=args.cache_directory,
                                   initialize_links=False,
                                   resolve_proxies=False)
    item_cache = ItemCache(cache_config)
    reset_done: set[str] = set()
    last_updates: dict[str, _LastUpdate] = {}
    for report_path in args.reports:
        logging.info("%s: evaluate reports", report_path)
        with open(report_path, "r", encoding="utf-8") as src:
            data = json.load(src)
        try:
            target = data["target"]
        except KeyError:
            logging.warning("%s: report has no target attribute", report_path)
            continue
        uid = f"{target.removesuffix('/target')}/{args.test_timeouts}"
        logging.info("%s: test timeouts item UID: %s", report_path, uid)
        item = item_cache[uid]
        time_of_last_update = datetime.datetime.fromisoformat(
            item.get("time-of-last-update", "1970-01-01"))
        last_update = last_updates.setdefault(
            uid, _LastUpdate(time_of_last_update, time_of_last_update))
        timeouts = _prepare_timeouts(item, report_path, data, args.reset,
                                     reset_done)
        _update_timeouts(args, report_path, last_update, timeouts,
                         data["reports"])
        if not args.dry_run:
            item["time-of-last-update"] = last_updates[uid].new.isoformat()
            item.save()
