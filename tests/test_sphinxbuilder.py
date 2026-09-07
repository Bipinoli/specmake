# SPDX-License-Identifier: BSD-2-Clause
""" Tests for the sphinxbuilder module. """

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

import logging
import os
from pathlib import Path

import pytest
from specitems import ItemGetValueContext

import specmake
from specmake import PackageComponent

from .util import create_package


def _set_enabled_set(item: PackageComponent, enabled_set: list[str]) -> None:
    logging.critical("%s: set enabled set: %s", item.uid, enabled_set)
    item["enabled-set"] = enabled_set
    item.selection.reset(enabled_set)
    for link in item.item.links_to_children("input"):
        child = item.director[link.item.uid]
        if isinstance(child, PackageComponent):
            _set_enabled_set(child, enabled_set)


def _run_command(args, cwd=None, stdout=None, env=None):
    if env is not None:
        assert "latexpdf" in args
        assert env["LATEXOPTS"] == "-halt-on-error"
    logging.info("run command: %s", " ".join(args))
    if args == ["python3", "-msphinx", "-M", "clean", "source", "build"]:
        return 0
    if args == ["python3", "-msphinx", "-M", "latexpdf", "source", "build"]:
        os.makedirs(os.path.join(cwd, "build/latex"))
        open(os.path.join(cwd, "build/latex/document.pdf"), "w+").close()
        return 0
    if args == ["python3", "-msphinx", "-M", "html", "source", "build"]:
        os.makedirs(os.path.join(cwd, "build/html"))
        open(os.path.join(cwd, "build/html/index.html"), "w+").close()
        return 0
    return 1


