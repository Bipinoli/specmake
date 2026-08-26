# SPDX-License-Identifier: BSD-2-Clause
""" Converts Doxygen XML content to interface specification files. """

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

# pylint: disable=too-many-lines

import dataclasses
import fnmatch
import itertools
from pathlib import Path
import posixpath
import re
from typing import Any, Iterator
from xml.etree import ElementTree

from specitems import save_data

_Data = dict[str, Any]


class ConfigError(ValueError):
    """
    Raised for a ``spec-from-source:`` configuration problem.

    Raised while processing Doxygen XML, for example an item-to-group
    entry naming an unknown group, as opposed to an internal invariant
    violation. The CLI entry point catches only this, not every
    ``ValueError``, so a bug elsewhere that happens to raise a plain
    ``ValueError`` still surfaces as a traceback instead of being
    mistaken for a user-facing config error.
    """


#: The interface types whose parameters come from the declaration.
_FUNCTION_LIKE_TYPES = ("function", "macro")

_INVALID_NAME_CHARS = re.compile(r"[^a-zA-Z0-9]+")

_FUNCTION_POINTER = re.compile(r"([^(]+)\(\*\)\((.*)")

_COMMENT = re.compile(r"/\*.*?\*/|//[^\n]*", re.DOTALL)


def _slugify(name: str) -> str:
    """ Convert a name to the lowercase, hyphenated form used in UIDs. """
    return _INVALID_NAME_CHARS.sub("-", name.lower())


def _strip(text: str | None, default: str | None) -> str | None:
    if text is None:
        return default
    text = text.strip()
    if not text:
        return default
    return text


def _documented_names(block: dict) -> Iterator[dict[str, Any]]:
    """
    Yield one entry for each name a documentation block gives.

    ``@param a,b The two operands.`` documents two parameters with one
    block.  Doxygen reports every name of the list in the same block, so
    each of them takes the description and the direction of it.
    """
    for name_and_dir in block["names"]:
        name = _strip(name_and_dir["name"], None)
        if name is not None:
            yield {"dir": name_and_dir["dir"], "name": name}


