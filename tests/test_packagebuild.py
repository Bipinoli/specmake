# SPDX-License-Identifier: BSD-2-Clause
""" Tests for the pkgitems module. """

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

import graphlib
import logging
import pytest
from pathlib import Path

import specitems
from specitems import EmptyItem, EmptyItemCache, Item, ItemGetValueContext

import specmake
from specmake import (BuildItem, BuildItemFactory, BuildItemMapper,
                      BuildItemTypeProvider, build_item_input,
                      PackageBuildDirector, PackageComponent)

from .util import create_package, create_test_director, get_and_clear_log


class _TestItem(BuildItem):

    def __init__(self, director: PackageBuildDirector, item: Item):
        super().__init__(director, item, BuildItemMapper(item, self))
        my_type = self.item.type
        self.mapper.add_get_value(f"{my_type}:/input", self._get_input)
        self.mapper.add_get_value(f"{my_type}:/inputs", self._get_inputs)
        self.mapper.add_get_value(f"{my_type}:/input-links",
                                  self._get_input_links)
        self.mapper.add_get_value(f"{my_type}:/output", self._get_output)

    def run(self):
        try:
            value = self.mapper.substitute("${.:/make-params/value}")
        except ValueError:
            pass
        else:
            logging.info("%s: substitute: %s", self.uid, value)
            self.item.cache["/pkg/output/test-make"]["links"][1]["params"][
                "result"] = self.mapper.substitute(value)

    def _get_input(self, ctx: ItemGetValueContext):
        name = ctx.mapper[".:/make-params/name"]
        logging.info("%s: get input for: %s", self.uid, name)
        return self.input(name).uid

    def _get_inputs(self, ctx: ItemGetValueContext):
        name = ctx.mapper[".:/make-params/name"]
        logging.info("%s: get inputs for: %s", self.uid, name)
        return " ".join(item.uid for item in self.inputs(name))

    def _get_input_links(self, ctx: ItemGetValueContext):
        name = ctx.mapper[".:/make-params/name"]
        logging.info("%s: get input links for: %s", self.uid, name)
        return " ".join(link.item.uid for link, _ in self.input_links(name))

    def _get_output(self, ctx: ItemGetValueContext):
        name = ctx.mapper.substitute("${.:/make-params/name}")
        logging.info("%s: get output for: %s", self.uid, name)
        return self.output(name).uid


def test_package_build_cycle(caplog, tmpdir):
    with pytest.raises(graphlib.CycleError, match="nodes are in a cycle"):
        package = create_package(caplog, Path(tmpdir), Path("spec-cycle"), [])


