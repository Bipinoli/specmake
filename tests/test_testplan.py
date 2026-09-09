# SPDX-License-Identifier: BSD-2-Clause
""" Tests for the testplanbuilder module. """

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

from pathlib import Path

import specmake
from specmake import RTEMSItemCache, TestRunner, TestPlanBuilder

from .util import create_package, get_document_text

TestPlanBuilder.__test__ = False
TestRunner.__test__ = False


def _run_command(args, cwd=None, stdout=None):
    return 0


def test_testplanbuilder(caplog, tmp_path, monkeypatch):
    monkeypatch.setattr(specmake.sphinxbuilder, "run_command", _run_command)
    package = create_package(caplog, tmp_path, Path("spec-packagebuild"), [
        "aggregate-test-results", "djf-svs", "link-hub", "run-tests",
        "test-plan"
    ])
    director = package.director
    director.factory.add_constructor("pkg/test-runner/test", TestRunner)
    director.build_package()
    svs_build = Path(director["/pkg/build/doc-djf-svs"].directory)
    svs_index = svs_build / "source" / "index.rst"
    assert get_document_text(
        tmp_path, svs_index) == """.. SPDX-License-Identifier: CC-BY-SA-4.0

.. Copyright (C) 2025 embedded brains GmbH & Co. KG

.. test-suites begin

.. test-suites end

.. test-cases begin

.. test-cases end

.. test-procedures begin
.. _SpecPkgTestRunnerSubprocess:

Subprocess
==========

For each test program (indicated by ``${test_program}``),
this test procedure runs the following command as a subprocess on the machine
building the package and captures the output:

.. code-block:: none

    foo --on 1 bar ${test_program}
.. test-procedures end

.. other-validations begin
.. _ValidationByAnalysis:

Validation by analysis
======================

This section lists validation evidence obtained by using the analysis validation method.

.. _SpecRtemsValByAnalysis:

spec:/rtems/val/by-analysis
---------------------------

Analysis
    The analysis.

Validated item
    This validation by analysis validates the runtime performance requirement
    `spec:/​rtems/​req/​perf
    </pkg/doc-ts-srs/html/requirements.html#specrtemsreqperf>`__.

.. _ValidationByInspection:

Validation by inspection
========================

This section lists validation evidence obtained by using the inspection validation method.

.. _SpecRtemsValByInspection:

spec:/rtems/val/by-inspection
-----------------------------

Inspection
    The inspection.

Validated item
    This validation by inspection validates the runtime performance requirement
    `spec:/​rtems/​req/​perf
    </pkg/doc-ts-srs/html/requirements.html#specrtemsreqperf>`__.

.. _ValidationByReviewOfDesign:

Validation by review of design
==============================

This section lists validation evidence obtained by using the review of design validation method.

.. _SpecRtemsValByReviewOfDesign:

spec:/rtems/val/by-review-of-design
-----------------------------------

Review of design
    The review of design.

Validated item
    This validation by review of design validates the runtime performance
    requirement `spec:/​rtems/​req/​perf
    </pkg/doc-ts-srs/html/requirements.html#specrtemsreqperf>`__.
.. other-validations end

.. not-validated-by-test begin
The following items are not specifically validated by a test:

- `spec:/​rtems/​req/​perf
  </pkg/doc-ts-srs/html/requirements.html#specrtemsreqperf>`__
.. not-validated-by-test end"""

    spec = director["/pkg/steps/rtems-item-cache"]
    assert isinstance(spec, RTEMSItemCache)
    by_analysis = director.item_cache["/rtems/val/by-analysis"]
    spec.related_items.remove(by_analysis)
    spec.related_items_by_type[by_analysis.type].remove(by_analysis)
    director.build_package(force=["/pkg/deployment/doc-test-plan"])
    tp_build = Path(director["/pkg/build/doc-test-plan"].directory)
    tp_index = tp_build / "source" / "index.rst"
    assert get_document_text(
        tmp_path, tp_index) == """.. SPDX-License-Identifier: CC-BY-SA-4.0

.. Copyright (C) 2025 embedded brains GmbH & Co. KG

.. test-suites begin
.. _SpecRtemsValMemBasic:

spec:/rtems/val/mem-basic
=========================

.. _SpecRtemsValMemBasicGeneral:

General
-------

Description
    This static memory usage benchmark program facilitates a basic application
    configuration using `CONFIGURE_INTEGER
    </pkg/doc-ts-icd/html/requirements-and-design.html#specrtemsifacfginteger>`__.

    This resource benchmark is configured for exactly one processor, no clock
    driver, no Newlib reentrancy support, and no file system.

.. _SpecRtemsValMemBasicFeaturesToBeTested:

Features to be tested
---------------------

Memory usage
benchmarks contain no test cases.  They are not executed on the
:term:`target`.  Instead the generated :term:`ELF` file
is analysed to gather the memory usage of sections and data structures.  The
analysis results are presented in the
*Package Manual* :cite:`PkgDeploymentDocPackageManual`.

.. _SpecRtemsValMemBasicApproachRefinements:

Approach refinements
--------------------

There are no approach refinements
necessary.  The test suite is implemented in the file
`tests/mem-rtems-basic.c </pkg/doc-ddf-sdd/html/mem-rtems-basic_8c.html>`__.

.. _SpecTestsuitesPerformanceNoClock0:

spec:/testsuites/performance-no-clock-0
=======================================

.. _SpecTestsuitesPerformanceNoClock0General:

General
-------

Description
    Brief.

    Description.

Test results
    For this test suite, the following test results are available:

    - `Target - Name Target A / Configuration - Build Configuration Name
      </a-build-config-key-testsuites-performance-no-clock-0.html#abuildconfigkeytestsuitesperformancenoclock0>`__

.. _SpecTestsuitesPerformanceNoClock0FeaturesToBeTested:

Features to be tested
---------------------

The features to be tested are defined by the following test cases:

- :ref:`spec:/​rtems/​req/​perf <SpecRtemsReqPerf>`

- :ref:`spec:/​rtems/​req/​perf-no-results <SpecRtemsReqPerfNoResults>`

- :ref:`spec:/​rtems/​val/​test-case <SpecRtemsValTestCase>`

- :ref:`spec:/​score/​cpu/​val/​perf <SpecScoreCpuValPerf>`

.. _SpecTestsuitesPerformanceNoClock0ApproachRefinements:

Approach refinements
--------------------

There are no approach refinements
necessary.  The test suite is implemented in the file
`tests/ts-blub.c </pkg/doc-ddf-sdd/html/ts-blub_8c.html>`__.

.. _SpecTestsuitesTestSuiteEmpty:

spec:/testsuites/test-suite-empty
=================================

.. _SpecTestsuitesTestSuiteEmptyGeneral:

General
-------

Description
    Brief.

    Description.

Test results
    There are no test results available.

.. _SpecTestsuitesTestSuiteEmptyFeaturesToBeTested:

Features to be tested
---------------------

The test suite contains no specified test cases.

.. _SpecTestsuitesTestSuiteEmptyApproachRefinements:

Approach refinements
--------------------

There are no approach refinements
necessary.  The test suite is implemented in the file
`tests/ts-empty.c </pkg/doc-ddf-sdd/html/ts-empty_8c.html>`__.

.. _SpecTestsuitesTestSuiteFail:

spec:/testsuites/test-suite-fail
================================

.. _SpecTestsuitesTestSuiteFailGeneral:

General
-------

Description
    Brief.

    Description.

Test results
    For this test suite, the following test results are available:

    - `Target - Name Target A / Configuration - Build Configuration Name
      </a-build-config-key-testsuites-test-suite-fail.html#abuildconfigkeytestsuitestestsuitefail>`__

.. _SpecTestsuitesTestSuiteFailFeaturesToBeTested:

Features to be tested
---------------------

The features to be tested are defined by the following test cases:

- :ref:`spec:/​rtems/​req/​action <SpecRtemsReqAction>`

- :ref:`spec:/​rtems/​req/​action-2 <SpecRtemsReqAction2>`

- :ref:`spec:/​rtems/​val/​test-case <SpecRtemsValTestCase>`

- :ref:`spec:/​rtems/​val/​test-case-fail <SpecRtemsValTestCaseFail>`

- :ref:`spec:/​rtems/​val/​test-case-run <SpecRtemsValTestCaseRun>`

.. _SpecTestsuitesTestSuiteFailApproachRefinements:

Approach refinements
--------------------

There are no approach refinements
necessary.  The test suite is implemented in the file
`tests/ts-fail.c </pkg/doc-ddf-sdd/html/ts-fail_8c.html>`__.

.. _SpecTestsuitesTestSuitePass:

spec:/testsuites/test-suite-pass
================================

.. _SpecTestsuitesTestSuitePassGeneral:

General
-------

Description
    Brief.

    Description.

Test results
    For this test suite, the following test results are available:

    - `Target - Name Target A / Configuration - Build Configuration Name
      </a-build-config-key-testsuites-test-suite-pass.html#abuildconfigkeytestsuitestestsuitepass>`__

.. _SpecTestsuitesTestSuitePassFeaturesToBeTested:

Features to be tested
---------------------

The features to be tested are defined by the test case :ref:`spec:/​rtems/​val/​test-case-pass <SpecRtemsValTestCasePass>`.

.. _SpecTestsuitesTestSuitePassApproachRefinements:

Approach refinements
--------------------

There are no approach refinements
necessary.  The test suite is implemented in the file
`tests/ts-pass.c </pkg/doc-ddf-sdd/html/ts-pass_8c.html>`__.

.. _SpecTestsuitesTestSuiteXfail:

spec:/testsuites/test-suite-xfail
=================================

.. _SpecTestsuitesTestSuiteXfailGeneral:

General
-------

Description
    Brief.

    Description.

Test results
    For this test suite, the following test results are available:

    - `Target - Name Target A / Configuration - Build Configuration Name
      </a-build-config-key-testsuites-test-suite-xfail.html#abuildconfigkeytestsuitestestsuitexfail>`__

.. _SpecTestsuitesTestSuiteXfailFeaturesToBeTested:

Features to be tested
---------------------

The features to be tested are defined by the test case :ref:`spec:/​rtems/​val/​test-case-xfail <SpecRtemsValTestCaseXfail>`.

.. _SpecTestsuitesTestSuiteXfailApproachRefinements:

Approach refinements
--------------------

There are no approach refinements
necessary.  The test suite is implemented in the file
`tests/ts-xfail.c </pkg/doc-ddf-sdd/html/ts-xfail_8c.html>`__.
.. test-suites end

.. test-cases begin
.. _SpecRtemsReqAction:

spec:/rtems/req/action
======================

.. _SpecRtemsReqActionGeneral:

General
-------

Description
    This test case validates all state transitions
    specified by the action requirement `spec:/​rtems/​req/​action </pkg/doc-ts-srs/html/requirements.html#specrtemsreqaction>`__.  The
    transition map is validated by the function
    `T_case_body_RtemsReqAction() </pkg/doc-ddf-sdd/html/group__RtemsReqAction.html#ga041c7d03352b4363574beb9d7bebfa54>`__
    contained in the file
    `tests/tc-action.c </pkg/doc-ddf-sdd/html/tc-action_8c.html>`__.

Test suites
    This test case is contained in the :ref:`spec:/​testsuites/​test-suite-fail <SpecTestsuitesTestSuiteFail>` test suite.

Test results
    There are no test results available.

.. _SpecRtemsReqActionInputSpecifications:

Input specifications
--------------------

The test case starts execution in the
system state defined by the test suite runner and the test suite configuration.
All other inputs required by the test case are produced by the test case code
itself.

.. _SpecRtemsReqActionOutputSpecifications:

Output specifications
---------------------

For the output specifications see section :ref:`TestPassFailCriteria`.

.. _SpecRtemsReqActionTestPassFailCriteria:

Test pass - fail criteria
-------------------------

For the test pass - fail criteria see section :ref:`TestPassFailCriteria`.

.. _SpecRtemsReqActionEnvironmentalNeeds:

Environmental needs
-------------------

There are no specific environmental needs.

.. _SpecRtemsReqActionSpecialProcedureConstraints:

Special procedure constraints
-----------------------------

There are no special procedure constraints applicable.

.. _SpecRtemsReqActionInterfaceDependencies:

Interface dependencies
----------------------

There are no specific interface dependencies present.

.. _SpecRtemsReqAction2:

spec:/rtems/req/action-2
========================

.. _SpecRtemsReqAction2General:

General
-------

Description
    This test case validates all state transitions
    specified by the action requirement `spec:/​rtems/​req/​action-2 </pkg/doc-ts-srs/html/requirements.html#specrtemsreqaction2>`__.  The
    transition map is validated by the function
    `T_case_body_RtemsReqAction2() </pkg/doc-ddf-sdd/html/group__RtemsReqAction2.html#ga5e62b99a0ea0b8fdece5bbfc3532300f>`__
    contained in the file
    `tests/tc-action-2.c </pkg/doc-ddf-sdd/html/tc-action-2_8c.html>`__.

Test suites
    This test case is contained in the :ref:`spec:/​testsuites/​test-suite-fail <SpecTestsuitesTestSuiteFail>` test suite.

Test results
    There are no test results available.

.. _SpecRtemsReqAction2InputSpecifications:

Input specifications
--------------------

The test case starts execution in the
system state defined by the test suite runner and the test suite configuration.
All other inputs required by the test case are produced by the test case code
itself.

.. _SpecRtemsReqAction2OutputSpecifications:

Output specifications
---------------------

For the output specifications see section :ref:`TestPassFailCriteria`.

.. _SpecRtemsReqAction2TestPassFailCriteria:

Test pass - fail criteria
-------------------------

For the test pass - fail criteria see section :ref:`TestPassFailCriteria`.

.. _SpecRtemsReqAction2EnvironmentalNeeds:

Environmental needs
-------------------

There are no specific environmental needs.

.. _SpecRtemsReqAction2SpecialProcedureConstraints:

Special procedure constraints
-----------------------------

There are no special procedure constraints applicable.

.. _SpecRtemsReqAction2InterfaceDependencies:

Interface dependencies
----------------------

There are no specific interface dependencies present.

.. _SpecRtemsReqPerf:

spec:/rtems/req/perf
====================

.. _SpecRtemsReqPerfGeneral:

General
-------

Description
    This test case performs a performance runtime
    measurement request which is carried out by
    :ref:`spec:/​score/​cpu/​val/​perf <SpecScoreCpuValPerf>`.  It produces the runtime measurements
    required by the runtime performance requirement `spec:/​rtems/​req/​perf </pkg/doc-ts-srs/html/requirements.html#specrtemsreqperf>`__.
    It is implemented by the function
    `RtemsReqPerf_Body() </pkg/doc-ddf-sdd/html/group__RtemsReqPerf.html#ga80297695652fb63b3f419701ebf5b8a7>`__
    contained in the file
    `tests/tc-perf.c </pkg/doc-ddf-sdd/html/tc-perf_8c.html>`__.

Test results
    For this test case, the following test results are available:

    - `Target - Name Target A / Configuration - Build Configuration Name / Test
      suite - spec:/​testsuites/​performance-no-clock-0
      </a-build-config-key-testsuites-performance-no-clock-0.html#abuildconfigkeytestsuitesperformancenoclock0rtemsreqperf>`__

.. _SpecRtemsReqPerfInputSpecifications:

Input specifications
--------------------

The test case starts execution in the
system state defined by the test suite runner and the test suite configuration.
All other inputs required by the test case are produced by the test case code
itself.

.. _SpecRtemsReqPerfOutputSpecifications:

Output specifications
---------------------

For the output specifications see section :ref:`TestPassFailCriteria`.

.. _SpecRtemsReqPerfTestPassFailCriteria:

Test pass - fail criteria
-------------------------

For the test pass - fail criteria see section :ref:`TestPassFailCriteria`.

.. _SpecRtemsReqPerfEnvironmentalNeeds:

Environmental needs
-------------------

There are no specific environmental needs.

.. _SpecRtemsReqPerfSpecialProcedureConstraints:

Special procedure constraints
-----------------------------

There are no special procedure constraints applicable.

.. _SpecRtemsReqPerfInterfaceDependencies:

Interface dependencies
----------------------

There are no specific interface dependencies present.

.. _SpecRtemsReqPerfNoResults:

spec:/rtems/req/perf-no-results
===============================

.. _SpecRtemsReqPerfNoResultsGeneral:

General
-------

Description
    This test case performs a performance runtime
    measurement request which is carried out by
    :ref:`spec:/​score/​cpu/​val/​perf <SpecScoreCpuValPerf>`.  It produces the runtime measurements
    required by the runtime performance requirement `spec:/​rtems/​req/​perf-no-results </pkg/doc-ts-srs/html/requirements.html#specrtemsreqperfnoresults>`__.
    It is implemented by the function
    `RtemsReqPerfNoResults_Body() </pkg/doc-ddf-sdd/html/group__RtemsReqPerfNoResults.html#gac756b36b1183be9770beb26f1e1b2bbf>`__
    contained in the file
    `tests/tc-perf.c </pkg/doc-ddf-sdd/html/tc-perf_8c.html>`__.

Test results
    There are no test results available.

.. _SpecRtemsReqPerfNoResultsInputSpecifications:

Input specifications
--------------------

The test case starts execution in the
system state defined by the test suite runner and the test suite configuration.
All other inputs required by the test case are produced by the test case code
itself.

.. _SpecRtemsReqPerfNoResultsOutputSpecifications:

Output specifications
---------------------

For the output specifications see section :ref:`TestPassFailCriteria`.

.. _SpecRtemsReqPerfNoResultsTestPassFailCriteria:

Test pass - fail criteria
-------------------------

For the test pass - fail criteria see section :ref:`TestPassFailCriteria`.

.. _SpecRtemsReqPerfNoResultsEnvironmentalNeeds:

Environmental needs
-------------------

There are no specific environmental needs.

.. _SpecRtemsReqPerfNoResultsSpecialProcedureConstraints:

Special procedure constraints
-----------------------------

There are no special procedure constraints applicable.

.. _SpecRtemsReqPerfNoResultsInterfaceDependencies:

Interface dependencies
----------------------

There are no specific interface dependencies present.

.. _SpecRtemsValTestCase:

spec:/rtems/val/test-case
=========================

.. _SpecRtemsValTestCaseGeneral:

General
-------

Description
    Brief.

    Description.
    The following test case actions are carried out:

    - Brief.

      - Check.
        This validates `spec:/​rtems/​req/​func </pkg/doc-ts-srs/html/requirements.html#specrtemsreqfunc>`__.

      This action validates `spec:/​rtems/​req/​group </pkg/doc-ts-srs/html/requirements.html#specrtemsreqgroup>`__ and `spec:/​rtems/​req/​perf </pkg/doc-ts-srs/html/requirements.html#specrtemsreqperf>`__.
      This action is implemented by
      the function `RtemsValTestCase_Action_0() </pkg/doc-ddf-sdd/html/group__RtemsValTestCase.html#ga3a02cc8507f203b9231feb6f5904c1ef>`__.

    This test case is implemented by the
    function `T_case_body_RtemsValTestCase() </pkg/doc-ddf-sdd/html/group__RtemsValTestCase.html#gabdf6e7d14949fd137b99d4efad655d34>`__
    contained in the file
    `tests/tc-blub.c </pkg/doc-ddf-sdd/html/tc-blub_8c.html>`__.

Test suites
    This test case is contained in the following test suites:

    - :ref:`spec:/​testsuites/​performance-no-clock-0
      <SpecTestsuitesPerformanceNoClock0>`

    - :ref:`spec:/​testsuites/​test-suite-fail <SpecTestsuitesTestSuiteFail>`

Test results
    There are no test results available.

.. _SpecRtemsValTestCaseInputSpecifications:

Input specifications
--------------------

The test case starts execution in the
system state defined by the test suite runner and the test suite configuration.
All other inputs required by the test case are produced by the test case code
itself.

.. _SpecRtemsValTestCaseOutputSpecifications:

Output specifications
---------------------

For the output specifications see section :ref:`TestPassFailCriteria`.

.. _SpecRtemsValTestCaseTestPassFailCriteria:

Test pass - fail criteria
-------------------------

For the test pass - fail criteria see section :ref:`TestPassFailCriteria`.

.. _SpecRtemsValTestCaseEnvironmentalNeeds:

Environmental needs
-------------------

There are no specific environmental needs.

.. _SpecRtemsValTestCaseSpecialProcedureConstraints:

Special procedure constraints
-----------------------------

There are no special procedure constraints applicable.

.. _SpecRtemsValTestCaseInterfaceDependencies:

Interface dependencies
----------------------

There are no specific interface dependencies present.

.. _SpecRtemsValTestCaseFail:

spec:/rtems/val/test-case-fail
==============================

.. _SpecRtemsValTestCaseFailGeneral:

General
-------

Description
    Brief.

    Description.
    The following test case actions are carried out:

    This test case is implemented by the
    function `T_case_body_RtemsValTestCaseFail() </pkg/doc-ddf-sdd/html/group__RtemsValTestCaseFail.html#gaf6e0cb824ab37c1fc93cb11de79ec7de>`__
    contained in the file
    `tests/tc-fail.c </pkg/doc-ddf-sdd/html/tc-fail_8c.html>`__.

Test suites
    This test case is contained in the :ref:`spec:/​testsuites/​test-suite-fail <SpecTestsuitesTestSuiteFail>` test suite.

Test results
    For this test case, the following test results are available:

    - `Target - Name Target A / Configuration - Build Configuration Name / Test
      suite - spec:/​testsuites/​test-suite-fail
      </a-build-config-key-testsuites-test-suite-fail.html#abuildconfigkeytestsuitestestsuitefailrtemsvaltestcasefail>`__

.. _SpecRtemsValTestCaseFailInputSpecifications:

Input specifications
--------------------

The test case starts execution in the
system state defined by the test suite runner and the test suite configuration.
All other inputs required by the test case are produced by the test case code
itself.

.. _SpecRtemsValTestCaseFailOutputSpecifications:

Output specifications
---------------------

For the output specifications see section :ref:`TestPassFailCriteria`.

.. _SpecRtemsValTestCaseFailTestPassFailCriteria:

Test pass - fail criteria
-------------------------

For the test pass - fail criteria see section :ref:`TestPassFailCriteria`.

.. _SpecRtemsValTestCaseFailEnvironmentalNeeds:

Environmental needs
-------------------

There are no specific environmental needs.

.. _SpecRtemsValTestCaseFailSpecialProcedureConstraints:

Special procedure constraints
-----------------------------

There are no special procedure constraints applicable.

.. _SpecRtemsValTestCaseFailInterfaceDependencies:

Interface dependencies
----------------------

There are no specific interface dependencies present.

.. _SpecRtemsValTestCasePass:

spec:/rtems/val/test-case-pass
==============================

.. _SpecRtemsValTestCasePassGeneral:

General
-------

Description
    Brief.

    Description.
    The following test case actions are carried out:

    This test case is implemented by the
    function `T_case_body_RtemsValTestCasePass() </pkg/doc-ddf-sdd/html/group__RtemsValTestCasePass.html#gac1d679420bcb7eab4d90e977023f3c70>`__
    contained in the file
    `tests/tc-pass.c </pkg/doc-ddf-sdd/html/tc-pass_8c.html>`__.

Test suites
    This test case is contained in the :ref:`spec:/​testsuites/​test-suite-pass <SpecTestsuitesTestSuitePass>` test suite.

Test results
    For this test case, the following test results are available:

    - `Target - Name Target A / Configuration - Build Configuration Name / Test
      suite - spec:/​testsuites/​test-suite-pass
      </a-build-config-key-testsuites-test-suite-pass.html#abuildconfigkeytestsuitestestsuitepassrtemsvaltestcasepass>`__

.. _SpecRtemsValTestCasePassInputSpecifications:

Input specifications
--------------------

The test case starts execution in the
system state defined by the test suite runner and the test suite configuration.
All other inputs required by the test case are produced by the test case code
itself.

.. _SpecRtemsValTestCasePassOutputSpecifications:

Output specifications
---------------------

For the output specifications see section :ref:`TestPassFailCriteria`.

.. _SpecRtemsValTestCasePassTestPassFailCriteria:

Test pass - fail criteria
-------------------------

For the test pass - fail criteria see section :ref:`TestPassFailCriteria`.

.. _SpecRtemsValTestCasePassEnvironmentalNeeds:

Environmental needs
-------------------

There are no specific environmental needs.

.. _SpecRtemsValTestCasePassSpecialProcedureConstraints:

Special procedure constraints
-----------------------------

There are no special procedure constraints applicable.

.. _SpecRtemsValTestCasePassInterfaceDependencies:

Interface dependencies
----------------------

There are no specific interface dependencies present.

.. _SpecRtemsValTestCaseRun:

spec:/rtems/val/test-case-run
=============================

.. _SpecRtemsValTestCaseRunGeneral:

General
-------

Description
    Test brief
    The following test case actions are carried out:

    - Action brief.

      - Check brief.
        This validates `spec:/​rtems/​req/​func </pkg/doc-ts-srs/html/requirements.html#specrtemsreqfunc>`__, `spec:/​rtems/​req/​group </pkg/doc-ts-srs/html/requirements.html#specrtemsreqgroup>`__, and `spec:/​rtems/​req/​perf </pkg/doc-ts-srs/html/requirements.html#specrtemsreqperf>`__.

      This action is implemented by
      the function `RtemsValTestCaseRun_Action_0() </pkg/doc-ddf-sdd/html/group__RtemsValTestCaseRun.html#ga3cbb537cb50db02607b786cec0cc3bd1>`__.

    This test case is implemented by the
    function `RtemsValTestCaseRun_Run() </pkg/doc-ddf-sdd/html/group__RtemsValTestCaseRun.html#ga301259ebfd4b0c947ad359e448a3a7bb>`__
    contained in the file
    `tests/tr-test-case.c </pkg/doc-ddf-sdd/html/tr-test-case_8c.html>`__.

Test suites
    This test case is contained in the :ref:`spec:/​testsuites/​test-suite-fail <SpecTestsuitesTestSuiteFail>` test suite.

Test results
    There are no test results available.

.. _SpecRtemsValTestCaseRunInputSpecifications:

Input specifications
--------------------

The test case starts execution in the
system state defined by the test suite runner and the test suite configuration.
All other inputs required by the test case are produced by the test case code
itself.

.. _SpecRtemsValTestCaseRunOutputSpecifications:

Output specifications
---------------------

For the output specifications see section :ref:`TestPassFailCriteria`.

.. _SpecRtemsValTestCaseRunTestPassFailCriteria:

Test pass - fail criteria
-------------------------

For the test pass - fail criteria see section :ref:`TestPassFailCriteria`.

.. _SpecRtemsValTestCaseRunEnvironmentalNeeds:

Environmental needs
-------------------

There are no specific environmental needs.

.. _SpecRtemsValTestCaseRunSpecialProcedureConstraints:

Special procedure constraints
-----------------------------

There are no special procedure constraints applicable.

.. _SpecRtemsValTestCaseRunInterfaceDependencies:

Interface dependencies
----------------------

There are no specific interface dependencies present.

.. _SpecRtemsValTestCaseXfail:

spec:/rtems/val/test-case-xfail
===============================

.. _SpecRtemsValTestCaseXfailGeneral:

General
-------

Description
    Brief.

    Description.
    The following test case actions are carried out:

    This test case is implemented by the
    function `T_case_body_RtemsValTestCaseXfail() </pkg/doc-ddf-sdd/html/group__RtemsValTestCaseXfail.html#ga8bd4229a2e63e549db1f0ad7c4f18a5c>`__
    contained in the file
    `tests/tc-xfail.c </pkg/doc-ddf-sdd/html/tc-xfail_8c.html>`__.

Test suites
    This test case is contained in the :ref:`spec:/​testsuites/​test-suite-xfail <SpecTestsuitesTestSuiteXfail>` test suite.

Test results
    For this test case, the following test results are available:

    - `Target - Name Target A / Configuration - Build Configuration Name / Test
      suite - spec:/​testsuites/​test-suite-xfail
      </a-build-config-key-testsuites-test-suite-xfail.html#abuildconfigkeytestsuitestestsuitexfailrtemsvaltestcasexfail>`__

.. _SpecRtemsValTestCaseXfailInputSpecifications:

Input specifications
--------------------

The test case starts execution in the
system state defined by the test suite runner and the test suite configuration.
All other inputs required by the test case are produced by the test case code
itself.

.. _SpecRtemsValTestCaseXfailOutputSpecifications:

Output specifications
---------------------

For the output specifications see section :ref:`TestPassFailCriteria`.

.. _SpecRtemsValTestCaseXfailTestPassFailCriteria:

Test pass - fail criteria
-------------------------

For the test pass - fail criteria see section :ref:`TestPassFailCriteria`.

.. _SpecRtemsValTestCaseXfailEnvironmentalNeeds:

Environmental needs
-------------------

There are no specific environmental needs.

.. _SpecRtemsValTestCaseXfailSpecialProcedureConstraints:

Special procedure constraints
-----------------------------

There are no special procedure constraints applicable.

.. _SpecRtemsValTestCaseXfailInterfaceDependencies:

Interface dependencies
----------------------

There are no specific interface dependencies present.

.. _SpecScoreCpuValPerf:

spec:/score/cpu/val/perf
========================

.. _SpecScoreCpuValPerfGeneral:

General
-------

Description
    Brief.
    The following runtime measurement requests are carried out:

    - :ref:`spec:/​rtems/​req/​perf <SpecRtemsReqPerf>`

    - :ref:`spec:/​rtems/​req/​perf-no-results <SpecRtemsReqPerfNoResults>`

    This test case validates `spec:/​req/​root </pkg/doc-ts-srs/html/requirements.html#specreqroot>`__.
    This test case is implemented by the
    function `T_case_body_ScoreCpuValPerf() </pkg/doc-ddf-sdd/html/group__ScoreCpuValPerf.html#ga00214d5ab555daf1418266e8733a91ad>`__
    contained in the file
    `tests/tc-perf.c </pkg/doc-ddf-sdd/html/tc-perf_8c.html>`__.

Test suites
    This test case is contained in the :ref:`spec:/​testsuites/​performance-no-clock-0 <SpecTestsuitesPerformanceNoClock0>` test suite.

Test results
    For this test case, the following test results are available:

    - `Target - Name Target A / Configuration - Build Configuration Name / Test
      suite - spec:/​testsuites/​performance-no-clock-0
      </a-build-config-key-testsuites-performance-no-clock-0.html#abuildconfigkeytestsuitesperformancenoclock0scorecpuvalperf>`__

.. _SpecScoreCpuValPerfInputSpecifications:

Input specifications
--------------------

The test case starts execution in the
system state defined by the test suite runner and the test suite configuration.
All other inputs required by the test case are produced by the test case code
itself.

.. _SpecScoreCpuValPerfOutputSpecifications:

Output specifications
---------------------

For the output specifications see section :ref:`TestPassFailCriteria`.

.. _SpecScoreCpuValPerfTestPassFailCriteria:

Test pass - fail criteria
-------------------------

For the test pass - fail criteria see section :ref:`TestPassFailCriteria`.

.. _SpecScoreCpuValPerfEnvironmentalNeeds:

Environmental needs
-------------------

There are no specific environmental needs.

.. _SpecScoreCpuValPerfSpecialProcedureConstraints:

Special procedure constraints
-----------------------------

There are no special procedure constraints applicable.

.. _SpecScoreCpuValPerfInterfaceDependencies:

Interface dependencies
----------------------

There are no specific interface dependencies present.
.. test-cases end

.. test-procedures begin
.. _SpecPkgTestRunnerSubprocess:

Subprocess
==========

For each test program (indicated by ``${test_program}``),
this test procedure runs the following command as a subprocess on the machine
building the package and captures the output:

.. code-block:: none

    foo --on 1 bar ${test_program}
.. test-procedures end

.. other-validations begin
.. _ValidationByInspection:

Validation by inspection
========================

This section lists validation evidence obtained by using the inspection validation method.

.. _SpecRtemsValByInspection:

spec:/rtems/val/by-inspection
-----------------------------

Inspection
    The inspection.

Validated item
    This validation by inspection validates the runtime performance requirement
    `spec:/​rtems/​req/​perf
    </pkg/doc-ts-srs/html/requirements.html#specrtemsreqperf>`__.

.. _ValidationByReviewOfDesign:

Validation by review of design
==============================

This section lists validation evidence obtained by using the review of design validation method.

.. _SpecRtemsValByReviewOfDesign:

spec:/rtems/val/by-review-of-design
-----------------------------------

Review of design
    The review of design.

Validated item
    This validation by review of design validates the runtime performance
    requirement `spec:/​rtems/​req/​perf
    </pkg/doc-ts-srs/html/requirements.html#specrtemsreqperf>`__.
.. other-validations end

.. not-validated-by-test begin
The following items are not specifically validated by a test:

- `spec:/​rtems/​req/​perf
  </pkg/doc-ts-srs/html/requirements.html#specrtemsreqperf>`__
.. not-validated-by-test end"""