class DoxygenItem:
    """ Represents a Doxygen item. """

    def __init__(self, ctx: "DoxygenContext", kind: str, doxygen_id: str,
                 name: str) -> None:
        self.ctx = ctx
        self.kind = kind
        self.doxygen_id = doxygen_id
        self.name = name
        self.data: _Data = {"brief": "", "description": ""}
        self.group_ids: list[str] = []
        self.file_ids: set[str] = set()

    def __lt__(self, other: "DoxygenItem") -> bool:
        return self.doxygen_id < other.doxygen_id

    @property
    def uid(self) -> str:
        """ Is the UID of the item. """
        group = self.group
        prefix = posixpath.dirname(group.uid)
        name = _slugify(self.name)
        name = name.removeprefix(
            self.ctx.groups.get(group.name, {}).get("remove-prefix", ""))
        return posixpath.join(prefix, name)

    def uid_relative_to(self, other: str) -> str:
        """ Get the UID of the item relative to the other UID. """
        return posixpath.relpath(self.uid, posixpath.dirname(other))

    @property
    def file(self) -> "DoxygenFile":
        """ Is the first file of the item. """
        try:
            return next(self.files)
        except StopIteration as err:
            raise ValueError(f"{self.name} has no file: {self}") from err

    @property
    def files(self) -> Iterator["DoxygenFile"]:
        """ Is the files of the item. """
        for file_id in self.file_ids:
            file = self.ctx.items[file_id]
            assert isinstance(file, DoxygenFile)
            yield file

    @property
    def group(self) -> "DoxygenGroup":
        """ Is the first group of the item. """
        try:
            return next(self.groups)
        except StopIteration as err:
            raise ValueError(f"{self.name} has no group: {self}") from err

    @property
    def groups(self) -> Iterator["DoxygenGroup"]:
        """ Is the group set of the item. """
        for group_id in self.group_ids:
            group = self.ctx.items[group_id]
            assert isinstance(group, DoxygenGroup)
            yield group

    @property
    def is_header(self) -> bool:
        """ Indicates if the item is a header file. """
        return False

    def _get_optional_text(self,
                           key: str,
                           default: str | None = None) -> str | None:
        return _strip(self.data.get(key), default)

    @property
    def brief(self) -> str | None:
        """ Is the brief description of the item. """
        return self._get_optional_text("brief", "Brief TODO.\n")

    @property
    def description(self) -> str | None:
        """ Is the detailed description of the item. """
        return self._get_optional_text("description")

    @property
    def notes(self) -> str | None:
        """ Is the notes section of the item. """
        return self._get_optional_text("notes")

    def export(self) -> dict:
        """
        Export the Doxygen item as specification item data.

        The data of the configuration applies to every item and the
        data of the group of the item applies over it, key by key.  A
        generated item copies the prose of its header word for word, so
        it carries the licence and the copyright of that header.  A run
        over headers of several authors has no single correct setting.
        """
        links: list[dict] = []
        for file in self.files:
            if file.is_header:
                links.append({
                    "role": "interface-placement",
                    "uid": file.uid_relative_to(self.uid)
                })
        for group in self.groups:
            links.append({
                "role": "interface-ingroup",
                "uid": group.uid_relative_to(self.uid)
            })
        data = {
            "SPDX-License-Identifier": "CC-BY-SA-4.0 OR BSD-2-Clause",
            "brief": self.brief,
            "copyrights": [],
            "description": self.description,
            "enabled-by": True,
            "index-entries": [],
            "links": links,
            "name": self.name,
            "notes": self.notes,
            "type": "interface"
        }
        data.update(self.ctx.data)
        data.update(self.group_config().get("data") or {})
        return data

    def config_group_name(self) -> str | None:
        """
        Is the name of the group whose configuration the item takes.

        A group item carries the configuration of its own name.  Every
        other item takes it from the group it belongs to, which may be
        absent, so resolve it without the exception raised by the group
        property.
        """
        if isinstance(self, DoxygenGroup):
            return self.name
        group = next(self.groups, None)
        return group.name if group is not None else None

    def group_config(self) -> dict[str, Any]:
        """ Is the configuration of the group of the item. """
        name = self.config_group_name()
        if name is None:
            return {}
        return self.ctx.groups.get(name, {})

    def add_extra_links(self, data: dict) -> None:
        """
        Add the links configured for the group of the item.

        Some links cannot be derived from the source, for example the
        constraint of a directive.  Without them, a regeneration would
        drop links a previous run had and the items would have to be
        edited by hand afterwards.

        An entry selects the items it applies to by their interface
        type, by their name, or by both.  A call context constraint
        holds for one function of a group and not for the next, so the
        interface type alone cannot address it.  The names are fnmatch
        patterns, like the patterns of a ``filter``.

        The links are added here rather than in ``export()``, since the
        ``interface-type`` used to select them is set by the subclasses
        after ``export()`` returned.
        """
        interface_type = data.get("interface-type")
        group_name = self.config_group_name()
        # A bare 'extra-links:' attribute parses as null, not as an
        # empty list, so treat it as absent rather than iterating over
        # None.
        for index, link in enumerate(self.group_config().get("extra-links")
                                     or []):
            interface_types = link.get("interface-types")
            if interface_types is not None \
               and interface_type not in interface_types:
                continue
            names = link.get("names")
            if names is not None and not self.matches_any(names):
                continue
            data["links"].append({"role": link["role"], "uid": link["uid"]})
            assert group_name is not None
            self.ctx.applied_extra_links.add((group_name, index))

    def save(self, dry_run: bool = False) -> None:
        """
        Save the exported item.

        A dry run resolves the item and writes no file, so it reaches
        every configuration attribute the item uses and reports what a
        real run would report.
        """
        data = self.export()
        self.add_extra_links(data)
        if dry_run:
            return
        path = self.ctx.spec_directory / f"{self.uid[1:]}.yml"
        path.parent.mkdir(parents=True, exist_ok=True)
        save_data(str(path), data)

    @property
    def is_excluded(self) -> bool:
        """
        Indicates if the item is left out of the generation.

        An interface item is generated only for what the specification
        covers.  A declaration which is not part of the interface, for
        example an include guard or a symbol of a source file which is
        not built, would otherwise have to be deleted after every run.

        The ``filter`` selects them.  It is a list of ``include`` and
        ``exclude`` rules, each holding fnmatch patterns.  The rules of
        the configuration are evaluated first and the rules of the group
        of the item after them, as one ordered list, and the first rule
        with a matching pattern decides.  So a family is included as a
        whole and the few members which are not part of the interface
        are excluded by a rule placed before it, and the precedence of
        the two levels is visible in their order rather than hidden in
        the name of a setting.

        An item no rule matches stays.  A group which specifies its
        interface therefore ends its filter with an ``exclude`` of
        ``'*'``.  A filter of excludes alone cannot express that: a
        register map holds thousands of names, so the rules would have
        to name each one, and a name added by a later vendor release
        would enter the interface unnoticed.

        A header file or a group is structural rather than a
        declaration.  No filter applies to it, so that the
        ``interface-placement`` of an included item still resolves and
        the header keeps saying that it is delivered.
        """
        if self.is_header or isinstance(self, DoxygenGroup):
            return False
        for rule in itertools.chain(self.ctx.filter,
                                    self.group_config().get("filter") or ()):
            for action, patterns in rule.items():
                if self.matches_any(patterns):
                    return action == "exclude"
        return False

    def matches_any(self, patterns: Any) -> bool:
        """
        Indicates if the item name matches one of the fnmatch patterns.

        Uses ``fnmatchcase()`` rather than ``fnmatch()``, which
        normalises the case of both operands on a case insensitive
        platform.  A C identifier is case sensitive, so ``FOO_BAR`` and
        ``foo_bar`` are two different declarations.
        """
        return any(
            fnmatch.fnmatchcase(self.name, pattern)
            for pattern in patterns or ())

    @property
    def review_gaps(self) -> list[str]:
        """ List what a human still has to supply for this item. """
        return self._review_gaps(self.export())

    def _review_gaps(self, data: dict) -> list[str]:
        gaps = []
        # An item type without a brief attribute, for example an
        # unspecified header file, has no brief to complete by hand.
        if "brief" in data and self._get_optional_text("brief") is None:
            gaps.append("placeholder brief")
        if any(not param["description"] for param in data.get("params") or []):
            gaps.append("undocumented params")
        # Only a function-like item takes its parameters from the
        # declaration.  A typedef of a function pointer documents the
        # parameters of the function it points to and specifies none
        # of them, so every name of it would count as a stray.
        if data.get("interface-type") in _FUNCTION_LIKE_TYPES:
            for name in self._stray_param_docs(data):
                gaps.append(f"stray param doc: {name}")
        # Only a function-like item carries the definition mapping with
        # a declared return type. A compound has a list of members here,
        # a typedef or a plain define a string, and none of them has a
        # return to document. A void function has none either, which is
        # why the declared type decides this and not a null 'return'.
        definition = data.get("definition")
        default = definition.get("default") if isinstance(definition,
                                                          dict) else None
        if (data.get("return") is None and isinstance(default, dict)
                and default["return"] is not None):
            gaps.append("undocumented return")
        return gaps

    def _stray_param_docs(self, data: dict) -> list[str]:
        """
        List the documented parameters which the declaration lacks.

        A block which reaches a parameter gives that parameter its name,
        by the match of the name or by the position.  A documented name
        which no parameter carries therefore documents nothing.  The
        vendor renamed the parameter or misspelled it, and a human has
        to decide which.
        """
        names = {param["name"] for param in data["params"]}
        return [
            name for name in self._documented_params() if name not in names
        ]

    def _get_initializer(self) -> str | None:
        body = self.data.get("initializer", None)
        if body is None:
            return None
        return body.replace("&gt;", ">").replace("&lt;", "<")

    def _documented_params(self) -> dict[str, dict[str, Any]]:
        """
        Collect the documented parameters of the item by name.

        A parameter documented twice keeps the last block, which is what
        Doxygen itself renders.
        """
        documented: dict[str, dict[str, Any]] = {}
        for block in self.data.get("param") or ():
            description = block["description"].strip()
            for entry in _documented_names(block):
                entry["description"] = description
                documented[entry["name"]] = entry
        return documented

    def _declared_params(self) -> list[tuple[dict[str, str], str | None]]:
        """
        Collect the declared parameters of the item with their names.

        A declaration names a parameter of a function through
        ``declname`` and a parameter of a macro through ``defname``.  A
        prototype may name none of its parameters, so the name is
        optional.  The lone ``void`` of an empty parameter list is a
        placeholder for the absence of a parameter and is left out.
        """
        declared: list[tuple[dict[str, str], str | None]] = []
        for definition in self.data.get("paramdefs") or ():
            name = _strip(definition.get("declname"),
                          _strip(definition.get("defname"), None))
            if name is None and _strip(definition.get("type"), None) == "void":
                continue
            declared.append((definition, name))
        return declared

    def _match_params(self) -> list[tuple[dict[str, str], str, Any]]:
        """
        Match the documented parameters to the declared ones.

        The declaration decides which parameters the item has and in
        which order.  A parameter takes the documentation block of its
        own name, so a header which documents its parameters in another
        order still describes each of them.  A parameter which the
        declaration does not name takes the next block which no other
        parameter claimed, since the documentation is then the only
        source of a name for it.
        """
        documented = self._documented_params()
        declared = self._declared_params()
        taken = {name for _, name in declared if name in documented}
        spare = [name for name in documented if name not in taken]
        matched: list[tuple[dict[str, str], str, Any]] = []
        for index, (definition, name) in enumerate(declared):
            if name is None:
                name = spare.pop(0) if spare else f"param_{index}"
            matched.append((definition, name, documented.get(name)))
        return matched

    def add_function_like_attributes(self, interface_type: str,
                                     data: dict[str, Any]) -> None:
        """ Add function-like attributes to the data. """
        assert interface_type in _FUNCTION_LIKE_TYPES
        data["interface-type"] = interface_type
        params: list[dict] = []
        paramdefs: list[str] = []
        for index, (definition, name,
                    entry) in enumerate(self._match_params()):
            params.append({
                "description": entry["description"] if entry else None,
                "dir": entry["dir"] if entry else None,
                "name": name
            })
            paramdefs.append(self.ctx.decl(definition, index))
        data["params"] = params
        type_name = self.data.get("type", None)
        data["definition"] = {
            "default": {
                "attributes": None,
                "body": self._get_initializer(),
                "params": paramdefs,
                "return": _strip(None if type_name == "void" else type_name,
                                 None)
            },
            "variants": []
        }
        retval = self.data.get("retval", [])
        if "return" in self.data or retval:
            data["return"] = {
                "return":
                _strip(self.data.get("return", None), None),
                "return-values": [{
                    "description": block["description"].strip(),
                    "value": entry["name"].strip(":")
                } for block in retval for entry in _documented_names(block)]
            }
        else:
            data["return"] = None

    def add_definition_kind(self, data: dict[str, Any]) -> None:
        """ Adds the definition kind attribute to the data. """
        if self.doxygen_id in self.ctx.compound_typedefs:
            if self.ctx.compound_typedefs[self.doxygen_id] is None:
                data["definition-kind"] = "typedef-only"
            else:
                data["definition-kind"] = f"typedef-and-{self.kind}"
        else:
            data["definition-kind"] = f"{self.kind}-only"


