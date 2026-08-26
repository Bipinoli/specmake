# SPDX-License-Identifier: BSD-2-Clause
""" Provides a command line interface to generate interface items. """

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

import contextlib
import glob
import io
import json
import os
import sys
from typing import Iterator, NamedTuple

import yaml

from specitems import atomic_dump_to_file, get_arguments
from specware import load_specware_config

from .sourcetospec import (ConfigError, DoxygenContext, DoxygenEnum,
                           DoxygenGroup, DoxygenFile, DoxygenItem,
                           DoxygenTypedef)


def _propose_config(ctx: DoxygenContext, config: dict) -> None:
    proposed = ctx.proposed_config(config)
    config_2 = {"spec-from-source": proposed}
    text = yaml.dump(config_2, default_flow_style=False, allow_unicode=True)
    print(text.rstrip())
    item_to_group = ctx.resolved_item_to_group()
    if item_to_group:
        print("  item-to-group:")
        for doxygen_id, group_ident in item_to_group.items():
            item = ctx.items[doxygen_id]
            # Serialise each entry through yaml rather than formatting it
            # directly, so a null group and any group name that would
            # otherwise need quoting both survive a copy-paste back into
            # the configuration.
            entry = yaml.safe_dump({
                doxygen_id: group_ident
            },
                                   default_flow_style=False).strip()
            print(f"    {entry} # {item.kind}/{item.name}")
    else:
        print("  item-to-group: {}")


def _apply_config(ctx: DoxygenContext, config: dict, config_file: str) -> None:
    """
    Write the proposed config directly to ``config_file``.

    ``config_file`` is the same file it was read from; this replaces
    printing the proposal for manual copy-paste, which is exactly how
    a bare ``item-to-group:`` attribute (parsed as YAML null rather than
    ``{}``) used to end up in a config verbatim.

    ``item-to-group`` itself is only ever pruned, never regenerated:
    an entry the config already had survives as long as its item
    still exists, regardless of whether this run would have inferred
    the same group on its own. Writing the full resolved mapping
    instead would bake every file-inferred and default-group-name
    assignment in as if it were a manual override, permanently hiding
    those items from future inference.
    """
    proposed = ctx.proposed_config(config)
    proposed["item-to-group"] = ctx.preserved_item_to_group(config)
    atomic_dump_to_file(
        config_file, {"spec-from-source": proposed}, lambda data: yaml.dump(
            data, default_flow_style=False, allow_unicode=True))
    print(f"applied proposed configuration to {config_file}")


class GenerationError(Exception):
    """ Raised when the generation of one item fails. """


def _origin(item: DoxygenItem) -> str:
    """
    Is the declaration the item comes from.

    The header is resolved through the file of the item, which raises
    when the item has none.  A group is such an item.  Leave the
    header out there rather than fail in a message.
    """
    try:
        return f"{item.kind} {item.name} of {item.file.name}"
    except ValueError:
        return f"{item.kind} {item.name}"


def _describe(item: DoxygenItem) -> str:
    """
    Describe the item by its declaration and its UID.

    The UID is resolved through the group of the item, which raises
    when the item has none.  A description is wanted where something
    already failed, so leave the UID out rather than fail again.
    """
    try:
        return f"{_origin(item)} at {item.uid}"
    except ValueError:
        return _origin(item)


@contextlib.contextmanager
def _generating(item: DoxygenItem) -> Iterator[None]:
    """
    Name the item which a failure comes from.

    A run turns hundreds of declarations of a vendor into items, and a
    shape the tool does not handle stops it.  The traceback names the
    code which raised, not the declaration which reached that code, so
    the item has to be found by hand.  Chain the failure to keep the
    traceback whole and name the item in the last line of it.
    """
    try:
        yield
    except Exception as err:
        raise GenerationError(f"cannot generate {_describe(item)}") from err


def _record_gaps(gaps: dict[str, list[str]], item: DoxygenItem) -> None:
    """ Record an item's manual review gaps, if it has any. """
    item_gaps = item.review_gaps
    if item_gaps:
        gaps[item.uid] = item_gaps


