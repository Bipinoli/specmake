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

Requirement
    The software product shall provide an API.

Refines
    This interface requirement refines the design requirement `spec:/​req/​root
    </pkg/doc-ts-srs/html/requirements.html#specreqroot>`__.

Refined by
    This interface requirement is refined by the following items:

    - `Blub
      </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__

    - `Blub2
      </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup2>`__

    - `A
      </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroupa>`__

    - `B
      </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroupb>`__

Validations
    The validation of this **not validated** interface requirement depends on
    the following items:

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

Requirement
    The `<bar/more/unspec.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__
    header file shall provide the type definition ``uint32_t``.

Interface
    .. code-block:: c

        typedef ... uint32_t ...;

Group membership
    This type definition is a member of the group `UnspecGroup
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecgroup>`__.

Interface placement
    This type definition is placed into the header file `<bar/more/unspec.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__.

Validation
    This type definition is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfAcfgInteger:

spec:/rtems/if/acfg-integer
---------------------------

Requirement
    The `Domain
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdomain>`__
    interface domain shall provide the application configuration option
    ``CONFIGURE_INTEGER``.

Option type
    This configuration option is an integer define.

Default value
    The default value is 0.

Description
    Integer configuration option description.

Constraints
    The configuration option is not included in the pre-qualified feature set
    of RTEMS.  Applications which are restricted to only use interfaces of the
    pre-qualified feature set of RTEMS shall not use the configuration option.

Software design
    This application configuration option is realised by the software design element `CONFIGURE_INTEGER </pkg/doc-ddf-sdd/html/group__RTEMSApplConfigSomethingConfiguration.html#ga714d5d7419c8b6c00f172e9a3c571a9b>`__.

Group membership
    This application configuration option is a member of the application
    configuration group `Something Configuration
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroupacfg>`__.

Interface placement
    This application configuration option is placed into the interface domain
    `Domain
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdomain>`__.

Validation
    This application configuration option is not pre-qualified.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfDefineDuplicate:

spec:/rtems/if/define-duplicate
-------------------------------

Requirement
    The `<bar/more/unspec.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__
    header file shall provide the define ``BLUB``.

Interface
    .. code-block:: c

        #define BLUB ...

Software design
    This define is realised by the software design element `BLUB </pkg/doc-ddf-sdd/html/group__Blub.html#gaf0277526715a0aa6e2ba520cc3399254>`__.

Group membership
    This define is a member of the group `UnspecGroup
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecgroup>`__.

Interface placement
    This define is placed into the header file `<bar/more/unspec.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__.

Validation
    This define is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfDefineNotDefined:

spec:/rtems/if/define-not-defined
---------------------------------

Define not defined brief.

Requirement
    The `<blub.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__
    header file shall provide the define ``DEFINE_NOT_DEFINED``.

Interface
    .. code-block:: c

        #define DEFINE_NOT_DEFINED 

Description
    Define not defined description.

Group membership
    This define is a member of the interface group `Blub
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__.

Interface placement
    This define is placed into the header file `<blub.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__.

Interface function
    The function of this define is specified by the interface define
    requirement `spec:/​rtems/​req/​define-not-defined
    </pkg/doc-ts-srs/html/requirements.html#specrtemsreqdefinenotdefined>`__.

Validation
    This **not validated** define is validated by the **not validated** interface function `spec:/​rtems/​req/​define-not-defined </pkg/doc-ts-srs/html/requirements.html#specrtemsreqdefinenotdefined>`__.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfDefineReal:

spec:/rtems/if/define-real
--------------------------

Define brief.

Requirement
    The `<blub.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__
    header file shall provide the define ``BLUB``.

Interface
    .. code-block:: c

        #define BLUB 123

Description
    Define description.

Software design
    This define is realised by the software design element `BLUB </pkg/doc-ddf-sdd/html/group__Blub.html#gaf0277526715a0aa6e2ba520cc3399254>`__.

Refined by
    This define is refined by the test case `spec:/​rtems/​val/​test-case
    </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsvaltestcase>`__.

Group membership
    This define is a member of the interface group `Blub
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__.

Interface placement
    This define is placed into the header file `<blub.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__.