class DoxygenContainer(DoxygenItem):
    """ Represents a Doxygen container item. """

    def __init__(self, ctx: "DoxygenContext", kind: str, doxygen_id: str,
                 name: str) -> None:
        super().__init__(ctx, kind, doxygen_id, name)
        self.member_ids: list[str] = []

    def members(self) -> Iterator[DoxygenItem]:
        """ Yields the members of the item. """
        for member_id in self.member_ids:
            yield self.ctx.items[member_id]


class DoxygenCompound(DoxygenContainer):
    """ Represents a Doxygen compound item. """

    def export(self) -> dict:
        data = super().export()
        data["interface-type"] = self.kind
        self.add_definition_kind(data)
        definition: list[dict] = []
        for member in self.members():
            definition.append({
                "default": {
                    "brief":
                    member.brief,
                    "definition":
                    member.data["definition"].replace(
                        f"{self.name}::{member.name}", "${.:name}"),
                    "description":
                    member.description,
                    "kind":
                    "member",
                    "name":
                    member.name
                },
                "variants": []
            })
        data["definition"] = definition
        return data


class DoxygenDefine(DoxygenItem):
    """ Represents a Doxygen define item. """

    @property
    def is_excluded(self) -> bool:
        return super().is_excluded or self.is_include_guard

    @property
    def is_include_guard(self) -> bool:
        """
        Indicates if the define is the include guard of its own header.

        The guard is an artefact of the header, not a part of the
        interface.  It is recognised by a define without a value whose
        name is the name of the header it is declared in, in the spelling
        conventionally used for a guard.
        """
        # A guard is often followed by a comment explaining it, and
        # Doxygen reports that comment as the value of the define.  Only
        # what remains after removing the comments decides whether the
        # define has a value.
        initializer = self._get_initializer()
        if initializer is not None and _COMMENT.sub("", initializer).strip():
            return False
        try:
            file = self.file
        except ValueError:
            return False
        if not file.is_header:
            return False
        return self.name == _INVALID_NAME_CHARS.sub("_", file.name).upper()

    def export(self) -> dict:
        data = super().export()
        if self.data.get("param", []):
            self.add_function_like_attributes("macro", data)
        else:
            data["interface-type"] = "define"
            data["definition"] = {
                "default": self._get_initializer(),
                "variants": []
            }
        return data


class DoxygenDir(DoxygenItem):
    """ Represents a Doxygen directory item. """


class DoxygenEnum(DoxygenContainer):
    """ Represents a Doxygen enumeration item. """

    def export(self) -> dict:
        data = super().export()
        data["interface-type"] = "enum"
        self.add_definition_kind(data)
        for member in self.members():
            data["links"].append({
                "role": "interface-enumerator",
                "uid": member.uid_relative_to(self.uid)
            })
        return data


class DoxygenEnumValue(DoxygenItem):
    """ Represents a Doxygen enumerator item. """

    def export(self) -> dict:
        data = super().export()
        data["interface-type"] = "enumerator"
        data["links"] = []
        data["definition"] = {"default": None, "variants": []}
        return data


