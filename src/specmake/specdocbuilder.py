# SPDX-License-Identifier: BSD-2-Clause
""" Builds documents presenting specification items. """

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

# pylint: disable=too-many-lines

import functools
import itertools
import os
import re
from typing import Any, Callable, Iterable, NamedTuple

from specitems import (COL_SPAN, EnabledSet, GenericContent, Item,
                       ItemGetValueContext, ItemMapper, ROW_SPAN, is_enabled,
                       Link, link_is_enabled, make_label, TextContent)
from specware import (CodeMapper, TransitionMap, PreCondsOfPostCond,
                      align_declarations, document_directive, document_option,
                      forward_declaration)

from .docbuilder import DocumentBuilder
from .pkgitems import PackageBuildDirector
from .linkhub import get_kind, spec_label, SpecMapper
from .perfimages import environment_order
from .rtems import RTEMSItemCache
from .speccompare import CompareSpecsRegistry
from .testaggregator import get_test_result_status
from .util import duration


class _Context(NamedTuple):
    content: TextContent
    item: Item
    mapper: SpecMapper
    code_mapper: ItemMapper
    spec: RTEMSItemCache
    file_path: str
    # An item's one-line facts (requirement, group membership, ...),
    # collected here for add_item() to render as one table at the end.
    details: list[tuple[str, str]]


def _emit_fact(ctx: _Context, label: str, sentence: str) -> None:
    """ Queue a one-line fact about an item instead of writing it now. """
    ctx.details.append((label, sentence))


def _add_text(ctx: _Context, key: str, name: str) -> None:
    text = ctx.item.get(key, None)
    if text:
        ctx.content.add_rubric(f"{name}:")
        ctx.content.wrap(ctx.mapper.substitute(text))


def _add_brief(ctx: _Context) -> None:
    """ The item's brief description, as the opening paragraph of its
    section (no heading -- the section title already names the item). """
    text = ctx.item.get("brief", None)
    if text:
        ctx.content.wrap(ctx.mapper.substitute(text))


def _add_sdd_link(ctx: _Context) -> None:
    path = ctx.item.view["document-paths"].get("sdd", None)
    if path:
        kind = get_kind(ctx.item)
        name = ctx.item.view["sdd-name"]
        _emit_fact(
            ctx, "SOFTWARE DESIGN",
            f"This {kind} is realised by the software design element "
            f"{ctx.mapper.format_link(name, path)}.")


def _add_links(
        ctx: _Context,
        role: str | list[str],
        name: str,
        parent_role: str,
        child_role: str,
        child_prefix: str = "This",
        is_link_enabled: Callable[[Link], bool] = link_is_enabled) -> None:
    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-positional-arguments
    # pylint: disable=too-many-locals
    parents = [
        link.item for link in ctx.item.links_to_parents(role)
        if is_link_enabled(link)
    ]
    children = [
        link.item for link in ctx.item.links_to_children(role)
        if is_link_enabled(link)
    ]
    if not (parents or children):
        return
    get_link = ctx.mapper.get_link
    kind = get_kind(ctx.item)
    if len(parents) == 1 and not children:
        parent = parents[0]
        parent_kind = get_kind(parent)
        _emit_fact(
            ctx, name, f"This {kind} {parent_role} the "
            f"{parent_kind} {get_link(parent)}.")
        return
    if len(children) == 1 and not parents:
        child = children[0]
        child_kind = get_kind(child)
        _emit_fact(
            ctx, name, f"{child_prefix} {kind} {child_role} "
            f"{child_kind} {get_link(child)}.")
        return
    # Multiple targets: too much for one fact, keeps its own heading+list.
    plural = "S" if len(parents) + len(children) > 1 else ""
    ctx.content.add_rubric(f"{name}{plural}:")
    if len(parents) == 1:
        parent = parents[0]
        parent_kind = get_kind(parent)
        ctx.content.wrap(f"This {kind} {parent_role} the "
                         f"{parent_kind} {get_link(parent)}.")
    elif len(parents) > 1:
        ctx.content.add_list([get_link(parent) for parent in parents],
                             f"This {kind} {parent_role} the following items:")
    if len(children) == 1:
        child = children[0]
        child_kind = get_kind(child)
        ctx.content.wrap(f"{child_prefix} {kind} {child_role} "
                         f"{child_kind} {get_link(child)}.")
    elif len(children) > 1:
        ctx.content.add_list(
            [get_link(child) for child in children],
            f"{child_prefix} {kind} {child_role} the following items:")


def _add_default_links(ctx: _Context) -> None:
    _add_sdd_link(ctx)
    _add_links(ctx, "interface-enumerator", "ENUMERATOR", "provides",
               "is provided by")
    _add_links(ctx, "requirement-refinement", "REFINEMENT", "refines",
               "is refined by")
    _add_links(ctx, ["interface-ingroup", "interface-ingroup-hidden"],
               "GROUP MEMBERSHIP", "is a member of", "contains")
    _add_links(ctx, "interface-placement", "INTERFACE PLACEMENT",
               "is placed into", "contains")
    _add_links(ctx,
               "interface-function",
               "INTERFACE FUNCTION",
               "specifies the function of",
               "is specified by the",
               child_prefix="The function of this")
    _add_links(ctx, "function-implementation", "FUNCTION IMPLEMENTATION",
               "uses functions implemented by",
               "implements a function used by")
    _add_links(ctx,
               "interface-include",
               "INTERFACE INCLUDE",
               "includes",
               "is included by",
               is_link_enabled=functools.partial(_is_include_enabled,
                                                 ctx.spec.enabled_set))


def _add_validated_items(ctx: _Context) -> None:
    _add_links(ctx, "validation", "VALIDATED ITEM", "validates", "oops")


def _add_code_block(content: TextContent, code: GenericContent) -> None:
    content.add_rubric("INTERFACE:")
    with content.directive("code-block", "c"):
        content.add(code)


def _add_type_definition(content: TextContent, name: str, definition_kind: str,
                         type_name: str, code: list[str]) -> None:
    if definition_kind == f"{type_name}-only":
        code.insert(0, f"{type_name} {name} {{")
        code.append("};")
    elif definition_kind == "typedef-only":
        code.insert(0, f"typedef {type_name} {{")
        code.append(f"}} {name};")
    else:
        code.insert(0, f"typedef {type_name} {name} {{")
        code.append(f"}} {name};")
    _add_code_block(content, code)