Validation
    This **not validated** define is validated by the **not validated** refinement `spec:/​rtems/​val/​test-case </pkg/doc-djf-svs/html/test-case-specification.html#specrtemsvaltestcase>`__.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfDefineSecondDuplicate:

spec:/rtems/if/define-second-duplicate
--------------------------------------

Requirement
    The `<bar/more/unspec.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__
    header file shall provide the define ``BLUB``.

Interface
    .. code-block:: c

        #define BLUB ...

Software design
    This define is realised by the software design element `BLUB </pkg/doc-ddf-sdd/html/group__Blub.html#gaf0277526715a0aa6e2ba520cc3399254>`__.

Group membership
    This define is a member of the group `UnspecGroup
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecgroup>`__.

Interface placement
    This define is placed into the header file `<bar/more/unspec.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__.

Validation
    This define is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfDomain:

spec:/rtems/if/domain
---------------------

Requirement
    There shall be the interface domain ``Domain``.

Description
    Description.

Refines
    This interface domain refines the design requirement `spec:/​req/​root
    </pkg/doc-ts-srs/html/requirements.html#specreqroot>`__.

Interface members
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

Validations
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

Enum brief.

Requirement
    The `<blub.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__
    header file shall provide the enumeration ``the_enum``.

Interface
    .. code-block:: c

        typedef enum {
          ENUMERATOR,
          ENUMERATOR_2 = 2,
        } the_enum;

Description
    Description.

Software design
    This enumeration is realised by the software design element `the_enum </pkg/doc-ddf-sdd/html/group__Blub.html#ga582a1afc79f3b607104a52d7aa268624>`__.

Enumerators
    This enumeration provides the following items:

    - `ENUMERATOR
      </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifenumerator>`__

    - `ENUMERATOR_2
      </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifenumerator2>`__

Group membership
    This enumeration is a member of the interface group `Blub
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__.

Interface placement
    This enumeration is placed into the header file `<blub.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__.

Validations
    The validation of this **not validated** enumeration depends on the
    following items:

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

Enumerator brief.

Requirement
    The `the_enum
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifenumreal>`__
    enumeration shall provide the enumerator ``ENUMERATOR``.

Interface
    .. code-block:: c

        typedef enum {
          ...
          ENUMERATOR
          ...
        } the_enum;

Description
    Description.

Software design
    This enumerator is realised by the software design element `ENUMERATOR </pkg/doc-ddf-sdd/html/group__Blub.html#gga582a1afc79f3b607104a52d7aa268624a183cf8edbca25c5db49f6fda4224f87a>`__.

Enumerator
    This enumerator is provided by the enumeration `the_enum
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifenumreal>`__.

Validation
    This enumerator is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfEnumerator2:

spec:/rtems/if/enumerator-2
---------------------------

Enumerator 2 brief.

Requirement
    The `the_enum
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifenumreal>`__
    enumeration shall provide the enumerator ``ENUMERATOR_2``.

Interface
    .. code-block:: c

        typedef enum {
          ...
          ENUMERATOR_2 = 2
          ...
        } the_enum;

Description
    Description 2.

Software design
    This enumerator is realised by the software design element `ENUMERATOR_2 </pkg/doc-ddf-sdd/html/group__Blub.html#gga582a1afc79f3b607104a52d7aa268624ac9cedcefbbfbc41195028b42a9830d2f>`__.

Enumerator
    This enumerator is provided by the enumeration `the_enum
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifenumreal>`__.

Validation
    This enumerator is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfForwardDecl:

spec:/rtems/if/forward-decl
---------------------------

Requirement
    The `<blub-2.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader2>`__
    header file shall provide a forward declaration of `StructOnly
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifstructonly>`__.

Interface
    .. code-block:: c

        struct StructOnly;

Group membership
    This forward declaration is a member of the interface group `Blub2
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup2>`__.

Interface placement
    This forward declaration is placed into the header file `<blub-2.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader2>`__.

Validation
    This forward declaration is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfFunc:

spec:/rtems/if/func
-------------------

Brief.

Requirement
    The `<blub.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__
    header file shall provide the directive ``blub()``.

Calling sequence
    .. code-block:: c

        int blub( int param );

Parameters
    .. table::
        :class: longtable
        :widths: 30,70

        +-+-+
        | ``param`` | Parameter. |
        +-+-+

Description
    Description.

Return values
    Returns.

Software design
    This directive is realised by the software design element `blub() </pkg/doc-ddf-sdd/html/group__Blub.html#ga754ccc677acbd87ede8b3c082bb9ff6b>`__.