class _UidRegistry:
    """
    Tracks which items produce which UID.

    A UID names one item of the specification, so two items which
    produce the same UID save one file and the second overwrites the
    first.  Every declaration of the lost item keeps a link to it, and
    the link then names the wrong item.  A single item reached through
    two groups or two headers keeps one Doxygen identifier, so the
    identifier, not the count of the entries, tells the two apart.
    """

    def __init__(self) -> None:
        self.items_by_uid: dict[str, dict[str, DoxygenItem]] = {}

    def add(self, item: DoxygenItem) -> None:
        """ Record the item under its UID. """
        self.items_by_uid.setdefault(item.uid, {})[item.doxygen_id] = item

    def check(self) -> None:
        """ Raise a single error naming every UID which two items claim. """
        collisions = [
            f"  - {uid} from " +
            " and ".join(_origin(item) for item in items.values())
            for uid, items in sorted(self.items_by_uid.items())
            if len(items) > 1
        ]
        if collisions:
            problems = "\n".join(collisions)
            raise ConfigError(
                "these items produce the same UID (check the uid and the "
                f"remove-prefix of the groups they belong to):\n{problems}")


class _HeaderResult(NamedTuple):
    """ What generating one header produced. """

    items: list[DoxygenItem]
    typedefs_skipped: int
    gaps: dict[str, list[str]]


def _generate_header(header: DoxygenFile,
                     dry_run: bool = False) -> _HeaderResult:
    """
    Generate a header and its members.

    With ``dry_run``, only reports what would be generated. Returns
    every (would-be) saved item, how many typedefs were skipped because
    they merely alias a compound (struct/union/enum) item saved under
    the same UID, and the manual review gaps per UID.
    """
    gaps: dict[str, list[str]] = {}
    with _generating(header):
        print("  ", header.uid)
        if not dry_run:
            header.save()
        items: list[DoxygenItem] = [header]
        _record_gaps(gaps, header)
    typedefs_skipped = 0
    for header_member in header.members():
        with _generating(header_member):
            if header_member.is_excluded:
                continue
            if (isinstance(header_member, DoxygenTypedef)
                    and header_member.aliases_compound):
                # For example `typedef enum e { ... } e;`. The enum item
                # already covers this under the same name, marked via
                # definition-kind.
                typedefs_skipped += 1
                continue
            print("    ", header_member.uid)
            if not dry_run:
                header_member.save()
            items.append(header_member)
            _record_gaps(gaps, header_member)
        if isinstance(header_member, DoxygenEnum):
            for enumerator in header_member.members():
                with _generating(enumerator):
                    if enumerator.is_excluded:
                        continue
                    print("      ", enumerator.uid)
                    if not dry_run:
                        enumerator.save()
                    items.append(enumerator)
                    _record_gaps(gaps, enumerator)
    return _HeaderResult(items, typedefs_skipped, gaps)


def _print_gaps(gaps: dict[str, list[str]]) -> None:
    """
    Report every item a human still has to complete by hand.

    There is nothing in an undocumented declaration for the tool to
    invent a description from, so these items are expected rather than
    wrong. Listing them keeps a bootstrap run's manual review to the
    items which need it instead of every generated file.
    """
    if not gaps:
        return
    width = max(len(uid) for uid in gaps)
    print("\nneeds attention:")
    for uid in sorted(gaps):
        print(f"  {uid.ljust(width)}  {', '.join(gaps[uid])}")


def _reachable_headers(group: DoxygenGroup) -> list[DoxygenFile]:
    """
    Find every header file reachable from a group's members.

    A header is reachable directly, when the file itself is a group
    member via ``@file \\ingroup``, or transitively, when a group
    member such as a function is declared in that file via a bare
    ``@ingroup``.
    """
    headers: dict[str, DoxygenFile] = {}
    for group_member in group.members():
        if group_member.is_header:
            assert isinstance(group_member, DoxygenFile)
            headers.setdefault(group_member.doxygen_id, group_member)
            continue
        for file in group_member.files:
            if not file.is_header:
                continue
            if not file.group_ids:
                # Reached only transitively, for example via a function
                # that carries its own @ingroup with no @file @ingroup on the
                # header itself: place it under the discovering group, the
                # same way it would be placed had it been an explicit group
                # member. If a later group also transitively reaches the
                # same file through a different member, that first
                # assignment wins (groups are processed in a fixed,
                # doxygen_id-sorted order): the file is placed once, under
                # whichever enabled group's member is encountered first.
                file.group_ids.append(group.doxygen_id)
            headers.setdefault(file.doxygen_id, file)
    return sorted(headers.values())