class DoxygenFile(DoxygenContainer):
    """ Represents a Doxygen file item. """

    @property
    def uid(self) -> str:
        """
        Is the UID of the item.

        A header of a directory which already carries its name is the
        header of that directory and takes the plain name ``header``.
        The name of the header is a component of the directory then, or
        the remove-prefix of the group reduced it to the extension.
        Every other header keeps its name after the ``header-`` prefix.
        """
        the_uid = super().uid
        if not self.is_header:
            return the_uid
        name = posixpath.basename(the_uid)[:-2]
        prefix = posixpath.dirname(the_uid)
        if not name or name in prefix.split("/"):
            basename = "header"
        else:
            basename = f"header-{name}"
        return posixpath.join(prefix, basename)

    @property
    def is_header(self) -> bool:
        return self.name.endswith(".h")

    @property
    def header_interface_type(self) -> str:
        """
        Is the interface type used for the header file item.

        A ``header-file`` item is the source of the generated header,
        while an ``unspecified-header-file`` item merely refers to a
        header which already exists and is itself the source of truth.
        """
        return self.group_config().get("header-interface-type", "header-file")

    def export(self) -> dict:
        data = super().export()
        del data["name"]
        interface_type = self.header_interface_type
        data["interface-type"] = interface_type
        data["path"] = self.name
        if interface_type == "unspecified-header-file":
            # The header is the source of truth, so the item specifies
            # no content of its own and has no place in an interface
            # domain to prefix a generated header with.
            for key in ("brief", "description", "notes"):
                del data[key]
            data["references"] = []
        else:
            data["prefix"] = ""
        return data


class DoxygenFunction(DoxygenItem):
    """ Represents a Doxygen function item. """

    def export(self) -> dict:
        data = super().export()
        self.add_function_like_attributes("function", data)
        return data


class DoxygenGroup(DoxygenContainer):
    """ Represents a Doxygen group item. """

    @property
    def uid(self) -> str:
        return self.ctx.groups.get(self.name, {}).get("uid",
                                                      f"/{self.name.lower()}")

    @property
    def generate_item(self) -> bool:
        """
        Indicates if a specification item is generated for the group.

        A project may have a hand-written item at the group uid, for
        example a design group requirement the generated items link to
        with an interface ingroup role.  Generating the group item would
        replace it.
        """
        return self.group_config().get("generate-group-item", True)

    def export(self) -> dict:
        data = super().export()
        data["name"] = self.data["title"]
        data["interface-type"] = "group"
        data["identifier"] = self.name
        return data

    def _review_gaps(self, data: dict) -> list[str]:
        gaps = super()._review_gaps(data)
        if not data.get("text"):
            gaps.append("missing text")
        return gaps


class DoxygenStruct(DoxygenCompound):
    """ Represents a Doxygen structure item. """


class DoxygenTypedef(DoxygenItem):
    """ Represents a Doxygen typedef item. """

    @property
    def aliases_compound(self) -> bool:
        """
        Indicate whether this typedef merely aliases a compound item.

        True if it merely names a struct/union/enum compound that
        Doxygen already represents as its own, separate item under the
        same generated UID, for example ``typedef enum e { ... } e;``,
        as opposed to a genuine standalone type alias such as
        ``typedef unsigned int my_type;`` that only coincidentally
        shares a name with some unrelated compound elsewhere.
        """
        for kind in ("struct", "union", "enum"):
            for candidate in self.ctx.items_by_name.get(kind,
                                                        {}).get(self.name, ()):
                if candidate.group_ids and candidate.uid == self.uid:
                    return True
        return False

    def export(self) -> dict:
        data = super().export()
        data["interface-type"] = "typedef"
        data["params"] = []
        data["return"] = None
        data["definition"] = {
            "default": "_ImplementationDefined",
            "variants": []
        }
        return data


class DoxygenUnion(DoxygenCompound):
    """ Represents a Doxygen union item. """


class DoxygenVariable(DoxygenItem):
    """ Represents a Doxygen variable item. """


class DoxygenNamespace(DoxygenItem):
    """ Represents a Doxygen namespace item. """


class DoxygenPage(DoxygenItem):
    """ Represents a Doxygen page item. """


_ITEM_TYPES = {
    "define": DoxygenDefine,
    "dir": DoxygenDir,
    "enum": DoxygenEnum,
    "enumvalue": DoxygenEnumValue,
    "file": DoxygenFile,
    "function": DoxygenFunction,
    "group": DoxygenGroup,
    "namespace": DoxygenNamespace,
    "page": DoxygenPage,
    "struct": DoxygenStruct,
    "typedef": DoxygenTypedef,
    "union": DoxygenUnion,
    "variable": DoxygenVariable
}


@dataclasses.dataclass
class _Scope:
    item: DoxygenItem
    data: Any
    key: str


def _tag_attribute(elem: ElementTree.Element, scope: _Scope,
                   attribute: str) -> _Scope:
    text = elem.text
    scope.data[attribute] = text if text is not None else ""
    return _Scope(scope.item, scope.data, attribute)


def _tag_item(elem: ElementTree.Element, scope: _Scope) -> _Scope:
    item = scope.item.ctx.items[_doxygen_id(elem)]
    if item.kind == "variable" and isinstance(scope.item, DoxygenCompound):
        scope.item.member_ids.append(item.doxygen_id)
    elif item.kind == "enumvalue":
        enum = scope.item
        assert isinstance(enum, DoxygenEnum)
        enum.member_ids.append(item.doxygen_id)

    # Doxygen places the description into multiple files.  Lets hope they are
    # all the same.
    item.data["brief"] = ""
    item.data["description"] = ""
    item.data["param"] = []
    item.data["paramdefs"] = []

    return _Scope(item, item.data, "")


def _tag_add_text(elem: ElementTree.Element, scope: _Scope) -> _Scope:
    text = elem.text
    # An unhandled container element leaves the ambient scope of the
    # enclosing item in place, and that scope has no text key.  Drop the
    # text instead of failing the whole run over a paragraph which
    # belongs to no documented field.
    if text is not None and scope.key in scope.data:
        scope.data[scope.key] = f"{scope.data[scope.key]} {text} "
    return scope


def _tag_brief(_elem: ElementTree.Element, scope: _Scope) -> _Scope:
    return _Scope(scope.item, scope.data, "brief")


def _tag_description(_elem: ElementTree.Element, scope: _Scope) -> _Scope:
    return _Scope(scope.item, scope.data, "description")


def _tag_param(_elem: ElementTree.Element, scope: _Scope) -> _Scope:
    paramdef: dict[str, str] = {}
    scope.item.data["paramdefs"].append(paramdef)
    return _Scope(scope.item, paramdef, "")