Group membership
    This directive is a member of the interface group `Blub
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__.

Interface placement
    This directive is placed into the header file `<blub.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__.

Interface functions
    The function of this directive is specified by the following items:

    - `spec:/​rtems/​req/​action-2
      </pkg/doc-ts-srs/html/requirements.html#specrtemsreqaction2>`__

    - `spec:/​rtems/​req/​func
      </pkg/doc-ts-srs/html/requirements.html#specrtemsreqfunc>`__

Validations
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

Brief.

Requirement
    There shall be the interface group ``Blub``.

Description
    Description.

Software design
    This interface group is realised by the software design element `Blub </pkg/doc-ddf-sdd/html/group__Blub.html>`__.

Refines
    This interface group refines the interface requirement `spec:/​req/​api
    </pkg/doc-ts-icd/html/requirements-and-design.html#specreqapi>`__.

Refined by
    This interface group is refined by the following items:

    - `spec:/​rtems/​req/​mem-basic
      </pkg/doc-ts-srs/html/requirements.html#specrtemsreqmembasic>`__

    - `spec:/​rtems/​req/​perf
      </pkg/doc-ts-srs/html/requirements.html#specrtemsreqperf>`__

    - `spec:/​rtems/​req/​perf-no-results
      </pkg/doc-ts-srs/html/requirements.html#specrtemsreqperfnoresults>`__

Group memberships
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

Interface placement
    This interface group is placed into the header file `<blub.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__.

Validations
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

Blub2 brief.

Requirement
    There shall be the interface group ``Blub2``.

Description
    Description.

Software design
    This interface group is realised by the software design element `Blub2 </pkg/doc-ddf-sdd/html/group__Blub2.html>`__.

Refines
    This interface group refines the interface requirement `spec:/​req/​api
    </pkg/doc-ts-icd/html/requirements-and-design.html#specreqapi>`__.

Group memberships
    This interface group contains the following items:

    - `StructOnly
      </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifforwarddecl>`__

    - `A
      </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroupa>`__

    - `B
      </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroupb>`__

    - `<blub-2.h>
      </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader2>`__

Interface placement
    This interface group is placed into the header file `<blub-2.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader2>`__.

Validations
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

Group A brief.

Requirement
    The `Blub2
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup2>`__
    interface group shall contain the interface group ``A``.

Description
    Description.

Software design
    This interface group is realised by the software design element `A </pkg/doc-ddf-sdd/html/group__GroupA.html>`__.

Refines
    This interface group refines the interface requirement `spec:/​req/​api
    </pkg/doc-ts-icd/html/requirements-and-design.html#specreqapi>`__.

Group membership
    This interface group is a member of the interface group `Blub2
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup2>`__.

Interface placement
    This interface group is placed into the header file `<blub-2.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader2>`__.

Validation
    This interface group is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfGroupAcfg:

spec:/rtems/if/group-acfg
-------------------------

Requirement
    The something configuration text.

Description
    Description.

Software design
    This application configuration group is realised by the software design element `Something Configuration </pkg/doc-ddf-sdd/html/group__RTEMSApplConfigSomethingConfiguration.html>`__.

Refines
    This application configuration group refines the design requirement
    `spec:/​req/​root
    </pkg/doc-ts-srs/html/requirements.html#specreqroot>`__.

Group membership
    This application configuration group contains the application configuration
    option `CONFIGURE_INTEGER
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifacfginteger>`__.

Interface placement
    This application configuration group is placed into the interface domain
    `Domain
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdomain>`__.

Validation
    This not pre-qualified application configuration group is validated by the not pre-qualified group member `CONFIGURE_INTEGER </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifacfginteger>`__.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfGroupB:

spec:/rtems/if/group-b
----------------------

Group B brief.

Requirement
    The `Blub2
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup2>`__
    interface group shall contain the interface group ``B``.

Description
    Description.

Software design
    This interface group is realised by the software design element `B </pkg/doc-ddf-sdd/html/group__GroupB.html>`__.

