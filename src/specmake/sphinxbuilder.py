# SPDX-License-Identifier: BSD-2-Clause
""" Builds documents for the Sphinx or MyST documentation framework. """

# Copyright (C) 2020, 2026 embedded brains GmbH & Co. KG
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

from contextlib import contextmanager
import fnmatch
import itertools
import logging
import os
import posixpath
import re
import shutil
from typing import Any, Callable, Iterator, Optional
import yaml

from specitems import (ROW_SPAN, BibTeXCitationProvider, Copyrights,
                       DocumentGlossaryConfig, GlossaryConfig, Item, ItemCache,
                       ItemGetValueContext, ItemMapper, ItemValueProvider,
                       Link, SphinxContent, TextContent, generate_glossary,
                       get_value_subprocess, is_enabled, list_terms,
                       to_iterable)
from specware import BSD_2_CLAUSE_LICENSE, run_command

from .directorystate import DirectoryState
from .pkgitems import (BuildItem, BuildItemFactory, BuildItemMapper,
                       PackageBuildDirector, PackageComponent)
from .testoutputparser import augment_report

_BREAK = "\\break"

_PUSH_ENABLED_BY = re.compile(r"^\${\.:/push-enabled-by:(.+)}$")

_POP_ENABLED_BY = re.compile(r"^\${\.:/pop-enabled-by")

_EXTENSIONS = (".md", ".rst")

_HEADERS = {
    ".md":
    re.compile(
        r"^% SPDX-License-Identifier: (.+)\n\n"
        r"((% Copyright \(C\).*\n)+)\n",
        flags=re.MULTILINE),
    ".rst":
    re.compile(
        r"^\.\. SPDX-License-Identifier: (.+)\n\n"
        r"((\.\. Copyright \(C\).*\n)+)\n",
        flags=re.MULTILINE)
}

_INVISIBLE_SPACES_AT = re.compile(r"([\/_-]+)")


def spacify(text: str) -> str:
    """ Add invisible spaces to enable line breaks. """
    return _INVISIBLE_SPACES_AT.sub("\u200b\\1", text)


def _kwargs_split(kwargs: dict[str, str], key: str) -> frozenset[str]:
    if key in kwargs:
        return frozenset(kwargs[key].split("+"))
    return frozenset()


def _kwargs_get(kwargs: dict[str, str], key: str, link: Link,
                default: str | None) -> str | None:
    return kwargs.get(key, link.data.get(key, default))


def _normal_title(item: Item) -> str:
    return item["document-title"].replace(_BREAK, " ")


def _get_normal_title(ctx: ItemGetValueContext) -> str:
    return ctx.substitute_and_transform(_normal_title(ctx.item))


def _get_sphinx_title(ctx: ItemGetValueContext) -> str:
    mapper = ctx.mapper
    assert isinstance(mapper, BuildItemMapper)
    content = mapper.create_content()
    content.add_header(_get_normal_title(ctx), level=1)
    return content.join().rstrip()


def _get_release(ctx: ItemGetValueContext) -> str:
    return str(len(ctx.item["document-releases"]))


def _no_action(_source_dir: str, _build_dir: str,
               _component: dict[str, Any]) -> None:
    pass


def _get_contributors(ctx: ItemGetValueContext) -> str:
    header = ("Action", "Name", "Organization", "Signature")
    rows: list[tuple[str | int, str, str, str]] = [header]
    last_action = ""
    for action in ctx.mapper.substitute_data(
            ctx.item["document-contributors"]):
        name = action["action"]
        for contributor in action["contributors"]:
            first = contributor["first-name"]
            last = contributor["last-name"]
            action_cell = ROW_SPAN if name == last_action else name
            rows.append((action_cell, f"{first} {last}",
                         contributor["organization"], ""))
            last_action = name
    mapper = ctx.mapper
    assert isinstance(mapper, BuildItemMapper)
    content = mapper.create_content()
    content.add_grid_table(rows, widths=[16, 26, 30, 28], header_rows=1)
    return content.join()


def _latex_escape(value: str) -> str:
    return value.replace("_", "\\_").replace("&", "\\&")


_COPYRIGHT = re.compile(r"^\s*Copyright\s+\(C\)\s+", re.IGNORECASE)
_YEARS = re.compile(r"^[0-9, ]*")


