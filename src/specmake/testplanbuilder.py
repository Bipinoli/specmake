# SPDX-License-Identifier: BSD-2-Clause
""" Builds test plans documents. """

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

from specitems import (Item, ItemGetValueContext, TextContent, to_camel_case)
from specware import gather_benchmarks_and_test_suites, gather_test_cases

from .pkgitems import PackageBuildDirector
from .linkhub import LinkHub, spec_label
from .specdocbuilder import SpecDocumentBuilder
from .testrunner import TestRunner


def _get_test_case_function(item: Item, ident: str) -> str:
    if item["test-header"] is None:
        return f"T_case_body_{ident}"
    return f"{ident}_Run"


class TestPlanBuilder(SpecDocumentBuilder):
    """ Builds a test plan document such as SVS or SUITP. """

    documents_items = True

    def __init__(self, director: PackageBuildDirector, item: Item):
        super().__init__(director, item)
        my_type = self.item.type
        self.mapper.add_get_value(f"{my_type}:/test-suites",
                                  self._get_test_suites)
        self.mapper.add_get_value(f"{my_type}:/test-cases",
                                  self._get_test_cases)
        self.mapper.add_get_value(f"{my_type}:/test-procedures",
                                  self._get_test_procedures)
        self.mapper.add_get_value(f"{my_type}:/other-validations",
                                  self._get_other_validations)
        self.mapper.add_get_value(f"{my_type}:/not-validated-by-test",
                                  self._get_not_validated_by_test)
        self._test_suites: list[Item] = []
        self._documenter = {
            "requirement/functional/action": self._document_action,
            "requirement/non-functional/performance-runtime":
            self._document_performance_runtime,
            "runtime-measurement-test":
            self._document_runtime_measurement_request,
            "test-case": self._document_test_case
        }

    def _get_link_hub(self) -> LinkHub:
        link_hub = self.input("link-hub")
        assert isinstance(link_hub, LinkHub)
        return link_hub

    def _gather_test_suites(self) -> list[Item]:
        test_suites = self._test_suites
        if not test_suites:
            for parent in self.inputs("test-suites"):
                gather_benchmarks_and_test_suites(parent.item, test_suites)
            test_suites.sort()
        return test_suites

    def _add_test_results(self, content: TextContent, kind: str,
                          item: Item) -> None:
        lines: list[str] = []
        for test_results in item.view.get("test-results", {}).values():
            for data in test_results:
                config_data = data["config"]
                target_data = config_data["target"]
                name = f"Target - {target_data['name']}"
                name = f"{name} / Configuration - {config_data['name']}"
                test_suite = data.get("test-suite", None)
                if test_suite is not None:
                    spec = item.cache[test_suite["uid"]].spec_2
                    name = f"{name} / Test suite - {spec}"
                lines.append(self.mapper.format_link(name, data["link"]))
        with content.topic("Test results"):
            content.add_list(lines,
                             f"For this {kind}, the following test results "
                             "are available:",
                             empty="There are no test results available.")

    def _add_test_suite(self, content: TextContent, item: Item) -> None:
        with content.section(item.spec, label=spec_label(item)):
            with content.section("General"):
                with content.topic("Description"):
                    self.wrap(content, item, item["test-brief"])
                    self.wrap(content, item, item["test-description"])
                if item.type != "memory-benchmark":
                    self._add_test_results(content, "test suite", item)
                self.add_item_changes(content, item)
            with content.section("Features to be tested"):
                gathered_test_cases: list[Item] = []
                gather_test_cases(item, gathered_test_cases)
                test_cases = sorted(set(gathered_test_cases))
                count = len(test_cases)
                if item.type == "memory-benchmark":
                    assert count == 0
                    content.add(
                        self.mapper.substitute("""Memory usage
benchmarks contain no test cases.  They are not executed on the
${/glossary/target:/term}.  Instead the generated ${/glossary/elf:/term} file
is analysed to gather the memory usage of sections and data structures.  The
analysis results are presented in the
${/pkg/deployment/doc-package-manual:/cite-long}."""))
                elif count == 1:
                    link = self.mapper.make_reference(test_cases[0])
                    content.add("The features to be tested are defined by "
                                f"the test case {link}.")
                elif count > 1:
                    prologue = ("The features to be tested are defined by "
                                "the following test cases:")
                    content.add_list([
                        self.mapper.make_reference(item_2)
                        for item_2 in test_cases
                    ], prologue)
                else:
                    content.add(
                        "The test suite contains no specified test cases.")
            with content.section("Approach refinements"):
                content.add(f"""There are no approach refinements
necessary.  The test suite is implemented in the file
{self._get_link_hub().get_file_sdd_link(item['test-target'], self.mapper)}.""")

    def _get_test_suites(self, _ctx: ItemGetValueContext) -> str:
        content = self.mapper.create_content(section_level=2)
        for item in self._gather_test_suites():
            with self.mapper.scope(item):
                self._add_test_suite(content, item)
        return content.join()

    def _add_test_case_validations(self, content: TextContent, item: Item,
                                   links: list[dict[str,
                                                    str]], what: str) -> bool:
        specs: list[str] = []
        for link in links:
            if link["role"] != "validation":
                continue
            item_2 = item.map(link["uid"])
            if not item_2.enabled:
                continue
            specs.append(self.mapper.get_link(item_2))
        count = len(specs)
        if count == 0:
            return True
        if count == 1:
            validations = specs[0]
        elif count == 2:
            validations = f"{specs[0]} and {specs[1]}"
        else:
            specs[-1] = f"and {specs[-1]}"
            validations = ", ".join(specs)
        content.add(f"{what} {validations}.")
        return False

    def _document_action(self, content: TextContent, link_hub: LinkHub,
                         item: Item, ident: str) -> None:
        test_case_function = _get_test_case_function(item, ident)
        content.add(f"""This test case validates all state transitions
specified by the action requirement {self.mapper.get_link(item)}.  The
transition map is validated by the function
{link_hub.get_function_sdd_link(test_case_function, self.mapper)}
contained in the file
{link_hub.get_file_sdd_link(item['test-target'], self.mapper)}.""")

    def _document_performance_runtime(self, content: TextContent,
                                      link_hub: LinkHub, item: Item,
                                      ident: str) -> None:
        context = item.parent("runtime-measurement-request")
        test_case_function = f"{ident}_Body"
        content.add(f"""This test case performs a performance runtime
measurement request which is carried out by
{self.mapper.make_reference(context)}.  It produces the runtime measurements
required by the runtime performance requirement {self.mapper.get_link(item)}.
It is implemented by the function
{link_hub.get_function_sdd_link(test_case_function, self.mapper)}
contained in the file
{link_hub.get_file_sdd_link(context['test-target'], self.mapper)}.""")

    def _document_runtime_measurement_request(self, content: TextContent,
                                              link_hub: LinkHub, item: Item,
                                              ident: str) -> None:
        self.wrap(content, item, item["test-brief"])
        content.gap = False
        content.add_list(
            sorted([
                self.mapper.make_reference(item_2)
                for item_2 in item.children("runtime-measurement-request")
            ]), "The following runtime measurement requests are carried out:")
        content.gap = self._add_test_case_validations(
            content, item, item["links"], "This test case validates")
        test_case_function = f"T_case_body_{ident}"
        content.add(f"""This test case is implemented by the
function {link_hub.get_function_sdd_link(test_case_function, self.mapper)}
contained in the file
{link_hub.get_file_sdd_link(item['test-target'], self.mapper)}.""")

    def _document_test_case(self, content: TextContent, link_hub: LinkHub,
                            item: Item, ident: str) -> None:
        self.wrap(content, item, item["test-brief"])
        self.wrap(content, item, item["test-description"])
        content.append("The following test case actions are carried out:")
        for index, action in enumerate(item["test-actions"]):
            with content.list_item(
                    self.mapper.substitute(action["action-brief"])):
                for check in action["checks"]:
                    with content.list_item(
                            self.mapper.substitute(check["brief"])):
                        content.gap = False
                        self._add_test_case_validations(
                            content, item, check["links"], "This validates")
                content.gap = bool(action["checks"])
                content.gap = self._add_test_case_validations(
                    content, item, action["links"], "This action validates")
                action_function = f"{ident}_Action_{index}"
                content.add(f"""This action is implemented by
the function {link_hub.get_function_sdd_link(action_function, self.mapper)}."""
                            )
        test_case_function = _get_test_case_function(item, ident)
        content.add(f"""This test case is implemented by the
function {link_hub.get_function_sdd_link(test_case_function, self.mapper)}
contained in the file
{link_hub.get_file_sdd_link(item['test-target'], self.mapper)}.""")

    def _add_test_suite_memberships(self, content: TextContent,
                                    item: Item) -> None:
        test_suites: list[str] = [
            self.mapper.make_reference(test_suite)
            for test_suite in item.parents("test-case")
        ]
        if not test_suites:
            return
        with content.topic("Test suites"):
            if len(test_suites) == 1:
                content.add("This test case is contained in the "
                            f"{test_suites[0]} test suite.")
            else:
                content.add_list(
                    test_suites, "This test case is contained in the "
                    "following test suites:")

    def _add_test_case(self, content: TextContent, item: Item) -> None:
        link_hub = self._get_link_hub()
        with content.section(item.spec, label=spec_label(item)):
            with content.section("General"):
                ident = to_camel_case(item.uid[1:])
                with content.topic("Description"):
                    self._documenter[item.type](content, link_hub, item, ident)
                self._add_test_suite_memberships(content, item)
                self._add_test_results(content, "test case", item)
                self.add_item_changes(content, item)
            with content.section("Input specifications"):
                content.add("""The test case starts execution in the
system state defined by the test suite runner and the test suite configuration.
All other inputs required by the test case are produced by the test case code
itself.""")
            with content.section("Output specifications"):
                content.add("For the output specifications see section "
                            ":ref:`TestPassFailCriteria`.")
            with content.section("Test pass - fail criteria"):
                content.add("For the test pass - fail criteria see section "
                            ":ref:`TestPassFailCriteria`.")
            with content.section("Environmental needs"):
                content.add("There are no specific environmental needs.")
            with content.section("Special procedure constraints"):
                content.add(
                    "There are no special procedure constraints applicable.")
            with content.section("Interface dependencies"):
                content.add(
                    "There are no specific interface dependencies present.")

    def _get_test_cases(self, _ctx: ItemGetValueContext) -> str:
        content = self.mapper.create_content(section_level=2)
        test_cases: list[Item] = []
        for item in self._gather_test_suites():
            gather_test_cases(item, test_cases)
        for item in sorted(set(test_cases)):
            with self.mapper.scope(item):
                self._add_test_case(content, item)
        return content.join()

    def _get_test_procedures(self, _ctx: ItemGetValueContext) -> str:
        test_runners: list[TestRunner] = []
        for item in self.component.item.parents("test-runner"):
            test_runner = self.director[item.uid]
            test_runners.append(test_runner)
        content = self.mapper.create_content(section_level=2)
        for test_runner in sorted(test_runners):
            label = spec_label(test_runner.item)
            with test_runner.component_scope(self.component):
                with content.section(test_runner["name"], label=label):
                    content.add(test_runner.describe())
        return content.join()

    def _add_other_validation(self, content: TextContent, method: str) -> None:
        items = self.spec.get_related_items_by_type(
            f"validation/by-{method.replace(' ', '-')}")
        if items:
            with content.section(f"Validation by {method}"):
                content.add(
                    "This section lists validation evidence obtained by "
                    f"using the {method} validation method.")
                for item in items:
                    self.add_item(content, item)

    def _get_other_validations(self, _ctx: ItemGetValueContext) -> str:
        content = self.mapper.create_content(section_level=2)
        for method in ("analysis", "inspection", "review of design"):
            self._add_other_validation(content, method)
        return content.join()

    def _get_not_validated_by_test(self, _ctx: ItemGetValueContext) -> str:
        content = self.mapper.create_content(section_level=2)
        types = [
            "validation/by-analysis", "validation/by-inspection",
            "validation/by-review-of-design"
        ]
        items: list[Item] = []
        for item in self.spec.get_related_items_by_type(types):
            items.extend(parent for parent in item.parents("validation"))
        content.add_list([
            self.mapper.get_link(item, document_key="default")
            for item in sorted(set(items))
        ], "The following items are not specifically validated by a test:")
        return content.join()