def _tag_parameteritem(_elem: ElementTree.Element, scope: _Scope) -> _Scope:
    block: dict[str, Any] = {"description": "", "names": []}
    scope.item.data[scope.key].append(block)
    return _Scope(scope.item, block, "description")


def _tag_parameterlist(elem: ElementTree.Element, scope: _Scope) -> _Scope:
    kind = elem.attrib["kind"]
    scope.item.data[kind] = []
    return _Scope(scope.item, scope.data, kind)


def _tag_parameternamelist(_elem: ElementTree.Element,
                           scope: _Scope) -> _Scope:
    # Carries no text of its own. It is a wrapper around <parametername>
    # that sits inside the same text-accumulating scope as the sibling
    # <parameterdescription>, so it must not fall through to the generic
    # tail-capturing fallback in _fill_items.
    return scope


def _tag_parametername(elem: ElementTree.Element, scope: _Scope) -> _Scope:
    # A documentation block lists one name per <parametername>, so the
    # names accumulate rather than replace each other.
    scope.data["names"].append({
        "dir": elem.attrib.get("direction"),
        "name": elem.text
    })
    return scope


def _append_element_text(elem: ElementTree.Element, scope: _Scope) -> _Scope:
    """ Appends an element's own text and tail to the current text scope. """
    text = elem.text or ""
    tail = elem.tail
    if tail is not None:
        text += tail
    if text:
        scope.data[scope.key] = f"{scope.data[scope.key].rstrip()} {text}"
    return scope


def _tag_type(elem: ElementTree.Element, scope: _Scope) -> _Scope:
    return _tag_attribute(elem, scope, "type")


def _tag_definition(elem: ElementTree.Element, scope: _Scope) -> _Scope:
    return _tag_attribute(elem, scope, "definition")


def _tag_argsstring(elem: ElementTree.Element, scope: _Scope) -> _Scope:
    return _tag_attribute(elem, scope, "argsstring")


def _tag_initializer(elem: ElementTree.Element, scope: _Scope) -> _Scope:
    return _tag_attribute(elem, scope, "initializer")


def _tag_declname(elem: ElementTree.Element, scope: _Scope) -> _Scope:
    return _tag_attribute(elem, scope, "declname")


def _tag_defname(elem: ElementTree.Element, scope: _Scope) -> _Scope:
    return _tag_attribute(elem, scope, "defname")


def _tag_simplesect(elem: ElementTree.Element, scope: _Scope) -> _Scope:
    return _tag_attribute(elem, scope, elem.attrib["kind"])


def _tag_title(elem: ElementTree.Element, scope: _Scope) -> _Scope:
    return _tag_attribute(elem, scope, "title")


def _tag_sectiondef(elem: ElementTree.Element, scope: _Scope) -> _Scope:
    kind = elem.attrib["kind"]
    more = {"description": ""}
    scope.data[f"section-{kind}"] = more
    return _Scope(scope.item, more, "description")


def _tag_listitem(_elem: ElementTree.Element, scope: _Scope) -> _Scope:
    scope.data[scope.key] = f"{scope.data[scope.key]}\n\n* "
    return scope


_TAG_HANDLER = {
    "argsstring": _tag_argsstring,
    "briefdescription": _tag_brief,
    "compounddef": _tag_item,
    "declname": _tag_declname,
    "definition": _tag_definition,
    "defname": _tag_defname,
    "description": _tag_description,
    "detaileddescription": _tag_description,
    "enumvalue": _tag_item,
    "initializer": _tag_initializer,
    "listitem": _tag_listitem,
    "memberdef": _tag_item,
    "para": _tag_add_text,
    "param": _tag_param,
    "parameterdescription": _tag_description,
    "parameteritem": _tag_parameteritem,
    "parameterlist": _tag_parameterlist,
    "parametername": _tag_parametername,
    "parameternamelist": _tag_parameternamelist,
    "ref": _append_element_text,
    "sectiondef": _tag_sectiondef,
    "simplesect": _tag_simplesect,
    "title": _tag_title,
    "type": _tag_type,
}


def _doxygen_id(elem: ElementTree.Element) -> str:
    try:
        return elem.attrib["id"]
    except KeyError:
        return elem.attrib["refid"]


def _relationships(elem: ElementTree.Element, item: DoxygenItem) -> None:
    assert isinstance(item, DoxygenContainer)
    for member_kind in ("enumvalue", "innerfile", "innerclass", "innergroup",
                        "member", "memberdef"):
        for member in elem.findall(f".//{member_kind}"):
            item.member_ids.append(_doxygen_id(member))


def _compound_relationships(elem: ElementTree.Element,
                            item: DoxygenItem) -> None:
    """
    Resolve the members which a compound only references.

    Doxygen documents a member of a struct or a union in the compound of
    that struct when it is declared outside a group, and in the compound
    of the group when the declaration is inside a group scope.  In the
    second case the compound of the struct holds a reference to the
    member instead of its definition, and the member would be lost.

    Only a member of a section definition is followed.  A member
    definition placed there directly is picked up by the scope while it
    is parsed, and the list of all members repeats every one of them, so
    following either would add a member twice.
    """
    assert isinstance(item, DoxygenContainer)
    for section in elem.findall("sectiondef"):
        for member in section.findall("member"):
            item.member_ids.append(_doxygen_id(member))


_RELATIONSHIP_HANDLER = {
    "file": _relationships,
    "group": _relationships,
    "struct": _compound_relationships,
    "union": _compound_relationships
}

_TAG_IS_KIND = {"enumvalue"}


def _get_kind_name(elem: ElementTree.Element) -> tuple[str, str]:
    try:
        kind = elem.attrib["kind"]
    except KeyError:
        if elem.tag not in _TAG_IS_KIND:
            raise
        kind = elem.tag
    name_tag = elem.find("name")
    if name_tag is None:
        name_tag = elem.find("compoundname")
    assert name_tag is not None
    name = name_tag.text
    assert name is not None
    return kind, name


