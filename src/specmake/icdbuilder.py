# SPDX-License-Identifier: BSD-2-Clause
""" Builds an Interface Control Document (ICD). """

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

from specitems import Item, ItemGetValueContext, TextContent

from .pkgitems import PackageBuildDirector
from .specdocbuilder import SpecDocumentBuilder


def _visit_domain(item: Item, interfaces: list[Item]) -> None:
    interfaces.append(item)
    for item_2 in itertools.chain(item.children("interface-placement"),
                                  item.parents("interface-enumerator")):
        _visit_domain(item_2, interfaces)


class ICDBuilder(SpecDocumentBuilder):
    """ Builds an Interface Control Document (ICD). """

    documents_items = True

    def __init__(self, director: PackageBuildDirector, item: Item) -> None:
        super().__init__(director, item)
        my_type = self.item.type
        self.mapper.add_get_value(f"{my_type}:/icd-requirements-and-design",
                                  self._get_requirements_and_design)

    def get_items_of_document(self) -> list[Item]:
        return self.spec.get_related_interfaces()

    def _add_interface_requirements(self, content: TextContent) -> None:
        types = ("requirement/non-functional/interface-requirement", )
        for item in self.spec.get_related_items_by_type(types):
            self.add_item(content, item)

    def _add_interface_design(self, content: TextContent) -> None:
        types = ("interface/domain", )
        for domain in self.spec.get_related_items_by_type(types):
            with content.section(domain["name"]):
                content.add(self.mapper.substitute(domain["description"]))
                interfaces: list[Item] = []
                _visit_domain(domain, interfaces)
                for item in sorted(interfaces):
                    self.add_item(content, item)

    def _get_requirements_and_design(self, ctx: ItemGetValueContext) -> str:
        with self.section_content(ctx) as (content, _):
            with content.section("Requirements and design"):
                with content.section(
                        "General provisions to the requirements in the IRD"):
                    content.add(
                        "There are no general provisions to requirements "
                        "in the :term:`IRD`.")
                with content.section("Interface requirements"):
                    self._add_interface_requirements(content)
                with content.section("Interface design"):
                    self._add_interface_design(content)
            return content.join()