def _definition(definition: dict, mapper: ItemMapper,
                enabled_set: EnabledSet) -> Any:
    enabled_set = frozenset(f"defined({enable})" for enable in enabled_set)
    for variant in definition["variants"]:
        if is_enabled(enabled_set,
                      mapper.substitute_data(variant["enabled-by"])):
            return variant["definition"]
    return definition["default"]


def _item_definition(item: Item, mapper: ItemMapper,
                     enabled_set: EnabledSet) -> str:
    return mapper.substitute(
        _definition(item["definition"], mapper, enabled_set)).strip()


def _document_unspecified(ctx: _Context,
                          prefix: str = "",
                          postfix: str = "") -> None:
    kind = get_kind(ctx.item)
    name = f"{prefix}{ctx.item['name']}{postfix}"
    container = ctx.item.parent('interface-placement')
    container_kind = get_kind(container)
    _emit_fact(
        ctx, "REQUIREMENT",
        f"The {ctx.mapper.get_link(container)} {container_kind} "
        f"shall provide the {kind} {ctx.content.code(name)}.")


def _document_unspecified_type(ctx: _Context) -> None:
    type_kind = ctx.item['interface-type'][12:]
    _document_unspecified(ctx, prefix=f"{type_kind} ")
    _add_code_block(ctx.content, f"{type_kind} {ctx.item['name']} {{ ... }};")
    _add_default_links(ctx)
    _add_validations(ctx)


def _document_unspecified_define(ctx: _Context) -> None:
    _document_unspecified(ctx)
    _add_code_block(ctx.content, f"#define {ctx.item['name']} ...")
    _add_default_links(ctx)
    _add_validations(ctx)


def _document_unspecified_enumerator(ctx: _Context) -> None:
    _document_unspecified(ctx)
    _add_code_block(
        ctx.content,
        ["enum ... {", "  ....", f"  {ctx.item['name']} ...", "  ....", "};"])
    _add_default_links(ctx)
    _add_validations(ctx)


def _document_unspecified_function(ctx: _Context) -> None:
    _document_unspecified(ctx, postfix="()")
    _add_code_block(ctx.content, f"... {ctx.item['name']}( ... );")
    _add_default_links(ctx)
    _add_validations(ctx)


def _document_unspecified_group(ctx: _Context) -> None:
    _document_unspecified(ctx)
    _add_default_links(ctx)
    _add_validations(ctx)


def _document_unspecified_object(ctx: _Context) -> None:
    _document_unspecified(ctx)
    _add_code_block(ctx.content, f"extern ... {ctx.item['name']} ...;")
    _add_default_links(ctx)
    _add_validations(ctx)


def _document_unspecified_typedef(ctx: _Context) -> None:
    _document_unspecified(ctx)
    _add_code_block(ctx.content, f"typedef ... {ctx.item['name']} ...;")
    _add_default_links(ctx)
    _add_validations(ctx)


def _document_constraint(ctx: _Context) -> None:
    _add_text(ctx, "text", "CONSTRAINT")
    _add_text(ctx, "rationale", "RATIONALE")
    _add_default_links(ctx)
    _add_links(ctx, "constraint", "CONSTRAINT ITEM", "constrained by",
               "is applicable to")


def _document_requirement(ctx: _Context) -> None:
    _add_text(ctx, "text", "REQUIREMENT")
    _add_text(ctx, "rationale", "RATIONALE")
    _add_default_links(ctx)
    _add_validations(ctx)


def _add_perf_measurement(ctx: _Context,
                          test_results: list[dict[str, Any]]) -> None:
    for measurement_data in test_results:
        test_case = measurement_data["test-case"]
        test_suite = test_case["test-suite"]
        config_data = test_suite["config"]
        test_case_link = ctx.mapper.format_link(
            ctx.item.cache[test_case["uid"]].spec_2, test_case["link"])
        test_suite_link = ctx.mapper.format_link(
            ctx.item.cache[test_suite["uid"]].spec_2, test_suite["link"])
        measurements_link = ctx.mapper.format_link(
            "runtime performance measurements", measurement_data["link"])
        ctx.content.wrap(f"""For the configuration
{ctx.content.code(config_data['name'])}, the test case {test_case_link} of the
test suite {test_suite_link} reported the following {measurements_link}:""")
        ctx.content.add_image(
            os.path.relpath(f"{measurement_data['boxplot']}.*",
                            os.path.dirname(ctx.file_path)), "50%")


def _document_perf_runtime(ctx: _Context) -> None:
    _add_text(ctx, "text", "REQUIREMENT")
    ctx.content.add_rubric("RUNTIME PERFORMANCE LIMITS:")
    for link in ctx.item.links_to_children("performance-runtime-limits"):
        for target in link.item.children(
                "performance-runtime-limits-provider"):
            ctx.content.wrap(f"""For the
{ctx.mapper.get_link(target)} target, the following runtime
performance limits shall apply:""")
            rows: list[tuple[str | int, ...]] = [
                ("${ENVIRONMENT}", "${LIMIT_KIND}", "${LIMIT_CONDITION}")
            ]
            for env, limits in sorted(link["limits"].items(),
                                      key=environment_order):
                env_name, _, _ = env.partition("/")
                env_item = ctx.spec.name_to_item[
                    f"perf-runtime-env/{env_name}"]
                lower_bound = limits["min-lower-bound"]
                rows.append(
                    (f":ref:`{env} <{make_label(env_item.spec)}>`", "Minimum",
                     f"{duration(lower_bound)} :math:`\\leq` Minimum"))
                lower_bound = limits["median-lower-bound"]
                upper_bound = limits["median-upper-bound"]
                rows.append((ROW_SPAN, "Median",
                             f"{duration(lower_bound)} :math:`\\leq` Median "
                             f":math:`\\leq` {duration(upper_bound)}"))
                upper_bound = limits["max-upper-bound"]
                rows.append((ROW_SPAN, "Maximum",
                             f"Maximum :math:`\\leq` {duration(upper_bound)}"))
            ctx.content.add_grid_table(rows, [25, 25, 50])
            try:
                test_results = ctx.item.view["test-results"][target.uid]
            except KeyError:
                with ctx.content.directive("warning"):
                    ctx.content.wrap("""There are no runtime measurements
available for this requirement.""")
            else:
                _add_perf_measurement(ctx, test_results)
    _add_text(ctx, "rationale", "RATIONALE")
    _add_default_links(ctx)
    _add_validations(ctx)