_IGNORE = (
    "programlisting",
    "preformatted",
    # xrefsect (@todo, @bug, @deprecated, ...) carries its own labelled
    # text (for example "Todo") via unhandled child tags. Ignoring it
    # outright prevents that label text and its cross-reference
    # paragraph from leaking into whatever brief/description field
    # happens to be the ambient text scope at that point in the tree.
    "xrefsect",
    # inbodydescription holds the comments found inside a function body.
    # They document the implementation, not the interface, so they must
    # not reach a brief or description.  Ignoring the element also keeps
    # its paragraphs away from the ambient text scope of the enclosing
    # item, which has no text key of its own.
    "inbodydescription",
)


def _fill_items(elem: ElementTree.Element, scope: _Scope) -> None:
    if elem.tag in _IGNORE:
        return
    handler = _TAG_HANDLER.get(elem.tag, None)
    if handler is not None:
        scope = handler(elem, scope)
    elif isinstance(scope.data.get(scope.key), str):
        # No handler is registered for this tag, but we are accumulating
        # text for scope.key. Without this, both the element's own text and
        # everything textually after it in the same field would silently be
        # dropped, for example any inline Doxygen command other than @ref.
        scope = _append_element_text(elem, scope)
    for child in elem.findall("*"):
        _fill_items(child, scope)


_COMPOUND_TYPEDEF = re.compile(
    r"typedef\s+(enum|struct|union)(\s+[a-zA-Z0-9_]+)?")


def _validate_string_list(errors: list[str], path: str, value: list) -> None:
    for index, element in enumerate(value):
        if not isinstance(element, str):
            errors.append(f"{path}[{index}] must be a string, "
                          f"got {element!r}")


def _validate_extra_links(errors: list[str], path: str, links: Any) -> None:
    if not isinstance(links, list):
        errors.append(f"{path} must be a list, got {links!r}")
        return
    for index, link in enumerate(links):
        where = f"{path}[{index}]"
        if not isinstance(link, dict):
            errors.append(f"{where} must be a dict, got {link!r}")
            continue
        for attribute in ["role", "uid"]:
            if attribute not in link:
                errors.append(f"{where}/{attribute} is missing")
            elif not isinstance(link[attribute], str):
                errors.append(f"{where}/{attribute} must be a string, "
                              f"got {link[attribute]!r}")
        for attribute in ["interface-types", "names"]:
            patterns = link.get(attribute)
            if patterns is None:
                continue
            if not isinstance(patterns, list):
                errors.append(f"{where}/{attribute} must be a list or null, "
                              f"got {patterns!r}")
                continue
            _validate_string_list(errors, f"{where}/{attribute}", patterns)


_HEADER_INTERFACE_TYPES = ("header-file", "unspecified-header-file")


def _validate_group_entry(errors: list[str], name: str, entry: dict) -> None:
    """ Validate a single ``groups`` entry of the configuration. """
    if entry.get("extra-links") is not None:
        _validate_extra_links(errors, f"/groups/{name}/extra-links",
                              entry["extra-links"])
    data = entry.get("data")
    if data is not None and not isinstance(data, dict):
        errors.append(f"/groups/{name}/data must be a dict or null, "
                      f"got {data!r}")
    if entry.get("filter") is not None:
        _validate_filter(errors, f"/groups/{name}/filter", entry["filter"])
    generate_group_item = entry.get("generate-group-item")
    if generate_group_item is not None and not isinstance(
            generate_group_item, bool):
        errors.append(f"/groups/{name}/generate-group-item must be a boolean, "
                      f"got {generate_group_item!r}")
    header_interface_type = entry.get("header-interface-type")
    if (header_interface_type is not None
            and header_interface_type not in _HEADER_INTERFACE_TYPES):
        expected = " or ".join(repr(t) for t in _HEADER_INTERFACE_TYPES)
        errors.append(f"/groups/{name}/header-interface-type must be "
                      f"{expected}, got {header_interface_type!r}")


_FILTER_ACTIONS = ("include", "exclude")


def _validate_filter(errors: list[str], path: str, rules: Any) -> None:
    """ Validate a ``filter``, of the configuration or of a group. """
    if not isinstance(rules, list):
        errors.append(f"{path} must be a list, got {rules!r}")
        return
    expected = " or ".join(repr(action) for action in _FILTER_ACTIONS)
    for index, rule in enumerate(rules):
        where = f"{path}[{index}]"
        if not isinstance(rule, dict):
            errors.append(f"{where} must be a dict, got {rule!r}")
            continue
        # Exactly one action, since two in one rule would be decided by
        # the order the mapping happens to have.
        if len(rule) != 1 or not set(rule) <= set(_FILTER_ACTIONS):
            errors.append(f"{where} must have exactly one {expected} "
                          f"attribute, got {sorted(rule)}")
            continue
        action, patterns = next(iter(rule.items()))
        if not isinstance(patterns, list):
            errors.append(f"{where}/{action} must be a list, "
                          f"got {patterns!r}")
            continue
        _validate_string_list(errors, f"{where}/{action}", patterns)


def _validate_groups(errors: list[str], groups: dict) -> None:
    for name, entry in groups.items():
        if not isinstance(name, str):
            errors.append(f"/groups has a non-string key {name!r}")
        elif not isinstance(entry, dict):
            errors.append(f"/groups/{name} must be a dict, got {entry!r}")
        else:
            _validate_group_entry(errors, name, entry)


def _validate_item_to_group(errors: list[str], item_to_group: dict) -> None:
    for doxygen_id, group_name in item_to_group.items():
        if not isinstance(doxygen_id, str):
            errors.append(
                f"/item-to-group has a non-string key {doxygen_id!r}")
        elif group_name is not None and not isinstance(group_name, str):
            errors.append(f"/item-to-group/{doxygen_id} must be a string or "
                          f"null, got {group_name!r}")


def _validate_type_map(errors: list[str], type_map: dict) -> None:
    for from_type, to_item in type_map.items():
        if not isinstance(from_type, str):
            errors.append(f"/type-map has a non-string key {from_type!r}")
        elif not isinstance(to_item, str):
            errors.append(f"/type-map/{from_type} must be a string, "
                          f"got {to_item!r}")