Refines
    This interface group refines the interface requirement `spec:/​req/​api
    </pkg/doc-ts-icd/html/requirements-and-design.html#specreqapi>`__.

Group membership
    This interface group is a member of the interface group `Blub2
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup2>`__.

Interface placement
    This interface group is placed into the header file `<blub-2.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader2>`__.

Validation
    This interface group is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfHeader:

spec:/rtems/if/header
---------------------

Brief.

Requirement
    The `Domain
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdomain>`__
    interface domain shall provide the header file ``<blub.h>``.

Interface
    .. code-block:: c

        #include <blub.h>

Software design
    This header file is realised by the software design element `<blub.h> </pkg/doc-ddf-sdd/html/blub_8h.html>`__.

Group membership
    This header file is a member of the interface group `Blub
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__.

Interface placement
    This header file is placed into the interface domain `Domain
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdomain>`__.

Interface members
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

Interface include
    This header file is included by the header file `<blub-2.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader2>`__.

Validations
    The validation of this **not validated** header file depends on the
    following items:

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

Blub2 header brief.

Requirement
    The `Domain
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdomain>`__
    interface domain shall provide the header file ``<blub-2.h>``.

Interface
    .. code-block:: c

        #include <blub-2.h>

Software design
    This header file is realised by the software design element `<blub-2.h> </pkg/doc-ddf-sdd/html/blub-2_8h.html>`__.

Group membership
    This header file is a member of the interface group `Blub2
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup2>`__.

Interface placement
    This header file is placed into the interface domain `Domain
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdomain>`__.

Interface members
    This header file contains the following items:

    - `StructOnly
      </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifforwarddecl>`__

    - `Blub2
      </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup2>`__

    - `A
      </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroupa>`__

    - `B
      </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroupb>`__

Interface include
    This header file includes the header file `<blub.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__.

Validations
    The validation of this **not validated** header file depends on the
    following items:

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

The obj brief.

Requirement
    The `<blub.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__
    header file shall provide the object ``obj``.

Interface
    .. code-block:: c

        extern int obj;

Description
    Description.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfRegBlock:

spec:/rtems/if/reg-block
------------------------

This structure defines the Reg Block register block memory map.

Requirement
    The `<blub.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__
    header file shall provide the register block ``reg_block``.

.. table::
    :class: longtable
    :widths: 20,80

    +-+-+
    | Register block |
    +-+-+
    | Offset | Register |
    +=+=+
    | 0x0 | REG_BLOCK_A |
    +-+-+
    | 0x4 | REG_BLOCK_B[ 4 ] |
    +-+-+
    | 0x100 | REG_BLOCK_2[ 16 ] |
    +-+-+

.. table::
    :class: longtable
    :widths: 20,80

    +-+-+
    | REG_BLOCK_A (register) |
    +-+-+
    | Bits [0:31] | REG_BLOCK_A bits. |
    +=+=+
    | 1 | BIT_A |
    +-+-+

.. table::
    :class: longtable
    :widths: 20,80

    +-+-+
    | REG_BLOCK_B (register) |
    +-+-+
    | Bits [0:7] | REG_BLOCK_B bits. |
    +-+-+

Software design
    This register block is realised by the software design element `reg_block </pkg/doc-ddf-sdd/html/group__RegBlock.html#ga4b1fce841b275741376210bf36459e32>`__.

Group membership
    This register block is a member of the interface group `Blub
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__.

Interface placement
    This register block is placed into the header file `<blub.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__.

Validation
    This register block is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfRegBlock2:

spec:/rtems/if/reg-block-2
--------------------------

This structure defines the Reg Block 2 register block memory map.

Requirement
    The `<blub.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__
    header file shall provide the register block ``reg_block_2``.

.. table::
    :class: longtable
    :widths: 20,80

    +-+-+
    | Register block |
    +-+-+
    | Offset | Register |
    +=+=+
    | 0x0 | REG_BLOCK_2_A |
    +-+-+
    | 0x4 | REG_BLOCK_2_B |
    +-+-+

.. table::
    :class: longtable
    :widths: 20,80

    +-+-+
    | REG_BLOCK_2_A (register) |
    +-+-+
    | Bits [0:31] | REG_BLOCK_2_A bits. |
    +=+=+
    | [0:31] | BITS_A |
    +-+-+

.. table::
    :class: longtable
    :widths: 20,80

    +-+-+
    | REG_BLOCK_2_B (register) |
    +-+-+
    | Bits [0:31] | REG_BLOCK_2_B bits. |
    +=+=+
    | [27:31] | BITS_B |
    +-+-+

Software design
    This register block is realised by the software design element `reg_block_2 </pkg/doc-ddf-sdd/html/group__RegBlock2.html#ga70a56c32b62caff7efa73f98f038320d>`__.

