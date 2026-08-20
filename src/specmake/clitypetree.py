# SPDX-License-Identifier: BSD-2-Clause
"""
Print the specification item type-refinement tree as ASCII tree.
"""

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

import argparse
import importlib.metadata
import importlib.util
import pickle
import posixpath
import re
import shutil
import sys
import textwrap
from pathlib import Path
from typing import Any, Iterable, Iterator, Literal, NamedTuple, Optional

import yaml

# names/types below are meant to speak for themselves; no docstring needed
# pylint: disable=missing-class-docstring,missing-function-docstring

_TYPE_PROVIDER_PLUGIN_GROUP = "specitems_type_provider.plugins"
_ALWAYS_INCLUDED_PACKAGES = ("specitems", )
_ROOT_UID = "/spec/root"
_UID_PREFIX = "/spec/"
_FALLBACK_WIDTH = 100


def _effective_width() -> int:
    return shutil.get_terminal_size(fallback=(_FALLBACK_WIDTH, 24)).columns


class TypeItem(NamedTuple):
    uid: str
    package: str
    data: dict[str, Any]

    @property
    def name(self) -> str:
        return self.data.get("spec-name", self.uid)

    @property
    def spec_type(self) -> str:
        return self.data.get("spec-type", self.uid)


class Edge(NamedTuple):
    key: str
    values: list[str]
    child_uid: str


class TypeSource(NamedTuple):
    kind: Literal["dir", "pickle"]
    path: Path


def _discover_type_sources() -> dict[str, TypeSource]:
    """ Prefer each package's live `spec-types/` directory (editable
    checkout); fall back to its bundled `spec.pickle`. """
    package_names = dict.fromkeys(_ALWAYS_INCLUDED_PACKAGES)
    for entry_point in importlib.metadata.entry_points(
            group=_TYPE_PROVIDER_PLUGIN_GROUP):
        package_names[entry_point.module.split(".")[0]] = None

    sources: dict[str, TypeSource] = {}
    for package_name in package_names:
        spec = importlib.util.find_spec(package_name)
        if spec is None or spec.origin is None:
            continue
        package_init = Path(spec.origin).resolve()
        spec_types_dir = package_init.parents[2] / "spec-types"
        if spec_types_dir.is_dir():
            sources[package_name] = TypeSource("dir", spec_types_dir)
            continue
        pickle_file = package_init.parent / "spec.pickle"
        if pickle_file.is_file():
            sources[package_name] = TypeSource("pickle", pickle_file)
    return sources


_REQUIREMENT_NAME = re.compile(r"^[A-Za-z0-9_.-]+")


def packages_up_to(package_name: str,
                   known_packages: Iterable[str]) -> set[str]:
    """ `package_name` plus every `known_packages` member it (transitively)
    depends on. """
    known = set(known_packages)
    closure = {package_name}
    pending = [package_name]
    while pending:
        current = pending.pop()
        for requirement in importlib.metadata.requires(current) or []:
            match = _REQUIREMENT_NAME.match(requirement)
            if match is None:
                continue
            dependency = match.group(0)
            if dependency in known and dependency not in closure:
                closure.add(dependency)
                pending.append(dependency)
    return closure


def _iter_yaml_files(directory: Path) -> Iterator[Path]:
    for path in sorted(directory.rglob("*.yml")):
        if not path.name.startswith("."):
            yield path


def _uid_for_file(spec_types_dir: Path, path: Path) -> str:
    relative = path.relative_to(spec_types_dir).with_suffix("")
    return "/" + relative.as_posix()


def _register_type_item(items: dict[str, TypeItem], item: TypeItem) -> None:
    """ Add `item`, warning instead of silently overwriting if its UID was
    already loaded from a different package (e.g. `/spec/int-or-str` is
    defined by both specitems and specware). """
    existing = items.get(item.uid)
    if existing is not None and existing.package != item.package:
        note = "" if existing.data == item.data else " with different content"
        print(
            f"warning: '{item.uid}' is defined by both "
            f"'{existing.package}' and '{item.package}'{note}; "
            f"using the '{item.package}' definition",
            file=sys.stderr)
    items[item.uid] = item


def _load_type_items_from_dir(package: str, spec_types_dir: Path,
                              items: dict[str, TypeItem]) -> None:
    for path in _iter_yaml_files(spec_types_dir):
        with path.open("r", encoding="utf-8") as src:
            data = yaml.safe_load(src)
        if not isinstance(data, dict) or data.get("type") != "spec":
            continue
        uid = _uid_for_file(spec_types_dir, path)
        _register_type_item(items, TypeItem(uid, package, data))


def _load_type_items_from_pickle(package: str, pickle_file: Path,
                                 items: dict[str, TypeItem]) -> None:
    with pickle_file.open("rb") as src:
        data_by_uid = pickle.load(src)
    for uid, data in data_by_uid.items():
        if not isinstance(data, dict) or data.get("type") != "spec":
            continue
        _register_type_item(items, TypeItem(uid, package, data))