def test_packagebuild(caplog, tmpdir, monkeypatch):
    command = []
    staged_files = []

    def _run_command(args, cwd, stdout=None):
        command.append(cwd)
        command.extend(args)
        if "--name-only" in args:
            stdout.extend(staged_files)
        return 0

    def _subprocess_run(args, check, input, cwd):
        command.append(cwd)
        command.extend(args)
        return 0

    monkeypatch.setattr(specmake.pkgitems, "run_command", _run_command)
    monkeypatch.setattr(specmake.pkgitems.subprocess, "run", _subprocess_run)
    tmp_dir = Path(tmpdir)
    package = create_package(caplog, tmp_dir, Path("spec-packagebuild"), [])
    director = package.director
    director.factory.add_constructor("pkg/test-mapper", _TestItem)

    mapper = BuildItemMapper(package.item, package)
    with pytest.raises(NotImplementedError):
        mapper.get_link(mapper.item)

    director.build_package()
    log = get_and_clear_log(caplog)
    assert "INFO /pkg/steps/a: create build item" in log
    assert "INFO /pkg/steps/b: create build item" not in log
    assert "INFO /pkg/steps/c: input is disabled: /pkg/steps/b" in log
    assert "INFO /pkg/steps/c: output is disabled: /pkg/output/b" in log

    director.build_package(force=["/pkg/steps/a"])
    log = get_and_clear_log(caplog)
    assert "INFO /pkg/steps/a: build is forced" in log
    assert "INFO /pkg/steps/c: input has not changed: /pkg/steps/a" in log

    director.build_package(only=["/pkg/steps/a"])
    log = get_and_clear_log(caplog)
    assert "INFO /pkg/steps/c" not in log

    director.build_package(skip=["/pkg/steps/a"])
    log = get_and_clear_log(caplog)
    assert "INFO /pkg/steps/a: build is skipped" in log

    director.build_package()
    log = get_and_clear_log(caplog)
    assert "INFO /pkg/steps/a: build is unnecessary" in log
    assert "INFO /pkg/steps/c: build is unnecessary" in log

    # Test PackageComponent
    subcomponent = director["/pkg/sub/component"]
    assert isinstance(subcomponent, PackageComponent)
    assert subcomponent["arch"] == "sub-arch"
    assert subcomponent["bsp"] == "gr712rc"
    assert subcomponent.enabled_set == set()
    assert subcomponent.selection.enabled_set == {"four", "five"}
    with pytest.raises(KeyError):
        subcomponent["does-not-exist"]
    with pytest.raises(ValueError):
        subcomponent.substitute("${.:/component/does-not-exist}")
    assert package.substitute("${.:/component/arch}") == "sparc"
    assert subcomponent.substitute("${.:/component/arch}") == "sub-arch"
    with pytest.raises(KeyError, match="there is no resource"):
        subcomponent.get_resource("foo")
    doc = director["/pkg/source/empty"]
    assert director.package.get_resource("blub") == (
        doc,
        f"{tmpdir}/path/to/blub",
        None,
        None,
    )
    assert subcomponent.get_resource("bar") == (
        doc,
        f"{tmpdir}/path/to/bar",
        "Label",
        "Name",
    )
    assert subcomponent.get_resource("blub") == (
        doc,
        f"{tmpdir}/path/to/blub",
        None,
        None,
    )
    assert director["/pkg/source/a"].get_resource("blub") == (
        doc,
        f"{tmpdir}/other/path/to/blub",
        None,
        None,
    )
    assert director["/pkg/source/b"].get_resource("blub") == (
        doc,
        f"{tmpdir}/path/to/blub",
        None,
        None,
    )

    # Test BuildItem methods
    c = director["/pkg/steps/c"]
    assert isinstance(c, _TestItem)
    assert c.is_present()
    data = director.factory.export_data(c.item, True, len(c.item.cache))
    assert data == director.factory.export_data(c.item, False,
                                                len(c.item.cache))
    assert data == {
        "SPDX-License-Identifier":
        "CC-BY-SA-4.0 OR BSD-2-Clause",
        "copyrights": [
            "Copyright (C) 2023 embedded brains GmbH & Co. KG",
        ],
        "enabled-by":
        True,
        "links": [
            {
                "hash": c["links"][0]["hash"],
                "name": "component",
                "role": "input",
                "uid": "../component",
            },
            {
                "hash": c["links"][1]["hash"],
                "name": "foo",
                "role": "input",
                "uid": "a",
            },
            {
                "name": "blub",
                "role": "output",
                "uid": "../output/a",
            },
            {
                "name": "moo",
                "role": "output",
                "uid": "../output/b",
            },
        ],
        "pkg-type":
        "test-mapper",
        "type":
        "pkg",
        "values": {
            "a":
            "a",
            "b": [
                "b1",
                "b2",
            ],
            "c":
            "c",
            "list": [
                "${.:/values/a}",
                "${.:/values/b}",
                [
                    "d",
                    "e",
                ],
                "${.:/values/c}",
            ],
        },
    }
    data = director.factory.export_data(c.item, True, 0)
    assert data == director.factory.export_data(c.item, False, 0)
    assert data == {
        "SPDX-License-Identifier":
        "CC-BY-SA-4.0 OR BSD-2-Clause",
        "copyrights": [
            "Copyright (C) 2023 embedded brains GmbH & Co. KG",
        ],
        "enabled-by":
        True,
        "links": [
            {
                "hash": None,
                "name": "component",
                "role": "input",
                "uid": "../component",
            },
            {
                "hash": None,
                "name": "foo",
                "role": "input",
                "uid": "a",
            },
            {
                "name": "blub",
                "role": "output",
                "uid": "../output/a",
            },
            {
                "name": "moo",
                "role": "output",
                "uid": "../output/b",
            },
        ],
        "pkg-type":
        "test-mapper",
        "type":
        "pkg",
        "values": {
            "a":
            "a",
            "b": [
                "b1",
                "b2",
            ],
            "c":
            "c",
            "list": [
                "${.:/values/a}",
                "${.:/values/b}",
                [
                    "d",
                    "e",
                ],
                "${.:/values/c}",
            ],
        },
    }
    assert c.lazy_verify()
    assert str(c.description) == ""
    c.commit("no description")
    assert c != 123
    with pytest.raises(TypeError):
        assert c < 123

    # Test build item substitution
    c["foo"] = "bar"
    c["blub"] = "${.:/foo}"
    assert c["foo"] == "bar"
    assert "foo" in c
    assert "nil" not in c
    assert c["blub"] == "bar"
    assert c.get("does-not-exist", "${.:/foo}") == "bar"
    assert c.substitute(c.item["blub"], c.item) == "bar"
    assert c.substitute(
        "${.:/component/deployment-directory:relpath %(.:/component/prefix-directory)}"
    ) == "pkg"
    assert c.substitute("${/pkg/component:/spec}") == "spec:/pkg/component"
    assert c.substitute(
        "${/pkg/issue/rtems/2189:/name}"
    ) == "`RTEMS Ticket #2189 <https://devel.rtems.org/ticket/2189>`__"
    assert c.substitute("${/pkg/component:/component/whoami}") == "pkg"
    assert c.substitute("${/pkg/sub/component:/component/whoami}") == "sub"
    assert c.substitute(
        "${/pkg/sub/s/component:/component/whoami}") == "sub-sub-s"
    assert c.substitute(
        "${/pkg/sub/s/link-hub:/component/whoami}") == "sub-sub-s"
    assert c.substitute(
        "${/pkg/sub/t/link-hub:/component/whoami}") == "sub-sub-t"
    with c.component_scope(subcomponent):
        assert c.component["arch"] == "sub-arch"
    assert c.component.uid == "/pkg/component"
    variant_config = c.component["config"]
    c.component["config"] = ""
    assert c.component["name"] == "sparc-gr712rc-4"
    assert c.component["ident"] == "sparc/gr712rc/4"
    c.component["config"] = variant_config
    assert c.component["name"] == "sparc-gr712rc-smp-4"
    assert c.component["ident"] == "sparc/gr712rc/smp/4"
    assert c.component["arch"] == "sparc"
    assert c.enabled_set == set()
    c.item.view["foo"] = "bar"
    with subcomponent.scope():
        assert sorted(c.enabled_set) == ["five", "four"]
        assert c.item.view["foo"] == "bar"
        c.item.view["foo"] = "blub"
        assert c.item.view["foo"] == "blub"
    assert c.item.view["foo"] == "bar"
    assert c.enabled
    assert build_item_input(c.item, "foo").uid == "/pkg/steps/a"
    assert build_item_input(c.item, "bar").uid == "/pkg/steps/a"
    with pytest.raises(KeyError):
        build_item_input(c.item, "blub")
    assert c.input("foo").uid == "/pkg/steps/a"
    assert list(item.uid
                for _, item in c.input_links("foo")) == ["/pkg/steps/a"]
    with pytest.raises(KeyError):
        c.input("nix")
    with pytest.raises(KeyError):
        c.input_link("nix")
    assert [item.uid for item in c.inputs()
            ] == ["/pkg/component", "/pkg/steps/a", "/pkg/steps/a"]
    assert [item.uid for item in c.inputs("foo")] == ["/pkg/steps/a"]
    assert c.output("blub").uid == "/pkg/output/a"
    with pytest.raises(KeyError):
        c.output("nix")
    with pytest.raises(KeyError):
        c.output("moo")
    assert c["values"]["list"] == ["a", "b1", "b2", ["d", "e"], "c"]
    c.clear()

    # Test Git support

    director.git_directory = None

    command = []
    c.git_commit("reason")
    assert command == []

    command = []
    c.git_add(["modules/foobar"])
    assert command == []

    assert c.git_is_clean()
    assert command == []

    director.git_directory = str(tmp_dir / "pkg")
    director.submodules = tuple()

    staged_files = []
    command = []
    c.git_commit("reason")
    assert command == [
        str(tmp_dir / "pkg"), "git", "diff", "--name-only", "--cached"
    ]

    staged_files = ["x"]
    command = []
    c.git_commit("reason")
    assert command == [
        str(tmp_dir / "pkg"), "git", "diff", "--name-only", "--cached",
        str(tmp_dir / "pkg"), "git", "commit", "-m", "/pkg/steps/c: reason"
    ]

    command = []
    assert c.git_is_clean()
    assert command == [str(tmp_dir / "pkg"), "git", "status", "--short"]

    command = []
    c.git_add("modules/foobar")
    assert command == [
        str(tmp_dir / "pkg"), "git", "add", "--force",
        "--pathspec-from-file=-", "--pathspec-file-nul"
    ]

    command = []
    c.git_add(["modules/foobar"])
    assert command == [
        str(tmp_dir / "pkg"), "git", "add", "--force",
        "--pathspec-from-file=-", "--pathspec-file-nul"
    ]

    command = []
    director.add_submodule("modules")
    c.git_add(["modules/foobar"])
    assert command == []