def _document_copyright(item: Item, mapper: ItemMapper) -> str:
    copyrights = item["document-copyrights"]
    main = _COPYRIGHT.sub("", copyrights[0])
    main = mapper.substitute(main)
    if len(copyrights) == 1:
        return main
    return f"{main} and contributors"


def _document_author(item: Item, mapper: ItemMapper) -> str:
    return _YEARS.sub("", _document_copyright(item, mapper))


def _document_year(item: Item, mapper: ItemMapper) -> str:
    match = _YEARS.search(_document_copyright(item, mapper))
    assert match
    return match.group(0).split(",")[-1].strip()


def _get_document_copyright(ctx: ItemGetValueContext) -> str:
    return _document_copyright(ctx.item, ctx.mapper)


def _get_document_author(ctx: ItemGetValueContext) -> str:
    return _document_author(ctx.item, ctx.mapper)


def _get_document_year(ctx: ItemGetValueContext) -> str:
    return _document_year(ctx.item, ctx.mapper)


def _get_latex_title(ctx: ItemGetValueContext) -> str:
    return _latex_escape(
        ctx.substitute_and_transform(ctx.item["document-title"].replace(
            _BREAK, " ").replace("\\strut", " ").replace("\\hfill", " ")))


def _get_value_latex(ctx: ItemGetValueContext) -> str:
    return _latex_escape(ctx.substitute_and_transform(ctx.value[ctx.key]))


def _get_latex_copyright(ctx: ItemGetValueContext) -> str:
    return _latex_escape(_get_document_copyright(ctx))


def _get_title_page_title(ctx: ItemGetValueContext) -> str:
    title: list[str] = []
    for part in ctx.substitute_and_transform(
            ctx.item["document-title"]).split(_BREAK):
        if len(part) < 23:
            title.append(part)
            continue
        parts = part.split("/")
        new_part = parts[0]
        for sub_part in parts[1:]:
            sub_part = f"/{sub_part}"
            if len(new_part) + len(sub_part) < 23:
                new_part += sub_part
            else:
                title.append(new_part)
                new_part = sub_part
        title.append(new_part)
    return _latex_escape(" \\break \\break ".join(title))


def _gather_subcomponents(component: Item, depth: int, at_depth: int,
                          component_list: list[str]) -> None:
    for subcomponent in component.children("input"):
        if not subcomponent.type.startswith("pkg/component"):
            continue
        if depth == at_depth:
            name = os.path.dirname(component.uid)
            subname = os.path.dirname(subcomponent.uid)
            component_list.append(subname.removeprefix(name).lstrip("/"))
        else:
            _gather_subcomponents(subcomponent, depth + 1, at_depth,
                                  component_list)


def _augment_report(
        lines: list[str]) -> tuple[list[str], list[tuple[int, int]]]:
    report: dict = {}
    augment_report(report, lines)
    return lines, report["data-ranges"]


class DocumentBuilderValueProvider(ItemValueProvider):
    """ Provides values for document builders. """

    def __init__(self, builder: "SphinxBuilder") -> None:
        super().__init__(builder.mapper)
        self.builder = builder
        self.whoami = builder["document-key"]

    def get_reference(self, ctx: ItemGetValueContext, resource_key: str,
                      name: str, label: str) -> str:
        """ Get a named reference to the label in the named resource. """
        document, path, *_ = self.builder.get_resource(resource_key)
        mapper = ctx.mapper
        assert isinstance(mapper, BuildItemMapper)
        if self.whoami == document.item["document-key"]:
            return mapper.format_reference(name, label)
        return mapper.format_link(name, f"{path}#{label.lower()}")


