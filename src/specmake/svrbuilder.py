# SPDX-License-Identifier: BSD-2-Clause
""" Builds an Software Verification Report (SVR). """

# Copyright (C) 2022, 2026 embedded brains GmbH & Co. KG
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

import itertools
from typing import Iterator

from specitems import Item, ItemGetValueContext, ROW_SPAN
from specware import gather_benchmarks_and_test_suites

from .directorystate import DirectoryState
from .membench import generate
from .pkgitems import PackageBuildDirector
from .linkhub import LinkHub
from .sphinxbuilder import spacify
from .specdocbuilder import SpecDocumentBuilder
from .testaggregator import get_test_result_status

_DEFINE_NOT_DEFINED = "requirement/functional/interface-define-not-defined"

_GROUP = ["interface/group", "requirement/non-functional/design-group"]


def _gather_design_components(item: Item, components: list[Item]) -> None:
    if item.type in _GROUP:
        components.append(item)
        return
    for parent in item.parents("interface-function"):
        components.append(parent)
    for parent in item.parents("requirement-refinement"):
        if parent.type in _GROUP:
            components.append(parent)
    if not components:
        for parent in item.parents("requirement-refinement"):
            _gather_design_components(parent, components)


def _get_name(kind_name: str) -> str:
    return kind_name[kind_name.find("/") + 1:]


def _get_kind_name(kind_name: str) -> tuple[str, str]:
    separator = kind_name.find("/")
    return kind_name[0:separator], kind_name[separator + 1:]