def test_packagebuild_show_list_build(caplog, tmp_path, capsys):
    # /pkg/source/sub-repo is the fixture's only build-uids-bearing item
    # (see test_reposubset.py) -- reused here rather than adding a new
    # one, since show_list_build() only cares that an item has a
    # "build-uids" field, not that it is specifically a RepositorySubset.
    # No other item in the whole fixture has one (grepped), so this
    # remains a single-section report despite show_list_build() no
    # longer taking a uid -- multi-root behavior is exercised separately
    # below.
    package = create_package(caplog, tmp_path, Path("spec-packagebuild"),
                             ["repository-subset"])
    director = package.director
    uid = "/pkg/source/sub-repo"
    subrepo = director[uid]
    # The fixture's own arch/bsp/base-directory-map default to real BSP
    # values with unsubstituted "${.:/component/tmpdir}/..." placeholders
    # (meant to be resolved elsewhere, not usable literally here) -- set
    # them explicitly so this test exercises only /pkg/steps/build-obj,
    # the one item added for this test.
    subrepo.item["arch"] = None
    subrepo.item["bsp"] = None
    subrepo.item["base-directory-map"] = []
    subrepo.item["build-uids"] = ["/pkg/steps/build-obj"]

    director.show_list_build()
    out = capsys.readouterr().out
    # A flat list, sorted by full path -- not a nested directory tree --
    # a report this size realistically gets grepped, and a bare "name"
    # leaf under a nested directory header carries no path information
    # once grep strips that header line. dir/nested.c (build-obj's own
    # source) shows with its full path on one line, not "dir/" then an
    # indented "nested.c". Only what is actually part of the build shows
    # at all -- no glyph, no bracketed reason, no excluded/unlinked/
    # skipped-template entries anywhere: this report answers "what", not
    # "why". build-obj-conditional (enabled-by: "repository-subset",
    # currently true -- create_package()'s own enabled-set for this
    # test, see test_reposubset.py) shows the same bare way as
    # obj.c/nested.c despite being conditionally, not unconditionally,
    # enabled -- the report does not distinguish the two.
    #
    # The "targets" section, printed before any root's own file
    # section, comes for free from three pre-existing fixture items
    # this test does not itself add (tests/spec-packagebuild/rtems/
    # target-{a,b,disabled}.yml, type: requirement, non-functional-
    # type: design-target -- used elsewhere, e.g. performance reporting
    # tests): only target-a (enabled-by: true) is available under this
    # test's enabled-set and so is the only one listed; target-b (a
    # compound and/or condition, unmet here) and target-disabled
    # (enabled-by: false) are both unavailable and so are simply absent,
    # not listed-and-marked-excluded.
    assert out == ("/pkg/component: targets\n"
                   f"{'=' * 23}\n"
                   "rtems/target-a\n"
                   "\n"
                   "/pkg/source/sub-repo\n"
                   f"{'=' * 20}\n"
                   "conditional.c\n"
                   "dir/nested.c\n"
                   "obj.c\n")