def test_sphinxbuilder(caplog, tmp_path, monkeypatch):
    monkeypatch.setattr(specmake.sphinxbuilder, "run_command", _run_command)
    package = create_package(caplog, tmp_path, Path("spec-packagebuild"),
                             ["sphinx-builder"])
    director = package.director
    doc = director["/pkg/deployment/doc"]

    def _show_inputs(ctx: ItemGetValueContext) -> str:
        lines: list[str] = []
        lines.append(f"input: {doc.input('document-section').uid}")
        lines.append(f"inputs: {[item.uid for item in doc.inputs()]}")
        link, item = doc.input_link("document-section")
        lines.append(f"input_link: {link.uid, item.uid}")
        lines.append(
            f"input_links: {[(link['name'], item.uid) for link, item in doc.input_links()]}"
        )
        return "\n".join(lines)

    doc.mapper.add_get_value("pkg/sphinx-section:/show-inputs", _show_inputs)

    assert doc.substitute(
        "${.:/document-author}") == "embedded brains GmbH & Co. KG"
    assert doc.substitute("${.:/document-year}") == "2020"
    assert doc.substitute(
        "${.:/document-copyright}") == "2020 embedded brains GmbH & Co. KG"
    doc.item["document-copyrights"].append("Copyright (C) 2023 John Doe")
    assert doc.substitute("${.:/document-author}"
                          ) == "embedded brains GmbH & Co. KG and contributors"
    assert doc.substitute(
        "${.:/document-copyright}"
    ) == "2020 embedded brains GmbH & Co. KG and contributors"
    doc.item["document-copyrights"].pop()
    assert doc.substitute(
        "${.:/document-title-page-title}") == "The \\break \\break Title"
    doc_title = doc.item["document-title"]
    doc.item["document-title"] = "012345678901234/678901234/6789"
    assert doc.substitute(
        "${.:/document-title-page-title}"
    ) == "012345678901234 \\break \\break /678901234/6789"
    doc.item["document-title"] = doc_title
    doc_src = director["/pkg/source/doc"]
    doc_src.load()
    doc_build = Path(director["/pkg/build/doc"].directory)
    assert not (doc_build / "source" / "copy.rst").exists()
    with pytest.raises(ValueError):
        doc.substitute("${.:/subprocess:args=error}}")
    assert "Interface" in doc.substitute("${.:/specdoc:0:specware}")
    assert "Package" in doc.substitute("${.:/specdoc:0:specmake}")
    director.build_package()
    assert (doc_build / "source" / "copy.rst").is_file()

    copy_and_substitute = doc_build / "source" / "copy-and-substitute.rst"
    with open(copy_and_substitute, "r", encoding="utf-8") as src:
        assert src.read() == """.. SPDX-License-Identifier: CC-BY-SA-4.0

.. Copyright (C) 2023 embedded brains GmbH & Co. KG

footer
2020 embedded brains GmbH \\& Co. KG
footer right
geometry
header left
sphinxsetup
The Title
The Title
2
The \\break \\break Title
:term:`Term`
:term:`Terms <Term>`
text
``blub()``
text
``DISABLED``
text
``spec:/​pkg/​deployment/​doc``
.. _SectionHeader:

Section content: sub-arch

.. _PkgSourceDocSubsection:

Subsection Header
^^^^^^^^^^^^^^^^^

Subsection content: sparc


Push component content: sub-arch

.. _subsection 2 Header:

subsection 2 Header
^^^^^^^^^^^^^^^^^^^

Subsection content: sub-arch

subsection 2 Header

input: /pkg/source/doc-subsection
inputs: ['/pkg/sub/component', '/pkg/source/empty', '/pkg/source/doc-subsection', '/pkg/source/doc-subsection-2', '/pkg/component', '/pkg/source/doc', '/pkg/source/doc-section', '/pkg/source/doc-element', '/pkg/source/doc-element-2', '/pkg/source/doc-element-3']
input_link: ('/pkg/source/doc-subsection', '/pkg/source/doc-subsection')
input_links: [('component', '/pkg/sub/component'), ('source', '/pkg/source/empty'), ('document-section', '/pkg/source/doc-subsection'), ('document-section', '/pkg/source/doc-subsection-2'), ('component', '/pkg/component'), ('source', '/pkg/source/doc'), ('document-section', '/pkg/source/doc-section'), ('document-element', '/pkg/source/doc-element'), ('document-element', '/pkg/source/doc-element-2'), ('document-element', '/pkg/source/doc-element-3')]
text
:ref:`SectionHeader`
text
:ref:`PkgSourceDocSubsection`
text
  Element content: sparc
- Element 2 Header

  Element 2 content: sparc

- Element 3 Header

  Element 3 content: sub-arch
text
:cite:`PkgDeploymentDoc`
text
*The Title* :cite:`PkgDeploymentDoc`
text
@manual{PkgDeploymentDoc,
  author = {{Bar, Foo and Doe, John and Long Name, This is a}},
  organization = {{Bár Organization, Short, Some Organization}},
  title = {{The Title}},
  url = {pkg/doc/doc.pdf},
  year = {2020},
}
text
- `spec:/​pkg/​component <pkg/component.extension>`__
text
Prologue

- `spec:/​pkg/​component <pkg/component.extension>`__

- `spec:/​pkg/​sub-b/​component <pkg/sub-b/component.extension>`__

- `spec:/​pkg/​sub/​component <pkg/sub/component.extension>`__

- `spec:/​pkg/​sub/​s/​component <pkg/sub/s/component.extension>`__

- `spec:/​pkg/​sub/​t/​component <pkg/sub/t/component.extension>`__

Epilogue
text
`spec:/​pkg/​sub-b/​component <pkg/sub-b/component.extension>`__, `spec:/​pkg/​sub/​component <pkg/sub/component.extension>`__, `spec:/​pkg/​sub/​s/​component <pkg/sub/s/component.extension>`__, and `spec:/​pkg/​sub/​t/​component <pkg/sub/t/component.extension>`__
text
Empty
text

text
- `spec:/​pkg/​source/​doc-element-3 <pkg/source/doc-element-3.extension>`__

- `spec:/​pkg/​source/​doc-section <pkg/source/doc-section.extension>`__

- `spec:/​pkg/​source/​doc-subsection-2
  <pkg/source/doc-subsection-2.extension>`__

- `spec:/​pkg/​source/​empty <pkg/source/empty.extension>`__

- `spec:/​pkg/​sub/​s/​component <pkg/sub/s/component.extension>`__

- `spec:/​pkg/​sub/​t/​component <pkg/sub/t/component.extension>`__
text
- `spec:/​pkg/​sub/​component <pkg/sub/component.extension>`__
text
- `spec:/​pkg/​sub-b/​component <pkg/sub-b/component.extension>`__

- `spec:/​pkg/​sub/​component <pkg/sub/component.extension>`__
text
- `spec:/​pkg/​component <pkg/component.extension>`__
text
- `spec:/​spec/​root <spec/root.extension>`__
text
"""

    copy_and_substitute_2 = doc_build / "source" / "copy-and-substitute-2.md"
    with open(copy_and_substitute_2, "r", encoding="utf-8") as src:
        assert src.read() == """% SPDX-License-Identifier: CC-BY-SA-4.0

% Copyright (C) 2023 embedded brains GmbH & Co. KG

footer
2020 embedded brains GmbH \\& Co. KG
footer right
geometry
header left
sphinxsetup
The Title
The Title
2
The \\break \\break Title
{term}`Term`
{term}`Terms <Term>`
{term}`target`
text
`blub()`
text
`DISABLED`
text
`spec:/​pkg/​deployment/​doc`
(SectionHeader)=

Section content: sub-arch

(PkgSourceDocSubsection)=

##### Subsection Header

Subsection content: sparc


Push component content: sub-arch

(subsection 2 Header)=

##### subsection 2 Header

Subsection content: sub-arch

subsection 2 Header

input: /pkg/source/doc-subsection
inputs: ['/pkg/sub/component', '/pkg/source/empty', '/pkg/source/doc-subsection', '/pkg/source/doc-subsection-2', '/pkg/component', '/pkg/source/doc', '/pkg/source/doc-section', '/pkg/source/doc-element', '/pkg/source/doc-element-2', '/pkg/source/doc-element-3']
input_link: ('/pkg/source/doc-subsection', '/pkg/source/doc-subsection')
input_links: [('component', '/pkg/sub/component'), ('source', '/pkg/source/empty'), ('document-section', '/pkg/source/doc-subsection'), ('document-section', '/pkg/source/doc-subsection-2'), ('component', '/pkg/component'), ('source', '/pkg/source/doc'), ('document-section', '/pkg/source/doc-section'), ('document-element', '/pkg/source/doc-element'), ('document-element', '/pkg/source/doc-element-2'), ('document-element', '/pkg/source/doc-element-3')]
text
{ref}`SectionHeader`
text
{ref}`PkgSourceDocSubsection`
text
  Element content: sparc
- Element 2 Header

  Element 2 content: sparc

- Element 3 Header

  Element 3 content: sub-arch
text
{cite}`PkgDeploymentDoc`
text
_The Title_ {cite}`PkgDeploymentDoc`
text
@manual{PkgDeploymentDoc,
  author = {{Bar, Foo and Doe, John and Long Name, This is a}},
  organization = {{Bár Organization, Short, Some Organization}},
  title = {{The Title}},
  url = {pkg/doc/doc.pdf},
  year = {2020},
}
text
- [spec:/​pkg/​component](pkg/component.extension)
text
Prologue

- [spec:/​pkg/​component](pkg/component.extension)

- [spec:/​pkg/​sub-b/​component](pkg/sub-b/component.extension)

- [spec:/​pkg/​sub/​component](pkg/sub/component.extension)

- [spec:/​pkg/​sub/​s/​component](pkg/sub/s/component.extension)

- [spec:/​pkg/​sub/​t/​component](pkg/sub/t/component.extension)

Epilogue
text
[spec:/​pkg/​sub-b/​component](pkg/sub-b/component.extension), [spec:/​pkg/​sub/​component](pkg/sub/component.extension), [spec:/​pkg/​sub/​s/​component](pkg/sub/s/component.extension), and [spec:/​pkg/​sub/​t/​component](pkg/sub/t/component.extension)
text
Empty
text

text
- [spec:/​pkg/​source/​doc-element-3](pkg/source/doc-element-3.extension)

- [spec:/​pkg/​source/​doc-section](pkg/source/doc-section.extension)

- [spec:/​pkg/​source/​doc-subsection-2](pkg/source/doc-subsection-2.extension)

- [spec:/​pkg/​source/​empty](pkg/source/empty.extension)

- [spec:/​pkg/​sub/​s/​component](pkg/sub/s/component.extension)

- [spec:/​pkg/​sub/​t/​component](pkg/sub/t/component.extension)
text
- [spec:/​pkg/​sub/​component](pkg/sub/component.extension)
text
- [spec:/​pkg/​sub-b/​component](pkg/sub-b/component.extension)

- [spec:/​pkg/​sub/​component](pkg/sub/component.extension)
text
- [spec:/​pkg/​component](pkg/component.extension)
text
- [spec:/​spec/​root](spec/root.extension)
text
"""

    doc_index = doc_build / "source" / "index.rst"
    with open(doc_index, "r", encoding="utf-8") as src:
        assert src.read() == """.. SPDX-License-Identifier: CC-BY-SA-4.0

.. Copyright (C) 2023 embedded brains GmbH & Co. KG

.. begin subcomponent list depth 0

.. end subcomponent list depth 0

.. begin subcomponent list depth 1
sub and sub-b
.. end subcomponent list depth 1

2020 embedded brains GmbH & Co. KG

embedded brains GmbH & Co. KG

| © 2023 Alice
| © 2020, 2026 embedded brains GmbH & Co. KG

| © 2023 Bob
| © 2023 embedded brains GmbH & Co. KG

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.

The Title
*********

.. topic:: Release: 2, Date: 2020-10-26, Status: Draft

    * 2020 embedded brains GmbH & Co. KG

    * e

.. topic:: Release: 1, Date: 1970-01-01, Status: Replaced

    Initial release.

.. _Release2Date20201026StatusDraft:

Release: 2, Date: 2020-10-26, Status: Draft
-------------------------------------------

* 2020 embedded brains GmbH & Co. KG

* e

.. _Release1Date19700101StatusReplaced:

Release: 1, Date: 1970-01-01, Status: Replaced
----------------------------------------------

Initial release.

.. table::
    :class: longtable
    :widths: 16,26,30,28

    +--------------+---------------------+-------------------+-----------+
    | Action       | Name                | Organization      | Signature |
    +==============+=====================+===================+===========+
    | Written by   | John Doe            | Some Organization |           |
    +              +---------------------+-------------------+-----------+
    |              | Foo Bar             | Bár Organization  |           |
    +--------------+---------------------+-------------------+-----------+
    | Super Action | This is a Long Name | Short             |           |
    +--------------+---------------------+-------------------+-----------+

.. toctree::
    :maxdepth: 4
    :numbered:

    copy-and-substitute
    copy-and-substitute-2
    glossary

.. begin specdoc
.. _SpecificationItems:

Specification items
===================

.. _SpecificationItemHierarchy:

Specification item hierarchy
----------------------------

The specification item types have the following hierarchy:

- :ref:`SpecTypeRootItemType`

.. _SpecificationItemTypes:

Specification item types
------------------------

.. _SpecTypeRootItemType:

Root Item Type
^^^^^^^^^^^^^^

This is the root specification item type.

Specification items consist of a defined set of key-value pairs called
attributes.  Each attribute key name shall be a :ref:`Name <SpecTypeName>`.
Item attributes may have dictionary, list, integer, floating-point number, and
string values or a combination of them.  The format of items is defined by the
type hierarchy rooting in this type.

The ``type`` attribute allows a specialization into domain-specific type
hierarchies.  For example, for a software specification possible type
refinements may be created to specify requirements, specializations of
requirements, interfaces, test suites, test cases, and requirement validations.

The specification items may be stored in or loaded from files in JSON or YAML
format. All explicit attributes shall be specified. The explicit attributes for
this type are:

SPDX-License-Identifier
    The attribute value shall be a :ref:`SpecTypeSPDXLicenseIdentifier`. It
    shall be the license of the item.

copyrights
    The attribute value shall be a list. Each list element shall be a
    :ref:`SpecTypeCopyright`. It shall be the list of copyright statements of
    the item.

enabled-by
    The attribute value shall be an :ref:`SpecTypeEnabledByExpression`. It
    shall define the conditions under which the item is enabled.

links
    The attribute value shall be a list. Each list element shall be a
    :ref:`SpecTypeLink`.

type
    The attribute value shall be a :ref:`SpecTypeName`. It shall be the item
    type.  The selection of types and the level of detail depends on a
    particular standard and product model.  We need enough flexibility to be in
    line with the European Cooperation for Space Standardization standard
    ECSS-E-ST-10-06 and possible future applications of other standards.  This
    attribute is used for type refinements.

.. _SpecificationAttributeSetsAndValueTypes:

Specification attribute sets and value types
--------------------------------------------

.. _SpecTypeCopyright:

Copyright
^^^^^^^^^

The value shall be a string. It shall be a copyright statement of a copyright
holder of the specification item. The value

- shall match with the regular expression
  "``^\\s*Copyright\\s+\\(C\)\\s+[0-9]+,\\s*[0-9]+\\s+.+\\s*$``",

- or, shall match with the regular expression
  "``^\\s*Copyright\\s+\\(C\)\\s+[0-9]+\\s*-\\s*[0-9]+\\s+.+\\s*$``",

- or, shall match with the regular expression
  "``^\\s*Copyright\\s+\\(C\)\\s+[0-9]+\\s+.+\\s*$``".

This type is used by the following types:

- :ref:`SpecTypeRootItemType`

.. _SpecTypeEnabledByExpression:

Enabled-By Expression
^^^^^^^^^^^^^^^^^^^^^

A value of this type shall be an expression which defines under which
conditions the specification item or parts of it are enabled.  The expression
is evaluated with the use of an *enabled set*.  This is a set of strings which
indicate enabled features.

A value of this type shall be of one of the following variants:

- The value may be a boolean. This expression evaluates directly to the boolean
  value.

- The value may be a set of attributes. Each attribute defines an operator.
  Exactly one of the explicit attributes shall be specified. The explicit
  attributes for this type are:

  and
      The attribute value shall be a list. Each list element shall be an
      :ref:`SpecTypeEnabledByExpression`. The **and** operator evaluates to the
      **logical and** of the evaluation results of the expressions in the list.

  eq
      The attribute value shall be a list of strings. The **eq** operator
      evaluates a list of strings with at least one element.  If all strings
      are equal, then the evaluation result is true, otherwise false.

  not
      The attribute value shall be an :ref:`SpecTypeEnabledByExpression`. The
      **not** operator evaluates to the **logical not** of the evaluation
      results of the expression.

  or
      The attribute value shall be a list. Each list element shall be an
      :ref:`SpecTypeEnabledByExpression`. The **or** operator evaluates to the
      **logical or** of the evaluation results of the expressions in the list.

- The value may be a list. Each list element shall be an
  :ref:`SpecTypeEnabledByExpression`. This list of expressions evaluates to the
  **logical or** of the evaluation results of the expressions in the list.

- The value may be a string. If the value is in the *enabled set*, this
  expression evaluates to true, otherwise to false.

This type is used by the following types:

- :ref:`SpecTypeEnabledByExpression`

- :ref:`SpecTypeRootItemType`

Please have a look at the following example:

.. code-block:: yaml

    enabled-by:
      and:
      - SOME_FEATURE
      - not: ANOTHER_FEATURE

.. _SpecTypeLink:

Link
^^^^

This set of attributes specifies a link from one specification item to another
specification item.  The links in a list are ordered.  The first link in the
list is processed first. All explicit attributes shall be specified. The
explicit attributes for this type are:

role
    The attribute value shall be a :ref:`SpecTypeName`. It shall be the role of
    the link.

uid
    The attribute value shall be an :ref:`SpecTypeUID`. It shall be the
    absolute or relative UID of the link target item.

This type is used by the following types:

- :ref:`SpecTypeRootItemType`

.. _SpecTypeName:

Name
^^^^

The value shall be a string. It shall be an attribute name. The value shall
match with the regular expression
"``^([a-z][a-z0-9-]*|SPDX-License-Identifier)$``".

This type is used by the following types:

- :ref:`SpecTypeLink`

- :ref:`SpecTypeRootItemType`

.. _SpecTypeSPDXLicenseIdentifier:

SPDX License Identifier
^^^^^^^^^^^^^^^^^^^^^^^

The value shall be a string. It defines the license of the item expressed
though an SPDX License Identifier. The value

- shall be equal to "``Apache-2.0``",

- or, shall be equal to "``CC-BY-SA-4.0``",

- or, shall be equal to "``CC-BY-SA-4.0 OR BSD-2-Clause``",

- or, shall be equal to "``CC-BY-SA-4.0 OR BSD-2-Clause OR MIT``",

- or, shall be equal to "``CC-BY-SA-4.0 OR BSD-2-Clause OR Apache-2.0 OR
  GPL-2.0-or-later``",

- or, shall be equal to "``CC-BY-SA-4.0 OR MIT``",

- or, shall be equal to "``BSD-2-Clause``",

- or, shall be equal to "``BSD-2-Clause OR MIT``",

- or, shall be equal to "``ECSS``",

- or, shall be equal to "``ESA UNCLASSIFIED - For Official Use``",

- or, shall be equal to "``MIT``".

This type is used by the following types:

- :ref:`SpecTypeRootItemType`

.. _SpecTypeUID:

UID
^^^

The value shall be a string. It shall be a valid absolute or relative item UID.

This type is used by the following types:

- :ref:`SpecTypeLink`
.. end specdoc

.. begin spec-name
:ref:`Root Item Type <SpecTypeRootItemType>`
.. end spec-name
"""
    doc_glossary = doc_build / "source" / "glossary.rst"
    with open(doc_glossary, "r", encoding="utf-8") as src:
        assert src.read() == """.. SPDX-License-Identifier: CC-BY-SA-4.0

.. Copyright (C) 2023 Alice
.. Copyright (C) 2020, 2026 embedded brains GmbH & Co. KG

.. _TermsDefinitionsAndAbbreviatedTerms:

Terms, definitions and abbreviated terms
########################################

.. glossary::

    target
        The target.

    Term
        This is the term.
"""
    doc_deployment = director["/pkg/deployment/doc"]
    assert doc_deployment["copyrights-by-license"] == {
        "BSD-2-Clause": [
            "Copyright (C) 2023 Bob",
            "Copyright (C) 2023 embedded brains GmbH & Co. KG"
        ]
    }

    _set_enabled_set(package, ["sphinx-builder-2"])
    doc_2 = director["/pkg/deployment/doc-2"]
    assert doc_2.substitute("${.:/document-bsd-2-clause-copyrights}") == ""
    assert doc_2.substitute(
        "${/spec/root:/spec-name}"
    ) == f"`Root Item Type <{tmp_path}/pkg/doc/index.html#spectyperootitemtype>`__"

    assert doc_2.section_level == 2
    with doc_2.section_level_scope(
            ItemGetValueContext(doc_2.item, "", "", None, None, {})) as args:
        assert doc_2.section_level == 3
        assert args == None
        with doc_2.section_level_scope(
                ItemGetValueContext(doc_2.item, "", "-1", None, None,
                                    {})) as args:
            assert doc_2.section_level == 2
            assert args == None
        assert doc_2.section_level == 3
        with doc_2.section_content(
                ItemGetValueContext(doc_2.item, "", "-1", None, None,
                                    {})) as (content, args):
            assert doc_2.section_level == 2
            assert content.section_level == 2
            assert args == None
        assert doc_2.section_level == 3
    with doc_2.section_level_scope(
            ItemGetValueContext(doc_2.item, "", "2:mo:re", None, None,
                                {})) as args:
        assert doc_2.section_level == 4
        assert args == "mo:re"
    assert doc_2.section_level == 2
    with doc_2.section_content(
            ItemGetValueContext(doc_2.item, "", "2:mo:re", None, None,
                                {})) as (content, args):
        assert doc_2.section_level == 4
        assert content.section_level == 4
        assert args == "mo:re"
    assert doc_2.section_level == 2

    doc_2.item["document-components"].append({
        "action": "foobar",
        "add-to-index": False,
        "value": 123
    })
    action_run = 0

    def action(_source_dir, _build_dir, component):
        nonlocal action_run
        action_run += 1
        assert component["value"] == 123

    doc_2.add_component_action("foobar", action)
    director.build_package()
    assert action_run == 1

    # Test make SphinxBuilder
    subcomponent = director["/pkg/sub/component"]
    _set_enabled_set(package, ["make"])
    director.build_package()
    doc_make_build = Path(director["/pkg/build/doc-make"].directory)
    doc_make_result = doc_make_build / "source" / "make.rst"
    with open(doc_make_result, "r", encoding="utf-8") as src:
        assert src.read() == f""".. SPDX-License-Identifier: CC-BY-SA-4.0

.. Copyright (C) 2024 embedded brains GmbH & Co. KG

bar
{tmp_path}/pkg/build/src/doc
{tmp_path}/pkg/build/doc-make
sparc/gr712rc/smp/4
"""