Group membership
    This register block is a member of the interface group `Blub
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__.

Interface placement
    This register block is placed into the header file `<blub.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__.

Validation
    This register block is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfStruct:

spec:/rtems/if/struct
---------------------

The Struct brief.

Requirement
    The `<blub.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__
    header file shall provide the structure ``Struct``.

Interface
    .. code-block:: c

        typedef struct {
          int b;
        } Struct;

Members
    .. table::
        :class: longtable
        :widths: 30,70

        +-+-+
        | a | The Struct member. |
        +-+-+

Description
    Description.

Software design
    This structure is realised by the software design element `Struct </pkg/doc-ddf-sdd/html/structStruct.html>`__.

Group membership
    This structure is a member of the interface group `Blub
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__.

Interface placement
    This structure is placed into the header file `<blub.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__.

Validation
    This structure is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfStructBoth:

spec:/rtems/if/struct-both
--------------------------

The StructBoth brief.

Requirement
    The `<blub.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__
    header file shall provide the structure ``StructBoth``.

Interface
    .. code-block:: c

        typedef struct StructBoth {
          int a;
        } StructBoth;

Members
    .. table::
        :class: longtable
        :widths: 30,70

        +-+-+
        | a | The StructBoth member. |
        | | Description. |
        +-+-+

Description
    Description.

Software design
    This structure is realised by the software design element `StructBoth </pkg/doc-ddf-sdd/html/group__Blub.html#gafc3408bd38e181fb80afd4d06fec20ff>`__.

Group membership
    This structure is a member of the interface group `Blub
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__.

Interface placement
    This structure is placed into the header file `<blub.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__.

Validation
    This structure is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfStructOnly:

spec:/rtems/if/struct-only
--------------------------

The StructOnly brief.

Requirement
    The `<blub.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__
    header file shall provide the structure ``StructOnly``.

Interface
    .. code-block:: c

        struct StructOnly {
          int a;
        };

Members
    .. table::
        :class: longtable
        :widths: 30,70

        +-+-+
        | a | The StructOnly member. |
        | | Description. |
        +-+-+

Description
    Description.

Software design
    This structure is realised by the software design element `StructOnly </pkg/doc-ddf-sdd/html/structStructOnly.html>`__.

Group membership
    This structure is a member of the interface group `Blub
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__.

Interface placement
    This structure is placed into the header file `<blub.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__.

Validation
    This structure is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfTypedef:

spec:/rtems/if/typedef
----------------------

Typedef brief.

Requirement
    The `<blub.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__
    header file shall provide the type definition ``Typedef``.

Interface
    .. code-block:: c

        typedef int Typedef;

Software design
    This type definition is realised by the software design element `Typedef </pkg/doc-ddf-sdd/html/group__Blub.html#gaedec7b8d93c84ed3293e685c1e0b444e>`__.

Group membership
    This type definition is a member of the interface group `Blub
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__.

Interface placement
    This type definition is placed into the header file `<blub.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__.

Validation
    This type definition is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfUnion:

spec:/rtems/if/union
--------------------

The Union brief.

Requirement
    The `<blub.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__
    header file shall provide the union ``Union``.

Interface
    .. code-block:: c

        typedef union {
          int a;
        } Union;

Members
    .. table::
        :class: longtable
        :widths: 30,70

        +-+-+
        | a | The Union member. |
        | | Description. |
        +-+-+

Description
    Description.

Software design
    This union is realised by the software design element `Union </pkg/doc-ddf-sdd/html/unionUnion.html>`__.

Group membership
    This union is a member of the interface group `Blub
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__.

