# SPDX-License-Identifier: BSD-2-Clause
""" ICD should compact brief-only defines and enumerations into a table. """

# Copyright (C) 2026 embedded brains GmbH & Co. KG
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

import re

from specitems import Item, SphinxContent

from specmake.linkhub import SpecMapper
from specmake.icdbuilder import ICDBuilder
from specmake.specdocbuilder import SpecDocumentBuilder, _spacify

from .util import create_item_cache

UIDS_DEFINE_WITH_ONLY_BRIEF = ("/define1", "/define2", "/define3", "/define4")
UID_DEFINE_WITH_DESCRIPTION = "/define-with-description"

UID_ENUM = "/enum"
UIDS_ENUM_WITH_ONLY_BRIEF = ("/enum-varient1", "/enum-varient2", "/enum-varient3")

class SpecMapperStub(SpecMapper):
    def get_link(self, item: Item, **_kwargs) -> str:
        name = item.get('name', item.get('path'))
        rst_markup = f"``{name}``"
        return rst_markup


class DocumentBuilderStub(ICDBuilder):
    def __init__(self, item_cache, mapper: SpecMapper) -> None:
        self.spec = item_cache
        self.mapper = mapper
        self.file_path = "icd.rst"
        self.spec_compare_registry = None
        self._pending_compact_items: list[Item] = []

    def add_item_changes(self, content, item: Item) -> None:
        pass


def stub_required_views_in_item(item: Item) -> None:
    item.view["document-paths"] = {}
    item.view["pre-qualified"] = True
    item.view["validated"] = True
    item.view["validation-dependencies"] = []


def render(item_cache, uids) -> str:
    domain = item_cache["/domain"]
    mapper = SpecMapperStub(domain, build_item=None, whoami="icd")
    builder = DocumentBuilderStub(item_cache, mapper)
    rst_content = SphinxContent()
    for uid in uids:
        item = item_cache[uid]
        stub_required_views_in_item(item)
        builder.add_item(rst_content, item)
    builder._flush_compact_items(rst_content)
    return str(rst_content)


def check_linkhub(uids, item_cache, text):
    # Each compacted item's name is present as text
    # which is a  target for a name-keyed linkhub link
    for uid in uids:
        item = item_cache[uid]
        assert _spacify(item["name"]) in text
        assert item["brief"].strip() in text

def check_compact_table(text):
    # Compact table with row per brief-only define
    assert re.search(r"^\s*\+[-+]+\+\s*$", text, re.MULTILINE), (
        "expected a grid table for the brief-only defines")
    assert "Name" in text
    assert "Brief Description" in text
    assert "Requirement" in text



def test_icd_compacts_all_brief_only_defines_into_a_table_but_leaves_others_into_section(tmpdir) -> None:
    item_cache = create_item_cache(tmpdir, "spec-icd-compact-table")

    # Enforcing order of defines with one non brief-only in the middle to check if all brief-only are grouped
    uids = (*UIDS_DEFINE_WITH_ONLY_BRIEF[:3], UID_DEFINE_WITH_DESCRIPTION, *UIDS_DEFINE_WITH_ONLY_BRIEF[3:])

    text = render(item_cache, uids)

    # Brief-only defines no longer get their own REQUIREMENT/BRIEF rubric pair
    assert text.count(".. rubric:: REQUIREMENT:") == 1
    assert text.count(".. rubric:: BRIEF DESCRIPTION:") == 1

    # Define with more than brief keeps the labelled section
    assert len(re.findall(r"^\.\. _Spec", text, re.MULTILINE)) == 1
    assert text.count(".. rubric:: DESCRIPTION:") == 1

    check_compact_table(text) 
    check_linkhub(UIDS_DEFINE_WITH_ONLY_BRIEF, item_cache, text)

    
def test_icd_leaves_less_than_3_defines_as_sections(tmpdir) -> None:
    item_cache = create_item_cache(tmpdir, "spec-icd-compact-table")
    two_brief_only = UIDS_DEFINE_WITH_ONLY_BRIEF[:2]
    text = render(item_cache, two_brief_only)

    assert text.count(".. rubric:: REQUIREMENT:") == 2
    assert text.count(".. rubric:: BRIEF DESCRIPTION:") == 2
    assert len(re.findall(r"^\.\. _Spec", text, re.MULTILINE)) == 2
    assert not re.search(r"^\s*\+[-+]+\+\s*$", text, re.MULTILINE), (
        "did not expect a grid table below the threshold")

    
def test_icd_compacts_brief_only_enums_into_a_table(tmpdir) -> None:
    item_cache = create_item_cache(tmpdir, "spec-icd-compact-table")

    uids = (UID_ENUM, *UIDS_ENUM_WITH_ONLY_BRIEF)
    text = render(item_cache, uids)

    assert text.count(".. rubric:: REQUIREMENT:") == 1
    assert text.count(".. rubric:: BRIEF DESCRIPTION:") == 1
    assert len(re.findall(r"^\.\. _Spec", text, re.MULTILINE)) == 1

    check_compact_table(text) 
    check_linkhub(uids, item_cache, text)
    