class SVRBuilder(SpecDocumentBuilder):
    """ Builds an Software Verification Report (SVR). """

    def __init__(self, director: PackageBuildDirector, item: Item):
        super().__init__(director, item)
        my_type = self.item.type
        self.mapper.add_get_value(
            f"{my_type}:/traceability-requirements-to-design",
            self._traceability_requirements_to_design)
        self.mapper.add_get_value(
            f"{my_type}:/traceability-design-to-requirements",
            self._traceability_design_to_requirements)
        self.mapper.add_get_value(f"{my_type}:/traceability-design-to-code",
                                  self._traceability_design_to_code)
        self.mapper.add_get_value(f"{my_type}:/traceability-code-to-design",
                                  self._traceability_code_to_design)
        self.mapper.add_get_value(f"{my_type}:/unit-verification",
                                  self._unit_verification)
        self.mapper.add_get_value(f"{my_type}:/performance-summary",
                                  self._performance_summary)
        self.mapper.add_get_value(f"{my_type}:/memory-benchmarks",
                                  self._get_membench)
        self._design_to_code: list[tuple[str, str]] = []

    def _req_to_design(self) -> Iterator[tuple[Item, list[Item]]]:
        for item in self.spec.get_related_requirements():
            components: list[Item] = []
            _gather_design_components(item, components)
            yield (item, components)

    def _traceability_requirements_to_design(self,
                                             _ctx: ItemGetValueContext) -> str:
        content = self.mapper.create_content(section_level=2)
        rows: list[tuple[str | int,
                         ...]] = [("Requirement", "Design Component")]
        for item, components in self._req_to_design():
            req: str | int = self.mapper.get_link(item)
            for component in sorted(set(components)):
                try:
                    path = component.view["document-paths"]["sdd"]
                except KeyError:
                    group = "requirement/non-functional/design-group"
                    if item.type == _DEFINE_NOT_DEFINED:
                        link = "N/A (interface define is not defined)"
                    elif item.type == group and item["identifier"] is None:
                        link = "N/A (external design)"
                    else:
                        link = "**no reference to SDD**"
                else:
                    link = self.mapper.format_link(component.view["sdd-name"],
                                                   path)
                rows.append((req, link))
                req = ROW_SPAN
            if isinstance(req, str) and req:
                rows.append(
                    (req, "N/A (no directly associated design components)"))
        content.add_grid_table(rows, [50, 50], font_size=-4)
        return str(content)

    def _traceability_design_to_requirements(self,
                                             _ctx: ItemGetValueContext) -> str:
        content = self.mapper.create_content(section_level=2)
        link_hub = self.input("link-hub")
        assert isinstance(link_hub, LinkHub)
        format_link = self.mapper.format_link
        rows = [("Design Component", "Requirement")]
        for _, info in sorted(link_hub.name_info.items(),
                              key=lambda x: _get_name(x[0])):
            if not isinstance(info, dict):
                continue
            variants = info.get("variants", [])
            for variant in itertools.chain([info], variants):
                name = format_link(spacify(variant["name"]), variant["link"])
                if variants:
                    file_path = variant["file"]
                    file_link = link_hub.name_info[f"file/{file_path}"]["link"]
                    file_link = format_link(spacify(file_path), file_link)
                    name = f"{name} in {file_link}"
                for item in sorted(variant["items"]):
                    path = item.view["default-document-path"]
                    rows.append((name, format_link(item.spec_2, path)))
        content.add_grid_table(rows, [60, 40], font_size=-4)
        return str(content)

    def _get_design_to_code(self) -> list[tuple[str, str]]:
        if self._design_to_code:
            return self._design_to_code
        link_hub = self.input("link-hub")
        assert isinstance(link_hub, LinkHub)
        format_link = self.mapper.format_link
        design_to_code: list[tuple[str, str]] = []
        for kind_name, info in sorted(link_hub.name_info.items(),
                                      key=lambda x: _get_name(x[0])):
            if not isinstance(info, dict):
                continue
            kind, name = _get_kind_name(kind_name)
            if kind == "file":
                continue
            if kind == "group":
                name = format_link(spacify(info["name"]), info["link"])
                for file_path in info["files"]:
                    file_link = link_hub.name_info[f"file/{file_path}"]["link"]
                    design_to_code.append(
                        (name, format_link(spacify(file_path), file_link)))
                continue
            variants = info.get("variants", [])
            for variant in itertools.chain([info], variants):
                name = format_link(spacify(variant["name"]), variant["link"])
                file_path = variant["file"]
                file_link = link_hub.name_info[f"file/{file_path}"]["link"]
                design_to_code.append(
                    (name, format_link(spacify(file_path), file_link)))
        self._design_to_code = design_to_code
        return design_to_code

    def _traceability_design_to_code(self, _ctx: ItemGetValueContext) -> str:
        content = self.mapper.create_content(section_level=2)
        rows: list[tuple[str | int, ...]] = [("Design Component", "File")]
        last = ""
        for design, code in self._get_design_to_code():
            rows.append((ROW_SPAN if last == design else design, code))
            last = design
        content.add_grid_table(rows, [60, 40], font_size=-4)
        return str(content)

    def _traceability_code_to_design(self, _ctx: ItemGetValueContext) -> str:
        content = self.mapper.create_content(section_level=2)
        code_to_design = sorted(
            (code, design) for design, code in self._get_design_to_code())
        rows: list[tuple[str | int, ...]] = [("File", "Design Component")]
        last: str | int = ROW_SPAN
        for code, design in code_to_design:
            rows.append((ROW_SPAN if last == code else code, design))
            last = code
        content.add_grid_table(rows, [40, 60], font_size=-4)
        return str(content)

    def _unit_verification(self, _ctx: ItemGetValueContext) -> str:
        content = self.mapper.create_content(section_level=2)
        test_suites: list[Item] = []
        gather_benchmarks_and_test_suites(self.item.cache["/testsuites/unit"],
                                          test_suites)
        get_link = self.mapper.get_link
        format_link = self.mapper.format_link
        rows = [("Test Case", "Status")]
        unspecified: dict[str, list[str]] = {}
        for test_suite in sorted(test_suites):
            for test_case in test_suite.children("test-case"):
                rows.append((get_link(test_case),
                             get_test_result_status(test_case, self.mapper, "",
                                                    "")))
            for test_results in test_suite.view.get("test-results",
                                                    {}).values():
                for data in test_results:
                    for test_case in data["unspecified-test-cases"]:
                        unspecified.setdefault(test_case["name"], []).append(
                            format_link(data["status"], data["link"]))
        rows_2 = [["Test Case without Specification", "Status"]]
        for name, status in sorted(unspecified.items()):
            rows_2.append([name, ", ".join(status)])
        content.add_grid_table(rows, [80, 20], font_size=-1)
        content.add_grid_table(rows_2, [80, 20], font_size=-1)
        return str(content)

    def _performance_summary(self, _ctx: ItemGetValueContext) -> str:
        content = self.mapper.create_content(section_level=2)
        types = ("requirement/non-functional/performance-runtime", )
        rows = [("Requirement", "Status")]
        for item in self.spec.get_related_items_by_type(types):
            rows.append((self.mapper.get_link(item),
                         get_test_result_status(item, self.mapper, "", "")))
        content.add_grid_table(rows, [80, 20], font_size=-1)
        return str(content)

    def _get_membench(self, ctx: ItemGetValueContext) -> str:
        with self.section_content(ctx) as (content, _):
            link, membench = self.input_link("membench-results")
            assert isinstance(membench, DirectoryState)
            label = membench.substitute(link["build-label"])
            sections_by_uid = membench.json_load()[label]["membench"]
            root = self.item.cache["/rtems/req/mem-basic"]
            table_pivots = ["/rtems/req/mem-smp-1"]
            generate(content, sections_by_uid, root, table_pivots, self.mapper)
            return "\n".join(content)