Interface placement
    This union is placed into the header file `<blub.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__.

Validation
    This union is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfUnionBoth:

spec:/rtems/if/union-both
-------------------------

The UnionBoth brief.

Requirement
    The `<blub.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__
    header file shall provide the union ``UnionBoth``.

Interface
    .. code-block:: c

        typedef union UnionBoth {
          int a;
        } UnionBoth;

Members
    .. table::
        :class: longtable
        :widths: 30,70

        +-+-+
        | a | The UnionBoth member. |
        | | Description. |
        +-+-+

Description
    Description.

Software design
    This union is realised by the software design element `UnionBoth </pkg/doc-ddf-sdd/html/group__Blub.html#ga82983277a27d470f93cb6843cc648a4a>`__.

Group membership
    This union is a member of the interface group `Blub
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__.

Interface placement
    This union is placed into the header file `<blub.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__.

Validation
    This union is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfUnionOnly:

spec:/rtems/if/union-only
-------------------------

The UnionOnly brief.

Requirement
    The `<blub.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__
    header file shall provide the union ``UnionOnly``.

Interface
    .. code-block:: c

        union UnionOnly {
        };

Description
    Description.

Software design
    This union is realised by the software design element `UnionOnly </pkg/doc-ddf-sdd/html/unionUnionOnly.html>`__.

Group membership
    This union is a member of the interface group `Blub
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifgroup>`__.

Interface placement
    This union is placed into the header file `<blub.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifheader>`__.

Validation
    This union is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfUnspecDefine:

spec:/rtems/if/unspec-define
----------------------------

Requirement
    The `<bar/more/unspec.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__
    header file shall provide the define ``UnspecDefine``.

Interface
    .. code-block:: c

        #define UnspecDefine ...

Software design
    This define is realised by the software design element `UnspecDefine </pkg/doc-ddf-sdd/html/group__UnspecGroup.html#gaabbf1afe2cb904ecf7ad8c8c0b6994e9>`__.

Group membership
    This define is a member of the group `UnspecGroup
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecgroup>`__.

Interface placement
    This define is placed into the header file `<bar/more/unspec.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__.

Validation
    This define is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfUnspecEnum:

spec:/rtems/if/unspec-enum
--------------------------

Requirement
    The `<bar/more/unspec.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__
    header file shall provide the enumeration ``enum UnspecEnum``.

Interface
    .. code-block:: c

        enum UnspecEnum { ... };

Software design
    This enumeration is realised by the software design element `enum UnspecEnum </pkg/doc-ddf-sdd/html/group__UnspecGroup.html#gab5f1de454010298047053bb570003d66>`__.

Group membership
    This enumeration is a member of the group `UnspecGroup
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecgroup>`__.

Interface placement
    This enumeration is placed into the header file `<bar/more/unspec.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__.

Validation
    This enumeration is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfUnspecEnumerator:

spec:/rtems/if/unspec-enumerator
--------------------------------

Requirement
    The `<bar/more/unspec.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__
    header file shall provide the enumerator ``UnspecEnumerator``.

Interface
    .. code-block:: c

        enum ... {
          ....
          UnspecEnumerator ...
          ....
        };

Software design
    This enumerator is realised by the software design element `UnspecEnumerator </pkg/doc-ddf-sdd/html/group__UnspecGroup.html#ggab5f1de454010298047053bb570003d66af6ed886e2b1b97a47752a5860507e740>`__.

Group membership
    This enumerator is a member of the group `UnspecGroup
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecgroup>`__.

Interface placement
    This enumerator is placed into the header file `<bar/more/unspec.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__.

Validation
    This enumerator is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfUnspecFunction:

spec:/rtems/if/unspec-function
------------------------------

Requirement
    The `<bar/more/unspec.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__
    header file shall provide the directive ``UnspecFunction()``.

Interface
    .. code-block:: c

        ... UnspecFunction( ... );

Software design
    This directive is realised by the software design element `UnspecFunction() </pkg/doc-ddf-sdd/html/group__UnspecGroup.html#gabf4d4a492e6cbd36fc586f533006983d>`__.

Group membership
    This directive is a member of the group `UnspecGroup
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecgroup>`__.