def test_packagebuild_show_list_build_no_build_uids():
    # create_test_director()'s item cache has a "/component" item and
    # nothing else -- no build-uids field anywhere -- so show_list_build()
    # has nothing to report on and must say so loudly, not print an
    # empty report.
    director = create_test_director()
    with pytest.raises(ValueError, match="no item in the loaded spec"):
        director.show_list_build()


def test_packagebuild_show_list_build_multiple_roots(caplog, tmp_path, capsys):
    # show_list_build() takes no uid -- every build-uids-bearing item in the
    # loaded spec gets its own section, not one silently chosen (see
    # _find_build_roots()'s docstring: real gr740 defines rtems-qual-only
    # *and* third-party-qual-only side by side). Three pre-existing
    # fixture items stand in for three such roots here, deliberately
    # spanning two different components: /pkg/component (the package
    # root -- the very item the pre-rename test above asserted could
    # *not* be used as a single required uid) and /pkg/source/sub-repo
    # share ONE component (/pkg/component itself -- confirmed directly:
    # item_cache["/pkg/source/sub-repo"].view["component"].uid ==
    # "/pkg/component"), the same real shape as gr740's rtems-qual-only/
    # third-party-qual-only pair; /pkg/sub/component is a genuinely
    # different component (its own "sub-arch"/"gr712rc" component,
    # exercised by test_packagebuild above), standing in for a second,
    # separate bsp/variant.
    package = create_package(caplog, tmp_path, Path("spec-packagebuild"),
                             ["repository-subset"])
    director = package.director
    for uid in ("/pkg/component", "/pkg/source/sub-repo",
                "/pkg/sub/component"):
        root = director[uid]
        root.item["arch"] = None
        root.item["bsp"] = None
        root.item["base-directory-map"] = []
        root.item["build-uids"] = ["/pkg/steps/build-obj"]

    director.show_list_build()
    out = capsys.readouterr().out
    # Each root gets its own fully-qualified heading (uid, then a
    # matching "=" underline, see _print_heading()) regardless of
    # grouping -- landing anywhere in a report that runs to several
    # thousand lines should never leave you guessing which bsp you're
    # looking at. /pkg/component and /pkg/source/sub-repo still share
    # one "targets" section (they share a component) despite having two
    # separate root headings; /pkg/sub/component, a genuinely different
    # component, gets its own.
    targets_component = "/pkg/component: targets"
    targets_subcomponent = "/pkg/sub/component: targets"
    # Trailing "\n" on each root needle: without it, "/pkg/component\n"
    # + 14 "="s would also match as a prefix of "/pkg/component:
    # targets"'s own (23 "="s) underline -- the "\n" only follows a real
    # heading's underline, whose length exactly matches its own heading
    # text.
    root_component = "/pkg/component\n" + "=" * len("/pkg/component") + "\n"
    root_subrepo = ("/pkg/source/sub-repo\n" +
                    "=" * len("/pkg/source/sub-repo") + "\n")
    root_subcomponent = ("/pkg/sub/component\n" +
                         "=" * len("/pkg/sub/component") + "\n")
    assert out.count(targets_component) == 1
    assert out.count(targets_subcomponent) == 1
    assert out.count(root_component) == 1
    assert out.count(root_subrepo) == 1
    assert out.count(root_subcomponent) == 1
    # Both "targets" sections print before any root's own file section:
    # the compact part comes first, the (much larger, on a real build)
    # file-level detail comes after.
    assert (out.index(targets_component) < out.index(targets_subcomponent) <
            out.index(root_component) < out.index(root_subrepo) <
            out.index(root_subcomponent))