def test_document_references(caplog, tmp_path):
    package = create_package(caplog, tmp_path, Path("spec-packagebuild"),
                             ["sphinx-builder", "sphinx-builder-2"])
    doc = package.director["/pkg/deployment/doc"]

    # Check references
    with pytest.raises(ValueError):
        doc.substitute("${.:/ref:key=doc}}")
    assert doc.substitute("${.:/ref:this is a name,key=doc,label=Label,text}"
                          ) == ":ref:`this is a name text <Label>`"
    assert doc.substitute(
        "${.:/ref:key=doc-extra}") == ":ref:`LinkName <LinkLabel>`"
    assert doc.substitute("${.:/ref:name,key=doc-2,label=Label2}"
                          ) == "`name <pkg/doc-2/path/to/doc-2#label2>`__"
    assert doc.substitute("${.:/ref:name,key=doc-2,label=Label3,path=/more}"
                          ) == "`name <pkg/doc-2/path/to/doc-2/more#label3>`__"
    assert doc.substitute("${.:/ref:key=doc-2-extra}"
                          ) == "`LinkName <pkg/doc-2/LinkPath#linklabel>`__"

    # Check cite groups
    assert doc.substitute("${/pkg/component:/cite-group:does-not-exist}") == ""
    assert doc.substitute(
        "${/pkg/component:/cite-group:does-not-exist,flat=0,prologue=Prologue,epilogue=Epilogue,empty=Empty}"
    ) == "Empty"
    assert doc.substitute(
        "${/pkg/component:/cite-group:the-,group}"
    ) == "*The Title* :cite:`PkgDeploymentDoc`, :cite:`PkgDeploymentDoc2`, and :cite:`RefMisc`"
    assert doc.substitute("${/pkg/component:/cite-group:the-misc}"
                          ) == ":cite:`RefMisc` and :cite:`RefMisc2`"
    assert doc.substitute("${/pkg/component:/cite-group:the-doc-2-only}"
                          ) == "*The Title 2* :cite:`PkgDeploymentDoc2`"
    assert doc.substitute(
        "${/pkg/component:/cite-group:the-doc-2-only,label=Label}"
    ) == "`The Title 2 <pkg/doc-2#label>`__ :cite:`PkgDeploymentDoc2`"
    assert doc.substitute(
        "${/pkg/component:/cite-group:the-doc-extra}"
    ) == "`The Title, LinkName <pkg/doc/LinkPath#linklabel>`__ :cite:`PkgDeploymentDoc`"
    assert doc.substitute(
        "${/pkg/component:/cite-group:the-doc-extra,name=Name,label=Label,path=/Path}"
    ) == "`The Title, Name <pkg/doc/Path#label>`__ :cite:`PkgDeploymentDoc`"
    assert doc.substitute(
        "${/pkg/component:/cite-group:the-group,flat=0,prologue=Prologue,epilogue=Epilogue,empty=Empty}"
    ) == """Prologue

- **The Title** :cite:`PkgDeploymentDoc`

- **The Title 2** :cite:`PkgDeploymentDoc2`

- **The Title - More** :cite:`RefMisc`

Epilogue"""
    assert doc.substitute(
        "${/pkg/component:/cite-group:the-group,flat=0,label=Label,path=/path}"
    ) == """- `The Title <pkg/doc/path#label>`__ :cite:`PkgDeploymentDoc`

- `The Title 2 <pkg/doc-2/path#label>`__ :cite:`PkgDeploymentDoc2`

- **The Title - More** :cite:`RefMisc`"""
    assert doc.substitute(
        "${/pkg/component:/cite-group:the-group,flat=0,label=Label,path=/path,name=Name}"
    ) == """- `The Title, Name <pkg/doc/path#label>`__ :cite:`PkgDeploymentDoc`

- `The Title 2, Name <pkg/doc-2/path#label>`__ :cite:`PkgDeploymentDoc2`

- **The Title - More** :cite:`RefMisc`"""


def test_contributors_myst(caplog, tmp_path):
    package = create_package(caplog, tmp_path, Path("spec-packagebuild"),
                             ["sphinx-builder"])
    doc = package.director["/pkg/deployment/doc"]
    doc.mapper.set_format("x.md")
    assert doc.substitute("${.:/document-contributors}") == """```{eval-rst}
.. table::
    :class: longtable
    :widths: 16,26,30,28

    +--------------+---------------------+-------------------+-----------+
    | Action       | Name                | Organization      | Signature |
    +==============+=====================+===================+===========+
    | Written by   | John Doe            | Some Organization |           |
    +              +---------------------+-------------------+-----------+
    |              | Foo Bar             | Bár Organization  |           |
    +--------------+---------------------+-------------------+-----------+
    | Super Action | This is a Long Name | Short             |           |
    +--------------+---------------------+-------------------+-----------+
```"""