Interface placement
    This directive is placed into the header file `<bar/more/unspec.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__.

Interface functions
    The function of this directive is specified by the following items:

    - `spec:/​rtems/​req/​action
      </pkg/doc-ts-srs/html/requirements.html#specrtemsreqaction>`__

    - `spec:/​rtems/​req/​action-2
      </pkg/doc-ts-srs/html/requirements.html#specrtemsreqaction2>`__

Validations
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

Requirement
    The `<bar/more/unspec.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__
    header file shall provide the group ``UnspecGroup``.

Group memberships
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

Interface placement
    This group is placed into the header file `<bar/more/unspec.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__.

Validations
    The validation of this **not validated** group depends on the following
    items:

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

Requirement
    The `Domain
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdomain>`__
    interface domain shall provide the header file ``<bar/more/unspec.h>``.

Interface
    .. code-block:: c

        #include <bar/more/unspec.h>

Group membership
    This header file is a member of the group `UnspecGroup
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecgroup>`__.

Interface placement
    This header file is placed into the interface domain `Domain
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifdomain>`__.

Interface members
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

Validations
    The validation of this **not validated** header file depends on the
    following items:

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

Requirement
    The `<bar/more/unspec.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__
    header file shall provide the macro ``UnspecMacro()``.

Interface
    .. code-block:: c

        ... UnspecMacro( ... );

Software design
    This macro is realised by the software design element `UnspecMacro() </pkg/doc-ddf-sdd/html/group__UnspecGroup.html#ga328c9728fbb436652a38e6790d740b54>`__.

Group membership
    This macro is a member of the group `UnspecGroup
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecgroup>`__.

Interface placement
    This macro is placed into the header file `<bar/more/unspec.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__.

Validation
    This macro is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfUnspecObject:

spec:/rtems/if/unspec-object
----------------------------

Requirement
    The `<bar/more/unspec.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__
    header file shall provide the object ``UnspecObject``.

Interface
    .. code-block:: c

        extern ... UnspecObject ...;

Software design
    This object is realised by the software design element `UnspecObject </pkg/doc-ddf-sdd/html/group__UnspecGroup.html#gacae496f6007d3f6dace628662204fb51>`__.

Group membership
    This object is a member of the group `UnspecGroup
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecgroup>`__.

Interface placement
    This object is placed into the header file `<bar/more/unspec.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__.

Validation
    This object is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfUnspecStruct:

spec:/rtems/if/unspec-struct
----------------------------

Requirement
    The `<bar/more/unspec.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__
    header file shall provide the type ``struct UnspecStruct``.

Interface
    .. code-block:: c

        struct UnspecStruct { ... };

Software design
    This type is realised by the software design element `struct UnspecStruct </pkg/doc-ddf-sdd/html/structUnspecStruct.html>`__.

Group membership
    This type is a member of the group `UnspecGroup
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecgroup>`__.

Interface placement
    This type is placed into the header file `<bar/more/unspec.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__.

Validation
    This type is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfUnspecTypedef:

spec:/rtems/if/unspec-typedef
-----------------------------

Requirement
    The `<bar/more/unspec.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__
    header file shall provide the type definition ``UnspecTypedef``.

Interface
    .. code-block:: c

        typedef ... UnspecTypedef ...;

Software design
    This type definition is realised by the software design element `UnspecTypedef </pkg/doc-ddf-sdd/html/group__UnspecGroup.html#gad2a639b23130f7fc86a53a26bb0d95d1>`__.

Group membership
    This type definition is a member of the group `UnspecGroup
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecgroup>`__.

Interface placement
    This type definition is placed into the header file `<bar/more/unspec.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__.

Validation
    This type definition is **not validated**.

.. raw:: latex

    \\clearpage

.. _SpecRtemsIfUnspecUnion:

spec:/rtems/if/unspec-union
---------------------------

Requirement
    The `<bar/more/unspec.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__
    header file shall provide the type ``union UnspecUnion``.

Interface
    .. code-block:: c

        union UnspecUnion { ... };

Software design
    This type is realised by the software design element `union UnspecUnion </pkg/doc-ddf-sdd/html/unionUnspecUnion.html>`__.

Group membership
    This type is a member of the group `UnspecGroup
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecgroup>`__.

Interface placement
    This type is placed into the header file `<bar/more/unspec.h>
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifunspecheader>`__.

Validation
    This type is **not validated**.
.. icd-requirements-and-design end"""