class _CitationProvider(BibTeXCitationProvider):

    def __init__(self, builder: "SphinxBuilder") -> None:
        super().__init__(builder.mapper)
        self.add_get_fields("pkg/directory-state/sphinx",
                            self._get_document_fields)
        self.mapper.add_get_value("pkg/directory-state/sphinx:/bibtex-entries",
                                  self.get_bibtex_entries)
        for type_name in ("pkg/component", "pkg/directory-state/sphinx",
                          "statement-of-compliance"):
            self.mapper.add_get_value(f"{type_name}:/cite-group",
                                      self.get_cite_group)

    def _get_document_fields(
            self, item: Item) -> tuple[str, dict[str, str | list[str]]]:
        organizations: set[str] = set()
        authors: set[str] = set()
        for action in item["document-contributors"]:
            for contributor in action["contributors"]:
                first = contributor["first-name"]
                last = contributor["last-name"]
                authors.add(f"{last}, {first}")
                organizations.add(contributor["organization"])
        mapper = self.mapper
        assert isinstance(mapper, BuildItemMapper)
        url = mapper.relpath(
            mapper.substitute(f"{item['directory']}/{item['output-pdf']}",
                              item))
        fields: dict[str, str | list[str]] = {
            "author": sorted(authors),
            "organization": ", ".join(sorted(organizations)),
            "title": _normal_title(item),
            "url": url,
            "year": _document_year(item, self.mapper)
        }
        return "manual", fields

    def get_cite_group(self, ctx: ItemGetValueContext) -> str:
        # pylint: disable=too-many-locals
        args, kwargs = ctx.unpack_args_dict(ctx.mapper.substitute)
        group = "".join(args)
        flat = int(kwargs.get("flat", 1))
        use_common_title = True
        citations: list[str] = []
        titles: list[str] = []
        mapper = ctx.mapper
        assert isinstance(mapper, BuildItemMapper)
        content = mapper.create_content()
        for link in ctx.item.links_to_children("citation-group-member"):
            if link["citation-group-key"] != group:
                continue
            _, fields = self.get_fields(link.item)
            title = ctx.substitute(fields["title"])
            cite = ctx.substitute(f"${{{link.uid}:/cite}}")
            if link.item.type.startswith("pkg/directory-state/sphinx"):
                label = _kwargs_get(kwargs, "label", link, None)
                if label is None:
                    if not flat:
                        title = f"{content.emphasize(title)} {cite}"
                else:
                    use_common_title = False
                    name = _kwargs_get(kwargs, "name", link, "")
                    path = mapper.substitute(link.item['directory'], link.item)
                    path = f"{path}{_kwargs_get(kwargs, 'path', link, '')}"
                    title = mapper.format_link(
                        f"{title}{', ' if name else ''}{name}",
                        f"{path}#{label.lower()}")
                    title = f"{title} {cite}"
                    cite = title
            else:
                if not flat:
                    title = f"{content.emphasize(title)} {cite}"
            titles.append(title)
            citations.append(cite)
        if not titles:
            logging.warning(
                "%s: the citation group associated with key '%s' is empty",
                ctx.item.uid, group)
        if flat:
            if use_common_title:
                title = os.path.commonprefix(titles)
                if title:
                    return (f"{content.emphasize(title)} "
                            f"{list_terms(citations)}")
            return list_terms(citations)
        content.add_list(titles,
                         prologue=kwargs.get("prologue"),
                         epilogue=kwargs.get("epilogue"),
                         empty=kwargs.get("empty"))
        return content.join()