def _validate_config(config: dict, require_full_config: bool) -> None:
    """
    Validate a ``spec-from-source:`` configuration upfront.

    Raises a single ``ConfigError`` naming every problem found, instead
    of letting each one surface separately as a raw crash deep inside a
    later call.

    Every attribute this module indexes or iterates into is checked
    down to its elements. A group name is looked up in a dict, an
    enabled group ends up in a set, and a type-map pair is handed to
    ``str.replace``, so an element of the wrong type would otherwise
    reach that code and raise ``TypeError`` well away from the
    configuration that caused it.

    ``--propose-config`` does not require a full config: it exists to
    bootstrap one, so ``data``, ``spec-directory``, ``groups`` and
    ``enabled-groups`` are only mandatory when ``require_full_config``
    is set, meaning a real generation run.

    A problem names its location as an attribute path relative to the
    ``spec-from-source`` attribute, for example ``/type-map/uint32_t``.
    The path uses the syntax of a variable substitution, so it reads the
    same way as the paths the specification uses elsewhere.
    """
    errors: list[str] = []

    def require(attribute: str, expected_type: type, type_name: str) -> bool:
        if attribute not in config:
            errors.append(f"/{attribute} is missing")
            return False
        if not isinstance(config[attribute], expected_type):
            errors.append(f"/{attribute} must be a {type_name}, "
                          f"got {config[attribute]!r}")
            return False
        return True

    def optional(attribute: str, expected_type: type, type_name: str) -> bool:
        value = config.get(attribute)
        if value is None:
            return False
        if not isinstance(value, expected_type):
            errors.append(f"/{attribute} must be a {type_name} or null, "
                          f"got {value!r}")
            return False
        return True

    def required_unless_bootstrapping(attribute: str, expected_type: type,
                                      type_name: str) -> bool:
        if require_full_config:
            return require(attribute, expected_type, type_name)
        return optional(attribute, expected_type, type_name)

    required_unless_bootstrapping("data", dict, "dict")
    required_unless_bootstrapping("spec-directory", str, "string")
    if required_unless_bootstrapping("groups", dict, "dict"):
        _validate_groups(errors, config["groups"])
    if optional("item-to-group", dict, "dict"):
        _validate_item_to_group(errors, config["item-to-group"])
    if optional("type-map", dict, "dict"):
        _validate_type_map(errors, config["type-map"])
    optional("default-group-name", str, "string")
    if config.get("filter") is not None:
        _validate_filter(errors, "/filter", config["filter"])
    if required_unless_bootstrapping("enabled-groups", list,
                                     "list of group names"):
        _validate_string_list(errors, "/enabled-groups",
                              config["enabled-groups"])

    if errors:
        problems = "\n".join(f"  - {error}" for error in errors)
        raise ConfigError(
            f"invalid 'spec-from-source' configuration:\n{problems}")


def _proposed_group_uid(group_name: str) -> str:
    # There's no way to guess which component a group actually belongs
    # under from its name alone, so make the placeholder impossible to
    # miss rather than emit something that merely looks plausible.
    return f"/TODO/{_slugify(group_name)}/if/group"