def test_build_item_run(caplog, tmp_path):
    package = create_package(caplog, tmp_path, Path("spec-packagebuild"),
                             ["test-make"])
    director = package.director
    director.factory.add_constructor("pkg/test-mapper", _TestItem)
    test_make = director["/pkg/output/test-make"]
    make_link = test_make.item["links"][1]

    make_link["params"]["name"] = "source"
    make_link["params"]["value"] = "$${.:/inputs}"
    make_link["hash"] = None
    director.build_package()
    assert make_link["params"]["result"] == "/pkg/source/a /pkg/source/e"

    make_link["params"]["name"] = "source"
    make_link["params"]["value"] = "$${.:/input-links}"
    make_link["hash"] = None
    director.build_package()
    assert make_link["params"]["result"] == "/pkg/source/a /pkg/source/e"

    make_link["params"]["name"] = None
    make_link["params"]["value"] = "$${.:/input-links}"
    make_link["hash"] = None
    director.build_package()
    assert make_link["params"][
        "result"] == "/pkg/component /pkg/source/a /pkg/source/e"

    make_link["params"]["name"] = "does-not-exist"
    make_link["params"]["value"] = "$${.:/input}"
    make_link["hash"] = None
    with pytest.raises(ValueError):
        director.build_package()

    make_link["params"]["name"] = "does-not-exist"
    make_link["params"]["value"] = "$${.:/output}"
    make_link["hash"] = None
    with pytest.raises(ValueError):
        director.build_package()


