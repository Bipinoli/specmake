# SPDX-License-Identifier: BSD-2-Clause
""" Tests for the icdbuilder module. """

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


def test_icdbuilder(caplog, tmpdir):
    package, text = build_document(
        caplog, tmpdir, "doc-ts-icd",
        ["aggregate-test-results", "link-hub", "ts-icd"])
    assert text == """.. SPDX-License-Identifier: CC-BY-SA-4.0

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
the status of the root item: `spec:/​req/​root </pkg/doc-ts-srs/html/requirements.html#specreqroot>`__.

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

    \\begin{tiny}

.. table::
    :class: longtable
    :widths: 32,14,32,22

    +-+-+-+-+
    | Interface / Requirement | Status | Refinement / Validation | Role |
    +=+=+=+=+
    | _`/req/api` | **not validated** | `/rtems/if/group`_ | **not validated** refinement |
    + + +-+-+
    | | | `/rtems/if/group-2`_ | **not validated** refinement |
    + + +-+-+
    | | | `/rtems/if/group-a`_ | **not validated** refinement |
    + + +-+-+
    | | | `/rtems/if/group-b`_ | **not validated** refinement |
    +-+-+-+-+
    | _`/rtems/if/domain` | **not validated** | `/rtems/if/acfg-integer`_ | not pre-qualified interface placement |
    + + +-+-+
    | | | `/rtems/if/group-acfg`_ | not pre-qualified interface placement |
    + + +-+-+
    | | | `/rtems/if/header`_ | **not validated** interface placement |
    + + +-+-+
    | | | `/rtems/if/header-2`_ | **not validated** interface placement |
    + + +-+-+
    | | | `/rtems/if/unspec-header`_ | **not validated** interface placement |
    +-+-+-+-+
    | _`/rtems/if/group-acfg` | not pre-qualified | `/rtems/if/acfg-integer`_ | not pre-qualified group member |
    +-+-+-+-+
    | _`/rtems/if/group` | **not validated** | `/rtems/if/define-not-defined`_ | **not validated** group member |
    + + +-+-+
    | | | `/rtems/if/define-real`_ | **not validated** group member |
    + + +-+-+
    | | | `/rtems/if/enum-real`_ | **not validated** group member |
    + + +-+-+
    | | | `/rtems/if/func`_ | **not validated** group member |
    + + +-+-+
    | | | `/rtems/if/header`_ | **not validated** group member |
    + + +-+-+
    | | | `/rtems/if/obj`_ | **not validated** group member |
    + + +-+-+
    | | | `/rtems/if/reg-block`_ | **not validated** group member |
    + + +-+-+
    | | | `/rtems/if/reg-block-2`_ | **not validated** group member |
    + + +-+-+
    | | | `/rtems/if/struct`_ | **not validated** group member |
    + + +-+-+
    | | | `/rtems/if/struct-both`_ | **not validated** group member |
    + + +-+-+
    | | | `/rtems/if/struct-only`_ | **not validated** group member |
    + + +-+-+
    | | | `/rtems/if/typedef`_ | **not validated** group member |
    + + +-+-+
    | | | `/rtems/if/union`_ | **not validated** group member |
    + + +-+-+
    | | | `/rtems/if/union-both`_ | **not validated** group member |
    + + +-+-+
    | | | `/rtems/if/union-only`_ | **not validated** group member |
    + + +-+-+
    | | | `/rtems/if/unspec-group`_ | **not validated** group member |
    + + +-+-+
    | | | `/​rtems/​req/​mem-basic </pkg/doc-ts-srs/html/requirements.html#specrtemsreqmembasic>`__ | validated refinement |
    + + +-+-+
    | | | `/​rtems/​req/​perf </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsreqperf>`__ | **not validated** refinement |
    + + +-+-+
    | | | `/​rtems/​req/​perf-no-results </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsreqperfnoresults>`__ | **not validated** refinement |
    +-+-+-+-+
    | _`/rtems/if/group-2` | **not validated** | `/rtems/if/forward-decl`_ | **not validated** group member |
    + + +-+-+
    | | | `/rtems/if/group-a`_ | **not validated** group member |
    + + +-+-+
    | | | `/rtems/if/group-b`_ | **not validated** group member |
    + + +-+-+
    | | | `/rtems/if/header-2`_ | **not validated** group member |
    +-+-+-+-+
    | _`/rtems/if/group-a` | **not validated** | N/A | N/A |
    +-+-+-+-+
    | _`/rtems/if/group-b` | **not validated** | N/A | N/A |
    +-+-+-+-+
    | _`/rtems/if/acfg-integer` | not pre-qualified | N/A | N/A |
    +-+-+-+-+
    | _`/rtems/if/define-not-defined` | **not validated** | `/​rtems/​req/​define-not-defined </pkg/doc-ts-srs/html/requirements.html#specrtemsreqdefinenotdefined>`__ | **not validated** interface function |
    +-+-+-+-+
    | _`/rtems/if/define-real` | **not validated** | `/​rtems/​val/​test-case </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsvaltestcase>`__ | **not validated** refinement |
    +-+-+-+-+
    | _`/rtems/if/enum-real` | **not validated** | `/rtems/if/enumerator`_ | **not validated** interface enumerator |
    + + +-+-+
    | | | `/rtems/if/enumerator-2`_ | **not validated** interface enumerator |
    +-+-+-+-+
    | _`/rtems/if/func` | **not validated** | `/​rtems/​req/​action-2 </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsreqaction2>`__ | **not validated** interface function |
    + + +-+-+
    | | | `/​rtems/​req/​func </pkg/doc-ts-srs/html/requirements.html#specrtemsreqfunc>`__ | **not validated** interface function |
    +-+-+-+-+
    | _`/rtems/if/header` | **not validated** | `/rtems/if/define-not-defined`_ | **not validated** interface placement |
    + + +-+-+
    | | | `/rtems/if/define-real`_ | **not validated** interface placement |
    + + +-+-+
    | | | `/rtems/if/enum-real`_ | **not validated** interface placement |
    + + +-+-+
    | | | `/rtems/if/func`_ | **not validated** interface placement |
    + + +-+-+
    | | | `/rtems/if/group`_ | **not validated** interface placement |
    + + +-+-+
    | | | `/rtems/if/obj`_ | **not validated** interface placement |
    + + +-+-+
    | | | `/rtems/if/reg-block`_ | **not validated** interface placement |
    + + +-+-+
    | | | `/rtems/if/reg-block-2`_ | **not validated** interface placement |
    + + +-+-+
    | | | `/rtems/if/struct`_ | **not validated** interface placement |
    + + +-+-+
    | | | `/rtems/if/struct-both`_ | **not validated** interface placement |
    + + +-+-+
    | | | `/rtems/if/struct-only`_ | **not validated** interface placement |
    + + +-+-+
    | | | `/rtems/if/typedef`_ | **not validated** interface placement |
    + + +-+-+
    | | | `/rtems/if/union`_ | **not validated** interface placement |
    + + +-+-+
    | | | `/rtems/if/union-both`_ | **not validated** interface placement |
    + + +-+-+
    | | | `/rtems/if/union-only`_ | **not validated** interface placement |
    +-+-+-+-+
    | _`/rtems/if/obj` | **not validated** | N/A | N/A |
    +-+-+-+-+
    | _`/rtems/if/reg-block` | **not validated** | N/A | N/A |
    +-+-+-+-+
    | _`/rtems/if/reg-block-2` | **not validated** | N/A | N/A |
    +-+-+-+-+
    | _`/rtems/if/struct` | **not validated** | N/A | N/A |
    +-+-+-+-+
    | _`/rtems/if/struct-both` | **not validated** | N/A | N/A |
    +-+-+-+-+
    | _`/rtems/if/struct-only` | **not validated** | N/A | N/A |
    +-+-+-+-+
    | _`/rtems/if/typedef` | **not validated** | N/A | N/A |
    +-+-+-+-+
    | _`/rtems/if/union` | **not validated** | N/A | N/A |
    +-+-+-+-+
    | _`/rtems/if/union-both` | **not validated** | N/A | N/A |
    +-+-+-+-+
    | _`/rtems/if/union-only` | **not validated** | N/A | N/A |
    +-+-+-+-+
    | _`/rtems/if/unspec-group` | **not validated** | `/c/if/uint32_t`_ | **not validated** group member |
    + + +-+-+
    | | | `/rtems/if/define-duplicate`_ | **not validated** group member |
    + + +-+-+
    | | | `/rtems/if/define-second-duplicate`_ | **not validated** group member |
    + + +-+-+
    | | | `/rtems/if/unspec-define`_ | **not validated** group member |
    + + +-+-+
    | | | `/rtems/if/unspec-enum`_ | **not validated** group member |
    + + +-+-+
    | | | `/rtems/if/unspec-enumerator`_ | **not validated** group member |
    + + +-+-+
    | | | `/rtems/if/unspec-function`_ | **not validated** group member |
    + + +-+-+
    | | | `/rtems/if/unspec-header`_ | **not validated** group member |
    + + +-+-+
    | | | `/rtems/if/unspec-macro`_ | **not validated** group member |
    + + +-+-+
    | | | `/rtems/if/unspec-object`_ | **not validated** group member |
    + + +-+-+
    | | | `/rtems/if/unspec-struct`_ | **not validated** group member |
    + + +-+-+
    | | | `/rtems/if/unspec-typedef`_ | **not validated** group member |
    + + +-+-+
    | | | `/rtems/if/unspec-union`_ | **not validated** group member |
    +-+-+-+-+
    | _`/rtems/if/forward-decl` | **not validated** | N/A | N/A |
    +-+-+-+-+
    | _`/rtems/if/header-2` | **not validated** | `/rtems/if/forward-decl`_ | **not validated** interface placement |
    + + +-+-+
    | | | `/rtems/if/group-2`_ | **not validated** interface placement |
    + + +-+-+
    | | | `/rtems/if/group-a`_ | **not validated** interface placement |
    + + +-+-+
    | | | `/rtems/if/group-b`_ | **not validated** interface placement |
    +-+-+-+-+
    | _`/rtems/if/enumerator` | **not validated** | N/A | N/A |
    +-+-+-+-+
    | _`/rtems/if/enumerator-2` | **not validated** | N/A | N/A |
    +-+-+-+-+
    | _`/c/if/uint32_t` | **not validated** | N/A | N/A |
    +-+-+-+-+
    | _`/rtems/if/define-duplicate` | **not validated** | N/A | N/A |
    +-+-+-+-+
    | _`/rtems/if/define-second-duplicate` | **not validated** | N/A | N/A |
    +-+-+-+-+
    | _`/rtems/if/unspec-define` | **not validated** | N/A | N/A |
    +-+-+-+-+
    | _`/rtems/if/unspec-enum` | **not validated** | N/A | N/A |
    +-+-+-+-+
    | _`/rtems/if/unspec-enumerator` | **not validated** | N/A | N/A |
    +-+-+-+-+
    | _`/rtems/if/unspec-function` | **not validated** | `/​rtems/​req/​action </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsreqaction>`__ | **not validated** interface function |
    + + +-+-+
    | | | `/​rtems/​req/​action-2 </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsreqaction2>`__ | **not validated** interface function |
    +-+-+-+-+
    | _`/rtems/if/unspec-header` | **not validated** | `/c/if/uint32_t`_ | **not validated** interface placement |
    + + +-+-+
    | | | `/rtems/if/define-duplicate`_ | **not validated** interface placement |
    + + +-+-+
    | | | `/rtems/if/define-second-duplicate`_ | **not validated** interface placement |
    + + +-+-+
    | | | `/rtems/if/unspec-define`_ | **not validated** interface placement |
    + + +-+-+
    | | | `/rtems/if/unspec-enum`_ | **not validated** interface placement |
    + + +-+-+
    | | | `/rtems/if/unspec-enumerator`_ | **not validated** interface placement |
    + + +-+-+
    | | | `/rtems/if/unspec-function`_ | **not validated** interface placement |
    + + +-+-+
    | | | `/rtems/if/unspec-group`_ | **not validated** interface placement |
    + + +-+-+
    | | | `/rtems/if/unspec-macro`_ | **not validated** interface placement |
    + + +-+-+
    | | | `/rtems/if/unspec-object`_ | **not validated** interface placement |
    + + +-+-+
    | | | `/rtems/if/unspec-struct`_ | **not validated** interface placement |
    + + +-+-+
    | | | `/rtems/if/unspec-typedef`_ | **not validated** interface placement |
    + + +-+-+
    | | | `/rtems/if/unspec-union`_ | **not validated** interface placement |
    +-+-+-+-+
    | _`/rtems/if/unspec-macro` | **not validated** | N/A | N/A |
    +-+-+-+-+
    | _`/rtems/if/unspec-object` | **not validated** | N/A | N/A |
    +-+-+-+-+
    | _`/rtems/if/unspec-struct` | **not validated** | N/A | N/A |
    +-+-+-+-+
    | _`/rtems/if/unspec-typedef` | **not validated** | N/A | N/A |
    +-+-+-+-+
    | _`/rtems/if/unspec-union` | **not validated** | N/A | N/A |
    +-+-+-+-+

.. raw:: latex

    \\end{tiny}
.. validation-verification end

.. icd-requirements-and-design begin
.. _RequirementsAndDesign:

Requirements and design
#######################

.. _RequirementsAndDesignGeneralProvisionsToTheRequirementsInTheIRD:

General provisions to the requirements in the IRD
*************************************************

There are no general provisions to requirements in the :term:`IRD`.

.. _RequirementsAndDesignInterfaceRequirements:

Interface requirements
**********************

.. raw:: latex

    \\clearpage

.. _SpecReqApi:

spec:/req/api
=============

.. rubric:: REQUIREMENT:

The software product shall provide an API.

.. rubric:: REFINEMENTS:

This interface requirement refines the design requirement `spec:/​req/​root
</pkg/doc-ts-srs/html/requirements.html#specreqroot>`__.

This interface requirement is refined by the following items:

- `Blub
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__

- `Blub2
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup2>`__

- `A
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroupa>`__

- `B
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroupb>`__

.. rubric:: VALIDATIONS:

The validation of this **not validated** interface requirement depends on the
following items:

- `Blub
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__
  (**not validated** refinement)

- `Blub2
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup2>`__
  (**not validated** refinement)

- `A
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroupa>`__
  (**not validated** refinement)

- `B
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroupb>`__
  (**not validated** refinement)

.. _RequirementsAndDesignInterfaceDesign:

Interface design
****************

.. _RequirementsAndDesignInterfaceDesignDomain:

Domain
======

Description.

.. raw:: latex

    \\clearpage

.. _SpecCIfUint32T:

spec:/c/if/uint32_t
-------------------

.. rubric:: REQUIREMENT:

The `<bar/more/unspec.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__
header file shall provide the type definition ``uint32_t``.

.. rubric:: INTERFACE:

.. code-block:: c

    typedef ... uint32_t ...;

.. rubric:: GROUP MEMBERSHIP:

This type definition is a member of the group `UnspecGroup
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecgroup>`__.

.. rubric:: INTERFACE PLACEMENT:

This type definition is placed into the header file `<bar/more/unspec.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__.

.. rubric:: VALIDATION:

This type definition is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfAcfgInteger:

spec:/rtems/if/acfg-integer
---------------------------

.. rubric:: REQUIREMENT:

The `Domain
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdomain>`__
interface domain shall provide the application configuration option
``CONFIGURE_INTEGER``.

.. rubric:: OPTION TYPE:

This configuration option is an integer define.

.. rubric:: DEFAULT VALUE:

The default value is 0.

.. rubric:: DESCRIPTION:

Integer configuration option description.

.. rubric:: CONSTRAINTS:

The configuration option is not included in the pre-qualified feature set of
RTEMS.  Applications which are restricted to only use interfaces of the
pre-qualified feature set of RTEMS shall not use the configuration option.

.. rubric:: SOFTWARE DESIGN:

This application configuration option is realised by the software design element `CONFIGURE_INTEGER </pkg/doc-ddf-sdd/html/group__RTEMSApplConfigSomethingConfiguration.html#ga714d5d7419c8b6c00f172e9a3c571a9b>`__.

.. rubric:: GROUP MEMBERSHIP:

This application configuration option is a member of the application
configuration group `Something Configuration
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroupacfg>`__.

.. rubric:: INTERFACE PLACEMENT:

This application configuration option is placed into the interface domain
`Domain
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdomain>`__.

.. rubric:: VALIDATION:

This application configuration option is not pre-qualified.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfDefineDuplicate:

spec:/rtems/if/define-duplicate
-------------------------------

.. rubric:: REQUIREMENT:

The `<bar/more/unspec.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__
header file shall provide the define ``BLUB``.

.. rubric:: INTERFACE:

.. code-block:: c

    #define BLUB ...

.. rubric:: SOFTWARE DESIGN:

This define is realised by the software design element `BLUB </pkg/doc-ddf-sdd/html/group__Blub.html#gaf0277526715a0aa6e2ba520cc3399254>`__.

.. rubric:: GROUP MEMBERSHIP:

This define is a member of the group `UnspecGroup
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecgroup>`__.

.. rubric:: INTERFACE PLACEMENT:

This define is placed into the header file `<bar/more/unspec.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__.

.. rubric:: VALIDATION:

This define is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfDefineNotDefined:

spec:/rtems/if/define-not-defined
---------------------------------

.. rubric:: REQUIREMENT:

The `<blub.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__
header file shall provide the define ``DEFINE_NOT_DEFINED``.

.. rubric:: BRIEF DESCRIPTION:

Define not defined brief.

.. rubric:: INTERFACE:

.. code-block:: c

    #define DEFINE_NOT_DEFINED 

.. rubric:: DESCRIPTION:

Define not defined description.

.. rubric:: GROUP MEMBERSHIP:

This define is a member of the interface group `Blub
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__.

.. rubric:: INTERFACE PLACEMENT:

This define is placed into the header file `<blub.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__.

.. rubric:: INTERFACE FUNCTION:

The function of this define is specified by the interface define requirement
`spec:/​rtems/​req/​define-not-defined
</pkg/doc-ts-srs/html/requirements.html#specrtemsreqdefinenotdefined>`__.

.. rubric:: VALIDATION:

This **not validated** define is validated by the **not validated** interface function `spec:/​rtems/​req/​define-not-defined </pkg/doc-ts-srs/html/requirements.html#specrtemsreqdefinenotdefined>`__.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfDefineReal:

spec:/rtems/if/define-real
--------------------------

.. rubric:: REQUIREMENT:

The `<blub.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__
header file shall provide the define ``BLUB``.

.. rubric:: BRIEF DESCRIPTION:

Define brief.

.. rubric:: INTERFACE:

.. code-block:: c

    #define BLUB 123

.. rubric:: DESCRIPTION:

Define description.

.. rubric:: SOFTWARE DESIGN:

This define is realised by the software design element `BLUB </pkg/doc-ddf-sdd/html/group__Blub.html#gaf0277526715a0aa6e2ba520cc3399254>`__.

.. rubric:: REFINEMENT:

This define is refined by the test case `spec:/​rtems/​val/​test-case
</pkg/doc-djf-svs/html/test-case-specification.html#specrtemsvaltestcase>`__.

.. rubric:: GROUP MEMBERSHIP:

This define is a member of the interface group `Blub
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__.

.. rubric:: INTERFACE PLACEMENT:

This define is placed into the header file `<blub.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__.

.. rubric:: VALIDATION:

This **not validated** define is validated by the **not validated** refinement `spec:/​rtems/​val/​test-case </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsvaltestcase>`__.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfDefineSecondDuplicate:

spec:/rtems/if/define-second-duplicate
--------------------------------------

.. rubric:: REQUIREMENT:

The `<bar/more/unspec.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__
header file shall provide the define ``BLUB``.

.. rubric:: INTERFACE:

.. code-block:: c

    #define BLUB ...

.. rubric:: SOFTWARE DESIGN:

This define is realised by the software design element `BLUB </pkg/doc-ddf-sdd/html/group__Blub.html#gaf0277526715a0aa6e2ba520cc3399254>`__.

.. rubric:: GROUP MEMBERSHIP:

This define is a member of the group `UnspecGroup
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecgroup>`__.

.. rubric:: INTERFACE PLACEMENT:

This define is placed into the header file `<bar/more/unspec.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__.

.. rubric:: VALIDATION:

This define is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfDomain:

spec:/rtems/if/domain
---------------------

.. rubric:: REQUIREMENT:

There shall be the interface domain ``Domain``.

.. rubric:: DESCRIPTION:

Description.

.. rubric:: REFINEMENT:

This interface domain refines the design requirement `spec:/​req/​root
</pkg/doc-ts-srs/html/requirements.html#specreqroot>`__.

.. rubric:: INTERFACE PLACEMENTS:

This interface domain contains the following items:

- `CONFIGURE_INTEGER
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifacfginteger>`__

- `Something Configuration
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroupacfg>`__

- `<blub.h>
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__

- `<blub-2.h>
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader2>`__

- `<bar/more/unspec.h>
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__

.. rubric:: VALIDATIONS:

The validation of this **not validated** interface domain depends on the
following items:

- `CONFIGURE_INTEGER
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifacfginteger>`__
  (not pre-qualified interface placement)

- `Something Configuration
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroupacfg>`__
  (not pre-qualified interface placement)

- `<blub.h>
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__
  (**not validated** interface placement)

- `<blub-2.h>
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader2>`__
  (**not validated** interface placement)

- `<bar/more/unspec.h>
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__
  (**not validated** interface placement)

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfEnumReal:

spec:/rtems/if/enum-real
------------------------

.. rubric:: REQUIREMENT:

The `<blub.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__
header file shall provide the enumeration ``the_enum``.

.. rubric:: BRIEF DESCRIPTION:

Enum brief.

.. rubric:: INTERFACE:

.. code-block:: c

    typedef enum {
      ENUMERATOR,
      ENUMERATOR_2 = 2,
    } the_enum;

.. rubric:: DESCRIPTION:

Description.

.. rubric:: SOFTWARE DESIGN:

This enumeration is realised by the software design element `the_enum </pkg/doc-ddf-sdd/html/group__Blub.html#ga582a1afc79f3b607104a52d7aa268624>`__.

.. rubric:: ENUMERATORS:

This enumeration provides the following items:

- `ENUMERATOR
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifenumerator>`__

- `ENUMERATOR_2
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifenumerator2>`__

.. rubric:: GROUP MEMBERSHIP:

This enumeration is a member of the interface group `Blub
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__.

.. rubric:: INTERFACE PLACEMENT:

This enumeration is placed into the header file `<blub.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__.

.. rubric:: VALIDATIONS:

The validation of this **not validated** enumeration depends on the following
items:

- `ENUMERATOR
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifenumerator>`__
  (**not validated** interface enumerator)

- `ENUMERATOR_2
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifenumerator2>`__
  (**not validated** interface enumerator)

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfEnumerator:

spec:/rtems/if/enumerator
-------------------------

.. rubric:: REQUIREMENT:

The `the_enum
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifenumreal>`__
enumeration shall provide the enumerator ``ENUMERATOR``.

.. rubric:: BRIEF DESCRIPTION:

Enumerator brief.

.. rubric:: INTERFACE:

.. code-block:: c

    typedef enum {
      ...
      ENUMERATOR
      ...
    } the_enum;

.. rubric:: DESCRIPTION:

Description.

.. rubric:: SOFTWARE DESIGN:

This enumerator is realised by the software design element `ENUMERATOR </pkg/doc-ddf-sdd/html/group__Blub.html#gga582a1afc79f3b607104a52d7aa268624a183cf8edbca25c5db49f6fda4224f87a>`__.

.. rubric:: ENUMERATOR:

This enumerator is provided by the enumeration `the_enum
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifenumreal>`__.

.. rubric:: VALIDATION:

This enumerator is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfEnumerator2:

spec:/rtems/if/enumerator-2
---------------------------

.. rubric:: REQUIREMENT:

The `the_enum
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifenumreal>`__
enumeration shall provide the enumerator ``ENUMERATOR_2``.

.. rubric:: BRIEF DESCRIPTION:

Enumerator 2 brief.

.. rubric:: INTERFACE:

.. code-block:: c

    typedef enum {
      ...
      ENUMERATOR_2 = 2
      ...
    } the_enum;

.. rubric:: DESCRIPTION:

Description 2.

.. rubric:: SOFTWARE DESIGN:

This enumerator is realised by the software design element `ENUMERATOR_2 </pkg/doc-ddf-sdd/html/group__Blub.html#gga582a1afc79f3b607104a52d7aa268624ac9cedcefbbfbc41195028b42a9830d2f>`__.

.. rubric:: ENUMERATOR:

This enumerator is provided by the enumeration `the_enum
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifenumreal>`__.

.. rubric:: VALIDATION:

This enumerator is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfForwardDecl:

spec:/rtems/if/forward-decl
---------------------------

.. rubric:: REQUIREMENT:

The `<blub-2.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader2>`__
header file shall provide a forward declaration of `StructOnly
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifstructonly>`__.

.. rubric:: INTERFACE:

.. code-block:: c

    struct StructOnly;

.. rubric:: GROUP MEMBERSHIP:

This forward declaration is a member of the interface group `Blub2
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup2>`__.

.. rubric:: INTERFACE PLACEMENT:

This forward declaration is placed into the header file `<blub-2.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader2>`__.

.. rubric:: VALIDATION:

This forward declaration is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfFunc:

spec:/rtems/if/func
-------------------

.. rubric:: REQUIREMENT:

The `<blub.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__
header file shall provide the directive ``blub()``.

.. rubric:: BRIEF DESCRIPTION:

Brief.

.. rubric:: CALLING SEQUENCE:

.. code-block:: c

    int blub( int param );

.. rubric:: PARAMETERS:

``param``
    This parameter Parameter.

.. rubric:: DESCRIPTION:

Description.

.. rubric:: RETURN VALUES:

Returns.

.. rubric:: SOFTWARE DESIGN:

This directive is realised by the software design element `blub() </pkg/doc-ddf-sdd/html/group__Blub.html#ga754ccc677acbd87ede8b3c082bb9ff6b>`__.

.. rubric:: GROUP MEMBERSHIP:

This directive is a member of the interface group `Blub
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__.

.. rubric:: INTERFACE PLACEMENT:

This directive is placed into the header file `<blub.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__.

.. rubric:: INTERFACE FUNCTIONS:

The function of this directive is specified by the following items:

- `spec:/​rtems/​req/​action-2
  </pkg/doc-ts-srs/html/requirements.html#specrtemsreqaction2>`__

- `spec:/​rtems/​req/​func
  </pkg/doc-ts-srs/html/requirements.html#specrtemsreqfunc>`__

.. rubric:: VALIDATIONS:

The validation of this **not validated** directive depends on the following
items:

- `spec:/​rtems/​req/​action-2
  </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsreqaction2>`__
  (**not validated** interface function)

- `spec:/​rtems/​req/​func
  </pkg/doc-ts-srs/html/requirements.html#specrtemsreqfunc>`__
  (**not validated** interface function)

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfGroup:

spec:/rtems/if/group
--------------------

.. rubric:: REQUIREMENT:

There shall be the interface group ``Blub``.

.. rubric:: BRIEF DESCRIPTION:

Brief.

.. rubric:: DESCRIPTION:

Description.

.. rubric:: SOFTWARE DESIGN:

This interface group is realised by the software design element `Blub </pkg/doc-ddf-sdd/html/group__Blub.html>`__.

.. rubric:: REFINEMENTS:

This interface group refines the interface requirement `spec:/​req/​api
</pkg/doc-ts-icd/html/requirements-and-design.html#specreqapi>`__.

This interface group is refined by the following items:

- `spec:/​rtems/​req/​mem-basic
  </pkg/doc-ts-srs/html/requirements.html#specrtemsreqmembasic>`__

- `spec:/​rtems/​req/​perf
  </pkg/doc-ts-srs/html/requirements.html#specrtemsreqperf>`__

- `spec:/​rtems/​req/​perf-no-results
  </pkg/doc-ts-srs/html/requirements.html#specrtemsreqperfnoresults>`__

.. rubric:: GROUP MEMBERSHIPS:

This interface group contains the following items:

- `DEFINE_NOT_DEFINED
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdefinenotdefined>`__

- `BLUB
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdefinereal>`__

- `the_enum
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifenumreal>`__

- `blub()
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsiffunc>`__

- `<blub.h>
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__

- `obj
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifobj>`__

- `reg_block
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifregblock>`__

- `reg_block_2
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifregblock2>`__

- `Struct
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifstruct>`__

- `StructBoth
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifstructboth>`__

- `StructOnly
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifstructonly>`__

- `Typedef
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsiftypedef>`__

- `Union
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunion>`__

- `UnionBoth
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunionboth>`__

- `UnionOnly
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifuniononly>`__

- `UnspecGroup
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecgroup>`__

.. rubric:: INTERFACE PLACEMENT:

This interface group is placed into the header file `<blub.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__.

.. rubric:: VALIDATIONS:

The validation of this **not validated** interface group depends on the
following items:

- `DEFINE_NOT_DEFINED
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdefinenotdefined>`__
  (**not validated** group member)

- `BLUB
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdefinereal>`__
  (**not validated** group member)

- `the_enum
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifenumreal>`__
  (**not validated** group member)

- `blub()
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsiffunc>`__
  (**not validated** group member)

- `<blub.h>
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__
  (**not validated** group member)

- `obj
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifobj>`__
  (**not validated** group member)

- `reg_block
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifregblock>`__
  (**not validated** group member)

- `reg_block_2
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifregblock2>`__
  (**not validated** group member)

- `Struct
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifstruct>`__
  (**not validated** group member)

- `StructBoth
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifstructboth>`__
  (**not validated** group member)

- `StructOnly
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifstructonly>`__
  (**not validated** group member)

- `Typedef
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsiftypedef>`__
  (**not validated** group member)

- `Union
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunion>`__
  (**not validated** group member)

- `UnionBoth
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunionboth>`__
  (**not validated** group member)

- `UnionOnly
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifuniononly>`__
  (**not validated** group member)

- `UnspecGroup
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecgroup>`__
  (**not validated** group member)

- `spec:/​rtems/​req/​mem-basic
  </pkg/doc-ts-srs/html/requirements.html#specrtemsreqmembasic>`__
  (validated refinement)

- `spec:/​rtems/​req/​perf
  </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsreqperf>`__
  (**not validated** refinement)

- `spec:/​rtems/​req/​perf-no-results
  </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsreqperfnoresults>`__
  (**not validated** refinement)

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfGroup2:

spec:/rtems/if/group-2
----------------------

.. rubric:: REQUIREMENT:

There shall be the interface group ``Blub2``.

.. rubric:: BRIEF DESCRIPTION:

Blub2 brief.

.. rubric:: DESCRIPTION:

Description.

.. rubric:: SOFTWARE DESIGN:

This interface group is realised by the software design element `Blub2 </pkg/doc-ddf-sdd/html/group__Blub2.html>`__.

.. rubric:: REFINEMENT:

This interface group refines the interface requirement `spec:/​req/​api
</pkg/doc-ts-icd/html/requirements-and-design.html#specreqapi>`__.

.. rubric:: GROUP MEMBERSHIPS:

This interface group contains the following items:

- `StructOnly
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifforwarddecl>`__

- `A
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroupa>`__

- `B
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroupb>`__

- `<blub-2.h>
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader2>`__

.. rubric:: INTERFACE PLACEMENT:

This interface group is placed into the header file `<blub-2.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader2>`__.

.. rubric:: VALIDATIONS:

The validation of this **not validated** interface group depends on the
following items:

- `StructOnly
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifforwarddecl>`__
  (**not validated** group member)

- `A
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroupa>`__
  (**not validated** group member)

- `B
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroupb>`__
  (**not validated** group member)

- `<blub-2.h>
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader2>`__
  (**not validated** group member)

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfGroupA:

spec:/rtems/if/group-a
----------------------

.. rubric:: REQUIREMENT:

The `Blub2
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup2>`__
interface group shall contain the interface group ``A``.

.. rubric:: BRIEF DESCRIPTION:

Group A brief.

.. rubric:: DESCRIPTION:

Description.

.. rubric:: SOFTWARE DESIGN:

This interface group is realised by the software design element `A </pkg/doc-ddf-sdd/html/group__GroupA.html>`__.

.. rubric:: REFINEMENT:

This interface group refines the interface requirement `spec:/​req/​api
</pkg/doc-ts-icd/html/requirements-and-design.html#specreqapi>`__.

.. rubric:: GROUP MEMBERSHIP:

This interface group is a member of the interface group `Blub2
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup2>`__.

.. rubric:: INTERFACE PLACEMENT:

This interface group is placed into the header file `<blub-2.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader2>`__.

.. rubric:: VALIDATION:

This interface group is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfGroupAcfg:

spec:/rtems/if/group-acfg
-------------------------

.. rubric:: REQUIREMENT:

The something configuration text.

.. rubric:: DESCRIPTION:

Description.

.. rubric:: SOFTWARE DESIGN:

This application configuration group is realised by the software design element `Something Configuration </pkg/doc-ddf-sdd/html/group__RTEMSApplConfigSomethingConfiguration.html>`__.

.. rubric:: REFINEMENT:

This application configuration group refines the design requirement
`spec:/​req/​root
</pkg/doc-ts-srs/html/requirements.html#specreqroot>`__.

.. rubric:: GROUP MEMBERSHIP:

This application configuration group contains the application configuration
option `CONFIGURE_INTEGER
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifacfginteger>`__.

.. rubric:: INTERFACE PLACEMENT:

This application configuration group is placed into the interface domain
`Domain
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdomain>`__.

.. rubric:: VALIDATION:

This not pre-qualified application configuration group is validated by the not pre-qualified group member `CONFIGURE_INTEGER </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifacfginteger>`__.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfGroupB:

spec:/rtems/if/group-b
----------------------

.. rubric:: REQUIREMENT:

The `Blub2
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup2>`__
interface group shall contain the interface group ``B``.

.. rubric:: BRIEF DESCRIPTION:

Group B brief.

.. rubric:: DESCRIPTION:

Description.

.. rubric:: SOFTWARE DESIGN:

This interface group is realised by the software design element `B </pkg/doc-ddf-sdd/html/group__GroupB.html>`__.

.. rubric:: REFINEMENT:

This interface group refines the interface requirement `spec:/​req/​api
</pkg/doc-ts-icd/html/requirements-and-design.html#specreqapi>`__.

.. rubric:: GROUP MEMBERSHIP:

This interface group is a member of the interface group `Blub2
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup2>`__.

.. rubric:: INTERFACE PLACEMENT:

This interface group is placed into the header file `<blub-2.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader2>`__.

.. rubric:: VALIDATION:

This interface group is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfHeader:

spec:/rtems/if/header
---------------------

.. rubric:: REQUIREMENT:

The `Domain
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdomain>`__
interface domain shall provide the header file ``<blub.h>``.

.. rubric:: BRIEF DESCRIPTION:

Brief.

.. rubric:: INTERFACE:

.. code-block:: c

    #include <blub.h>

.. rubric:: SOFTWARE DESIGN:

This header file is realised by the software design element `<blub.h> </pkg/doc-ddf-sdd/html/blub_8h.html>`__.

.. rubric:: GROUP MEMBERSHIP:

This header file is a member of the interface group `Blub
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__.

.. rubric:: INTERFACE PLACEMENTS:

This header file is placed into the interface domain `Domain
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdomain>`__.

This header file contains the following items:

- `DEFINE_NOT_DEFINED
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdefinenotdefined>`__

- `BLUB
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdefinereal>`__

- `the_enum
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifenumreal>`__

- `blub()
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsiffunc>`__

- `Blub
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__

- `obj
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifobj>`__

- `reg_block
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifregblock>`__

- `reg_block_2
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifregblock2>`__

- `Struct
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifstruct>`__

- `StructBoth
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifstructboth>`__

- `StructOnly
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifstructonly>`__

- `Typedef
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsiftypedef>`__

- `Union
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunion>`__

- `UnionBoth
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunionboth>`__

- `UnionOnly
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifuniononly>`__

.. rubric:: INTERFACE INCLUDE:

This header file is included by the header file `<blub-2.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader2>`__.

.. rubric:: VALIDATIONS:

The validation of this **not validated** header file depends on the following
items:

- `DEFINE_NOT_DEFINED
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdefinenotdefined>`__
  (**not validated** interface placement)

- `BLUB
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdefinereal>`__
  (**not validated** interface placement)

- `the_enum
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifenumreal>`__
  (**not validated** interface placement)

- `blub()
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsiffunc>`__
  (**not validated** interface placement)

- `Blub
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__
  (**not validated** interface placement)

- `obj
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifobj>`__
  (**not validated** interface placement)

- `reg_block
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifregblock>`__
  (**not validated** interface placement)

- `reg_block_2
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifregblock2>`__
  (**not validated** interface placement)

- `Struct
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifstruct>`__
  (**not validated** interface placement)

- `StructBoth
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifstructboth>`__
  (**not validated** interface placement)

- `StructOnly
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifstructonly>`__
  (**not validated** interface placement)

- `Typedef
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsiftypedef>`__
  (**not validated** interface placement)

- `Union
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunion>`__
  (**not validated** interface placement)

- `UnionBoth
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunionboth>`__
  (**not validated** interface placement)

- `UnionOnly
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifuniononly>`__
  (**not validated** interface placement)

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfHeader2:

spec:/rtems/if/header-2
-----------------------

.. rubric:: REQUIREMENT:

The `Domain
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdomain>`__
interface domain shall provide the header file ``<blub-2.h>``.

.. rubric:: BRIEF DESCRIPTION:

Blub2 header brief.

.. rubric:: INTERFACE:

.. code-block:: c

    #include <blub-2.h>

.. rubric:: SOFTWARE DESIGN:

This header file is realised by the software design element `<blub-2.h> </pkg/doc-ddf-sdd/html/blub-2_8h.html>`__.

.. rubric:: GROUP MEMBERSHIP:

This header file is a member of the interface group `Blub2
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup2>`__.

.. rubric:: INTERFACE PLACEMENTS:

This header file is placed into the interface domain `Domain
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdomain>`__.

This header file contains the following items:

- `StructOnly
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifforwarddecl>`__

- `Blub2
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup2>`__

- `A
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroupa>`__

- `B
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroupb>`__

.. rubric:: INTERFACE INCLUDE:

This header file includes the header file `<blub.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__.

.. rubric:: VALIDATIONS:

The validation of this **not validated** header file depends on the following
items:

- `StructOnly
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifforwarddecl>`__
  (**not validated** interface placement)

- `Blub2
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup2>`__
  (**not validated** interface placement)

- `A
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroupa>`__
  (**not validated** interface placement)

- `B
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroupb>`__
  (**not validated** interface placement)

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfObj:

spec:/rtems/if/obj
------------------

.. rubric:: REQUIREMENT:

The `<blub.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__
header file shall provide the object ``obj``.

.. rubric:: BRIEF DESCRIPTION:

The obj brief.

.. rubric:: INTERFACE:

.. code-block:: c

    extern int obj;

.. rubric:: DESCRIPTION:

Description.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfRegBlock:

spec:/rtems/if/reg-block
------------------------

.. rubric:: REQUIREMENT:

The `<blub.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__
header file shall provide the register block ``reg_block``.

.. rubric:: BRIEF DESCRIPTION:

This structure defines the Reg Block register block memory map.

.. rubric:: REGISTER BLOCK:

.. table::
    :class: longtable
    :widths: 20,80

    +-+-+
    | Offset | Register |
    +=+=+
    | 0x0 | REG_BLOCK_A |
    +-+-+
    | 0x4 | REG_BLOCK_B[ 4 ] |
    +-+-+
    | 0x100 | REG_BLOCK_2[ 16 ] |
    +-+-+

.. rubric:: REGISTER REG_BLOCK_A:

.. table::
    :class: longtable
    :widths: 20,80

    +-+-+
    | Bits [0:31] | REG_BLOCK_A bits. |
    +=+=+
    | 1 | BIT_A |
    +-+-+

.. rubric:: REGISTER REG_BLOCK_B:

.. table::
    :class: longtable
    :widths: 20,80

    +-+-+
    | Bits [0:7] | REG_BLOCK_B bits. |
    +-+-+

.. rubric:: SOFTWARE DESIGN:

This register block is realised by the software design element `reg_block </pkg/doc-ddf-sdd/html/group__RegBlock.html#ga4b1fce841b275741376210bf36459e32>`__.

.. rubric:: GROUP MEMBERSHIP:

This register block is a member of the interface group `Blub
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__.

.. rubric:: INTERFACE PLACEMENT:

This register block is placed into the header file `<blub.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__.

.. rubric:: VALIDATION:

This register block is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfRegBlock2:

spec:/rtems/if/reg-block-2
--------------------------

.. rubric:: REQUIREMENT:

The `<blub.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__
header file shall provide the register block ``reg_block_2``.

.. rubric:: BRIEF DESCRIPTION:

This structure defines the Reg Block 2 register block memory map.

.. rubric:: REGISTER BLOCK:

.. table::
    :class: longtable
    :widths: 20,80

    +-+-+
    | Offset | Register |
    +=+=+
    | 0x0 | REG_BLOCK_2_A |
    +-+-+
    | 0x4 | REG_BLOCK_2_B |
    +-+-+

.. rubric:: REGISTER REG_BLOCK_2_A:

.. table::
    :class: longtable
    :widths: 20,80

    +-+-+
    | Bits [0:31] | REG_BLOCK_2_A bits. |
    +=+=+
    | [0:31] | BITS_A |
    +-+-+

.. rubric:: REGISTER REG_BLOCK_2_B:

.. table::
    :class: longtable
    :widths: 20,80

    +-+-+
    | Bits [0:31] | REG_BLOCK_2_B bits. |
    +=+=+
    | [27:31] | BITS_B |
    +-+-+

.. rubric:: SOFTWARE DESIGN:

This register block is realised by the software design element `reg_block_2 </pkg/doc-ddf-sdd/html/group__RegBlock2.html#ga70a56c32b62caff7efa73f98f038320d>`__.

.. rubric:: GROUP MEMBERSHIP:

This register block is a member of the interface group `Blub
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__.

.. rubric:: INTERFACE PLACEMENT:

This register block is placed into the header file `<blub.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__.

.. rubric:: VALIDATION:

This register block is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfStruct:

spec:/rtems/if/struct
---------------------

.. rubric:: REQUIREMENT:

The `<blub.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__
header file shall provide the structure ``Struct``.

.. rubric:: BRIEF DESCRIPTION:

The Struct brief.

.. rubric:: INTERFACE:

.. code-block:: c

    typedef struct {
      int b;
    } Struct;

.. rubric:: MEMBERS:

a
    The Struct member.

.. rubric:: DESCRIPTION:

Description.

.. rubric:: SOFTWARE DESIGN:

This structure is realised by the software design element `Struct </pkg/doc-ddf-sdd/html/structStruct.html>`__.

.. rubric:: GROUP MEMBERSHIP:

This structure is a member of the interface group `Blub
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__.

.. rubric:: INTERFACE PLACEMENT:

This structure is placed into the header file `<blub.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__.

.. rubric:: VALIDATION:

This structure is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfStructBoth:

spec:/rtems/if/struct-both
--------------------------

.. rubric:: REQUIREMENT:

The `<blub.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__
header file shall provide the structure ``StructBoth``.

.. rubric:: BRIEF DESCRIPTION:

The StructBoth brief.

.. rubric:: INTERFACE:

.. code-block:: c

    typedef struct StructBoth {
      int a;
    } StructBoth;

.. rubric:: MEMBERS:

a
    The StructBoth member. Description.

.. rubric:: DESCRIPTION:

Description.

.. rubric:: SOFTWARE DESIGN:

This structure is realised by the software design element `StructBoth </pkg/doc-ddf-sdd/html/group__Blub.html#gafc3408bd38e181fb80afd4d06fec20ff>`__.

.. rubric:: GROUP MEMBERSHIP:

This structure is a member of the interface group `Blub
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__.

.. rubric:: INTERFACE PLACEMENT:

This structure is placed into the header file `<blub.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__.

.. rubric:: VALIDATION:

This structure is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfStructOnly:

spec:/rtems/if/struct-only
--------------------------

.. rubric:: REQUIREMENT:

The `<blub.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__
header file shall provide the structure ``StructOnly``.

.. rubric:: BRIEF DESCRIPTION:

The StructOnly brief.

.. rubric:: INTERFACE:

.. code-block:: c

    struct StructOnly {
      int a;
    };

.. rubric:: MEMBERS:

a
    The StructOnly member. Description.

.. rubric:: DESCRIPTION:

Description.

.. rubric:: SOFTWARE DESIGN:

This structure is realised by the software design element `StructOnly </pkg/doc-ddf-sdd/html/structStructOnly.html>`__.

.. rubric:: GROUP MEMBERSHIP:

This structure is a member of the interface group `Blub
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__.

.. rubric:: INTERFACE PLACEMENT:

This structure is placed into the header file `<blub.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__.

.. rubric:: VALIDATION:

This structure is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfTypedef:

spec:/rtems/if/typedef
----------------------

.. rubric:: REQUIREMENT:

The `<blub.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__
header file shall provide the type definition ``Typedef``.

.. rubric:: BRIEF DESCRIPTION:

Typedef brief.

.. rubric:: INTERFACE:

.. code-block:: c

    typedef int Typedef;

.. rubric:: SOFTWARE DESIGN:

This type definition is realised by the software design element `Typedef </pkg/doc-ddf-sdd/html/group__Blub.html#gaedec7b8d93c84ed3293e685c1e0b444e>`__.

.. rubric:: GROUP MEMBERSHIP:

This type definition is a member of the interface group `Blub
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__.

.. rubric:: INTERFACE PLACEMENT:

This type definition is placed into the header file `<blub.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__.

.. rubric:: VALIDATION:

This type definition is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfUnion:

spec:/rtems/if/union
--------------------

.. rubric:: REQUIREMENT:

The `<blub.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__
header file shall provide the union ``Union``.

.. rubric:: BRIEF DESCRIPTION:

The Union brief.

.. rubric:: INTERFACE:

.. code-block:: c

    typedef union {
      int a;
    } Union;

.. rubric:: MEMBERS:

a
    The Union member. Description.

.. rubric:: DESCRIPTION:

Description.

.. rubric:: SOFTWARE DESIGN:

This union is realised by the software design element `Union </pkg/doc-ddf-sdd/html/unionUnion.html>`__.

.. rubric:: GROUP MEMBERSHIP:

This union is a member of the interface group `Blub
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__.

.. rubric:: INTERFACE PLACEMENT:

This union is placed into the header file `<blub.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__.

.. rubric:: VALIDATION:

This union is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfUnionBoth:

spec:/rtems/if/union-both
-------------------------

.. rubric:: REQUIREMENT:

The `<blub.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__
header file shall provide the union ``UnionBoth``.

.. rubric:: BRIEF DESCRIPTION:

The UnionBoth brief.

.. rubric:: INTERFACE:

.. code-block:: c

    typedef union UnionBoth {
      int a;
    } UnionBoth;

.. rubric:: MEMBERS:

a
    The UnionBoth member. Description.

.. rubric:: DESCRIPTION:

Description.

.. rubric:: SOFTWARE DESIGN:

This union is realised by the software design element `UnionBoth </pkg/doc-ddf-sdd/html/group__Blub.html#ga82983277a27d470f93cb6843cc648a4a>`__.

.. rubric:: GROUP MEMBERSHIP:

This union is a member of the interface group `Blub
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__.

.. rubric:: INTERFACE PLACEMENT:

This union is placed into the header file `<blub.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__.

.. rubric:: VALIDATION:

This union is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfUnionOnly:

spec:/rtems/if/union-only
-------------------------

.. rubric:: REQUIREMENT:

The `<blub.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__
header file shall provide the union ``UnionOnly``.

.. rubric:: BRIEF DESCRIPTION:

The UnionOnly brief.

.. rubric:: INTERFACE:

.. code-block:: c

    union UnionOnly {
    };

.. rubric:: DESCRIPTION:

Description.

.. rubric:: SOFTWARE DESIGN:

This union is realised by the software design element `UnionOnly </pkg/doc-ddf-sdd/html/unionUnionOnly.html>`__.

.. rubric:: GROUP MEMBERSHIP:

This union is a member of the interface group `Blub
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__.

.. rubric:: INTERFACE PLACEMENT:

This union is placed into the header file `<blub.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__.

.. rubric:: VALIDATION:

This union is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfUnspecDefine:

spec:/rtems/if/unspec-define
----------------------------

.. rubric:: REQUIREMENT:

The `<bar/more/unspec.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__
header file shall provide the define ``UnspecDefine``.

.. rubric:: INTERFACE:

.. code-block:: c

    #define UnspecDefine ...

.. rubric:: SOFTWARE DESIGN:

This define is realised by the software design element `UnspecDefine </pkg/doc-ddf-sdd/html/group__UnspecGroup.html#gaabbf1afe2cb904ecf7ad8c8c0b6994e9>`__.

.. rubric:: GROUP MEMBERSHIP:

This define is a member of the group `UnspecGroup
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecgroup>`__.

.. rubric:: INTERFACE PLACEMENT:

This define is placed into the header file `<bar/more/unspec.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__.

.. rubric:: VALIDATION:

This define is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfUnspecEnum:

spec:/rtems/if/unspec-enum
--------------------------

.. rubric:: REQUIREMENT:

The `<bar/more/unspec.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__
header file shall provide the enumeration ``enum UnspecEnum``.

.. rubric:: INTERFACE:

.. code-block:: c

    enum UnspecEnum { ... };

.. rubric:: SOFTWARE DESIGN:

This enumeration is realised by the software design element `enum UnspecEnum </pkg/doc-ddf-sdd/html/group__UnspecGroup.html#gab5f1de454010298047053bb570003d66>`__.

.. rubric:: GROUP MEMBERSHIP:

This enumeration is a member of the group `UnspecGroup
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecgroup>`__.

.. rubric:: INTERFACE PLACEMENT:

This enumeration is placed into the header file `<bar/more/unspec.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__.

.. rubric:: VALIDATION:

This enumeration is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfUnspecEnumerator:

spec:/rtems/if/unspec-enumerator
--------------------------------

.. rubric:: REQUIREMENT:

The `<bar/more/unspec.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__
header file shall provide the enumerator ``UnspecEnumerator``.

.. rubric:: INTERFACE:

.. code-block:: c

    enum ... {
      ....
      UnspecEnumerator ...
      ....
    };

.. rubric:: SOFTWARE DESIGN:

This enumerator is realised by the software design element `UnspecEnumerator </pkg/doc-ddf-sdd/html/group__UnspecGroup.html#ggab5f1de454010298047053bb570003d66af6ed886e2b1b97a47752a5860507e740>`__.

.. rubric:: GROUP MEMBERSHIP:

This enumerator is a member of the group `UnspecGroup
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecgroup>`__.

.. rubric:: INTERFACE PLACEMENT:

This enumerator is placed into the header file `<bar/more/unspec.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__.

.. rubric:: VALIDATION:

This enumerator is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfUnspecFunction:

spec:/rtems/if/unspec-function
------------------------------

.. rubric:: REQUIREMENT:

The `<bar/more/unspec.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__
header file shall provide the directive ``UnspecFunction()``.

.. rubric:: INTERFACE:

.. code-block:: c

    ... UnspecFunction( ... );

.. rubric:: SOFTWARE DESIGN:

This directive is realised by the software design element `UnspecFunction() </pkg/doc-ddf-sdd/html/group__UnspecGroup.html#gabf4d4a492e6cbd36fc586f533006983d>`__.

.. rubric:: GROUP MEMBERSHIP:

This directive is a member of the group `UnspecGroup
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecgroup>`__.

.. rubric:: INTERFACE PLACEMENT:

This directive is placed into the header file `<bar/more/unspec.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__.

.. rubric:: INTERFACE FUNCTIONS:

The function of this directive is specified by the following items:

- `spec:/​rtems/​req/​action
  </pkg/doc-ts-srs/html/requirements.html#specrtemsreqaction>`__

- `spec:/​rtems/​req/​action-2
  </pkg/doc-ts-srs/html/requirements.html#specrtemsreqaction2>`__

.. rubric:: VALIDATIONS:

The validation of this **not validated** directive depends on the following
items:

- `spec:/​rtems/​req/​action
  </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsreqaction>`__
  (**not validated** interface function)

- `spec:/​rtems/​req/​action-2
  </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsreqaction2>`__
  (**not validated** interface function)

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfUnspecGroup:

spec:/rtems/if/unspec-group
---------------------------

.. rubric:: REQUIREMENT:

The `<bar/more/unspec.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__
header file shall provide the group ``UnspecGroup``.

.. rubric:: GROUP MEMBERSHIPS:

This group is a member of the interface group `Blub
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__.

This group contains the following items:

- `uint32_t
  </pkg/doc-ts-icd/html/requirements-and-design.html#speccifuint32t>`__

- `BLUB
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdefineduplicate>`__

- `BLUB
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdefinesecondduplicate>`__

- `UnspecDefine
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecdefine>`__

- `enum UnspecEnum
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecenum>`__

- `UnspecEnumerator
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecenumerator>`__

- `UnspecFunction()
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecfunction>`__

- `<bar/more/unspec.h>
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__

- `UnspecMacro()
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecmacro>`__

- `UnspecObject
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecobject>`__

- `struct UnspecStruct
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecstruct>`__

- `UnspecTypedef
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspectypedef>`__

- `union UnspecUnion
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecunion>`__

.. rubric:: INTERFACE PLACEMENT:

This group is placed into the header file `<bar/more/unspec.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__.

.. rubric:: VALIDATIONS:

The validation of this **not validated** group depends on the following items:

- `uint32_t
  </pkg/doc-ts-icd/html/requirements-and-design.html#speccifuint32t>`__
  (**not validated** group member)

- `BLUB
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdefineduplicate>`__
  (**not validated** group member)

- `BLUB
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdefinesecondduplicate>`__
  (**not validated** group member)

- `UnspecDefine
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecdefine>`__
  (**not validated** group member)

- `enum UnspecEnum
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecenum>`__
  (**not validated** group member)

- `UnspecEnumerator
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecenumerator>`__
  (**not validated** group member)

- `UnspecFunction()
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecfunction>`__
  (**not validated** group member)

- `<bar/more/unspec.h>
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__
  (**not validated** group member)

- `UnspecMacro()
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecmacro>`__
  (**not validated** group member)

- `UnspecObject
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecobject>`__
  (**not validated** group member)

- `struct UnspecStruct
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecstruct>`__
  (**not validated** group member)

- `UnspecTypedef
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspectypedef>`__
  (**not validated** group member)

- `union UnspecUnion
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecunion>`__
  (**not validated** group member)

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfUnspecHeader:

spec:/rtems/if/unspec-header
----------------------------

.. rubric:: REQUIREMENT:

The `Domain
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdomain>`__
interface domain shall provide the header file ``<bar/more/unspec.h>``.

.. rubric:: INTERFACE:

.. code-block:: c

    #include <bar/more/unspec.h>

.. rubric:: GROUP MEMBERSHIP:

This header file is a member of the group `UnspecGroup
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecgroup>`__.

.. rubric:: INTERFACE PLACEMENTS:

This header file is placed into the interface domain `Domain
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdomain>`__.

This header file contains the following items:

- `uint32_t
  </pkg/doc-ts-icd/html/requirements-and-design.html#speccifuint32t>`__

- `BLUB
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdefineduplicate>`__

- `BLUB
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdefinesecondduplicate>`__

- `UnspecDefine
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecdefine>`__

- `enum UnspecEnum
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecenum>`__

- `UnspecEnumerator
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecenumerator>`__

- `UnspecFunction()
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecfunction>`__

- `UnspecGroup
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecgroup>`__

- `UnspecMacro()
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecmacro>`__

- `UnspecObject
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecobject>`__

- `struct UnspecStruct
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecstruct>`__

- `UnspecTypedef
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspectypedef>`__

- `union UnspecUnion
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecunion>`__

.. rubric:: VALIDATIONS:

The validation of this **not validated** header file depends on the following
items:

- `uint32_t
  </pkg/doc-ts-icd/html/requirements-and-design.html#speccifuint32t>`__
  (**not validated** interface placement)

- `BLUB
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdefineduplicate>`__
  (**not validated** interface placement)

- `BLUB
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdefinesecondduplicate>`__
  (**not validated** interface placement)

- `UnspecDefine
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecdefine>`__
  (**not validated** interface placement)

- `enum UnspecEnum
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecenum>`__
  (**not validated** interface placement)

- `UnspecEnumerator
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecenumerator>`__
  (**not validated** interface placement)

- `UnspecFunction()
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecfunction>`__
  (**not validated** interface placement)

- `UnspecGroup
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecgroup>`__
  (**not validated** interface placement)

- `UnspecMacro()
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecmacro>`__
  (**not validated** interface placement)

- `UnspecObject
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecobject>`__
  (**not validated** interface placement)

- `struct UnspecStruct
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecstruct>`__
  (**not validated** interface placement)

- `UnspecTypedef
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspectypedef>`__
  (**not validated** interface placement)

- `union UnspecUnion
  </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecunion>`__
  (**not validated** interface placement)

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfUnspecMacro:

spec:/rtems/if/unspec-macro
---------------------------

.. rubric:: REQUIREMENT:

The `<bar/more/unspec.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__
header file shall provide the macro ``UnspecMacro()``.

.. rubric:: INTERFACE:

.. code-block:: c

    ... UnspecMacro( ... );

.. rubric:: SOFTWARE DESIGN:

This macro is realised by the software design element `UnspecMacro() </pkg/doc-ddf-sdd/html/group__UnspecGroup.html#ga328c9728fbb436652a38e6790d740b54>`__.

.. rubric:: GROUP MEMBERSHIP:

This macro is a member of the group `UnspecGroup
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecgroup>`__.

.. rubric:: INTERFACE PLACEMENT:

This macro is placed into the header file `<bar/more/unspec.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__.

.. rubric:: VALIDATION:

This macro is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfUnspecObject:

spec:/rtems/if/unspec-object
----------------------------

.. rubric:: REQUIREMENT:

The `<bar/more/unspec.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__
header file shall provide the object ``UnspecObject``.

.. rubric:: INTERFACE:

.. code-block:: c

    extern ... UnspecObject ...;

.. rubric:: SOFTWARE DESIGN:

This object is realised by the software design element `UnspecObject </pkg/doc-ddf-sdd/html/group__UnspecGroup.html#gacae496f6007d3f6dace628662204fb51>`__.

.. rubric:: GROUP MEMBERSHIP:

This object is a member of the group `UnspecGroup
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecgroup>`__.

.. rubric:: INTERFACE PLACEMENT:

This object is placed into the header file `<bar/more/unspec.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__.

.. rubric:: VALIDATION:

This object is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfUnspecStruct:

spec:/rtems/if/unspec-struct
----------------------------

.. rubric:: REQUIREMENT:

The `<bar/more/unspec.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__
header file shall provide the type ``struct UnspecStruct``.

.. rubric:: INTERFACE:

.. code-block:: c

    struct UnspecStruct { ... };

.. rubric:: SOFTWARE DESIGN:

This type is realised by the software design element `struct UnspecStruct </pkg/doc-ddf-sdd/html/structUnspecStruct.html>`__.

.. rubric:: GROUP MEMBERSHIP:

This type is a member of the group `UnspecGroup
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecgroup>`__.

.. rubric:: INTERFACE PLACEMENT:

This type is placed into the header file `<bar/more/unspec.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__.

.. rubric:: VALIDATION:

This type is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfUnspecTypedef:

spec:/rtems/if/unspec-typedef
-----------------------------

.. rubric:: REQUIREMENT:

The `<bar/more/unspec.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__
header file shall provide the type definition ``UnspecTypedef``.

.. rubric:: INTERFACE:

.. code-block:: c

    typedef ... UnspecTypedef ...;

.. rubric:: SOFTWARE DESIGN:

This type definition is realised by the software design element `UnspecTypedef </pkg/doc-ddf-sdd/html/group__UnspecGroup.html#gad2a639b23130f7fc86a53a26bb0d95d1>`__.

.. rubric:: GROUP MEMBERSHIP:

This type definition is a member of the group `UnspecGroup
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecgroup>`__.

.. rubric:: INTERFACE PLACEMENT:

This type definition is placed into the header file `<bar/more/unspec.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__.

.. rubric:: VALIDATION:

This type definition is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfUnspecUnion:

spec:/rtems/if/unspec-union
---------------------------

.. rubric:: REQUIREMENT:

The `<bar/more/unspec.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__
header file shall provide the type ``union UnspecUnion``.

.. rubric:: INTERFACE:

.. code-block:: c

    union UnspecUnion { ... };

.. rubric:: SOFTWARE DESIGN:

This type is realised by the software design element `union UnspecUnion </pkg/doc-ddf-sdd/html/unionUnspecUnion.html>`__.

.. rubric:: GROUP MEMBERSHIP:

This type is a member of the group `UnspecGroup
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecgroup>`__.

.. rubric:: INTERFACE PLACEMENT:

This type is placed into the header file `<bar/more/unspec.h>
</pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__.

.. rubric:: VALIDATION:

This type is **not validated**.
.. icd-requirements-and-design end"""
