# SPDX-License-Identifier: BSD-2-Clause
""" Tests for the srsbuilder module. """

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

from .util import build_document


def test_srsbuilder(caplog, tmpdir):
    package, text = build_document(
        caplog, tmpdir, "doc-ts-srs",
        ["aggregate-test-results", "link-hub", "dummy-images", "ts-srs"])
    assert text == r""".. SPDX-License-Identifier: CC-BY-SA-4.0

.. Copyright (C) 2026 embedded brains GmbH & Co. KG

.. validation-verification begin
The specification is a tree of specification items.
The root of the specification tree is `spec:/​req/​root </pkg/doc-ts-srs/html/requirements.html#specreqroot>`__.  For each requirement
and interface a validation status can be determined.  An interface is *not
pre-qualified* if and only if at least one of the following conditions is met:

* *N1*: It has the `spec:/​acfg/​constraint/​option-not-pre-qualified </pkg/doc-ts-srs/html/requirements.html#specacfgconstraintoptionnotprequalified>`__ usage
  constraint.

* *N2*: It has the ``spec:/​constraint/​constant-not-pre-qualified`` usage
  constraint.

* *N3*: It has the ``spec:/​constraint/​directive-not-pre-qualified`` usage
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
  `spec:/​req/​usage-constraints </pkg/doc-ts-srs/html/requirements.html#specrequsageconstraints>`__.

* *V6*: It is a design target and at least one test result is available for
  this target and there are no unexpected test failures in the test results for
  this target.

An item which is neither *validated* nor *not pre-qualified* is *not
validated*.  To check that all items are validated it is sufficient to check
the status of the root item: :ref:`spec:/req/root </req/root>`.

Because of condition *V1* it is important to also consider the *not
pre-qualified* items in the validation procedure.  Some of the not
pre-qualified interfaces are fully specified with documentation entries.  They
are used to generate the :term:`API` header files and documentation.
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
validations, so the corresponding table entries are N/A.

.. raw:: latex

    \begin{tiny}

.. table::
    :class: longtable
    :widths: 32,14,32,22

    +-+-+-+-+
    | Interface / Requirement | Status | Refinement / Validation | Role |
    +=+=+=+=+
    | _`/req/root` | **not validated** | `/glossary/group`_ | validated refinement |
    + + +-+-+
    | | | `/​req/​api </pkg/doc-ts-icd/html/requirements-and-design.html#specreqapi>`__ | **not validated** refinement |
    + + +-+-+
    | | | `/req/glossary`_ | **not validated** refinement |
    + + +-+-+
    | | | `/req/perf-runtime`_ | **not validated** refinement |
    + + +-+-+
    | | | `/req/usage-constraints`_ | validated refinement |
    + + +-+-+
    | | | `Domain </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdomain>`__ | **not validated** refinement |
    + + +-+-+
    | | | `Something Configuration </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroupacfg>`__ | not pre-qualified refinement |
    + + +-+-+
    | | | `/rtems/req/group`_ | **not validated** refinement |
    + + +-+-+
    | | | `/rtems/req/group-no-identifier`_ | **not validated** refinement |
    + + +-+-+
    | | | `/rtems/target-a`_ | **not validated** refinement |
    + + +-+-+
    | | | `/​score/​cpu/​val/​perf </pkg/doc-djf-svs/html/test-case-specification.html#specscorecpuvalperf>`__ | validation by test (`P </a-build-config-key-testsuites-performance-no-clock-0.html#abuildconfigkeytestsuitesperformancenoclock0scorecpuvalperf>`__) |
    + + +-+-+
    | | | `/testsuites/unit`_ | **not validated** refinement |
    + + +-+-+
    | | | `/testsuites/validation`_ | **not validated** refinement |
    +-+-+-+-+
    | _`/glossary/group` | validated | N/A | N/A |
    +-+-+-+-+
    | _`/req/glossary` | **not validated** | N/A | N/A |
    +-+-+-+-+
    | _`/req/perf-runtime` | **not validated** | `/req/perf-runtime-environment`_ | **not validated** refinement |
    +-+-+-+-+
    | _`/req/usage-constraints` | validated | `/​acfg/​constraint/​option-not-pre-qualified </pkg/doc-ts-srs/html/requirements.html#specacfgconstraintoptionnotprequalified>`__ | validated refinement |
    +-+-+-+-+
    | _`/rtems/req/group` | **not validated** | `/​rtems/​val/​test-case </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsvaltestcase>`__ | validation by test **no test results** |
    + + +-+-+
    | | | `/​rtems/​val/​test-case-run </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsvaltestcaserun>`__ | validation by test **no test results** |
    +-+-+-+-+
    | _`/rtems/req/group-no-identifier` | **not validated** | N/A | N/A |
    +-+-+-+-+
    | _`/rtems/target-a` | **not validated** | N/A | N/A (`at least one unexpected test failure <reports.html#a>`__) |
    +-+-+-+-+
    | _`/testsuites/unit` | **not validated** | `/​testsuites/​unit-0 </pkg/doc-djf-suitp/html/test-design.html#spectestsuitesunit0>`__ | **not validated** refinement |
    +-+-+-+-+
    | _`/testsuites/validation` | **not validated** | :ref:`/rtems/val/mem-basic <BenchmarkSpecRtemsValMemBasic>` | validated refinement |
    + + +-+-+
    | | | `/​testsuites/​performance-no-clock-0 </pkg/doc-djf-svs/html/test-design.html#spectestsuitesperformancenoclock0>`__ | **not validated** refinement |
    + + +-+-+
    | | | `/​testsuites/​test-suite-empty </pkg/doc-djf-svs/html/test-design.html#spectestsuitestestsuiteempty>`__ | **not validated** refinement |
    + + +-+-+
    | | | `/​testsuites/​test-suite-pass </pkg/doc-djf-svs/html/test-design.html#spectestsuitestestsuitepass>`__ | validated refinement |
    + + +-+-+
    | | | `/​testsuites/​test-suite-xfail </pkg/doc-djf-svs/html/test-design.html#spectestsuitestestsuitexfail>`__ | validated refinement |
    + + +-+-+
    | | | `/testsuites/validation-refinement`_ | **not validated** refinement |
    +-+-+-+-+
    | _`/req/perf-runtime-environment` | **not validated** | `/req/perf-runtime-environment-dirty-cache`_ | **not validated** refinement |
    + + +-+-+
    | | | `/req/perf-runtime-environment-full-cache`_ | **not validated** refinement |
    + + +-+-+
    | | | `/req/perf-runtime-environment-hot-cache`_ | **not validated** refinement |
    + + +-+-+
    | | | `/req/perf-runtime-environment-load`_ | **not validated** refinement |
    +-+-+-+-+
    | _`/testsuites/validation-refinement` | **not validated** | `/​testsuites/​test-suite-fail </pkg/doc-djf-svs/html/test-design.html#spectestsuitestestsuitefail>`__ | **not validated** refinement |
    +-+-+-+-+
    | _`/rtems/req/mem-basic` | validated | :ref:`/rtems/val/mem-basic <BenchmarkSpecRtemsValMemBasic>` | validation by inspection |
    +-+-+-+-+
    | _`/rtems/req/perf` | **not validated** | `/​rtems/​req/​perf </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsreqperf>`__ | validation by test (`F </a-build-config-key-testsuites-performance-no-clock-0.html#abuildconfigkeytestsuitesperformancenoclock0rtemsreqperf>`__) |
    + + +-+-+
    | | | `/​rtems/​val/​by-inspection </pkg/doc-djf-svs/html/validation-other.html#specrtemsvalbyinspection>`__ | validation by inspection |
    + + +-+-+
    | | | `/​rtems/​val/​by-review-of-design </pkg/doc-djf-svs/html/validation-other.html#specrtemsvalbyreviewofdesign>`__ | validation by review of design |
    + + +-+-+
    | | | `/​rtems/​val/​test-case </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsvaltestcase>`__ | validation by test **no test results** |
    + + +-+-+
    | | | `/​rtems/​val/​test-case-run </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsvaltestcaserun>`__ | validation by test **no test results** |
    +-+-+-+-+
    | _`/rtems/req/perf-no-results` | **not validated** | `/​rtems/​req/​perf-no-results </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsreqperfnoresults>`__ | validation by test **no test results** |
    +-+-+-+-+
    | _`/req/perf-runtime-environment-dirty-cache` | **not validated** | N/A | N/A |
    +-+-+-+-+
    | _`/req/perf-runtime-environment-full-cache` | **not validated** | N/A | N/A |
    +-+-+-+-+
    | _`/req/perf-runtime-environment-hot-cache` | **not validated** | N/A | N/A |
    +-+-+-+-+
    | _`/req/perf-runtime-environment-load` | **not validated** | N/A | N/A |
    +-+-+-+-+
    | _`/rtems/req/define-not-defined` | **not validated** | N/A | N/A |
    +-+-+-+-+
    | _`/rtems/req/func` | **not validated** | `/​rtems/​val/​test-case </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsvaltestcase>`__ | validation by test **no test results** |
    + + +-+-+
    | | | `/​rtems/​val/​test-case-run </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsvaltestcaserun>`__ | validation by test **no test results** |
    +-+-+-+-+
    | _`/rtems/req/action` | **not validated** | `/​rtems/​req/​action </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsreqaction>`__ | validation by test **no test results** |
    +-+-+-+-+
    | _`/rtems/req/action-2` | **not validated** | `/​rtems/​req/​action-2 </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsreqaction2>`__ | validation by test **no test results** |
    +-+-+-+-+

.. raw:: latex

    \end{tiny}
.. validation-verification end

.. srs-requirements begin
.. include:: ../include/abbreviations.rst

.. _Requirements:

Requirements
############

.. _RequirementsFunctionalRequirements:

Functional requirements
***********************

.. role:: factlabel

.. raw:: latex

    \providecommand{\DUrolefactlabel}[1]{{\sffamily\bfseries%
      \ifcsname color@TitleColor\endcsname\color{TitleColor}\fi%
      \ifcsname l@nohyphenation\endcsname%
        \language\csname l@nohyphenation\endcsname%
      \fi%
      #1}}

.. _SpecRtemsReqAction:

spec:/rtems/req/action
======================

.. rubric:: REQUIREMENT:

The function shall be specified by the following state transition map which
defines for each feasible pre-condition state variant the resulting
post-condition state variant produced by the trigger action.

.. rubric:: PRE-CONDITIONS:

.. _SpecRtemsReqActionPreValue:

.. topic:: Pre-Condition - Value

    The *Value* pre-condition has the
    following states:

.. table::
    :class: longtable
    :widths: 11,89

    +-+-+
    | Zero | While the parameter value is equal to zero. |
    +-+-+
    | Non​Zero | While the parameter value is not equal to zero. |
    +-+-+

.. rubric:: TRIGGER ACTION:

When the `UnspecFunction()
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecfunction>`__
directive is called.

.. rubric:: POST-CONDITIONS:

.. _SpecRtemsReqActionPostResult:

.. topic:: Post-Condition - Result

    The *Result* post-condition has the
    following states:

.. table::
    :class: longtable
    :widths: 15,85

    +-+-+
    | Zero | The return value of `UnspecFunction() </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecfunction>`__ shall be equal to zero. |
    +-+-+
    | Last​Bit​Set | The return value of `UnspecFunction() </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecfunction>`__ shall be equal to the index of the most-significant bit set in the parameter value. |
    +-+-+

.. rubric:: TRANSITION MAP:

For each of the resulting post-condition state variants below, the set of
producing pre-condition variants is listed.

.. raw:: latex

    \begin{small}

.. table::
    :class: longtable
    :widths: 50,50

    +-+-+
    | Pre-Conditions | Post-Conditions |
    +-+-+
    | :ref:`Value <SpecRtemsReqActionPreValue>` | :ref:`Result <SpecRtemsReqActionPostResult>` |
    +=+=+
    | Zero | Zero |
    +-+-+
    | Non​Zero | Last​Bit​Set |
    +-+-+

.. raw:: latex

    \end{small}

.. rubric:: CHANGES:

There are no changes since Name v1.

.. table::
    :class: longtable
    :widths: 26,74

    +-+-+
    | :factlabel:`Interface function` | This action requirement specifies the function of the directive `UnspecFunction() </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecfunction>`__. |
    +-+-+
    | :factlabel:`Validation` | This action requirement is validated by a validation by test specified by `spec:/​rtems/​req/​action </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsreqaction>`__. |
    +-+-+

.. _SpecRtemsReqAction2:

spec:/rtems/req/action-2
========================

.. rubric:: REQUIREMENT:

The function shall be specified by the following state transition map which
defines for each feasible pre-condition state variant the resulting
post-condition state variant produced by the trigger action.

.. rubric:: INTERFACE FUNCTIONS:

This action requirement specifies the function of the following items:

- `blub()
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsiffunc>`__

- `UnspecFunction()
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecfunction>`__

.. rubric:: PRE-CONDITIONS:

.. _SpecRtemsReqAction2PreA:

.. topic:: Pre-Condition - A

    The *A* pre-condition has the
    following states:

.. table::
    :class: longtable
    :widths: 10,90

    +-+-+
    | AA | AA |
    +-+-+
    | AB | AB |
    +-+-+

.. _SpecRtemsReqAction2PreB:

.. topic:: Pre-Condition - B

    The *B* pre-condition has the
    following states:

.. table::
    :class: longtable
    :widths: 10,90

    +-+-+
    | BA | BA |
    +-+-+
    | BB | BB |
    +-+-+

.. _SpecRtemsReqAction2PreC:

.. topic:: Pre-Condition - C

    The *C* pre-condition has the
    following states:

.. table::
    :class: longtable
    :widths: 10,90

    +-+-+
    | CA | CA |
    +-+-+
    | CB | CB |
    +-+-+
    | CC | CC |
    +-+-+

.. rubric:: TRIGGER ACTION:

When the directive is called.

.. rubric:: POST-CONDITIONS:

.. _SpecRtemsReqAction2PostX:

.. topic:: Post-Condition - X

    The *X* post-condition has the
    following states:

.. table::
    :class: longtable
    :widths: 10,90

    +-+-+
    | XA | XA |
    +-+-+
    | XB | XB |
    +-+-+

.. _SpecRtemsReqAction2PostY:

.. topic:: Post-Condition - Y

    The *Y* post-condition has the
    following states:

.. table::
    :class: longtable
    :widths: 10,90

    +-+-+
    | YA | YA |
    +-+-+
    | YB | YB |
    +-+-+

.. rubric:: TRANSITION MAP:

For each of the resulting post-condition state variants below, the set of
producing pre-condition variants is listed.

.. raw:: latex

    \begin{small}

.. table::
    :class: longtable
    :widths: 20,20,20,20,20

    +-+-+-+-+-+
    | Pre-Conditions | Post-Conditions |
    +-+-+-+-+-+
    | :ref:`A <SpecRtemsReqAction2PreA>` | :ref:`B <SpecRtemsReqAction2PreB>` | :ref:`C <SpecRtemsReqAction2PreC>` | :ref:`X <SpecRtemsReqAction2PostX>` | :ref:`Y <SpecRtemsReqAction2PostY>` |
    +=+=+=+=+=+
    | AA | N/​A | CA, CB, CC | XA | YA |
    +-+-+-+-+-+
    | AB | N/​A | CA, CB, CC | XB | N/​A |
    +-+-+-+-+-+
    | AA | BA | CA, CC | :ref:`S <SpecRtemsReqAction2SkipS>` |
    +-+-+-+-+-+

.. raw:: latex

    \end{small}

.. rubric:: INFEASIBLE PRE-CONDITION VARIANTS:

.. _SpecRtemsReqAction2SkipS:

*S*: Skip Therefore, the following pre-condition state variants are infeasible:

    * :ref:`A <SpecRtemsReqAction2PreA>` = AA, :ref:`B <SpecRtemsReqAction2PreB>` = BA, :ref:`C <SpecRtemsReqAction2PreC>` = {CA, CC}

.. rubric:: CHANGES:

There are no changes since Name v1.

.. table::
    :class: longtable
    :widths: 26,74

    +-+-+
    | :factlabel:`Validation` | This action requirement is validated by a validation by test specified by `spec:/​rtems/​req/​action-2 </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsreqaction2>`__. |
    +-+-+

.. _SpecRtemsReqDefineNotDefined:

spec:/rtems/req/define-not-defined
==================================

.. rubric:: REQUIREMENT:

The define shall not be defined.

.. rubric:: CHANGES:

There are no changes since Name v1.

.. table::
    :class: longtable
    :widths: 26,74

    +-+-+
    | :factlabel:`Interface function` | This interface define requirement specifies the function of the define `DEFINE_NOT_DEFINED </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdefinenotdefined>`__. |
    +-+-+
    | :factlabel:`Validation` | This interface define requirement is **not validated**. |
    +-+-+

.. _SpecRtemsReqFunc:

spec:/rtems/req/func
====================

.. rubric:: REQUIREMENT:

Text.

.. rubric:: VALIDATIONS:

The validation of this **not validated** function requirement depends on the
following items:

- `spec:/​rtems/​val/​test-case
  </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsvaltestcase>`__
  (validation by test)

- `spec:/​rtems/​val/​test-case-run
  </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsvaltestcaserun>`__
  (validation by test)

.. rubric:: CHANGES:

There are no changes since Name v1.

.. table::
    :class: longtable
    :widths: 26,74

    +-+-+
    | :factlabel:`Interface function` | This function requirement specifies the function of the directive `blub() </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsiffunc>`__. |
    +-+-+

.. _RequirementsPerformanceRequirements:

Performance requirements
************************

.. _SpecReqPerfRuntime:

spec:/req/perf-runtime
======================

.. rubric:: REQUIREMENT:

The runtime of interface functions shall be measured.

.. rubric:: REFINEMENTS:

This performance requirement refines the design requirement `spec:/​req/​root
</pkg/doc-ts-srs/html/requirements.html#specreqroot>`__.

This performance requirement is refined by performance requirement
`spec:/​req/​perf-runtime-environment
</pkg/doc-ts-srs/html/requirements.html#specreqperfruntimeenvironment>`__.

.. rubric:: CHANGES:

There are no changes since Name v1.

.. table::
    :class: longtable
    :widths: 26,74

    +-+-+
    | :factlabel:`Validation` | This **not validated** performance requirement is validated by the **not validated** refinement `spec:/​req/​perf-runtime-environment </pkg/doc-ts-srs/html/requirements.html#specreqperfruntimeenvironment>`__. |
    +-+-+

.. _SpecReqPerfRuntimeEnvironment:

spec:/req/perf-runtime-environment
==================================

.. rubric:: REQUIREMENT:

The runtime measurement shall be done in different runtime measurement
environments.

.. rubric:: RATIONALE:

The state of the memory system on the :term:`target` has usually a significant
influence on timings.

.. rubric:: REFINEMENTS:

This performance requirement refines the performance requirement
`spec:/​req/​perf-runtime
</pkg/doc-ts-srs/html/requirements.html#specreqperfruntime>`__.

This performance requirement is refined by the following items:

- `spec:/​req/​perf-runtime-environment-dirty-cache
  </pkg/doc-ts-srs/html/requirements.html#specreqperfruntimeenvironmentdirtycache>`__

- `spec:/​req/​perf-runtime-environment-full-cache
  </pkg/doc-ts-srs/html/requirements.html#specreqperfruntimeenvironmentfullcache>`__

- `spec:/​req/​perf-runtime-environment-hot-cache
  </pkg/doc-ts-srs/html/requirements.html#specreqperfruntimeenvironmenthotcache>`__

- `spec:/​req/​perf-runtime-environment-load
  </pkg/doc-ts-srs/html/requirements.html#specreqperfruntimeenvironmentload>`__

.. rubric:: VALIDATIONS:

The validation of this **not validated** performance requirement depends on the
following items:

- `spec:/​req/​perf-runtime-environment-dirty-cache
  </pkg/doc-ts-srs/html/requirements.html#specreqperfruntimeenvironmentdirtycache>`__
  (**not validated** refinement)

- `spec:/​req/​perf-runtime-environment-full-cache
  </pkg/doc-ts-srs/html/requirements.html#specreqperfruntimeenvironmentfullcache>`__
  (**not validated** refinement)

- `spec:/​req/​perf-runtime-environment-hot-cache
  </pkg/doc-ts-srs/html/requirements.html#specreqperfruntimeenvironmenthotcache>`__
  (**not validated** refinement)

- `spec:/​req/​perf-runtime-environment-load
  </pkg/doc-ts-srs/html/requirements.html#specreqperfruntimeenvironmentload>`__
  (**not validated** refinement)

.. rubric:: CHANGES:

There are no changes since Name v1.

.. _SpecReqPerfRuntimeEnvironmentDirtyCache:

spec:/req/perf-runtime-environment-dirty-cache
==============================================

.. rubric:: REQUIREMENT:

A :term:`target` state in which the caches are fully loaded with dirty data and
instructions unrelated to the measured code section shall be a runtime
measurement environment.

.. rubric:: RATIONALE:

This runtime measurement environment is used to measure the runtime of code
sections while data and instructions of the code section have to be loaded from
main memory and the loaded data has to wait for the write out of dirty data.

.. rubric:: NAME:

The RTEMS Test Framework name of this runtime measurement environment is
``DirtyCache``.

.. rubric:: CHANGES:

There are no changes since Name v1.

.. table::
    :class: longtable
    :widths: 26,74

    +-+-+
    | :factlabel:`Refinement` | This runtime performance measurement environment refines the performance requirement `spec:/​req/​perf-runtime-environment </pkg/doc-ts-srs/html/requirements.html#specreqperfruntimeenvironment>`__. |
    +-+-+
    | :factlabel:`Validation` | This runtime performance measurement environment is **not validated**. |
    +-+-+

.. _SpecReqPerfRuntimeEnvironmentFullCache:

spec:/req/perf-runtime-environment-full-cache
=============================================

.. rubric:: REQUIREMENT:

A :term:`target` state in which the caches are fully loaded with valid data and
instructions unrelated to the measured code section shall be a runtime
measurement environment.

.. rubric:: RATIONALE:

This runtime measurement environment is used to measure the runtime of code
sections while data and instructions of the code section have to be loaded from
main memory without having to wait for the write out of dirty data.

.. rubric:: NAME:

The RTEMS Test Framework name of this runtime measurement environment is
``FullCache``.

.. rubric:: CHANGES:

There are no changes since Name v1.

.. table::
    :class: longtable
    :widths: 26,74

    +-+-+
    | :factlabel:`Refinement` | This runtime performance measurement environment refines the performance requirement `spec:/​req/​perf-runtime-environment </pkg/doc-ts-srs/html/requirements.html#specreqperfruntimeenvironment>`__. |
    +-+-+
    | :factlabel:`Validation` | This runtime performance measurement environment is **not validated**. |
    +-+-+

.. _SpecReqPerfRuntimeEnvironmentHotCache:

spec:/req/perf-runtime-environment-hot-cache
============================================

.. rubric:: REQUIREMENT:

A :term:`target` state in which the caches are fully loaded with data and
instructions related to the measured code section shall be a runtime
measurement environment.

.. rubric:: RATIONALE:

This runtime measurement environment is used to measure the runtime of code
sections while data and instructions of the code section are already in the
cache.  This should give a good estimate of best case conditions.

.. rubric:: NAME:

The RTEMS Test Framework name of this runtime measurement environment is
``HotCache``.

.. rubric:: CHANGES:

There are no changes since Name v1.

.. table::
    :class: longtable
    :widths: 26,74

    +-+-+
    | :factlabel:`Refinement` | This runtime performance measurement environment refines the performance requirement `spec:/​req/​perf-runtime-environment </pkg/doc-ts-srs/html/requirements.html#specreqperfruntimeenvironment>`__. |
    +-+-+
    | :factlabel:`Validation` | This runtime performance measurement environment is **not validated**. |
    +-+-+

.. _SpecReqPerfRuntimeEnvironmentLoad:

spec:/req/perf-runtime-environment-load
=======================================

.. rubric:: REQUIREMENT:

A :term:`target` state in which the caches are fully loaded with dirty data and
instructions unrelated to the measured code section and data bus load from
background tasks shall be a runtime measurement environment.

.. rubric:: RATIONALE:

This runtime measurement environment is intended to get close to worst case
execution conditions.

.. rubric:: NAME:

The RTEMS Test Framework name of this runtime measurement environment is
``Load``.

.. rubric:: CHANGES:

There are no changes since Name v1.

.. table::
    :class: longtable
    :widths: 26,74

    +-+-+
    | :factlabel:`Refinement` | This runtime performance measurement environment refines the performance requirement `spec:/​req/​perf-runtime-environment </pkg/doc-ts-srs/html/requirements.html#specreqperfruntimeenvironment>`__. |
    +-+-+
    | :factlabel:`Validation` | This runtime performance measurement environment is **not validated**. |
    +-+-+

.. _SpecRtemsReqPerf:

spec:/rtems/req/perf
====================

.. rubric:: REQUIREMENT:

Environment is ${ENVIRONMENT}, limit kind is ${LIMIT_KIND}, limit condition is
${LIMIT_CONDITION}, buffer count is 10, sample count is 100.

.. rubric:: RUNTIME PERFORMANCE LIMITS:

For the `spec:/​rtems/​target-a
</pkg/doc-ts-srs/html/requirements.html#specrtemstargeta>`__
target, the following runtime performance limits shall apply:

.. table::
    :class: longtable
    :widths: 25,25,50

    +-+-+-+
    | ${ENVIRONMENT} | ${LIMIT_KIND} | ${LIMIT_CONDITION} |
    +=+=+=+
    | :ref:`HotCache <SpecReqPerfRuntimeEnvironmentHotCache>` | Minimum | 298.000ns :math:`\leq` Minimum |
    + +-+-+
    | | Median | 298.000ns :math:`\leq` Median :math:`\leq` 1.192μs |
    + +-+-+
    | | Maximum | Maximum :math:`\leq` 1.192μs |
    +-+-+-+
    | :ref:`FullCache <SpecReqPerfRuntimeEnvironmentFullCache>` | Minimum | 275.000ns :math:`\leq` Minimum |
    + +-+-+
    | | Median | 275.000ns :math:`\leq` Median :math:`\leq` 475.000ns |
    + +-+-+
    | | Maximum | Maximum :math:`\leq` 475.000ns |
    +-+-+-+
    | :ref:`DirtyCache <SpecReqPerfRuntimeEnvironmentDirtyCache>` | Minimum | 588.600ns :math:`\leq` Minimum |
    + +-+-+
    | | Median | 602.100ns :math:`\leq` Median :math:`\leq` 10.312μs |
    + +-+-+
    | | Maximum | Maximum :math:`\leq` 12.728μs |
    +-+-+-+
    | :ref:`Load/1 <SpecReqPerfRuntimeEnvironmentLoad>` | Minimum | 583.200ns :math:`\leq` Minimum |
    + +-+-+
    | | Median | 618.300ns :math:`\leq` Median :math:`\leq` 15.080μs |
    + +-+-+
    | | Maximum | Maximum :math:`\leq` 0s |
    +-+-+-+

For the configuration ``Build Configuration Name``, the test case
`spec:/​score/​cpu/​val/​perf
</a-build-config-key-testsuites-performance-no-clock-0.html#abuildconfigkeytestsuitesperformancenoclock0scorecpuvalperf>`__
of the test suite `spec:/​testsuites/​performance-no-clock-0
</a-build-config-key-testsuites-performance-no-clock-0.html#abuildconfigkeytestsuitesperformancenoclock0>`__
reported the following `runtime performance measurements
</a-build-config-key-testsuites-performance-no-clock-0.html#abuildconfigkeytestsuitesperformancenoclock0rtemsreqperf>`__:

.. image:: ../../../perf-images/a-build-config-key-rtems-req-perf.*
    :align: center
    :width: 50%

.. rubric:: VALIDATIONS:

The validation of this **not validated** runtime performance requirement
depends on the following items:

- `spec:/​rtems/​req/​perf
  </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsreqperf>`__
  (validation by test)

- `spec:/​rtems/​val/​by-inspection
  </pkg/doc-djf-svs/html/validation-other.html#specrtemsvalbyinspection>`__
  (validation by inspection)

- `spec:/​rtems/​val/​by-review-of-design
  </pkg/doc-djf-svs/html/validation-other.html#specrtemsvalbyreviewofdesign>`__
  (validation by review of design)

- `spec:/​rtems/​val/​test-case
  </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsvaltestcase>`__
  (validation by test)

- `spec:/​rtems/​val/​test-case-run
  </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsvaltestcaserun>`__
  (validation by test)

.. rubric:: CHANGES:

There are no changes since Name v1.

.. table::
    :class: longtable
    :widths: 26,74

    +-+-+
    | :factlabel:`Refinement` | This runtime performance requirement refines the interface group `Blub </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__. |
    +-+-+

.. _SpecRtemsReqPerfNoResults:

spec:/rtems/req/perf-no-results
===============================

.. rubric:: REQUIREMENT:

Text.

.. rubric:: RUNTIME PERFORMANCE LIMITS:

For the `spec:/​rtems/​target-a
</pkg/doc-ts-srs/html/requirements.html#specrtemstargeta>`__
target, the following runtime performance limits shall apply:

.. table::
    :class: longtable
    :widths: 25,25,50

    +-+-+-+
    | ${ENVIRONMENT} | ${LIMIT_KIND} | ${LIMIT_CONDITION} |
    +=+=+=+
    | :ref:`HotCache <SpecReqPerfRuntimeEnvironmentHotCache>` | Minimum | 298.000ns :math:`\leq` Minimum |
    + +-+-+
    | | Median | 298.000ns :math:`\leq` Median :math:`\leq` 1.192μs |
    + +-+-+
    | | Maximum | Maximum :math:`\leq` 1.192μs |
    +-+-+-+
    | :ref:`FullCache <SpecReqPerfRuntimeEnvironmentFullCache>` | Minimum | 275.000ns :math:`\leq` Minimum |
    + +-+-+
    | | Median | 275.000ns :math:`\leq` Median :math:`\leq` 475.000ns |
    + +-+-+
    | | Maximum | Maximum :math:`\leq` 475.000ns |
    +-+-+-+
    | :ref:`DirtyCache <SpecReqPerfRuntimeEnvironmentDirtyCache>` | Minimum | 588.600ns :math:`\leq` Minimum |
    + +-+-+
    | | Median | 602.100ns :math:`\leq` Median :math:`\leq` 10.312μs |
    + +-+-+
    | | Maximum | Maximum :math:`\leq` 12.728μs |
    +-+-+-+
    | :ref:`Load/1 <SpecReqPerfRuntimeEnvironmentLoad>` | Minimum | 583.200ns :math:`\leq` Minimum |
    + +-+-+
    | | Median | 618.300ns :math:`\leq` Median :math:`\leq` 15.080μs |
    + +-+-+
    | | Maximum | Maximum :math:`\leq` 0s |
    +-+-+-+

.. warning::

    There are no runtime measurements available for this requirement.

.. rubric:: CHANGES:

There are no changes since Name v1.

.. table::
    :class: longtable
    :widths: 26,74

    +-+-+
    | :factlabel:`Refinement` | This runtime performance requirement refines the interface group `Blub </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__. |
    +-+-+
    | :factlabel:`Validation` | This runtime performance requirement is validated by a validation by test specified by `spec:/​rtems/​req/​perf-no-results </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsreqperfnoresults>`__. |
    +-+-+

.. _RequirementsInterfaceRequirements:

Interface requirements
**********************

For interface requirements see the *ICD* :cite:`PkgDeploymentDocTsIcd`.

.. _RequirementsOperationalRequirements:

Operational requirements
************************

At the time of pre-qualification, no specific operational
requirements have been identified, but they shall be determined as
appropriate for each individual mission or system in which RTEMS is
integrated.

.. _RequirementsResourcesRequirements:

Resources requirements
**********************

At the time of pre-qualification, no specific resources
requirements have been identified, but they shall be determined as
appropriate for each individual mission or system in which RTEMS is
integrated.

.. _RequirementsDesignRequirementsAndImplementationConstraints:

Design requirements and implementation constraints
**************************************************

.. _SpecGlossaryGroup:

spec:/glossary/group
====================

.. rubric:: REQUIREMENT:

The system shall have a general glossary of terms.

.. rubric:: CHANGES:

There are no changes since Name v1.

.. table::
    :class: longtable
    :widths: 26,74

    +-+-+
    | :factlabel:`Refinement` | This glossary group refines the design requirement `spec:/​req/​root </pkg/doc-ts-srs/html/requirements.html#specreqroot>`__. |
    +-+-+
    | :factlabel:`Validation` | This glossary group is validated. |
    +-+-+

.. _SpecReqGlossary:

spec:/req/glossary
==================

.. rubric:: REQUIREMENT:

The system shall have a glossary of specification-specific terms.

.. rubric:: CHANGES:

There are no changes since Name v1.

.. table::
    :class: longtable
    :widths: 26,74

    +-+-+
    | :factlabel:`Refinement` | This glossary group refines the design requirement `spec:/​req/​root </pkg/doc-ts-srs/html/requirements.html#specreqroot>`__. |
    +-+-+
    | :factlabel:`Validation` | This glossary group is **not validated**. |
    +-+-+

.. _SpecReqRoot:

spec:/req/root
==============

.. rubric:: REQUIREMENT:

The software product shall be a real-time operating system.

.. rubric:: REFINEMENTS:

This design requirement is refined by the following items:

- `spec:/​glossary/​group
  </pkg/doc-ts-srs/html/requirements.html#specglossarygroup>`__

- `spec:/​req/​api
  </pkg/doc-ts-icd/html/requirements-and-design.html#specreqapi>`__

- `spec:/​req/​glossary
  </pkg/doc-ts-srs/html/requirements.html#specreqglossary>`__

- `spec:/​req/​perf-runtime
  </pkg/doc-ts-srs/html/requirements.html#specreqperfruntime>`__

- `spec:/​req/​usage-constraints
  </pkg/doc-ts-srs/html/requirements.html#specrequsageconstraints>`__

- `Domain
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdomain>`__

- `Something Configuration
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroupacfg>`__

- `spec:/​rtems/​req/​group
  </pkg/doc-ts-srs/html/requirements.html#specrtemsreqgroup>`__

- `spec:/​rtems/​req/​group-no-identifier
  </pkg/doc-ts-srs/html/requirements.html#specrtemsreqgroupnoidentifier>`__

- `spec:/​rtems/​target-a
  </pkg/doc-ts-srs/html/requirements.html#specrtemstargeta>`__

- `spec:/​testsuites/​unit
  </pkg/doc-ts-srs/html/requirements.html#spectestsuitesunit>`__

- `spec:/​testsuites/​validation
  </pkg/doc-ts-srs/html/requirements.html#spectestsuitesvalidation>`__

.. rubric:: VALIDATIONS:

The validation of this **not validated** design requirement depends on the
following items:

- `spec:/​glossary/​group
  </pkg/doc-ts-srs/html/requirements.html#specglossarygroup>`__
  (validated refinement)

- `spec:/​req/​api
  </pkg/doc-ts-icd/html/requirements-and-design.html#specreqapi>`__
  (**not validated** refinement)

- `spec:/​req/​glossary
  </pkg/doc-ts-srs/html/requirements.html#specreqglossary>`__
  (**not validated** refinement)

- `spec:/​req/​perf-runtime
  </pkg/doc-ts-srs/html/requirements.html#specreqperfruntime>`__
  (**not validated** refinement)

- `spec:/​req/​usage-constraints
  </pkg/doc-ts-srs/html/requirements.html#specrequsageconstraints>`__
  (validated refinement)

- `Domain
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdomain>`__
  (**not validated** refinement)

- `Something Configuration
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroupacfg>`__
  (not pre-qualified refinement)

- `spec:/​rtems/​req/​group
  </pkg/doc-ts-srs/html/requirements.html#specrtemsreqgroup>`__
  (**not validated** refinement)

- `spec:/​rtems/​req/​group-no-identifier
  </pkg/doc-ts-srs/html/requirements.html#specrtemsreqgroupnoidentifier>`__
  (**not validated** refinement)

- `spec:/​rtems/​target-a
  </pkg/doc-ts-srs/html/requirements.html#specrtemstargeta>`__
  (**not validated** refinement)

- `spec:/​score/​cpu/​val/​perf
  </pkg/doc-djf-svs/html/test-case-specification.html#specscorecpuvalperf>`__
  (validation by test)

- `spec:/​testsuites/​unit
  </pkg/doc-ts-srs/html/requirements.html#spectestsuitesunit>`__
  (**not validated** refinement)

- `spec:/​testsuites/​validation
  </pkg/doc-ts-srs/html/requirements.html#spectestsuitesvalidation>`__
  (**not validated** refinement)

.. rubric:: CHANGES:

There are no changes since Name v1.

.. _SpecReqUsageConstraints:

spec:/req/usage-constraints
===========================

.. rubric:: REQUIREMENT:

The system shall document usage constraints of interfaces.

.. rubric:: REFINEMENTS:

This design requirement refines the design requirement `spec:/​req/​root
</pkg/doc-ts-srs/html/requirements.html#specreqroot>`__.

This design requirement is refined by constraint
`spec:/​acfg/​constraint/​option-not-pre-qualified
</pkg/doc-ts-srs/html/requirements.html#specacfgconstraintoptionnotprequalified>`__.

.. rubric:: CHANGES:

There are no changes since Name v1.

.. table::
    :class: longtable
    :widths: 26,74

    +-+-+
    | :factlabel:`Validation` | This validated design requirement is validated by the validated refinement `spec:/​acfg/​constraint/​option-not-pre-qualified </pkg/doc-ts-srs/html/requirements.html#specacfgconstraintoptionnotprequalified>`__. |
    +-+-+

.. _SpecRtemsReqGroup:

spec:/rtems/req/group
=====================

.. rubric:: REQUIREMENT:

Text.

.. rubric:: VALIDATIONS:

The validation of this **not validated** design group depends on the following
items:

- `spec:/​rtems/​val/​test-case
  </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsvaltestcase>`__
  (validation by test)

- `spec:/​rtems/​val/​test-case-run
  </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsvaltestcaserun>`__
  (validation by test)

.. rubric:: CHANGES:

There are no changes since Name v1.

.. table::
    :class: longtable
    :widths: 26,74

    +-+-+
    | :factlabel:`Software design` | This design group is realised by the software design element `Blub3 </pkg/doc-ddf-sdd/html/group__Blub3.html>`__. |
    +-+-+
    | :factlabel:`Refinement` | This design group refines the design requirement `spec:/​req/​root </pkg/doc-ts-srs/html/requirements.html#specreqroot>`__. |
    +-+-+

.. _SpecRtemsReqGroupNoIdentifier:

spec:/rtems/req/group-no-identifier
===================================

.. rubric:: REQUIREMENT:

Text.

.. rubric:: CHANGES:

There are no changes since Name v1.

.. table::
    :class: longtable
    :widths: 26,74

    +-+-+
    | :factlabel:`Refinement` | This design group refines the design requirement `spec:/​req/​root </pkg/doc-ts-srs/html/requirements.html#specreqroot>`__. |
    +-+-+
    | :factlabel:`Validation` | This design group is **not validated**. |
    +-+-+

.. _SpecRtemsTargetA:

spec:/rtems/target-a
====================

.. rubric:: REQUIREMENT:

The Name Target A shall be a target.

.. rubric:: CHANGES:

There are no changes since Name v1.

.. table::
    :class: longtable
    :widths: 26,74

    +-+-+
    | :factlabel:`Refinement` | This design target refines the design requirement `spec:/​req/​root </pkg/doc-ts-srs/html/requirements.html#specreqroot>`__. |
    +-+-+
    | :factlabel:`Validation` | This design target is **not validated**. |
    +-+-+

.. _SpecTestsuitesUnit:

spec:/testsuites/unit
=====================

.. rubric:: REQUIREMENT:

The unit tests shall be a contained in test suites.

.. rubric:: REFINEMENTS:

This design group refines the design requirement `spec:/​req/​root
</pkg/doc-ts-srs/html/requirements.html#specreqroot>`__.

This design group is refined by test suite `spec:/​testsuites/​unit-0
</pkg/doc-djf-suitp/html/test-design.html#spectestsuitesunit0>`__.

.. rubric:: CHANGES:

There are no changes since Name v1.

.. table::
    :class: longtable
    :widths: 26,74

    +-+-+
    | :factlabel:`Validation` | This **not validated** design group is validated by the **not validated** refinement `spec:/​testsuites/​unit-0 </pkg/doc-djf-suitp/html/test-design.html#spectestsuitesunit0>`__. |
    +-+-+

.. _SpecTestsuitesValidation:

spec:/testsuites/validation
===========================

.. rubric:: REQUIREMENT:

The validation tests shall be a contained in test suites.

.. rubric:: REFINEMENTS:

This design group refines the design requirement `spec:/​req/​root
</pkg/doc-ts-srs/html/requirements.html#specreqroot>`__.

This design group is refined by the following items:

- `spec:/​rtems/​val/​mem-basic
  </pkg/doc-djf-svs/html/test-design.html#specrtemsvalmembasic>`__

- `spec:/​testsuites/​performance-no-clock-0
  </pkg/doc-djf-svs/html/test-design.html#spectestsuitesperformancenoclock0>`__

- `spec:/​testsuites/​test-suite-empty
  </pkg/doc-djf-svs/html/test-design.html#spectestsuitestestsuiteempty>`__

- `spec:/​testsuites/​test-suite-pass
  </pkg/doc-djf-svs/html/test-design.html#spectestsuitestestsuitepass>`__

- `spec:/​testsuites/​test-suite-xfail
  </pkg/doc-djf-svs/html/test-design.html#spectestsuitestestsuitexfail>`__

- `spec:/​testsuites/​validation-refinement
  </pkg/doc-ts-srs/html/requirements.html#spectestsuitesvalidationrefinement>`__

.. rubric:: VALIDATIONS:

The validation of this **not validated** design group depends on the following
items:

- `spec:/​rtems/​val/​mem-basic
  </pkg/doc-djf-svs/html/test-design.html#specrtemsvalmembasic>`__
  (validated refinement)

- `spec:/​testsuites/​performance-no-clock-0
  </pkg/doc-djf-svs/html/test-design.html#spectestsuitesperformancenoclock0>`__
  (**not validated** refinement)

- `spec:/​testsuites/​test-suite-empty
  </pkg/doc-djf-svs/html/test-design.html#spectestsuitestestsuiteempty>`__
  (**not validated** refinement)

- `spec:/​testsuites/​test-suite-pass
  </pkg/doc-djf-svs/html/test-design.html#spectestsuitestestsuitepass>`__
  (validated refinement)

- `spec:/​testsuites/​test-suite-xfail
  </pkg/doc-djf-svs/html/test-design.html#spectestsuitestestsuitexfail>`__
  (validated refinement)

- `spec:/​testsuites/​validation-refinement
  </pkg/doc-ts-srs/html/requirements.html#spectestsuitesvalidationrefinement>`__
  (**not validated** refinement)

.. rubric:: CHANGES:

There are no changes since Name v1.

.. _SpecTestsuitesValidationRefinement:

spec:/testsuites/validation-refinement
======================================

.. rubric:: REQUIREMENT:

The validation refinement text.

.. rubric:: REFINEMENTS:

This design group refines the design group `spec:/​testsuites/​validation
</pkg/doc-ts-srs/html/requirements.html#spectestsuitesvalidation>`__.

This design group is refined by test suite `spec:/​testsuites/​test-suite-fail
</pkg/doc-djf-svs/html/test-design.html#spectestsuitestestsuitefail>`__.

.. rubric:: CHANGES:

There are no changes since Name v1.

.. table::
    :class: longtable
    :widths: 26,74

    +-+-+
    | :factlabel:`Validation` | This **not validated** design group is validated by the **not validated** refinement `spec:/​testsuites/​test-suite-fail </pkg/doc-djf-svs/html/test-design.html#spectestsuitestestsuitefail>`__. |
    +-+-+

.. _RequirementsSecurityAndPrivacyRequirements:

Security and privacy requirements
*********************************

At the time of pre-qualification, no specific security and privacy
requirements have been identified, but they shall be determined as
appropriate for each individual mission or system in which RTEMS is
integrated.

.. _RequirementsPortabilityRequirements:

Portability requirements
************************

At the time of pre-qualification, no specific portability
requirements have been identified, but they shall be determined as
appropriate for each individual mission or system in which RTEMS is
integrated.

.. _RequirementsSoftwareQualityRequirements:

Software quality requirements
*****************************

.. _SpecRtemsReqMemBasic:

spec:/rtems/req/mem-basic
=========================

.. rubric:: REQUIREMENT:

The system shall provide a benchmark program to show the static memory usage of
a basic application configuration.

.. rubric:: CHANGES:

There are no changes since Name v1.

.. table::
    :class: longtable
    :widths: 26,74

    +-+-+
    | :factlabel:`Refinement` | This quality requirement refines the interface group `Blub </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__. |
    +-+-+
    | :factlabel:`Validation` | This validated quality requirement is validated by the validation by inspection `spec:/​rtems/​val/​mem-basic </pkg/doc-djf-svs/html/test-design.html#specrtemsvalmembasic>`__. |
    +-+-+

.. _RequirementsSoftwareReliabilityRequirements:

Software reliability requirements
*********************************

At the time of pre-qualification, no specific software reliability
requirements have been identified, but they shall be determined as
appropriate for each individual mission or system in which RTEMS is
integrated.

.. _RequirementsSoftwareMaintainabilityRequirements:

Software maintainability requirements
*************************************

At the time of pre-qualification, no specific software maintainability
requirements have been identified, but they shall be determined as
appropriate for each individual mission or system in which RTEMS is
integrated.

.. _RequirementsSoftwareSafetyRequirements:

Software safety requirements
****************************

At the time of pre-qualification, no specific software safety
requirements have been identified, but they shall be determined as
appropriate for each individual mission or system in which RTEMS is
integrated.

.. _RequirementsDataDefinitionAndDatabaseRequirements:

Data definition and database requirements
*****************************************

At the time of pre-qualification, no specific data definition and database
requirements have been identified, but they shall be determined as
appropriate for each individual mission or system in which RTEMS is
integrated.

.. _RequirementsHumanFactorsRelatedRequirements:

Human factors related requirements
**********************************

At the time of pre-qualification, no specific human factors
requirements have been identified, but they shall be determined as
appropriate for each individual mission or system in which RTEMS is
integrated.

.. _RequirementsAdaptationAndInstallationRequirements:

Adaptation and installation requirements
****************************************

At the time of pre-qualification, no specific adaption and installation
requirements have been identified, but they shall be determined as
appropriate for each individual mission or system in which RTEMS is
integrated.
.. srs-requirements end

.. srs-constraints begin
.. role:: factlabel

.. raw:: latex

    \providecommand{\DUrolefactlabel}[1]{{\sffamily\bfseries%
      \ifcsname color@TitleColor\endcsname\color{TitleColor}\fi%
      \ifcsname l@nohyphenation\endcsname%
        \language\csname l@nohyphenation\endcsname%
      \fi%
      #1}}

.. _SpecAcfgConstraintOptionNotPreQualified:

spec:/acfg/constraint/option-not-pre-qualified
##############################################

.. rubric:: CONSTRAINT:

The application configuration option is not included in the pre-qualified
feature set of RTEMS.  Applications which are restricted to only use interfaces
of the pre-qualified feature set of RTEMS shall not use the application
configuration option.

.. rubric:: CHANGES:

There are no changes since Name v1.

.. table::
    :class: longtable
    :widths: 26,74

    +-+-+
    | :factlabel:`Refinement` | This constraint refines the design requirement `spec:/​req/​usage-constraints </pkg/doc-ts-srs/html/requirements.html#specrequsageconstraints>`__. |
    +-+-+
    | :factlabel:`Constraint item` | This constraint is applicable to application configuration option `CONFIGURE_INTEGER </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifacfginteger>`__. |
    +-+-+
.. srs-constraints end"""
