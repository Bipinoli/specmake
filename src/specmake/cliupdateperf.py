# SPDX-License-Identifier: BSD-2-Clause
""" Provides a command line interface to update a performance limits item. """

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
import json

from specitems import (Item, ItemCache, ItemCacheConfig,
                       get_item_cache_arguments)

from .testoutputparser import augment_report
from .util import command_arguments

_LimitsByUID = dict[str, dict[str, dict[str, float]]]


def _calculate_limits(runtime_measurement: dict[str, float], uid: str,
                      variant: str, limits_by_uid: _LimitsByUID,
                      args: argparse.Namespace) -> dict[str, float]:
    minimum = runtime_measurement["min"]
    median = runtime_measurement["q2"]
    maximum = runtime_measurement["max"]
    min_lower_bound = args.lower_bound_scaler * minimum
    max_upper_bound = args.upper_bound_scaler * maximum
    median_lower_bound = max(args.lower_bound_scaler * median, min_lower_bound)
    median_upper_bound = min(args.upper_bound_scaler * median, max_upper_bound)
    if args.lazy:
        try:
            current_limits = limits_by_uid[uid][variant]
        except KeyError:
            pass
        else:
            limit = current_limits["min-lower-bound"]
            if limit <= minimum:
                min_lower_bound = limit
            limit = current_limits["median-lower-bound"]
            if limit <= median:
                median_lower_bound = limit
            limit = current_limits["median-upper-bound"]
            if limit >= median:
                median_upper_bound = limit
            limit = current_limits["max-upper-bound"]
            if limit >= maximum:
                max_upper_bound = limit
    return {
        "max-upper-bound": max_upper_bound,
        "median-lower-bound": median_lower_bound,
        "median-upper-bound": median_upper_bound,
        "min-lower-bound": min_lower_bound
    }


def _update_perf_limits(reports: list[dict], name_to_uid: dict[str, str],
                        limits_by_uid: _LimitsByUID,
                        args: argparse.Namespace) -> None:
    for report in reports:
        if "performance" in report["executable"]:
            if "info" not in report:
                augment_report(report, report["output"])
            try:
                test_cases = report["test-suite"]["test-cases"]
            except KeyError:
                print("no performance data available for:",
                      report["executable"])
                continue
            for test_case in test_cases:
                for runtime_measurement in test_case["runtime-measurements"]:
                    uid = name_to_uid[runtime_measurement["name"]]
                    variant = runtime_measurement["variant"]
                    limits_by_uid.setdefault(uid,
                                             {})[variant] = _calculate_limits(
                                                 runtime_measurement, uid,
                                                 variant, limits_by_uid, args)


def _write_perf_limits(perf_limits: Item, limits_by_uid: _LimitsByUID) -> None:
    links = [
        link for link in perf_limits["links"]
        if link["role"] != "performance-runtime-limits"
    ]
    for uid, limits in sorted(limits_by_uid.items()):
        links.append({
            "limits": limits,
            "role": "performance-runtime-limits",
            "uid": uid
        })
    perf_limits.data["links"] = links
    perf_limits.save()


def cliupdateperf(argv: list[str] | None = None) -> None:
    """ Update a performance limits item using test results. """

    def _add_arguments(parser):
        parser.add_argument("--lazy",
                            action="store_true",
                            help="only update necessary limits")
        parser.add_argument(
            "--lower-bound-scaler",
            type=float,
            default=0.9,
            help="scaler to define lower bounds (default: 0.9)")
        parser.add_argument(
            "--upper-bound-scaler",
            type=float,
            default=1.1,
            help="scaler to define upper bounds (default: 1.1)")
        parser.add_argument(
            "perf_limits_uid",
            metavar="PERF_LIMITS_UID",
            help="the UID of a performance limits item to update")
        parser.add_argument("reports",
                            metavar="REPORT",
                            nargs="+",
                            help="a test report JSON file")

    args = get_item_cache_arguments(command_arguments(argv),
                                    description=cliupdateperf.__doc__,
                                    add_arguments=(_add_arguments, ))
    cache_config = ItemCacheConfig(paths=args.spec_directories,
                                   cache_directory=args.cache_directory,
                                   initialize_links=False,
                                   resolve_proxies=False)
    item_cache = ItemCache(cache_config)
    name_to_uid: dict[str, str] = {}
    for item in item_cache.values():
        if item.get("type") != "requirement":
            continue
        if item["requirement-type"] != "non-functional":
            continue
        if item["non-functional-type"] == "performance-runtime":
            name_to_uid[item.ident] = item.uid
    perf_limits = item_cache[args.perf_limits_uid]
    limits_by_uid: _LimitsByUID = {}
    for link in perf_limits["links"]:
        if link["role"] == "performance-runtime-limits":
            limits_by_uid[link["uid"]] = link["limits"]
    for report in args.reports:
        with open(report, "r", encoding="utf-8") as src:
            data = json.load(src)
        _update_perf_limits(data["reports"], name_to_uid, limits_by_uid, args)
    _write_perf_limits(perf_limits, limits_by_uid)