def _record_owner(generated: dict[str, list[str]], uid: str,
                  group_name: str) -> None:
    """
    Record ``group_name`` as an owner of ``uid``, at most once.

    Two headers in the same group can yield the same UID, for example
    an enumerator reachable through either of them, so the same owner
    can be offered for one UID more than once.
    """
    owners = generated.setdefault(uid, [])
    if group_name not in owners:
        owners.append(group_name)


def _print_generated_summary(dry_run: bool, item_count: int, group_count: int,
                             typedefs_skipped: int) -> None:
    """ Report what the run produced. """
    verb = "would generate" if dry_run else "generated"
    summary = f"{verb} {item_count} item(s) across {group_count} group(s)"
    if typedefs_skipped:
        summary += (f", {typedefs_skipped} typedef(s) skipped as "
                    "compound aliases")
    print(summary)


class _GroupsResult(NamedTuple):
    """ What generating every enabled group produced. """

    generated: dict[str, list[str]]
    gaps: dict[str, list[str]]


def _generate_groups(ctx: DoxygenContext,
                     config: dict,
                     dry_run: bool = False) -> _GroupsResult:
    """
    Generate every enabled group's contents.

    With ``dry_run``, only reports what would be generated without
    writing anything. Returns every (would-be) generated item's UID
    mapped to the names of the enabled groups that own it, for
    ``--prune`` to compare against a previous run's manifest, and the
    manual review gaps per UID. A header reachable from several enabled
    groups is owned by all of them, so ownership is a list rather than
    a single name.
    """
    generated: dict[str, list[str]] = {}
    # A header carrying several @ingroup blocks, or one reached
    # transitively by members of different groups, is reachable from
    # more than one enabled group. Its content does not depend on which
    # group discovered it, so generate it once for the whole run rather
    # than rewriting the identical file under every owner. The items it
    # produced are cached, because every later owner still has to be
    # recorded against them.
    header_items: dict[str, list[DoxygenItem]] = {}
    registry = _UidRegistry()
    groups_processed = 0
    typedefs_skipped = 0
    gaps: dict[str, list[str]] = {}
    for group in sorted(ctx.items_by_kind["group"].values()):
        assert isinstance(group, DoxygenGroup)
        if group.name not in config["enabled-groups"]:
            continue
        print(group.doxygen_id)
        if group.generate_item:
            with _generating(group):
                if not dry_run:
                    group.save()
                # A suppressed group item is deliberately left out of
                # the generated set, so --prune never offers to delete
                # the hand-written item sitting at the group uid.
                _record_owner(generated, group.uid, group.name)
                _record_gaps(gaps, group)
                registry.add(group)
        groups_processed += 1
        for header in _reachable_headers(group):
            items = header_items.get(header.doxygen_id)
            if items is None:
                # Counted here rather than per owner, so a header shared
                # by several groups contributes its skipped typedefs to
                # the run's total once.
                result = _generate_header(header, dry_run=dry_run)
                items = result.items
                typedefs_skipped += result.typedefs_skipped
                gaps.update(result.gaps)
                header_items[header.doxygen_id] = items
                for item in items:
                    registry.add(item)
            for item in items:
                _record_owner(generated, item.uid, group.name)
    _print_generated_summary(dry_run, len(generated), groups_processed,
                             typedefs_skipped)
    registry.check()
    return _GroupsResult(generated, gaps)


_MANIFEST_FILENAME = ".specfromsource-manifest.json"


def _load_manifest(path: str) -> dict[str, list[str]]:
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as src:
        manifest = json.load(src)
    if not isinstance(manifest, dict):
        return {}
    # A manifest is written by this tool but read back as a plain file
    # that could be stale, hand-edited, or shared across checkouts, the
    # same reason pruning refuses to unlink outside spec-directory. A
    # value that isn't a group name or a list of them yields no owners,
    # which spares the entry rather than raising on it. A bare name is
    # what a manifest written before ownership became a list records.
    owners_by_uid: dict[str, list[str]] = {}
    for uid, owners in manifest.items():
        if isinstance(owners, str):
            owners_by_uid[uid] = [owners]
        elif isinstance(owners, list):
            owners_by_uid[uid] = [
                owner for owner in owners if isinstance(owner, str)
            ]
        else:
            owners_by_uid[uid] = []
    return owners_by_uid