def load_type_items(sources: dict[str, TypeSource]) -> dict[str, TypeItem]:
    items: dict[str, TypeItem] = {}
    for package, source in sources.items():
        if source.kind == "dir":
            _load_type_items_from_dir(package, source.path, items)
        else:
            _load_type_items_from_pickle(package, source.path, items)
    return items


def _resolve_uid(from_uid: str, uid_or_relative: str) -> str:
    if uid_or_relative.startswith("/"):
        return uid_or_relative
    return posixpath.normpath(
        posixpath.join(posixpath.dirname(from_uid), uid_or_relative))


def build_children_map(items: dict[str, TypeItem]) -> dict[str, list[Edge]]:
    """ Map each parent UID to its child Edges, merging several
    `spec-refinement` links to the same parent into one multi-value Edge. """
    by_parent_and_child: dict[str, dict[str, tuple[str, list[str]]]] = {}
    missing_parents: set[str] = set()
    for uid, item in items.items():
        for link in item.data.get("links") or []:
            if link.get("role") != "spec-refinement":
                continue
            parent_uid = _resolve_uid(uid, link["uid"])
            if parent_uid not in items:
                missing_parents.add(parent_uid)
                continue
            by_child = by_parent_and_child.setdefault(parent_uid, {})
            _, values = by_child.setdefault(uid, (link["spec-key"], []))
            values.append(link["spec-value"])
    for parent_uid in sorted(missing_parents):
        print(
            f"warning: '{parent_uid}' is not among the loaded types; "
            "ignoring spec-refinement link(s) to it "
            "(mismatched package versions?)",
            file=sys.stderr)

    children: dict[str, list[Edge]] = {}
    for parent_uid, by_child in by_parent_and_child.items():
        edges = [
            Edge(key, sorted(values), child_uid)
            for child_uid, (key, values) in by_child.items()
        ]
        edges.sort(key=lambda edge: (edge.values[0], edge.child_uid))
        children[parent_uid] = edges
    return children


def _find(items: dict[str, TypeItem], name: str) -> TypeItem:
    """ Find a type item by UID, short UID, or `spec-type` slug. """
    if name in items:
        return items[name]
    if not name.startswith("/") and _UID_PREFIX + name in items:
        return items[_UID_PREFIX + name]
    candidates = [item for item in items.values() if item.spec_type == name]
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise SystemExit(f"no type named or UID'd '{name}' found")
    raise SystemExit(f"ambiguous type name '{name}': "
                     f"{', '.join(c.uid for c in candidates)}")


def filter_by_package(items: dict[str, TypeItem],
                      allowed_packages: set[str]) -> dict[str, TypeItem]:
    return {
        uid: item
        for uid, item in items.items() if item.package in allowed_packages
    }


def _attach_forest_roots(
        items: dict[str, TypeItem],
        children: dict[str, list[Edge]]) -> dict[str, list[Edge]]:
    """ Attach every type unreachable from `_ROOT_UID` by a spec-refinement
    walk (e.g. plain "value types" like `name` that are never refined and
    never refine anything) to it via a synthetic `[member]` edge, so the
    whole type system prints as one connected tree. """
    has_parent = {
        edge.child_uid
        for edges in children.values()
        for edge in edges
    }
    other_roots = sorted(uid for uid in items
                         if uid not in has_parent and uid != _ROOT_UID)
    result = {uid: list(edges) for uid, edges in children.items()}
    if other_roots:
        result.setdefault(_ROOT_UID, []).extend(
            Edge("", ["member"], uid) for uid in other_roots)
    return result


def _short_uid(uid: str) -> str:
    if uid.startswith(_UID_PREFIX):
        return uid[len(_UID_PREFIX):]
    return uid


def _label_parts(item: TypeItem) -> list[str]:
    """ `item`'s own display parts, short uid first (most useful if the
    line wraps) and descriptive name last (usually the longest). """
    return [_short_uid(item.uid), f"[{item.package}]", item.name]