class DoxygenContext:
    """ Represents the Doxygen context. """

    # pylint: disable=too-many-instance-attributes
    def __init__(self,
                 config: dict,
                 require_full_config: bool = False) -> None:
        # Validate here rather than trusting the caller, so every
        # consumer of this class gets the same named error instead of a
        # crash deep in resolution. Only the caller knows whether this
        # run needs a full config, so it says so.
        _validate_config(config, require_full_config)
        # data/spec-directory/groups default rather than subscript
        # directly so --propose-config can bootstrap a DoxygenContext
        # from an empty (or nearly empty) config to discover what to
        # propose.
        spec_directory = config.get("spec-directory")
        self.spec_directory = Path(
            spec_directory if spec_directory is not None else "spec")
        self.data: dict = config.get("data") or {}
        # A bare 'type-map:' attribute parses as null, not as an empty
        # dict. Treat it as absent, otherwise _map_types() raises an
        # AttributeError on every declaration it processes.
        self.type_map: dict[str, str] = config.get("type-map") or {}
        self.default_group_name: str | None = config.get("default-group-name")
        # A bare 'filter:' attribute parses as null, not as an empty
        # list, so treat it as absent rather than iterating over None.
        self.filter: list[dict] = config.get("filter") or []
        self.groups: dict[str, dict[str, Any]] = config.get("groups") or {}
        # Copied, not aliased: resolution below adds an entry to
        # self.item_to_group for every inferred association, and that
        # must never leak back into the caller's config dict.
        self.item_to_group: dict[str, str | None] = dict(
            config.get("item-to-group") or {})
        self.items_by_kind: dict[str, dict[str, "DoxygenItem"]] = {}
        self.items_by_name: dict[str, dict[str, list["DoxygenItem"]]] = {}
        self.items: dict[str, "DoxygenItem"] = {}
        self.compound_typedefs: dict[str, str] = {}
        # Every extra link entry which reached an item, as the name of
        # its group and its index in the entries of that group.  An
        # entry which reaches no item matches nothing the run
        # generated, so the run reports it.
        self.applied_extra_links: set[tuple[str, int]] = set()

    def doxygen_xml_to_spec(self, xml_files: list[str]) -> None:
        """ Convert Doxygen XML files to specification item data.  """

        # In the first pass get the Doxygen identifier to item mappings and
        # vice versa.  Associate items with groups.
        self._gather_doxygen_id_to_item_mappings(xml_files)
        self._add_group_associations()
        self._add_file_associations()
        self._add_group_through_file_associations_or_config()

        # In the second pass fill the items
        for xml_file in xml_files:
            tree = ElementTree.parse(xml_file)
            _fill_items(tree.getroot(),
                        _Scope(DoxygenItem(self, "root", "", ""), {}, ""))

    def proposed_config(self, config: dict) -> dict:
        """
        Build the proposed ``spec-from-source:`` config.

        ``config`` with a ``groups:`` skeleton entry added for every
        group discovered in the Doxygen XML that isn't already
        configured, and ``data``/``spec-directory``/``enabled-groups``
        defaulted if absent. Never overwrites an existing ``groups``
        entry. Does not include ``item-to-group``, which
        ``--propose-config``'s two consumers handle separately:
        printing for review shows everything this run resolved, while
        ``--apply`` writing to disk only ever preserves what the config
        already had.

        Absent means missing or null, the same way validation and this
        constructor read it. A bare ``spec-directory:`` attribute left
        in the proposal would be written back by ``--apply`` and then
        rejected by the next real generation run, which does require a
        string there.
        """
        proposed = dict(config)
        proposed.pop("item-to-group", None)
        proposed["data"] = config.get("data") or {}
        spec_directory = config.get("spec-directory")
        proposed["spec-directory"] = (spec_directory if spec_directory
                                      is not None else "spec")
        proposed["enabled-groups"] = config.get("enabled-groups") or []
        groups = dict(proposed.get("groups") or {})
        for group in sorted(self.items_by_kind.get("group", {}).values()):
            groups.setdefault(group.name,
                              {"uid": _proposed_group_uid(group.name)})
        proposed["groups"] = groups
        return proposed

    def resolved_item_to_group(self) -> dict[str, str | None]:
        """
        Filter stale entries out of ``item_to_group``.

        Resolution mutates ``item_to_group`` with every association this
        run inferred, from an XML group, a containing file's group, or
        ``default-group-name``, not just the entries the config started
        with. It may also contain entries whose doxygen_id no longer
        corresponds to any item discovered in the current XML, for
        example the declaration was removed from the header. Filtering
        them out avoids crashing on the lookup or carrying a reference
        to a nonexistent item forward into a fresh proposal.
        """
        return {
            doxygen_id: group_name
            for doxygen_id, group_name in sorted(self.item_to_group.items())
            if doxygen_id in self.items
        }

    def preserved_item_to_group(self, config: dict) -> dict[str, str | None]:
        """
        Filter stale entries out of the config's own ``item-to-group``.

        Unlike ``item_to_group``, which resolution mutates with every
        inferred association, this dict is only ever what the config
        already had before this run: entries a user wrote by hand to pin
        an item to a group. Only entries whose doxygen_id no longer
        corresponds to any item discovered in the current XML are
        dropped; every other entry is preserved as is, including one
        currently shadowed by the item's own XML group membership.
        """
        item_to_group = config.get("item-to-group") or {}
        return {
            doxygen_id: group_name
            for doxygen_id, group_name in sorted(item_to_group.items())
            if doxygen_id in self.items
        }

    def decl(self, defs: dict[str, str], index: int) -> str:
        """ Get the declaration for the index-th parameter. """
        name = f"${{.:/params[{index}]/name}}"
        type_name = defs.get("type", None)
        if type_name is None:
            return name
        mobj = _FUNCTION_POINTER.match(type_name)
        if mobj is not None:
            type_name = mobj.group(1).strip()
            name = f"(*{name})({mobj.group(2)}"
        type_name = type_name.strip()
        if type_name.endswith("*"):
            return self._map_types(f"{type_name}{name}")
        return self._map_types(f"{type_name} {name}")

    def _map_types(self, declaration: str) -> str:
        for from_type, to_item in self.type_map.items():
            declaration = declaration.replace(from_type, to_item)
        return declaration

    def _learn_compound_typedefs(self, elem: ElementTree.Element) -> None:
        text = " ".join(elem.itertext()).strip()
        mobj = _COMPOUND_TYPEDEF.match(text)
        if mobj:
            self.compound_typedefs[elem.attrib["refid"]] = mobj.group(2)

    def _gather_doxygen_id_to_item_mappings(self, xml_files: list[str]):
        for xml_file in xml_files:
            tree = ElementTree.parse(xml_file)
            for elem in tree.iter():
                if elem.tag == "codeline" and elem.attrib.get(
                        "refkind", None) in ("compound", "member"):
                    self._learn_compound_typedefs(elem)
                    continue
                try:
                    doxygen_id = elem.attrib["id"]
                except KeyError:
                    continue
                try:
                    kind, name = _get_kind_name(elem)
                except KeyError:
                    continue
                item = self.items.setdefault(
                    doxygen_id, _ITEM_TYPES[kind](self, kind, doxygen_id,
                                                  name))
                self.items_by_kind.setdefault(kind,
                                              {}).setdefault(doxygen_id, item)
                self.items_by_name.setdefault(kind,
                                              {}).setdefault(name,
                                                             []).append(item)
                handler = _RELATIONSHIP_HANDLER.get(kind, None)
                if handler is not None:
                    handler(elem, item)

    def _add_group_associations(self):
        for group in self.items_by_kind["group"].values():
            assert isinstance(group, DoxygenGroup)
            group_id = group.doxygen_id
            for member_id in group.member_ids:
                self.items[member_id].group_ids.append(group_id)

    def _add_file_associations(self):
        for file in self.items_by_kind["file"].values():
            assert isinstance(file, DoxygenFile)
            for member_id in file.member_ids:
                self.items[member_id].file_ids.add(file.doxygen_id)

    def _add_to_group(self, item: DoxygenItem, group_name: str) -> None:
        # A caller reaching this with a group_name derived from an
        # already-discovered group (rather than user-supplied config) can
        # never miss the lookup below, since that name came from a group
        # already present in items_by_name, so a lookup miss here always
        # traces back to user-supplied config (an item-to-group entry or
        # default-group-name), never an internal invariant failure.
        #
        # KeyError is the only miss worth catching: _validate_config()
        # has already rejected an item-to-group value or a
        # default-group-name that is not a string, so group_name cannot
        # be unhashable here and the lookup cannot raise TypeError
        # instead.
        try:
            group = self.items_by_name["group"][group_name][0]
        except KeyError as err:
            raise ConfigError(
                f"cannot associate item {item.doxygen_id!r} with group "
                f"{group_name!r}: no such group was discovered in the "
                "Doxygen XML (check item-to-group and default-group-name "
                "in the configuration)") from err
        assert isinstance(group, DoxygenGroup)
        self.item_to_group[item.doxygen_id] = group_name
        group.member_ids.append(item.doxygen_id)
        item.group_ids.append(group.doxygen_id)

    def _add_group_through_file_associations_or_config(self):
        for kind, items in self.items_by_kind.items():
            if kind in ("dir", "group"):
                continue
            for item in items.values():
                if item.group_ids:
                    continue
                group_name = self.item_to_group.get(item.doxygen_id)
                if group_name is not None:
                    self._add_to_group(item, group_name)
                    continue
                try:
                    file_item = self.items[item.file.doxygen_id]
                    assert isinstance(file_item, DoxygenFile)
                except ValueError:
                    pass
                else:
                    try:
                        group_id = file_item.group_ids[0]
                    except IndexError:
                        pass
                    else:
                        group_name = self.items[group_id].name
                        self._add_to_group(item, group_name)
                        continue
                if self.default_group_name is not None:
                    self._add_to_group(item, self.default_group_name)