def _save_manifest(path: str, manifest: dict[str, list[str]]) -> None:
    with open(path, "w", encoding="utf-8") as dst:
        json.dump(manifest, dst, indent=2, sort_keys=True)
        dst.write("\n")


def _prune(ctx: DoxygenContext,
           enabled_groups: list[str],
           generated: dict[str, list[str]],
           dry_run: bool = False) -> None:
    """
    Remove previously-generated items no longer produced by this run.

    Uses a manifest tracking each UID's owning enabled groups from the
    last ``--prune`` run. A UID is stale once this run produced no such
    item and at least one of its recorded owners is enabled: that owner
    is present and no longer generating it, which is what makes the
    item obsolete rather than merely unvisited. A UID none of whose
    owners are enabled is left alone, so a group left out of
    ``enabled-groups`` this time around (by oversight or otherwise)
    never has its previously-generated items pruned out from under it.
    With ``dry_run``, only reports what would be removed: neither the
    items nor the manifest itself are touched.
    """
    manifest_path = str(ctx.spec_directory / _MANIFEST_FILENAME)
    previous = _load_manifest(manifest_path)
    this_run_groups = set(enabled_groups)
    stale = {
        uid
        for uid, owners in previous.items()
        if uid not in generated and any(owner in this_run_groups
                                        for owner in owners)
    }
    spec_directory = ctx.spec_directory.resolve()
    pruned_count = 0
    verb = "would prune" if dry_run else "pruned"
    for uid in sorted(stale):
        item_path = (ctx.spec_directory / f"{uid[1:]}.yml").resolve()
        if not item_path.is_relative_to(spec_directory):
            # A manifest is trusted state written by a prior run of this
            # same tool, but it's still just a file on disk that could be
            # stale, hand-edited, or shared across checkouts. Never unlink
            # outside spec-directory on its say-so.
            print("  skipped pruning", uid, "(escapes spec-directory)")
            continue
        if item_path.is_file():
            print(f"  {verb}", uid)
            if not dry_run:
                item_path.unlink()
            pruned_count += 1
    print(f"{verb} {pruned_count} stale item(s)")
    if dry_run:
        return
    # Entries this run had nothing to say about, because none of their
    # owners took part, carry over untouched. Everything else is
    # replaced by what this run actually produced.
    new_manifest = {
        uid: owners
        for uid, owners in previous.items()
        if not any(owner in this_run_groups for owner in owners)
    }
    new_manifest.update(
        (uid, sorted(owners)) for uid, owners in generated.items())
    _save_manifest(manifest_path, new_manifest)


def _resolve_xml_files(doxygen_xml_files: list[str],
                       doxygen_xml_dir: str | None) -> list[str]:
    """
    Resolve the Doxygen XML files to process.

    Either from an explicit list or by globbing ``*.xml`` in
    ``--doxygen-xml-dir``. Exactly one of the two must be given.
    """
    if doxygen_xml_dir is not None:
        if doxygen_xml_files:
            raise ConfigError(
                "DOXYGEN_XML_FILES and --doxygen-xml-dir are mutually "
                "exclusive")
        resolved = sorted(glob.glob(os.path.join(doxygen_xml_dir, "*.xml")))
        if not resolved:
            raise ConfigError("no *.xml files found in --doxygen-xml-dir "
                              f"{doxygen_xml_dir!r}")
        return resolved
    if not doxygen_xml_files:
        raise ConfigError(
            "no Doxygen XML files given: pass DOXYGEN_XML_FILES or "
            "--doxygen-xml-dir")
    return doxygen_xml_files


def _bootstrap_directory(config_file: str | None) -> str:
    """
    Return the working directory for a bootstrapped configuration.

    The configuration file does not exist yet, so take the directory it
    would live in, just like an existing file's directory is used.
    """
    if config_file is None:
        return "."
    directory = os.path.dirname(config_file) or "."
    if not os.path.isdir(directory):
        raise ConfigError(f"cannot bootstrap {config_file}: there is no "
                          f"directory {directory}")
    return directory