def _wrap_bracket(first_prefix: str, continuation_prefix: str, edge_key: str,
                  edge_values: list[str], width: int) -> list[str]:
    """ Render ``[key=v1|v2|...]`` packed onto as few lines as fit in
    `width`, breaking only *between* values, never inside one. """
    opening = f"[{edge_key}=" if edge_key else "["
    tokens = [opening + edge_values[0]
              ] + [f"|{value}" for value in edge_values[1:]]
    lines: list[str] = []
    prefix = first_prefix
    current = prefix
    last_index = len(tokens) - 1
    for index, token in enumerate(tokens):
        bracket_width = 1 if index == last_index else 0
        candidate = current + token
        if current != prefix and len(candidate) + bracket_width > width:
            lines.append(current)
            prefix = continuation_prefix
            current = prefix + token
        else:
            current = candidate
    lines.append(current + "]")
    return lines


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def _print_entry(prefix: str, connector: str, continuation_prefix: str,
                 edge_key: str, edge_values: list[str], label_parts: list[str],
                 width: int) -> None:
    """ Print one tree/ancestor-chain entry: ``prefix connector [key=value]
    uid [package] name``, splitting it across lines only when it doesn't
    fit `width`. """
    edge_text = ""
    if edge_values:
        edge_text = (f"[{edge_key}={'|'.join(edge_values)}]"
                     if edge_key else f"[{'|'.join(edge_values)}]")

    components = ([edge_text] if edge_text else []) + label_parts
    full_line = f"{prefix}{connector}" + " ".join(components)
    if len(full_line) <= width:
        print(full_line)
        return

    line_prefix = prefix + connector
    if edge_text:
        for line in _wrap_bracket(line_prefix, continuation_prefix, edge_key,
                                  edge_values, width):
            print(line)
        line_prefix = continuation_prefix
    for part in label_parts:
        line = line_prefix + part
        if len(line) > width:
            # avoid splitting an overlong uid/name mid-word
            wrapped_lines = textwrap.wrap(
                part,
                width=width,
                initial_indent=line_prefix,
                subsequent_indent=continuation_prefix,
                break_on_hyphens=False,
                break_long_words=False)
            for wrapped in wrapped_lines or [line]:
                print(wrapped)
        else:
            print(line)
        line_prefix = continuation_prefix


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def _print_tree(items: dict[str, TypeItem],
                children: dict[str, list[Edge]],
                uid: str,
                width: int,
                prefix: str = "",
                is_last: bool = True,
                is_root: bool = True,
                edge: Optional[Edge] = None) -> None:
    connector = "" if is_root else ("└── " if is_last else "├── ")
    child_prefix = prefix if is_root else prefix + (
        "    " if is_last else "│   ")
    own_continuation_prefix = prefix + "    " if is_root else child_prefix
    _print_entry(prefix, connector, own_continuation_prefix,
                 edge.key if edge else "", edge.values if edge else [],
                 _label_parts(items[uid]), width)
    edges = children.get(uid, [])
    for index, child_edge in enumerate(edges):
        _print_tree(items, children, child_edge.child_uid, width, child_prefix,
                    index == len(edges) - 1, False, child_edge)


def _print_ancestors(items: dict[str, TypeItem], uid: str, width: int) -> None:
    # built leaf-to-root, then reversed below to print root-to-leaf
    chain = [uid]
    edge_infos: list[tuple[str, list[str]]] = []
    current = items[uid]
    while True:
        links = [
            candidate for candidate in current.data.get("links") or []
            if candidate.get("role") == "spec-refinement"
        ]
        if not links:
            break
        parent_uid = _resolve_uid(current.uid, links[0]["uid"])
        same_parent = [
            link for link in links
            if _resolve_uid(current.uid, link["uid"]) == parent_uid
        ]
        edge_infos.append((same_parent[0]["spec-key"],
                           sorted(link["spec-value"] for link in same_parent)))
        chain.append(parent_uid)
        current = items[parent_uid]
    chain.reverse()
    edge_infos.reverse()
    for depth, node_uid in enumerate(chain):
        prefix = "    " * depth
        connector = "" if depth == 0 else "└── "
        continuation_prefix = "    " * (depth + 1)
        edge = edge_infos[depth - 1] if depth > 0 else ("", [])
        _print_entry(prefix, connector, continuation_prefix, edge[0], edge[1],
                     _label_parts(items[node_uid]), width)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=clitypetree.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--ancestors",
        metavar="TYPE",
        default=None,
        help="print only the ancestor chain from the root down to TYPE, "
        "not its subtree")
    parser.add_argument(
        "--package",
        metavar="PACKAGE",
        default=None,
        help="only show types up to this package: the package itself "
        "plus every package it depends on -- e.g. --package specware "
        "shows specitems and specware, but not specmake")
    return parser.parse_args(argv[1:])


def clitypetree(argv: list[str] = sys.argv) -> Optional[int]:
    """ Print the specification item type-refinement tree. """
    args = _parse_args(argv)

    sources = _discover_type_sources()
    if not sources:
        print(
            "no specification type sources (a spec-types/ directory or "
            "a bundled spec.pickle) found for any installed package",
            file=sys.stderr)
        return 1
    items = load_type_items(sources)

    if args.package:
        if args.package not in sources:
            print(
                f"unknown package '{args.package}'; discovered packages "
                f"are: {', '.join(sorted(sources))}",
                file=sys.stderr)
            return 1
        items = filter_by_package(items, packages_up_to(args.package, sources))

    width = _effective_width()

    if args.ancestors:
        _print_ancestors(items, _find(items, args.ancestors).uid, width)
        return None

    if _ROOT_UID not in items:
        print(
            f"the root type '{_ROOT_UID}' was not found among the "
            "loaded types",
            file=sys.stderr)
        return 1

    children = _attach_forest_roots(items, build_children_map(items))
    _print_tree(items, children, _ROOT_UID, width)
    return None


if __name__ == "__main__":
    sys.exit(clitypetree(sys.argv))