def _document_perf_runtime_env(ctx: _Context) -> None:
    _document_requirement(ctx)
    ctx.content.add_rubric("NAME:")
    ctx.content.wrap(f"""The RTEMS Test Framework name of this runtime
measurement environment is {ctx.content.code(ctx.item['name'])}.""")


_UPPER = re.compile(r"[A-Z]+")


def _upper_spacify(match: re.Match[str]) -> str:
    return f"\u200b{match.group(0)}"


def _spacify(name: str) -> str:
    return _UPPER.sub(_upper_spacify, name).lstrip("\u200b")


def _name_ref(ctx: _Context, name: str, which: str) -> str:
    label = make_label(f"{ctx.item.spec} {which} {name}")
    return f":ref:`{_spacify(name)} <{label}>`"


def _add_pre_condition_variants(ctx: _Context, transition_map: TransitionMap,
                                pre_conds: Any) -> None:
    for row in pre_conds:
        entries = []
        for co_idx, co_states in enumerate(row):
            co_name = transition_map.pre_co_idx_to_co_name(co_idx)
            co_name = _name_ref(ctx, co_name, "Pre")
            states = [
                transition_map.pre_co_idx_st_idx_to_st_name(co_idx, st_idx)
                for st_idx in set(co_states)
            ]
            if len(states) == 1:
                entries.append(f"{co_name} = {states[0]}")
            else:
                entries.append(f"{co_name} = {{{', '.join(states)}}}")
        ctx.content.add("")
        ctx.content.add("    * " + ", ".join(entries))


def _states(transition_map: TransitionMap, co_idx: int,
            states: list[int]) -> str:
    return ", ".join(
        _spacify(transition_map.pre_co_idx_st_idx_to_st_name(co_idx, st_idx))
        for st_idx in set(states))