def _spec_from_source(config, config_file: str | None) -> dict:
    """
    Return the 'spec-from-source' attribute of the configuration.

    A null configuration file and a null attribute both count as an
    empty mapping, so that --propose-config can bootstrap from them.
    """
    name = config_file or "specware.yml"
    if config is None:
        return {}
    if not isinstance(config, dict):
        raise ConfigError(f"{name} does not contain a mapping")
    try:
        spec_from_source = config["spec-from-source"]
    except KeyError as err:
        raise ConfigError(f"{name} is missing the top-level "
                          "'spec-from-source' attribute") from err
    if spec_from_source is None:
        return {}
    if not isinstance(spec_from_source, dict):
        raise ConfigError(
            f"{name} has a 'spec-from-source' attribute which is not a "
            "mapping")
    return spec_from_source


def _run(args) -> None:
    if args.apply and not args.propose_config:
        raise ConfigError("--apply requires --propose-config")
    if args.dry_run and args.propose_config:
        raise ConfigError("--dry-run is not compatible with --propose-config")
    try:
        config, working_directory = load_specware_config(args.config_file)
    except FileNotFoundError as err:
        if not args.propose_config:
            raise ConfigError(str(err)) from err
        # --propose-config exists to bootstrap a config in the first
        # place: propose one from just the Doxygen XML instead of
        # requiring a placeholder file to already exist.
        config = None
        working_directory = _bootstrap_directory(args.config_file)
    config = _spec_from_source(config, args.config_file)
    config_file_name = os.path.basename(args.config_file or "specware.yml")
    with contextlib.chdir(working_directory):
        xml_files = _resolve_xml_files(args.doxygen_xml_files,
                                       args.doxygen_xml_dir)
        ctx = DoxygenContext(config,
                             require_full_config=not args.propose_config)
        if not args.dry_run:
            os.makedirs(ctx.spec_directory, exist_ok=True)
        ctx.doxygen_xml_to_spec(xml_files)
        if args.propose_config:
            if args.apply:
                _apply_config(ctx, config, config_file_name)
            else:
                _propose_config(ctx, config)
        else:
            # Resolve every item before the first write, so a UID which
            # two items claim stops the run with nothing generated and
            # nothing overwritten.  The pass writes no file and reports
            # nothing, since the run which follows it lists the items
            # it generates.
            with contextlib.redirect_stdout(io.StringIO()):
                _generate_groups(ctx, config, dry_run=True)
            result = _generate_groups(ctx, config, dry_run=args.dry_run)
            if args.prune:
                _prune(ctx,
                       config["enabled-groups"],
                       result.generated,
                       dry_run=args.dry_run)
            # Last, so that what still needs a human is the final thing
            # the run reports rather than something buried above the
            # pruning summary.
            _print_gaps(result.gaps)


def clifromsource(argv: list[str] = sys.argv) -> None:
    """
    Generate interface items from Doxygen generated XML files using the
    configuration.
    """

    def _add_arguments(parser):
        parser.add_argument("--config-file",
                            type=str,
                            default=None,
                            help="use this configuration file")
        parser.add_argument("--propose-config",
                            action="store_true",
                            help="propose a configuration")
        parser.add_argument(
            "--apply",
            action="store_true",
            help="with --propose-config, write the proposal directly to "
            "the config file instead of printing it for manual review")
        parser.add_argument(
            "--prune",
            action="store_true",
            help="remove previously generated items no longer produced by "
            "this run, tracked via a manifest file in spec-directory")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="report what would be generated (and pruned, with "
            "--prune) without writing or deleting anything; not "
            "compatible with --propose-config")
        parser.add_argument(
            "--doxygen-xml-dir",
            type=str,
            default=None,
            help="use every *.xml file in this directory instead of "
            "listing DOXYGEN_XML_FILES individually")
        parser.add_argument("doxygen_xml_files",
                            metavar="DOXYGEN_XML_FILES",
                            nargs="*",
                            help="the Doxygen generated XML files")

    args = get_arguments(argv[1:],
                         description=clifromsource.__doc__,
                         add_arguments=(_add_arguments, ))
    try:
        _run(args)
    except ConfigError as err:
        # Every known, anticipated failure mode (a bad --config-file path,
        # a malformed config, no XML source given, an item-to-group entry
        # naming an unknown group, ...) is raised as a ConfigError with a
        # message that already names the offending attribute/item. Surface
        # that message directly instead of a traceback. Catching only
        # ConfigError, not ValueError generally, means a ValueError raised
        # by an actual internal bug elsewhere still surfaces as a
        # traceback instead of being mistaken for a config problem.
        sys.exit(f"specfromsource: error: {err}")