class SphinxBuilder(DirectoryState):
    """ Base class for Sphinx document builds. """

    # pylint: disable=too-many-instance-attributes
    @classmethod
    def prepare_factory(cls, factory: BuildItemFactory,
                        type_name: str) -> None:
        DirectoryState.prepare_factory(factory, type_name)
        factory.add_get_value(f"{type_name}:/document-release", _get_release)
        factory.add_get_value(f"{type_name}:/document-year",
                              _get_document_year)

    def __init__(self,
                 director: PackageBuildDirector,
                 item: Item,
                 mapper: Optional[BuildItemMapper] = None) -> None:
        super().__init__(director, item, mapper)
        self.mapper.base_path = self["document-base-path"]
        self._whoami = self["document-key"]
        self._index: list[str] = []
        self._section_level_stack: list[int] = [2]
        self._section_lifo: list[BuildItem] = [self]
        self.content_license: set[str] = {self["document-license"]}
        for source_license in self["document-license-map"].keys():
            for the_license in source_license.split(" OR "):
                self.content_license.add(the_license)
        self.file_path = ""
        my_type = self.item.type
        self.mapper.add_get_value(f"{my_type}:/subcomponent-list",
                                  self._get_subcomponent_list)
        self.mapper.add_get_value(f"{my_type}:/document-author",
                                  _get_document_author)
        self.mapper.add_get_value(f"{my_type}:/document-latex-footer-right",
                                  _get_value_latex)
        self.mapper.add_get_value(f"{my_type}:/document-latex-header-left",
                                  _get_value_latex)
        self.mapper.add_get_value(f"{my_type}:/document-copyright",
                                  _get_document_copyright)
        self.mapper.add_get_value(f"{my_type}:/document-copyrights",
                                  self._get_document_copyrights)
        self.mapper.add_get_value(
            f"{my_type}:/document-bsd-2-clause-copyrights",
            self._get_document_bsd_2_clause_copyrights)
        self.mapper.add_get_value(f"{my_type}:/document-third-party-licenses",
                                  self._get_document_third_party_licenses)
        self.mapper.add_get_value(f"{my_type}:/document-normal-title",
                                  _get_normal_title)
        self.mapper.add_get_value(f"{my_type}:/document-latex-copyright",
                                  _get_latex_copyright)
        self.mapper.add_get_value(f"{my_type}:/document-latex-title",
                                  _get_latex_title)
        self.mapper.add_get_value(f"{my_type}:/document-sphinx-title",
                                  _get_sphinx_title)
        self.mapper.add_get_value(f"{my_type}:/document-title-page-title",
                                  _get_title_page_title)
        self.mapper.add_get_value(f"{my_type}:/document-index",
                                  self._get_index)
        self.mapper.add_get_value(f"{my_type}:/document-releases",
                                  self._get_release_topics)
        self.mapper.add_get_value(f"{my_type}:/document-release-sections",
                                  self._get_release_sections)
        self.mapper.add_get_value(f"{my_type}:/document-contributors",
                                  _get_contributors)
        self.mapper.add_get_value(f"{my_type}:/item-files",
                                  self._get_item_files)
        self.mapper.add_get_value(f"{my_type}:/ref", self._get_ref)
        for name in [my_type, "pkg/sphinx-section"]:
            self.mapper.add_get_value(f"{name}:/build-description",
                                      self._get_build_description)
            self.mapper.add_get_value(f"{name}:/document-elements",
                                      self._get_document_elements)
            self.mapper.add_get_value(f"{name}:/push-component",
                                      self._push_component)
            self.mapper.add_get_value(f"{name}:/pop-component",
                                      self._pop_component)
            self.mapper.add_get_value(f"{name}:/sections", self._get_sections)
            self.mapper.add_get_value(f"{name}:/subprocess",
                                      self._get_subprocess)
        self.mapper.add_get_value("pkg/sphinx-section:/ref",
                                  self._get_section_ref)
        self._actions = {
            "add-to-index": _no_action,
            "copy": self._copy,
            "copy-and-substitute": self._copy_and_substitute,
            "glossary": self._glossary
        }
        _CitationProvider(self)

    def yield_item_input_links(self) -> Iterator[Link]:
        for section in self._section_lifo:
            item = section.item
            yield from itertools.chain(item.links_to_parents("input"),
                                       item.links_to_children("input-to"))

    def _run_actions(self, source: DirectoryState, build_dir: str) -> None:
        source_dir = source.directory
        document_components = self["document-components"]
        files = set(source.files(base=""))
        for component in document_components:
            files.difference_update(to_iterable(component.get("file",
                                                              tuple())))
        for file in sorted(files):
            self._do_copy(source_dir, build_dir, file)
        enabled_set = self.enabled_set
        for component in document_components:
            if is_enabled(enabled_set, component.get("enabled-by", True)):
                self._actions[component["action"]](source_dir, build_dir,
                                                   component)
                self._add_to_index(component)

    def run(self) -> None:
        self.mapper.copyrights_by_license.clear()

        source = self.input("source")
        assert isinstance(source, DirectoryState)

        build = self.output("build")
        assert isinstance(build, DirectoryState)
        build.discard_and_clear()
        build_dir = build.directory

        try:
            destination = self.output("destination")
            assert isinstance(destination, DirectoryState)
        except KeyError:
            destination = self
        destination.discard_and_clear()

        os.makedirs(os.path.join(build_dir, "source"), exist_ok=True)
        status = run_command(
            ["python3", "-msphinx", "-M", "clean", "source", "build"],
            build_dir)
        assert status == 0
        self._run_actions(source, build_dir)
        output = self["output-pdf"]
        if output:
            stdout: list[str] = []
            env = os.environ.copy()
            env["LATEXOPTS"] = "-halt-on-error"
            status = run_command(
                ["python3", "-msphinx", "-M", "latexpdf", "source", "build"],
                build_dir,
                stdout=stdout,
                env=env)
            unstable = ("Latexmk: Maximum runs of pdflatex reached"
                        " without getting stable files")
            assert status == 0 or unstable in stdout
            src_path = os.path.join(build_dir, "build", "latex",
                                    "document.pdf")
            destination.copy_file(src_path, output)
        output = self["output-html"]
        if output:
            status = run_command(
                ["python3", "-msphinx", "-M", "html", "source", "build"],
                build_dir)
            assert status == 0
            src_path = os.path.join(build_dir, "build", "html")
            destination.copy_tree(src_path, output)

        my_license = self["document-license"]
        destination["copyrights-by-license"] = dict(
            (key, value.get_statements())
            for key, value in self._get_copyrights().items()
            if key != my_license)

        self.description.add(f"""Produce documents in
{self.description.path(destination.directory)} using sources from
{source.reference()}.""")

    def add_component_action(
            self, name: str, action: Callable[[str, str, dict[str, Any]],
                                              None]) -> None:
        """ Adds a component action. """
        self._actions[name] = action

    def wrap(self, content: TextContent, item: Item, text: str) -> None:
        """ Substitute the text and wrap the text to the content. """
        content.wrap(self.mapper.substitute(text, item))

    def _get_subcomponent_list(self, ctx: ItemGetValueContext) -> str:
        assert ctx.args
        at_depth = int(ctx.args)
        component_list: list[str] = []
        _gather_subcomponents(self.director[self.director.package_uid].item, 1,
                              at_depth, component_list)
        return list_terms(sorted(component_list))

    def _get_releases(self, ctx: ItemGetValueContext, scope: Callable) -> str:
        with self.section_content(ctx) as (content, _):
            mapper = ctx.mapper
            assert isinstance(mapper, BuildItemMapper)
            releases = ctx.item["document-releases"]
            count = len(releases)
            for idx, release in enumerate(reversed(releases)):
                date = release["date"]
                status = release["status"]
                header = ctx.substitute(
                    f"Release: {count - idx}, Date: {date}, Status: {status}")
                with scope(content, header):
                    lines = self._push_pop_enabled_by(
                        release["changes"].splitlines())
                    content.add(ctx.substitute("\n".join(lines)))
            return content.join()

    def _get_release_topics(self, ctx: ItemGetValueContext) -> str:

        @contextmanager
        def _scope(content: TextContent, header: str) -> Iterator[None]:
            with content.directive("topic", header):
                yield

        return self._get_releases(ctx, _scope)

    def _get_release_sections(self, ctx: ItemGetValueContext) -> str:

        @contextmanager
        def _scope(content: TextContent, header: str) -> Iterator[None]:
            with content.section(header):
                yield

        return self._get_releases(ctx, _scope)

    def _add_to_index(self, component: dict[str, Any]) -> None:
        if component.get("add-to-index", False):
            for file in to_iterable(component["file"]):
                self._index.append(os.path.splitext(os.path.basename(file))[0])

    def _get_index(self, ctx: ItemGetValueContext) -> str:
        mapper = ctx.mapper
        assert isinstance(mapper, BuildItemMapper)
        content = mapper.create_content()
        maxdepth = f":maxdepth: {ctx.item['document-toctree-maxdepth']}"
        with content.directive("toctree", options=[maxdepth, ":numbered:"]):
            content.add(self._index)
        return content.join()

    def _get_copyrights(self) -> dict[str, Copyrights]:
        my_license = self["document-license"]
        copyrights: dict[str, Copyrights] = {}
        copyrights.setdefault(my_license, Copyrights()).register(
            self["document-copyrights"])
        license_map = self["document-license-map"]
        for key, statements in self.mapper.copyrights_by_license.items():
            the_license = license_map.get(key, key)
            copyrights.setdefault(the_license, Copyrights()).register([
                license_map.get(statement, statement)
                for statement in statements
            ])
        return copyrights

    def _get_document_copyrights(self, ctx: ItemGetValueContext) -> str:
        my_license = self["document-license"]
        assert " OR " not in my_license
        copyrights = self._get_copyrights()
        prefix = ctx.args if ctx.args else ""
        return "\n".join(copyrights[my_license].get_statements(f"{prefix}| ©"))

    def _get_document_third_party_licenses(self,
                                           ctx: ItemGetValueContext) -> str:
        """
        Get the licenses of the parts which the document takes from another
        source, with the copyright holders of each.

        The result is empty where the document takes no such part, so a
        document of one license states nothing.
        """
        my_license = self["document-license"]
        copyrights = self._get_copyrights()
        others = sorted(the_license for the_license in copyrights
                        if the_license != my_license)
        if not others:
            return ""
        prefix = ctx.args if ctx.args else ""
        lines = [
            f"{prefix}This document reproduces parts of the",
            f"{prefix}documentation of other work.  Each part stays",
            f"{prefix}under the license of its source, which the list",
            f"{prefix}below names.  The text of such a part comes from",
            f"{prefix}the source through a generator and carries the",
            f"{prefix}changes which this document needs.", ""
        ]
        for the_license in others:
            lines.append(f"{prefix}{the_license}:")
            lines.append("")
            lines.extend(
                copyrights[the_license].get_statements(f"{prefix}| \u00a9"))
            lines.append("")
        return "\n".join(lines[:-1])

    def _get_document_bsd_2_clause_copyrights(
            self, _ctx: ItemGetValueContext) -> str:
        copyrights = self._get_copyrights()
        the_license = "BSD-2-Clause"
        if the_license not in copyrights:
            return ""
        statements = "\n".join(copyrights[the_license].get_statements("| ©"))
        return f"""{statements}

{BSD_2_CLAUSE_LICENSE}"""

    @property
    def section_level(self) -> int:
        """ Is the current section level. """
        return self._section_level_stack[-1]

    @contextmanager
    def section_level_scope(self,
                            ctx: ItemGetValueContext) -> Iterator[str | None]:
        """ Open a section level scope with optional additional arguments. """
        if ctx.args:
            colon = ctx.args.find(":")
            if colon >= 0:
                level_change = int(ctx.args[:colon])
                args: str | None = ctx.args[colon + 1:]
            else:
                level_change = int(ctx.args)
                args = None
        else:
            level_change = 1
            args = None
        self._section_level_stack.append(self.section_level + level_change)
        try:
            yield args
        finally:
            self._section_level_stack.pop()

    @contextmanager
    def section_content(
            self, ctx: ItemGetValueContext
    ) -> Iterator[tuple[TextContent, str | None]]:
        """
        Open a section level scope with a section content and optional
        additional arguments.
        """
        with self.section_level_scope(ctx) as args:
            yield (self.mapper.create_content(
                section_level=self.section_level,
                the_license=self.content_license), args)

    def _add_section_content(self, content: TextContent,
                             section: BuildItem) -> None:
        lines = self._push_pop_enabled_by(
            section.item["content"].strip().splitlines())
        self._section_lifo.insert(0, section)
        try:
            content.add(self.substitute("\n".join(lines), section.item))
        finally:
            self._section_lifo.pop(0)

    def _push_component(self, ctx: ItemGetValueContext) -> str:
        assert ctx.args
        component = self.director[ctx.args]
        assert isinstance(component, PackageComponent)
        self.push_component(component)
        item_cache = self.item.cache
        item_cache.push_selection(component.selection)
        item_cache.push_view(component.view)
        return ""

    def _pop_component(self, _ctx: ItemGetValueContext) -> str:
        item_cache = self.item.cache
        item_cache.pop_view()
        item_cache.pop_selection()
        self.pop_component()
        return ""

    def _get_section_label(self, item: Item) -> str:
        label = item["label"]
        if label is None:
            return item.ident
        return self.substitute(label, item)

    def _get_sections(self, ctx: ItemGetValueContext) -> str:
        with self.section_content(ctx) as (content, section_key):
            assert section_key
            mapper = ctx.mapper
            assert isinstance(mapper, BuildItemMapper)
            links_sections = [
                (link, section)
                for link, section in self._section_lifo[0].input_links(
                    "document-section") if link["section-key"] == section_key
            ]
            if len(links_sections
                   ) == 1 and links_sections[0][0]["header-is-optional"]:
                section = links_sections[0][1]
                self._section_level_stack[-1] = self._section_level_stack[-2]
                logging.debug("%s: add content %s at level %s using %s",
                              self.uid, section.uid, self.section_level,
                              section.component.uid)
                with self.component_scope(section.component):
                    content.add_label(self._get_section_label(section.item))
                    self._add_section_content(content, section)
            else:
                for link, section in links_sections:
                    logging.debug("%s: add section %s at level %s using %s",
                                  self.uid, section.uid, self.section_level,
                                  section.component.uid)
                    with self.component_scope(section.component):
                        with content.section(
                                self.substitute(link["header"], section.item),
                                label=self._get_section_label(section.item)):
                            self._add_section_content(content, section)
            return content.join()

    def _get_section_ref(self, ctx: ItemGetValueContext) -> str:
        section = self.director[ctx.item.uid]
        with self.component_scope(section.component):
            mapper = ctx.mapper
            assert isinstance(mapper, BuildItemMapper)
            return mapper.create_content().reference(
                self._get_section_label(section.item))

    def _get_matching_uids(self, item_cache: ItemCache, args: list[str],
                           kwargs: dict[str, str]) -> list[str]:
        matching: set[str] = set()
        uids = list(item_cache.keys())
        for pattern in args:
            matching.update(fnmatch.filter(uids, pattern))
        child_roles: frozenset[str] = _kwargs_split(kwargs, "children")
        parent_roles: frozenset[str] = _kwargs_split(kwargs, "parents")
        if child_roles or parent_roles:
            anchors = matching
            matching = set()
            for uid in anchors:
                item = item_cache[uid]
                component = item.view["component"]
                with item_cache.selection(component.selection):
                    matching.update(item_2.uid
                                    for item_2 in itertools.chain(
                                        item.parents(parent_roles),
                                        item.children(child_roles)))
        types: frozenset[str] = _kwargs_split(kwargs, "types")
        if types:
            return sorted(
                filter(lambda x: item_cache[x].type in types, matching))
        return sorted(matching)

    def _get_item_files(self, ctx: ItemGetValueContext) -> str:
        args, kwargs = ctx.unpack_args_dict(ctx.mapper.substitute)
        item_cache = self.item.cache
        _, path, *_ = self.get_resource("item-files")
        extension = posixpath.basename(path)
        path = posixpath.dirname(path)
        mapper = ctx.mapper
        assert isinstance(mapper, BuildItemMapper)
        uids = [
            mapper.format_link(item_cache[uid].spec_2,
                               posixpath.join(path, f"{uid[1:]}{extension}"))
            for uid in self._get_matching_uids(item_cache, args, kwargs)
        ]
        if int(kwargs.get("flat", 0)):
            return list_terms(uids)
        content = mapper.create_content()
        content.add_list(uids,
                         prologue=kwargs.get("prologue"),
                         epilogue=kwargs.get("epilogue"),
                         empty=kwargs.get("empty"))
        return content.join()

    def _get_ref(self, ctx: ItemGetValueContext) -> str:
        args, kwargs = ctx.unpack_args_dict(ctx.mapper.substitute)
        resource = self.get_resource(kwargs["key"])
        name: str | None = " ".join(args)
        if not name:
            name = resource.name
        label = kwargs.get(
            "label", resource.label if resource.label is not None else "")
        if not name or not label:
            raise ValueError(
                f"{ctx.item.uid}: no name or label specified for reference")
        mapper = ctx.mapper
        assert isinstance(mapper, BuildItemMapper)
        if self._whoami == resource.item["document-key"]:
            return mapper.format_reference(name, label)
        return mapper.format_link(
            name, f"{resource.path}{kwargs.get('path', '')}#{label.lower()}")

    def _get_document_elements(self, ctx: ItemGetValueContext) -> str:
        assert ctx.args
        indent, element_key = ctx.args.split(":")
        mapper = ctx.mapper
        assert isinstance(mapper, BuildItemMapper)
        content = mapper.create_content()
        content.push_indent(int(indent) * " ")
        elements = [
            element for element in self.inputs("document-element")
            if element["element-key"] == element_key
        ]
        if len(elements) == 1:
            element = elements[0]
            logging.debug("%s: add element %s using %s", self.uid, element.uid,
                          element.component.uid)
            with self.component_scope(element.component):
                content.add(self.substitute(element.item["content"]))
        else:
            for element in elements:
                logging.debug("%s: add element %s using %s", self.uid,
                              element.uid, element.component.uid)
                with self.component_scope(element.component):
                    content.add_list_item(
                        self.substitute(element.item["header"]))
                    content.add_blank_line()
                    with content.indent("  "):
                        content.add(self.substitute(element.item["content"]))
        return content.join()

    def _get_subprocess(self, ctx: ItemGetValueContext) -> str:
        return get_value_subprocess(self.substitute, _augment_report, ctx)

    def _get_build_description(self, ctx: ItemGetValueContext) -> str:
        with self.section_level_scope(ctx) as args:
            content = SphinxContent(self.section_level)
            assert args
            self.director.add_build_description(content, args.split(":"))
            return content.join()

    def _register_text_copyrights(self, path: str, text: str) -> None:
        match = _HEADERS[os.path.splitext(path)[1]].match(text)
        assert match
        the_license = match.group(1)
        statements = [
            statement.partition(" ")[2]
            for statement in match.group(2).split("\n")[:-1]
        ]
        logging.info("%s: register license %s with copyrights %s", self.uid,
                     the_license, statements)
        self.mapper.copyrights_by_license.setdefault(the_license,
                                                     set()).update(statements)

    def _do_copy(self, source_dir: str, build_dir: str, file: str) -> None:
        src_file = os.path.join(source_dir, file)
        dst_file = os.path.join(build_dir, file)
        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
        if dst_file.endswith(_EXTENSIONS):
            logging.info("%s: read: %s", self.uid, src_file)
            with open(src_file, "r", encoding="utf-8") as src:
                text = src.read()
                self._register_text_copyrights(src_file, text)
                logging.info("%s: write: %s", self.uid, dst_file)
                with open(dst_file, "w+", encoding="utf-8") as dst:
                    dst.write(text)
        else:
            logging.info("%s: copy '%s' to '%s'", self.uid, src_file, dst_file)
            shutil.copy2(src_file, dst_file)

    def _copy(self, source_dir: str, build_dir: str,
              component: dict[str, Any]) -> None:
        for file in to_iterable(component["file"]):
            self._do_copy(source_dir, build_dir, file)

    def _push_pop_enabled_by(self, lines: list[str]) -> list[str]:
        logging.info("%s: process push/pop enabled by using enabled set: %s",
                     self.uid, sorted(self.enabled_set))
        filtered_lines: list[str] = []
        enabled: list[bool] = [True]
        for line in lines:
            push_match = _PUSH_ENABLED_BY.search(line)
            if push_match is not None:
                data = push_match.group(1)
                enabled_by = yaml.load(data, yaml.SafeLoader)
                enabled.append(enabled[-1]
                               and is_enabled(self.enabled_set, enabled_by))
                continue
            if _POP_ENABLED_BY.search(line) is not None:
                enabled.pop()
            elif enabled[-1]:
                filtered_lines.append(line)
        return filtered_lines

    def _copy_and_substitute(self, source_dir: str, build_dir: str,
                             component: dict[str, Any]) -> None:
        for file in to_iterable(component["file"]):
            src_path = os.path.join(source_dir, file)
            dst_path = os.path.join(build_dir, file)
            self.file_path = dst_path
            logging.info("%s: read: %s", self.uid, src_path)
            with open(src_path, "r", encoding="utf-8") as src:
                component_depth = self.component_depth
                text = "".join(self._push_pop_enabled_by(src.readlines()))
                if dst_path.endswith(_EXTENSIONS):
                    self.mapper.set_format(dst_path)
                    self._register_text_copyrights(src_path, text)
                logging.info("%s: substitute", self.uid)
                text = self.mapper.substitute(text)
                logging.info("%s: write: %s", self.uid, dst_path)
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                with open(dst_path, "w+", encoding="utf-8") as dst:
                    dst.write(text)
                assert component_depth == self.component_depth

    def _glossary(self, _source_dir: str, build_dir: str,
                  component: dict[str, Any]) -> None:
        target = str(os.path.join(build_dir, component["file"]))
        document_config = DocumentGlossaryConfig(
            target=target,
            header="Terms, definitions and abbreviated terms",
            md_source_paths=[
                str(os.path.join(build_dir, "source")),
                str(os.path.join(build_dir, "include"))
            ],
            rest_source_paths=[
                str(os.path.join(build_dir, "source")),
                str(os.path.join(build_dir, "include"))
            ])
        config = GlossaryConfig(project_groups=component["glossary-groups"],
                                documents=[document_config])
        self.mapper.set_format(target)
        generate_glossary(config, self.item.cache, self.mapper,
                          self.mapper.content_constructor)