def _add_transition_map(
    ctx: _Context
) -> tuple[TransitionMap, list[tuple[str, PreCondsOfPostCond]]]:
    infeasible_pre_conds: list[tuple[str, PreCondsOfPostCond]] = []
    transition_map = TransitionMap(ctx.item, "N/A")
    rows: list[Iterable[str | int]] = [
        ("Pre-Conditions", ) + (COL_SPAN, ) *
        (transition_map.pre_co_count - 1) + ("Post-Conditions", ) +
        (COL_SPAN, ) * (transition_map.post_co_count - 1)
    ]
    rows.append(
        tuple(
            itertools.chain((_name_ref(ctx, condition["name"], "Pre")
                             for condition in ctx.item["pre-conditions"]),
                            (_name_ref(ctx, condition["name"], "Post")
                             for condition in ctx.item["post-conditions"]))))
    for post_co, pre_co_collection in transition_map.get_post_conditions(
            ctx.spec.enabled_set):
        if post_co[0]:
            infeasible_pre_conds.append(
                (transition_map.skip_idx_to_name(post_co[0]),
                 pre_co_collection))
            post_co_row = ((_name_ref(
                ctx, transition_map.skip_idx_to_name(post_co[0]), "Skip"), ) +
                           (COL_SPAN, ) * (transition_map.post_co_count - 1))
            post_co_col_span: tuple[str | int,
                                    ...] = ((ROW_SPAN, ) +
                                            (ROW_SPAN | COL_SPAN, ) *
                                            (transition_map.post_co_count - 1))
        else:
            post_co_row = tuple(
                _spacify(
                    transition_map.post_co_idx_st_idx_to_st_name(
                        co_idx, st_idx))
                for co_idx, st_idx in enumerate(post_co[1:]))
            post_co_col_span = (ROW_SPAN, ) * transition_map.post_co_count
        for pre_co in pre_co_collection:
            pre_co_row = tuple(
                _states(transition_map, co_idx, co_states)
                for co_idx, co_states in enumerate(pre_co))
            rows.append(pre_co_row + post_co_row)
            post_co_row = post_co_col_span
    co_count = transition_map.pre_co_count + transition_map.post_co_count
    with ctx.content.latex_environment("landscape", use=co_count > 10):
        font_size = -((co_count + 4) // 5)
        with ctx.content.latex_font_size(font_size):
            cell_width = 100 // co_count
            widths = [100 - cell_width *
                      (co_count - 1)] + [cell_width] * (co_count - 1)
            ctx.content.add_grid_table(rows, widths=widths, header_rows=2)
    return transition_map, infeasible_pre_conds


def _add_conditions(ctx: _Context, which: str) -> None:
    ctx.content.add_rubric(f"{which.upper()}-CONDITIONS:")
    caption = which[0].upper() + which[1:]
    for condition in ctx.item[f"{which}-conditions"]:
        name = condition['name']
        ctx.content.add_label(make_label(f"{ctx.item.spec} {caption} {name}"))
        with ctx.content.directive("topic", f"{caption}-Condition - {name}"):
            ctx.content.add(f"""The *{name}* {which}-condition has the
following states:""")
            for state in condition["states"]:
                text = ctx.mapper.substitute(state["text"])
                ctx.content.add_definition_item(state["name"], text)


def _document_action_requirement(ctx: _Context) -> None:
    ctx.content.add_rubric("REQUIREMENT:")
    ctx.content.wrap("""The function shall be specified by the following state
transition map which defines for each feasible pre-condition state variant the
resulting post-condition state variant produced by the trigger action.""")
    _add_text(ctx, "rationale", "RATIONALE")
    _add_default_links(ctx)
    _add_validations(ctx)
    _add_conditions(ctx, "pre")
    ctx.content.add_rubric("TRIGGER ACTION:")
    ctx.content.wrap(ctx.mapper.substitute(ctx.item["text"]))
    _add_conditions(ctx, "post")
    ctx.content.add_rubric("TRANSITION MAP:")
    ctx.content.wrap("""For each of the resulting post-condition state variants
below, the set of producing pre-condition variants is listed.""")
    transition_map, infeasible_pre_conds = _add_transition_map(ctx)
    if infeasible_pre_conds:
        ctx.content.add_rubric("INFEASIBLE PRE-CONDITION VARIANTS:")
        for reason, pre_conds in infeasible_pre_conds:
            ctx.content.add_label(make_label(f"{ctx.item.spec} Skip {reason}"))
            ctx.content.add(f"{ctx.content.emphasize(reason)}:")
            ctx.content.paste(
                ctx.mapper.substitute(ctx.item["skip-reasons"][reason]))
            ctx.content.paste(
                """Therefore, the following pre-condition state variants
are infeasible:""")
            _add_pre_condition_variants(ctx, transition_map, pre_conds)


def _document_acfg_group(ctx: _Context) -> None:
    _add_text(ctx, "text", "REQUIREMENT")
    _add_text(ctx, "rationale", "RATIONALE")
    _add_text(ctx, "description", "DESCRIPTION")
    _add_default_links(ctx)
    _add_validations(ctx)


def _document_acfg_option(ctx: _Context) -> None:
    container = ctx.item.parent('interface-placement')
    container_kind = get_kind(container)
    _emit_fact(
        ctx, "REQUIREMENT",
        f"The {ctx.mapper.get_link(container)} {container_kind} shall "
        "provide the application configuration option "
        f"{ctx.content.code(ctx.item['name'])}.")
    document_option(ctx.content, ctx.mapper, ctx.item, ctx.spec.enabled_set)
    _add_default_links(ctx)
    _add_validations(ctx)


def _document_directive(ctx: _Context) -> None:
    _document_unspecified(ctx, postfix="()")
    document_directive(ctx.content, ctx.mapper, ctx.item, ctx.spec.enabled_set)
    _add_default_links(ctx)
    _add_validations(ctx)


def _document_register_block(ctx: _Context) -> None:
    _document_unspecified(ctx)
    _add_brief(ctx)
    ctx.content.add_rubric("REGISTER BLOCK:")
    rows: list[tuple[str | int, ...]] = [("Offset", "Register")]
    for member in ctx.item["definition"]:
        definition = _definition(member, ctx.mapper, ctx.spec.enabled_set)
        count = definition["count"]
        array = f"[ {count} ]" if count > 1 else ""
        rows.append((f"{member['offset']:#x}", f"{definition['name']}{array}"))
    ctx.content.add_grid_table(rows, [20, 80])
    for reg in ctx.item["registers"]:
        ctx.content.add_rubric(f"REGISTER {reg['name']}:")
        rows = [(f"Bits [0:{reg['width'] - 1}]", f"{reg['brief'].strip()}")]
        for bits in reg["bits"]:
            definition = _definition(bits, ctx.mapper, ctx.spec.enabled_set)
            for field in definition:
                start = field["start"]
                width = field["width"]
                if width == 1:
                    pos = str(start)
                else:
                    pos = f"[{start}:{start + width - 1}]"
                rows.append((pos, field["name"]))
        ctx.content.add_grid_table(rows, [20, 80])
    _add_text(ctx, "description", "DESCRIPTION")
    _add_text(ctx, "notes", "NOTES")
    _add_default_links(ctx)
    _add_validations(ctx)


def _document_compound(ctx: _Context) -> None:
    _document_unspecified(ctx)
    _add_brief(ctx)
    enabled_set = frozenset(f"defined({enable})"
                            for enable in ctx.spec.enabled_set)
    members = []
    definitions = []
    for index, member in enumerate(ctx.item["definition"]):
        prefix = f"definition[{index}]"
        for variant in member["variants"]:
            if is_enabled(enabled_set,
                          ctx.mapper.substitute_data(variant["enabled-by"])):
                prefix_2 = f"{prefix}/variants[{index}]/definition"
                definition = variant["definition"]
                break
        else:
            prefix_2 = f"{prefix}/default"
            definition = member["default"]
        if definition is not None:
            text = definition["brief"].strip()
            if definition["description"]:
                text += "\n" + definition["description"].strip()
            members.append((definition["name"],
                            ctx.mapper.substitute(text, prefix=prefix_2)))
            definitions.append(
                ctx.code_mapper.substitute(definition["definition"],
                                           prefix=prefix_2))
    # A compound may legitimately have no member, for example an opaque
    # type documented by its typedef alone.  align_declarations() takes
    # the maximum over the declarations, which raises on an empty list.
    if definitions:
        decls = [f"  {decl};" for decl in align_declarations(definitions)]
    else:
        decls = []
    _add_type_definition(ctx.content, ctx.item["name"],
                         ctx.item["definition-kind"],
                         ctx.item["interface-type"], decls)
    if members:
        ctx.content.add_rubric("MEMBERS:")
        for member in members:
            ctx.content.add_definition_item(member[0], member[1])
    _add_text(ctx, "description", "DESCRIPTION")
    _add_text(ctx, "notes", "NOTES")
    _add_default_links(ctx)
    _add_validations(ctx)


_SPACE = re.compile(r"\s+")


def _enumerator(item: Item, mapper: ItemMapper,
                enabled_set: EnabledSet) -> str:
    definition = _item_definition(item, mapper, enabled_set)
    name = item["name"]
    if definition:
        definition = _SPACE.sub(" ", definition)
        return f"{name} = {definition}"
    return name


def _document_enumeration(ctx: _Context) -> None:
    _document_unspecified(ctx)
    _add_brief(ctx)
    enumerators = [
        f"  {_enumerator(name, ctx.code_mapper, ctx.spec.enabled_set)},"
        for name in ctx.item.parents("interface-enumerator")
    ]
    _add_type_definition(ctx.content, ctx.item["name"],
                         ctx.item["definition-kind"], "enum", enumerators)
    _add_text(ctx, "description", "DESCRIPTION")
    _add_text(ctx, "notes", "NOTES")
    _add_default_links(ctx)
    _add_validations(ctx)


def _document_enumerator(ctx: _Context) -> None:
    name = ctx.item["name"]
    enum = ctx.item.child('interface-enumerator')
    _emit_fact(
        ctx, "REQUIREMENT", f"The {ctx.mapper.get_link(enum)} enumeration "
        f"shall provide the enumerator {ctx.content.code(name)}.")
    _add_brief(ctx)
    enumerator = [
        "  ...",
        f"  {_enumerator(ctx.item, ctx.code_mapper, ctx.spec.enabled_set)}",
        "  ...",
    ]
    _add_type_definition(ctx.content, enum["name"], enum["definition-kind"],
                         "enum", enumerator)
    _add_text(ctx, "description", "DESCRIPTION")
    _add_text(ctx, "notes", "NOTES")
    _add_default_links(ctx)
    _add_validations(ctx)


def _document_define(ctx: _Context) -> None:
    _document_unspecified(ctx)
    _add_brief(ctx)
    _add_code_block(
        ctx.content, f"#define {ctx.item['name']} "
        f"{_item_definition(ctx.item, ctx.code_mapper, ctx.spec.enabled_set)}")
    _add_text(ctx, "description", "DESCRIPTION")
    _add_text(ctx, "notes", "NOTES")
    _add_default_links(ctx)
    _add_validations(ctx)


def _document_domain(ctx: _Context) -> None:
    _emit_fact(
        ctx, "REQUIREMENT", "There shall be the interface domain "
        f"{ctx.content.code(ctx.item['name'])}.")
    _add_text(ctx, "description", "DESCRIPTION")
    _add_default_links(ctx)
    _add_validations(ctx)


def _document_group(ctx: _Context) -> None:
    what = f"the interface group {ctx.content.code(ctx.item['name'])}"
    try:
        parent = ctx.item.parent("interface-ingroup")
        parent_kind = get_kind(parent)
        _emit_fact(
            ctx, "REQUIREMENT", f"The {ctx.mapper.get_link(parent)} "
            f"{parent_kind} shall contain {what}.")
    except IndexError:
        _emit_fact(ctx, "REQUIREMENT", f"There shall be {what}.")
    _add_brief(ctx)
    _add_text(ctx, "description", "DESCRIPTION")
    _add_default_links(ctx)
    _add_validations(ctx)


def _document_header_file(ctx: _Context) -> None:
    path = ctx.item["path"]
    formatted_path = ctx.content.code(f"<{path}>")
    container = ctx.item.parent('interface-placement')
    container_kind = get_kind(container)
    _emit_fact(
        ctx, "REQUIREMENT",
        f"The {ctx.mapper.get_link(container)} {container_kind} "
        f"shall provide the header file {formatted_path}.")
    _add_brief(ctx)
    _add_code_block(ctx.content, f"#include <{path}>")
    _add_default_links(ctx)
    _add_validations(ctx)


def _document_forward_declaration(ctx: _Context) -> None:
    container = ctx.item.parent('interface-placement')
    container_kind = get_kind(container)
    _emit_fact(
        ctx, "REQUIREMENT",
        f"The {ctx.mapper.get_link(container)} {container_kind} shall "
        "provide a forward declaration of "
        f"{ctx.mapper.get_link(ctx.item.parent('interface-target'))}.")
    _add_code_block(ctx.content, f"{forward_declaration(ctx.item)};")
    _add_default_links(ctx)
    _add_validations(ctx)


def _document_object(ctx: _Context) -> None:
    _document_unspecified(ctx)
    _add_brief(ctx)
    definition = _SPACE.sub(
        " ", _item_definition(ctx.item, ctx.code_mapper, ctx.spec.enabled_set))
    _add_code_block(ctx.content, f"extern {definition};")
    _add_text(ctx, "description", "DESCRIPTION")
    _add_text(ctx, "notes", "NOTES")


def _document_typedef(ctx: _Context) -> None:
    _document_unspecified(ctx)
    _add_brief(ctx)
    definition = _SPACE.sub(
        " ", _item_definition(ctx.item, ctx.code_mapper, ctx.spec.enabled_set))
    _add_code_block(ctx.content, f"typedef {definition};")
    _add_text(ctx, "description", "DESCRIPTION")
    _add_text(ctx, "notes", "NOTES")
    _add_default_links(ctx)
    _add_validations(ctx)


def _document_validation_by_analysis(ctx: _Context) -> None:
    _add_text(ctx, "text", "ANALYSIS")
    _add_validated_items(ctx)


def _document_validation_by_inspection(ctx: _Context) -> None:
    _add_text(ctx, "text", "INSPECTION")
    _add_validated_items(ctx)


def _document_validation_by_review_of_design(ctx: _Context) -> None:
    _add_text(ctx, "text", "REVIEW OF DESIGN")
    _add_validated_items(ctx)


def _flatten_text(value: GenericContent) -> str:
    """ Collapse a definition item's body to one line of text.

    A definition body may arrive as a string, a list of lines, or a Content
    (all of which iterate as lines); a table cell needs all of them as a
    single whitespace-normalised string.
    """
    if isinstance(value, str):
        lines: Iterable[str] = (value, )
    else:
        lines = value
    return " ".join(" ".join(lines).split())


class _DefinitionTable:
    """ Buffers a run of definition items (parameters, return values, error
    codes, structure members) and renders them as one aligned table instead
    of a docutils definition list (term on its own line, body indented
    below).  Intercepting ``add_definition_item`` this way needs no change
    to ``specware``, where that call comes from.

    Other attributes delegate to the wrapped content and flush first,
    except a handful of pure formatting helpers callers use to format the
    *next* item's term between two ``add_definition_item`` calls -- which
    would otherwise split one table into one per entry.
    """

    _PURE = frozenset({
        "cite",
        "code",
        "emphasize",
        "escape",
        "gap",
        "licenses",
        "path",
        "reference",
        "tab",
        "term",
    })

    def __init__(self, content: TextContent) -> None:
        self._content = content
        self._pending: list[tuple[str, str]] = []

    def __getattr__(self, name: str) -> Any:
        if name not in _DefinitionTable._PURE:
            self.flush()
        return getattr(self._content, name)

    def add_definition_item(self, name: GenericContent,
                            definition: GenericContent) -> None:
        """ Buffer the definition item instead of writing it immediately. """
        self._pending.append((_flatten_text(name), _flatten_text(definition)))

    def flush(self) -> None:
        """ Emit any buffered run of definition items as one table. """
        if not self._pending:
            return
        pending, self._pending = self._pending, []
        percent = term_column_percent(name for name, _ in pending)
        rows = [(_breakable_term(name), text) for name, text in pending]
        self._content.add_grid_table(rows,
                                     widths=[percent, 100 - percent],
                                     header_rows=0)


_ROLE_PREFIX = re.compile(r"^:[\w.+-]+(?::[\w.+-]+)*:")
_LINK_TARGET = re.compile(r"\s*<[^>]*>")
_BREAK_AFTER_SEPARATOR = re.compile(r"[_/-]+")
_BREAK_BEFORE_CAPITALS = re.compile(r"[A-Z]+")
# Longest run left unbroken before a last-resort fixed-stride break.
_LONGEST_UNBREAKABLE = 16


def _visible_text(text: str) -> str:
    """ Approximate the text a reader actually sees for a marked up term. """
    text = _ROLE_PREFIX.sub("", text)
    text = _LINK_TARGET.sub("", text)
    return text.replace("`", "").replace("*", "").strip()


def _add_breaks(text: str) -> str:
    """ Insert zero-width spaces at the safe break points of an identifier:
    after each run of ``_``, ``-`` or ``/``, and before each run of
    capitals, covering both ``some_long_parameter_name`` and
    ``RTEMS_INVALID_ADDRESS``.  A run with neither still has no break
    point, so as a last resort long runs break on a fixed stride. """
    text = _BREAK_BEFORE_CAPITALS.sub(lambda match: f"\u200b{match.group(0)}",
                                      text)
    text = _BREAK_AFTER_SEPARATOR.sub(lambda match: f"{match.group(0)}\u200b",
                                      text)
    while "\u200b\u200b" in text:
        text = text.replace("\u200b\u200b", "\u200b")
    text = text.strip("\u200b")
    parts: list[str] = []
    for run in text.split("\u200b"):
        while len(run) > _LONGEST_UNBREAKABLE:
            parts.append(run[:_LONGEST_UNBREAKABLE])
            run = run[_LONGEST_UNBREAKABLE:]
        parts.append(run)
    return "\u200b".join(part for part in parts if part)


def _breakable_term(term: str) -> str:
    """ Make a term wrappable, without breaking inside a ``<...>``
    reference target (that would change what it points at). """
    out: list[str] = []
    position = 0
    for match in _LINK_TARGET.finditer(term):
        out.append(_add_breaks(term[position:match.start()]))
        out.append(match.group(0))
        position = match.end()
    out.append(_add_breaks(term[position:]))
    return "".join(out)


# Text block width in em, for A4 with the document's margins:
# (210mm - 2*20mm) / 11pt.
_TEXT_WIDTH_EM = 44.0
# Per-character advance widths in em, approximating the body face (capitals
# run about half again as wide as lowercase).
_EM_UPPER = 0.72
_EM_LOWER = 0.50
_EM_OTHER = 0.55
_EM_PADDING = 0.6  # breathing room so a term isn't flush against the edge
_TERM_MIN_PERCENT = 10  # floor: two-letter names still read as a column
_TERM_MAX_PERCENT = 38  # ceiling: one long name can't squeeze descriptions


def _em_width(text: str) -> float:
    """ Approximate the rendered width of a term, in em. """
    total = 0.0
    for char in text:
        if char.isupper() or char.isdigit():
            total += _EM_UPPER
        elif char.islower():
            total += _EM_LOWER
        else:
            total += _EM_OTHER
    return total


def term_column_percent(terms: Iterable[str]) -> int:
    """ Width for a term column, sized to the longest term it holds. """
    widest = max((_em_width(_visible_text(term)) for term in terms),
                 default=0.0)
    percent = int(100.0 * (widest + _EM_PADDING) / _TEXT_WIDTH_EM) + 1
    return min(max(percent, _TERM_MIN_PERCENT), _TERM_MAX_PERCENT)


# One fixed label column for the whole document, unlike a parameter table's
# per-item fit: sizing it per item would make the column jitter.  26% fits
# the labels an item commonly carries, measured against the widest of them,
# "Interface placement"; a rarer, wider one wraps at its space instead
# (see the nohyphenation test in _FACT_LABEL_ROLE_LATEX below).
_FACT_LABEL_PERCENT = 26

# TitleColor is Sphinx's own heading colour, so the label reads as part of
# the document's existing heading language.
_FACT_LABEL_ROLE = "factlabel"

# \providecommand makes this styling only -- \DUrole falls back to plain
# text if \DUrole<name> is undefined, and project.sty can still override
# it.  \ifcsname tests for TitleColor and the nohyphenation language rather
# than assuming either exists.
_FACT_LABEL_ROLE_LATEX = [
    r"\providecommand{\DUrolefactlabel}[1]{{\sffamily\bfseries%",
    r"  \ifcsname color@TitleColor\endcsname\color{TitleColor}\fi%",
    r"  \ifcsname l@nohyphenation\endcsname%",
    r"    \language\csname l@nohyphenation\endcsname%",
    r"  \fi%",
    r"  #1}}",
]


def _declare_fact_label_role(content: TextContent) -> None:
    """ Declare and define the facts table's styled label role.

    A role must be declared in the same file as its uses; a document is
    assembled from several blocks that may land in different files, so the
    caller declares this once per block rather than once per document.
    """
    content.add(f".. role:: {_FACT_LABEL_ROLE}")
    with content.directive("raw", "latex"):
        content.add(_FACT_LABEL_ROLE_LATEX)


def _add_facts_table(content: TextContent, details: list[tuple[str,
                                                               str]]) -> None:
    """ Render an item's one-line facts (requirement, group membership,
    interface placement, validation, ...) as one aligned table instead of a
    heading and paragraph each. """
    rows = [(f":{_FACT_LABEL_ROLE}:`{label.capitalize()}`", sentence)
            for label, sentence in details]
    content.add_grid_table(
        rows,
        widths=[_FACT_LABEL_PERCENT, 100 - _FACT_LABEL_PERCENT],
        header_rows=0)


_ITEM_DOCUMENTER = {
    "constraint": _document_constraint,
    "glossary/group": _document_requirement,
    "glossary/term": _document_requirement,
    "interface/appl-config-group": _document_acfg_group,
    "interface/appl-config-option/feature": _document_acfg_option,
    "interface/appl-config-option/feature-enable": _document_acfg_option,
    "interface/appl-config-option/initializer": _document_acfg_option,
    "interface/appl-config-option/integer": _document_acfg_option,
    "interface/define": _document_define,
    "interface/domain": _document_domain,
    "interface/enum": _document_enumeration,
    "interface/enumerator": _document_enumerator,
    "interface/forward-declaration": _document_forward_declaration,
    "interface/function": _document_directive,
    "interface/group": _document_group,
    "interface/header-file": _document_header_file,
    "interface/macro": _document_directive,
    "interface/register-block": _document_register_block,
    "interface/struct": _document_compound,
    "interface/typedef": _document_typedef,
    "interface/union": _document_compound,
    "interface/unspecified-define": _document_unspecified_define,
    "interface/unspecified-enum": _document_unspecified_type,
    "interface/unspecified-enumerator": _document_unspecified_enumerator,
    "interface/unspecified-function": _document_unspecified_function,
    "interface/unspecified-group": _document_unspecified_group,
    "interface/unspecified-header-file": _document_header_file,
    "interface/unspecified-macro": _document_unspecified_function,
    "interface/unspecified-object": _document_unspecified_object,
    "interface/unspecified-struct": _document_unspecified_type,
    "interface/unspecified-typedef": _document_unspecified_typedef,
    "interface/unspecified-union": _document_unspecified_type,
    "interface/variable": _document_object,
    "memory-benchmark": _document_requirement,
    "requirement/functional/action": _document_action_requirement,
    "requirement/functional/capability": _document_requirement,
    "requirement/functional/interface-define-not-defined":
    _document_requirement,
    "requirement/functional/function": _document_requirement,
    "requirement/non-functional/design": _document_requirement,
    "requirement/non-functional/design-group": _document_requirement,
    "requirement/non-functional/design-target": _document_requirement,
    "requirement/non-functional/interface": _document_requirement,
    "requirement/non-functional/interface-requirement": _document_requirement,
    "requirement/non-functional/performance": _document_requirement,
    "requirement/non-functional/performance-runtime": _document_perf_runtime,
    "requirement/non-functional/performance-runtime-environment":
    _document_perf_runtime_env,
    "requirement/non-functional/quality": _document_requirement,
    "runtime-measurement-test": _document_requirement,
    "test-case": _document_requirement,
    "test-suite": _document_requirement,
    "validation/by-analysis": _document_validation_by_analysis,
    "validation/by-inspection": _document_validation_by_inspection,
    "validation/by-review-of-design": _document_validation_by_review_of_design,
}


def _status(item: Item) -> str:
    if not item.view["pre-qualified"]:
        return "not pre-qualified"
    if item.view["validated"]:
        return "validated"
    return "**not validated**"


def _validation_role(item: Item, role: str) -> str:
    if role.startswith("validation"):
        return role
    return f"{_status(item)} {role}"


def _validation_status(item: Item, role: str) -> str:
    if role.startswith("validation"):
        return role
    return f"{_status(item)} {role}"


def _is_include_enabled(enabled_set: EnabledSet, link: Link) -> bool:
    return is_enabled(enabled_set, link["enabled-by"])


def _add_validations(ctx: _Context) -> None:
    status = _status(ctx.item)
    kind = get_kind(ctx.item)
    validations = ctx.item.view["validation-dependencies"]
    if len(validations) == 0:
        _emit_fact(ctx, "VALIDATION", f"This {kind} is {status}.")
    elif len(validations) == 1:
        validation = validations[0]
        item_2 = ctx.item.cache[validation[0]]
        link = ctx.mapper.get_link(ctx.item.cache[validation[0]],
                                   document_key="test-plan")
        if ctx.item == item_2:
            _emit_fact(
                ctx, "VALIDATION",
                f"This {kind} is validated by a {validation[1]} "
                f"specified by {link}.")
        else:
            _emit_fact(
                ctx, "VALIDATION", f"This {status} {kind} is validated by "
                f"the {_validation_status(item_2, validation[1])} {link}.")
    else:
        ctx.content.add_rubric("VALIDATIONS:")
        items: list[str] = []
        for validation in validations:
            item_2 = ctx.item.cache[validation[0]]
            link = ctx.mapper.get_link(item_2, document_key="test-plan")
            items.append(
                f"{link} ({_validation_status(item_2, validation[1])})")
        ctx.content.add_list(
            items, f"The validation of this {status} {kind} "
            "depends on the following items:")


_VALIDATION_APPROACH = """The specification is a tree of specification items.
The root of the specification tree is ${/req/root:/spec}.  For each requirement
and interface a validation status can be determined.  An interface is *not
pre-qualified* if and only if at least one of the following conditions is met:

* *N1*: It has the ${/acfg/constraint/option-not-pre-qualified:/spec} usage
  constraint.

* *N2*: It has the ${/constraint/constant-not-pre-qualified:/spec} usage
  constraint.

* *N3*: It has the ${/constraint/directive-not-pre-qualified:/spec} usage
  constraint.

* *N4*: It is an interface container and all interfaces placed into this
  container are *not pre-qualified*.

An item is *validated* if and only if at least one of the following conditions
is met:

* *V1*: It has at least one not *not pre-qualified* refinement and all its
  refinements are *validated* or *not pre-qualified*.

* *V2*: It is a validation by test and at least one test result is available
  for this test and there are no unexpected test failures in the test results
  for this test.

* *V3*: It is a validation by analysis, inspection, or review of design.

* *V4*: It is a glossary term and its a member of a glossary group.

* *V5*: It is a constraint and it is a refinement of
  ${/req/usage-constraints:/spec}.

* *V6*: It is a design target and at least one test result is available for
  this target and there are no unexpected test failures in the test results for
  this target.

An item which is neither *validated* nor *not pre-qualified* is *not
validated*.  To check that all items are validated it is sufficient to check
the status of the root item: SPEC_ROOT.

Because of condition *V1* it is important to also consider the *not
pre-qualified* items in the validation procedure.  Some of the not
pre-qualified interfaces are fully specified with documentation entries.  They
are used to generate the ${/glossary/api:/term} header files and documentation.
In the generated API header files, there is a mix of pre-qualified and not
pre-qualified interfaces.  The not pre-qualified interfaces have no functional
specification and their implementation is removed from the pre-qualified
libraries.  For example, the use of a not pre-qualified function, would lead to
unresolved symbols at application link time.  In the user documentation, they
are marked as not pre-qualified through the corresponding usage constraint.

There are the following roles of refinement and validation items:

* *refinement*: The item is a requirement which refines a more general
  requirement.

* *group member*: The item is a member of an interface group.  Interfaces are
  organized in interface groups.  The interface groups define the software
  architecture and detailed design components.

* *interface placement*: The item is placed into an interface container.  For
  example, header files are interface containers.

* *interface function*: The item is a functional requirement which defines a
  function of an interface.

* *interface enumerator*: The item is an enumerator of an enumeration
  interface.

* *function implementation*: The item is the specification of a function used
  to implement interface functions.

* *validation by test*: The item is a test case which validates a requirement.
  The test case status is listed along the role in parenthesis where ``P``
  indicates a passed test case, ``F`` indicates an unexpectedly failed test
  case, and ``X`` indicates an expectedly failed test case.  For each test
  result, a status is listed.

* *validation by analysis*, *validation by inspection*, *validation by review
  of design*: The item is an analysis, inspection, or review of design which
  validates a requirement.

The table below lists for each requirement and interface related to the current
document, the validation status (*validated*, *not pre-qualified*, or *not
validated*), the associated refinement or validation items, and the role of the
refinement or validation item.  The table is a linearization of the
specification tree.  Parent items are on the left hand side.  Child items are
on the right hand side.  The table is ordered by the tree depth of parent items
starting with the root item.  Some items contain a functional or performance
specification along the associated validation test code.  These items show up
both as parent and child item in the same row where the child item has a
validation by test role.  The *not pre-qualified* interfaces (with the
exception of interface groups and containers) have no associated refinements or
validations, so the corresponding table entries are N/A."""


class SpecDocumentBuilder(DocumentBuilder):
    """ Builds documents presenting specification items. """

    def __init__(self, director: PackageBuildDirector, item: Item):
        super().__init__(director, item)
        spec = self.input("spec")
        assert isinstance(spec, RTEMSItemCache)
        self.spec = spec
        try:
            spec_compare_registry = self.input("spec-compare-registry")
            assert isinstance(spec_compare_registry, CompareSpecsRegistry)
        except KeyError:
            spec_compare_registry = None
        self.spec_compare_registry = spec_compare_registry
        # Contents the facts table's role has already been declared in
        # (identity, not equality -- there are only ever a handful).
        self._fact_label_role_declared: list[TextContent] = []
        my_type = self.item.type
        self.mapper.add_get_value(f"{my_type}:/validation-verification",
                                  self._validation_verification)

    def get_items_of_document(self) -> list[Item]:
        """ Get the items of this document. """
        return self.spec.get_related_interfaces_and_requirements()

    def add_item_changes(self, content: TextContent, item: Item) -> None:
        """ Add the item changes to the content. """
        spec_compare_registry = self.spec_compare_registry
        if spec_compare_registry is not None:
            content.add_rubric("CHANGES:")
            spec_compare_registry.add_item_changes(content, item.uid)

    def add_item(self, content: TextContent, item: Item) -> None:
        """ Add the item documentation to the content. """
        content.register_license_and_copyrights_of_item(item)
        if not any(seen is content for seen in self._fact_label_role_declared):
            self._fact_label_role_declared.append(content)
            _declare_fact_label_role(content)
        with self.mapper.scope(item):
            with content.section(item.spec, label=spec_label(item)):
                details: list[tuple[str, str]] = []
                item_content: Any = _DefinitionTable(content)
                _ITEM_DOCUMENTER[item.type](_Context(item_content, item,
                                                     self.mapper,
                                                     CodeMapper(item),
                                                     self.spec, self.file_path,
                                                     details))
                item_content.flush()
                self.add_item_changes(content, item)
                _add_facts_table(content, details)

    def _validation_status(self, item: Item) -> str:
        validation_status = item.view.get("validation-status", "N/A")
        if isinstance(validation_status, str):
            return validation_status
        validation_status = self.mapper.format_link(validation_status[0],
                                                    validation_status[1])
        return f"N/A ({validation_status})"

    def _add_validation_table(self, content: TextContent) -> None:
        """ Add the document item validation table to the content. """
        get_link = self.mapper.get_link
        item_cache = self.item.cache
        items = self.get_items_of_document()
        root_item = item_cache["/req/root"]
        if root_item in items:
            spec_root = ":ref:`spec:/req/root </req/root>`"
        else:
            spec_root = get_link(root_item)
        content.add(
            self.mapper.substitute(
                _VALIDATION_APPROACH.replace("SPEC_ROOT", spec_root)))
        rows: list[tuple[str | int,
                         ...]] = [("Interface / Requirement", "Status",
                                   "Refinement / Validation", "Role")]
        for item in sorted(items,
                           key=lambda x:
                           (len(x.view["order"]), x.view["order"])):
            req: str | int = f"_`{item.uid}`"
            status: str | int = _status(item)
            for validation in item.view["validation-dependencies"]:
                item_2 = item_cache[validation[0]]
                role = _validation_role(item_2, validation[1])
                if role == "validation by test":
                    role = (f"{role} "
                            f"{get_test_result_status(item_2, self.mapper)}")
                if item != item_2 and item_2 in items:
                    item_2_ref = f"`{item_2.uid}`_"
                elif item_2.type == "memory-benchmark":
                    item_2_ref = (f":ref:`{item_2.uid} "
                                  f"<BenchmarkSpec{item_2.ident}>`")
                else:
                    item_2_ref = get_link(item_2,
                                          document_key="test-plan").replace(
                                              "spec:", "")
                rows.append((req, status, item_2_ref, role))
                req = ROW_SPAN
                status = ROW_SPAN
            if isinstance(req, str) and req:
                rows.append(
                    (req, status, "N/A", self._validation_status(item)))
        content.add_grid_table(rows, [32, 14, 32, 22], font_size=-4)

    def _validation_verification(self, ctx: ItemGetValueContext) -> str:
        with self.section_content(ctx) as (content, _):
            self._add_validation_table(content)
            return content.join()