def test_builditemmapper():
    director = create_test_director()
    data = {
        "SPDX-License-Identifier": "CC-BY-SA-4.0 OR BSD-2-Clause",
        "copyrights": ["Copyright (C) 2026 embedded brains GmbH & Co. KG"],
        "copyrights-by-license": {},
        "directory": "",
        "directory-state-type": "explicit",
        "enabled-by": True,
        "files": [],
        "hash": None,
        "links": [],
        "pkg-type": "directory-state",
        "type": "pkg",
    }
    item = director.item_cache.add_item("/item", data)
    build_item = director["/item"]
    mapper = build_item.mapper

    assert mapper.base_path == "/"
    assert mapper.format == ".rst"
    assert mapper.format_code("code") == "``code``"
    assert mapper.format_link("name", "target") == "`name <target>`__"
    assert mapper.relpath("/foo/bar") == "/foo/bar"
    mapper.base_path = "/foo"
    assert mapper.relpath("/foo/bar") == "bar"
    assert mapper.relpath("foo/bar") == "foo/bar"
    assert mapper.format_link("name", "/foo/bar") == "`name <bar>`__"
    assert mapper.format_link("name",
                              "https://x.y") == "`name <https://x.y>`__"
    mapper.base_path = "/"
    assert mapper.format_reference("name", "label") == ":ref:`name <label>`"

    mapper.set_format("foobar.md")
    assert mapper.base_path == "/"
    assert mapper.format == ".md"
    assert mapper.format_code("code") == "`code`"
    assert mapper.format_link("name", "target") == "[name](target)"
    mapper.base_path = "/foo"
    assert mapper.format_link("name", "/foo/bar") == "[name](bar)"
    assert mapper.format_link("name", "https://x.y") == "[name](https://x.y)"
    mapper.base_path = "/"
    assert mapper.format_reference("name", "label") == "{ref}`name <label>`"

    mapper.set_format("foobar.rst")
    assert mapper.base_path == "/"
    assert mapper.format == ".rst"
    assert mapper.format_code("code") == "``code``"
    assert mapper.format_link("name", "target") == "`name <target>`__"
    mapper.base_path = "/foo"
    assert mapper.format_link("name", "/foo/bar") == "`name <bar>`__"
    assert mapper.format_link("name",
                              "https://x.y") == "`name <https://x.y>`__"
    mapper.base_path = "/"
    assert mapper.format_reference("name", "label") == ":ref:`name <label>`"


def test_builditem_transformer():
    director = create_test_director()
    director.package["list"] = [
        {
            "enabled-by": True,
            "value": "A"
        },
        {
            "enabled-by": False,
            "value": "B"
        },
        "${.:/x}",
    ]
    director.package["x"] = "C"
    data = {
        "SPDX-License-Identifier": "CC-BY-SA-4.0 OR BSD-2-Clause",
        "copyrights": ["Copyright (C) 2026 embedded brains GmbH & Co. KG"],
        "copyrights-by-license": {},
        "directory": "",
        "directory-state-type": "explicit",
        "enabled-by": True,
        "files": [],
        "hash": None,
        "links": [],
        "params": {
            "list": [
                {
                    "enabled-by": True,
                    "value": "a"
                },
                {
                    "enabled-by": False,
                    "value": "b"
                },
                "${.:/params/x}",
            ],
            "x":
            "c"
        },
        "pkg-type": "directory-state",
        "type": "pkg",
    }
    item = director.item_cache.add_item("/item", data)
    build_item = director["/item"]
    assert build_item.substitute("${.:/params/list:join}") == "a,c"
    assert build_item.substitute("${.:/params/list:join separator=+}") == "a+c"
    assert build_item.substitute("${.:/component/list:join}") == "A,C"
