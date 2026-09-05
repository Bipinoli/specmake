# SPDX-License-Identifier: BSD-2-Clause
""" Builds a Software Requirements Specification (SRS). """

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

from specitems import Item, ItemGetValueContext, TextContent

from .pkgitems import PackageBuildDirector
from .specdocbuilder import SpecDocumentBuilder


def _add_no_requirements(content: TextContent, which: str) -> None:
    content.add(f"""At the time of pre-qualification, no specific {which}
requirements have been identified, but they shall be determined as
appropriate for each individual mission or system in which RTEMS is
integrated.""")


class SRSBuilder(SpecDocumentBuilder):
    """ Builds a Software Requirements Specification (SRS). """

    documents_items = True

    def __init__(self, director: PackageBuildDirector, item: Item) -> None:
        super().__init__(director, item)
        my_type = self.item.type
        self.mapper.add_get_value(f"{my_type}:/srs-requirements",
                                  self._get_requirements)
        self.mapper.add_get_value(f"{my_type}:/srs-constraints",
                                  self._get_constraints)
        self.mapper.add_get_value(
            "requirement/functional/action:/text-template",
            self._get_action_template)
        perf_runtime = "requirement/non-functional/performance-runtime"
        self.mapper.add_get_value(f"{perf_runtime}:/environment",
                                  self._get_environment)
        self.mapper.add_get_value(f"{perf_runtime}:/limit-kind",
                                  self._get_limit_kind)
        self.mapper.add_get_value(f"{perf_runtime}:/limit-condition",
                                  self._get_limit_condition)
        self.mapper.add_get_value(
            "runtime-measurement-test:/params/buffer-count", self._get_count)
        self.mapper.add_get_value(
            "runtime-measurement-test:/params/sample-count", self._get_count)

    def get_items_of_document(self) -> list[Item]:
        return self.spec.get_related_requirements()

    def _get_constraints(self, ctx: ItemGetValueContext) -> str:
        with self.section_content(ctx) as (content, _):
            for item in self.spec.get_related_items_by_type("constraint"):
                self.add_item(content, item)
            return content.join()

    def _get_action_template(self, ctx: ItemGetValueContext) -> str:
        interface_functions = list(ctx.item.parents("interface-function"))
        if len(interface_functions) == 1:
            link = self.mapper.get_link(interface_functions[0])
            return f"When the {link} directive is called."
        return "When the directive is called."

    def _get_environment(self, _ctx: ItemGetValueContext) -> str:
        return "${ENVIRONMENT}"

    def _get_limit_kind(self, _ctx: ItemGetValueContext) -> str:
        return "${LIMIT_KIND}"

    def _get_limit_condition(self, _ctx: ItemGetValueContext) -> str:
        return "${LIMIT_CONDITION}"

    def _get_count(self, ctx: ItemGetValueContext) -> str:
        return str(ctx.value[ctx.key])

    def _add_requirements(self, content: TextContent, section: str,
                          types: tuple[str, ...]) -> None:
        with content.section(section):
            for item in self.spec.get_related_items_by_type(types):
                self.add_item(content, item)

    def _get_requirements(self, ctx: ItemGetValueContext) -> str:
        with self.section_content(ctx) as (content, _):
            content.add(".. include:: ../include/abbreviations.rst")
            with content.section("Requirements"):
                self._add_requirements(
                    content, "Functional requirements",
                    ("requirement/functional/action",
                     "requirement/functional/capability",
                     "requirement/functional/function",
                     "requirement/functional/interface-define-not-defined"))
                self._add_requirements(
                    content, "Performance requirements",
                    ("requirement/non-functional/performance",
                     "requirement/non-functional/performance-runtime",
                     "requirement/non-functional"
                     "/performance-runtime-environment",
                     "requirement/non-functional/performance-runtime-limits"))
                with content.section("Interface requirements"):
                    icd = self.substitute("${doc-ts-icd:/cite-long}")
                    content.add(f"For interface requirements see the {icd}.")
                with content.section("Operational requirements"):
                    _add_no_requirements(content, "operational")
                with content.section("Resources requirements"):
                    _add_no_requirements(content, "resources")
                self._add_requirements(
                    content,
                    "Design requirements and implementation constraints",
                    ("glossary/group", "requirement/non-functional/design",
                     "requirement/non-functional/design-group",
                     "requirement/non-functional/design-target"))
                with content.section("Security and privacy requirements"):
                    _add_no_requirements(content, "security and privacy")
                with content.section("Portability requirements"):
                    _add_no_requirements(content, "portability")
                self._add_requirements(
                    content, "Software quality requirements",
                    ("requirement/non-functional/quality", ))
                with content.section("Software reliability requirements"):
                    _add_no_requirements(content, "software reliability")
                with content.section("Software maintainability requirements"):
                    _add_no_requirements(content, "software maintainability")
                with content.section("Software safety requirements"):
                    _add_no_requirements(content, "software safety")
                with content.section(
                        "Data definition and database requirements"):
                    _add_no_requirements(content,
                                         "data definition and database")
                with content.section("Human factors related requirements"):
                    _add_no_requirements(content, "human factors")
                with content.section(
                        "Adaptation and installation requirements"):
                    _add_no_requirements(content, "adaption and installation")
            return content.join()
