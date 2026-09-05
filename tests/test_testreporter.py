# SPDX-License-Identifier: BSD-2-Clause
""" Tests for the testaggregator module. """

# Copyright (C) 2025 embedded brains GmbH & Co. KG
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

import pytest

from .util import create_package, get_document_text


def test_testreporter(caplog, tmpdir):
    package = create_package(caplog, Path(tmpdir), Path("spec-packagebuild"), [
        "aggregate-test-results", "dummy-images", "target-b", "test-reporter"
    ])
    director = package.director
    director.build_package(only=[
        "/pkg/deployment/doc-djf-tr", "/pkg/deployment/doc-djf-tr-2",
        "/pkg/deployment/doc-djf-tr-3"
    ])

    def _get_content(uid, name):
        path = Path(director[uid].directory) / "source" / name
        return get_document_text(tmpdir, path)

    def _get_tr(name):
        return _get_content("/pkg/build/doc-djf-tr", name)

    assert _get_tr("index.rst") == """.. SPDX-License-Identifier: CC-BY-SA-4.0

.. Copyright (C) 2025 embedded brains GmbH & Co. KG

.. reports begin
.. _A:

Target - Name Target A
######################

.. _ABuildConfigKey:

Configuration - build-config-key
********************************

.. toctree::

    a-build-config-key-testsuites-performance-no-clock-0

    a-build-config-key-testsuites-test-suite-fail

    a-build-config-key-testsuites-test-suite-pass

    a-build-config-key-testsuites-test-suite-xfail

    a-build-config-key-testsuites-unit-0

    a-build-config-key-build-test-program

    a-build-config-key-build-testsuites-smptests-smplock01

    a-build-config-key-build-testsuites-smptests-smpopenmp01

    a-build-config-key-build-testsuites-sptests-sptimecounter02

    a-build-config-key-build-testsuites-tmtests-tmcontext01

    a-build-config-key-build-testsuites-tmtests-tmfine01

    a-build-config-key-build-testsuites-tmtests-tmtimer01

    a-build-config-key-hello.exe

    a-build-config-key-ts-no-spec.exe

.. _AEmptyKey:

Configuration - empty-key
*************************

.. toctree::

.. _ABuildConfigKey:

Configuration - build-config-key
********************************

.. toctree::

    a-build-config-key-build-testsuites-tmtests-tmfine01

.. _CoverageData:

Coverage data
#############

.. toctree::

    coverage

.. _ListOfExpectedTestFailures:

List of expected test failures
##############################

.. _ListOfExpectedTestFailuresTargetNameTargetA:

Target - Name Target A
**********************

.. _ListOfExpectedTestFailuresTargetNameTargetASpecRtemsValTestCase:

spec:/​rtems/​val/​test-case
============================

This target cannot provide test results for this validation test.

.. _ListOfExpectedTestFailuresTargetNameTargetASpecRtemsValTestCaseXfail:

spec:/​rtems/​val/​test-case-xfail
==================================

This test failure is expected to fail.

- :ref:`Configuration - build-config-key
  <ABuildConfigKeyTestsuitesTestSuiteXfailRtemsValTestCaseXfail>`:

  - The failed test steps count value is not zero.

.. _ListOfUnexpectedTestFailures:

List of unexpected test failures
################################

.. _ListOfUnexpectedTestFailuresTargetNameTargetA:

Target - Name Target A
**********************

.. _ListOfUnexpectedTestFailuresTargetNameTargetASpecBuildTestProgram:

spec:/​build/​test-program
==========================

- :ref:`Configuration - build-config-key
  <a-build-config-key-build-test-program>`:

  - At least one build configuration option has not the expected value or the
    build configuration information is not present.

  - The RTEMS Git commit has not the expected value.

  - The test output contains no begin of test message.

  - The test output contains no end of test message.

  - The tools version has not the expected value.

.. _ListOfUnexpectedTestFailuresTargetNameTargetASpecBuildTestsuitesSmptestsSmplock01:

spec:/​build/​testsuites/​smptests/​smplock01
=============================================

- :ref:`Configuration - build-config-key
  <a-build-config-key-build-testsuites-smptests-smplock01>`:

  - At least one build configuration option has not the expected value or the
    build configuration information is not present.

  - The RTEMS Git commit has not the expected value.

  - The tools version has not the expected value.

.. _ListOfUnexpectedTestFailuresTargetNameTargetASpecBuildTestsuitesSmptestsSmpopenmp01:

spec:/​build/​testsuites/​smptests/​smpopenmp01
===============================================

- :ref:`Configuration - build-config-key
  <a-build-config-key-build-testsuites-smptests-smpopenmp01>`:

  - At least one build configuration option has not the expected value or the
    build configuration information is not present.

  - The RTEMS Git commit has not the expected value.

  - The tools version has not the expected value.

.. _ListOfUnexpectedTestFailuresTargetNameTargetASpecBuildTestsuitesSptestsSptimecounter02:

spec:/​build/​testsuites/​sptests/​sptimecounter02
==================================================

- :ref:`Configuration - build-config-key
  <a-build-config-key-build-testsuites-sptests-sptimecounter02>`:

  - At least one build configuration option has not the expected value or the
    build configuration information is not present.

  - The RTEMS Git commit has not the expected value.

  - The tools version has not the expected value.

.. _ListOfUnexpectedTestFailuresTargetNameTargetASpecBuildTestsuitesTmtestsTmcontext01:

spec:/​build/​testsuites/​tmtests/​tmcontext01
==============================================

- :ref:`Configuration - build-config-key
  <a-build-config-key-build-testsuites-tmtests-tmcontext01>`:

  - At least one build configuration option has not the expected value or the
    build configuration information is not present.

  - The RTEMS Git commit has not the expected value.

  - The tools version has not the expected value.

.. _ListOfUnexpectedTestFailuresTargetNameTargetASpecBuildTestsuitesTmtestsTmfine01:

spec:/​build/​testsuites/​tmtests/​tmfine01
===========================================

- :ref:`Configuration - build-config-key
  <a-build-config-key-build-testsuites-tmtests-tmfine01>`:

  - At least one build configuration option has not the expected value or the
    build configuration information is not present.

  - The RTEMS Git commit has not the expected value.

  - The tools version has not the expected value.

.. _ListOfUnexpectedTestFailuresTargetNameTargetASpecBuildTestsuitesTmtestsTmtimer01:

spec:/​build/​testsuites/​tmtests/​tmtimer01
============================================

- :ref:`Configuration - build-config-key
  <a-build-config-key-build-testsuites-tmtests-tmtimer01>`:

  - At least one build configuration option has not the expected value or the
    build configuration information is not present.

  - The RTEMS Git commit has not the expected value.

  - The tools version has not the expected value.

.. _ListOfUnexpectedTestFailuresTargetNameTargetASpecRtemsReqAction:

spec:/​rtems/​req/​action
=========================

There are no test results available for this target.

.. _ListOfUnexpectedTestFailuresTargetNameTargetASpecRtemsReqAction2:

spec:/​rtems/​req/​action-2
===========================

There are no test results available for this target.

.. _ListOfUnexpectedTestFailuresTargetNameTargetASpecRtemsReqPerfNoResults:

spec:/​rtems/​req/​perf-no-results
==================================

There are no test results available for this target.

.. _ListOfUnexpectedTestFailuresTargetNameTargetASpecRtemsTargetA:

spec:/​rtems/​target-a
======================

For this target, the following code coverage issues were present.

- Coverage limits met only with an excluded test, and no target gives complete
  evidence:

  - Scope - Scope

- Excluded tests which no other target ran:

  - excluded​-second​-board.exe

- Excluded tests without a reason:

  - excluded​-silent.exe

- Insufficient file-specific branch coverage:

  - `cpukit​/score​/src​/chain.c
    </pkg/coverage-overall-html/index.chain.c.fb6aee9b3f6ae0998256d52130e2c678.html>`__

- Insufficient file-specific function coverage:

  - `cpukit​/score​/src​/chain.c
    </pkg/coverage-overall-html/index.chain.c.fb6aee9b3f6ae0998256d52130e2c678.html>`__

  - `cpukit​/score​/src​/threadqenqueue.c
    </pkg/coverage-html/index.threadqenqueue.c.49433ec925b45a09aa7c6c6f0199f026.html>`__

- Insufficient file-specific line coverage:

  - `bsps​/include​/bsp​/fatal.h
    </pkg/coverage-overall-html/index.fatal.h.7f3bb1e879e3580b41139d705e6b007f.html>`__

  - `cpukit​/score​/src​/chain.c
    </pkg/coverage-overall-html/index.chain.c.fb6aee9b3f6ae0998256d52130e2c678.html>`__

  - `cpukit​/score​/src​/threadqenqueue.c
    </pkg/coverage-html/index.threadqenqueue.c.49433ec925b45a09aa7c6c6f0199f026.html>`__

- Insufficient overall branch coverage:

  - Scope - Overall

- Insufficient overall function coverage:

  - Scope - Overall

- Insufficient overall line coverage:

  - Scope - Overall

- No branch information in coverage data:

  - Scope - Empty

- No function information in coverage data:

  - Scope - Empty

- No general function information in coverage data:

  - Scope - Scope

- No line information in coverage data:

  - Scope - Empty

- Out of date branch coverage gap justifications:

  - spec:​/verification​/code​-coverage​-gap​/gap

- Out of date line coverage gap justifications:

  - spec:​/verification​/code​-coverage​-gap​/gap

- Unrelated code coverage justifications:

  - spec:​/verification​/code​-coverage​-gap​/gap

- Unused code coverage justifications:

  - spec:​/verification​/code​-coverage​-gap​/unused

.. _ListOfUnexpectedTestFailuresTargetNameTargetASpecRtemsValTestCaseFail:

spec:/​rtems/​val/​test-case-fail
=================================

- :ref:`Configuration - build-config-key
  <ABuildConfigKeyTestsuitesTestSuiteFailRtemsValTestCaseFail>`:

  - The failed test steps count value is not zero.

  - The test duration has not the expected value.

  - The test step count value is not positive.

.. _ListOfUnexpectedTestFailuresTargetNameTargetASpecRtemsValTestCaseRun:

spec:/​rtems/​val/​test-case-run
================================

There are no test results available for this target.

.. _ListOfUnexpectedTestFailuresTargetNameTargetASpecRtemsValTestCaseUnit:

spec:/​rtems/​val/​test-case-unit
=================================

There are no test results available for this target.

.. _ListOfUnexpectedTestFailuresTargetNameTargetASpecRtemsValTestCaseXfail:

spec:/​rtems/​val/​test-case-xfail
==================================

- :ref:`Configuration - build-config-key
  <ABuildConfigKeyTestsuitesTestSuiteXfailRtemsValTestCaseXfail>`:

  - The test duration has not the expected value.

.. _ListOfUnexpectedTestFailuresTargetNameTargetASpecTestsuitesPerformanceNoClock0:

spec:/​testsuites/​performance-no-clock-0
=========================================

- :ref:`Configuration - build-config-key
  <ABuildConfigKeyTestsuitesPerformanceNoClock0>`:

  - The RTEMS Git commit has not the expected value.

  - The build label has not the expected value.

  - The compiler version has not the expected value.

  - The tools version has not the expected value.

- :ref:`Configuration - build-config-key
  <ABuildConfigKeyTestsuitesPerformanceNoClock0RtemsReqPerf>`:

  - A maximum runtime value is greater than expected.

  - A median runtime value is not in the expected interval.

  - A minimum runtime value is less than expected.

.. _ListOfUnexpectedTestFailuresTargetNameTargetASpecTestsuitesTestSuiteFail:

spec:/​testsuites/​test-suite-fail
==================================

- :ref:`Configuration - build-config-key
  <ABuildConfigKeyTestsuitesTestSuiteFail>`:

  - At least one build configuration option has not the expected value or the
    build configuration information is not present.

  - The BSP has not the expected name.

  - The RTEMS Git commit has not the expected value.

  - The RTEMS_SMP build configuration option has not the expected value.

  - The build label has not the expected value.

  - The compiler version has not the expected value.

  - The failed test steps count value is not zero.

  - The test output contains no end of test message.

  - The test step count value is not positive.

  - The tools version has not the expected value.

.. _ListOfUnexpectedTestFailuresTargetNameTargetASpecTestsuitesTestSuitePass:

spec:/​testsuites/​test-suite-pass
==================================

- :ref:`Configuration - build-config-key
  <ABuildConfigKeyTestsuitesTestSuitePass>`:

  - The BSP has not the expected name.

  - The RTEMS Git commit has not the expected value.

  - The build label has not the expected value.

  - The compiler version has not the expected value.

  - The target hash has not the expected value.

  - The tools version has not the expected value.

.. _ListOfUnexpectedTestFailuresTargetNameTargetASpecTestsuitesTestSuiteXfail:

spec:/​testsuites/​test-suite-xfail
===================================

- :ref:`Configuration - build-config-key
  <ABuildConfigKeyTestsuitesTestSuiteXfail>`:

  - The BSP has not the expected name.

  - The RTEMS Git commit has not the expected value.

  - The build label has not the expected value.

  - The compiler version has not the expected value.

  - The failed test steps count value is not zero.

  - The test output contains no end of test message.

  - The tools version has not the expected value.
.. reports end"""

    assert _get_tr("a-build-config-key-build-test-program.rst"
                   ) == """.. _a-build-config-key-build-test-program:

Test program - spec:/​build/​test-program
#########################################

This report was produced by the
:file:`test-program.exe`
executable.  The executable file had an SHA512 digest of
e​3​d​b​7​1​4​3​b​1​7​2​e​7​7​3​2​b​9​9​4​1​d​5​1​a​f​2​b​2​9​5​7​b​c​3​1​4​3​8​0​7​1​3​a​0​3​d​0​a​e​9​c​8​0​8​6​a​a​4​5​1​4​4​2​e​7​7​1​a​3​4​a​f​5​2​c​5​8​d​d​9​e​0​5​2​c​b​0​5​5​4​2​1​1​5​e​5​4​3​9​1​6​6​a​1​a​4​2​5​a​a​9​7​7​8​7​c​e​d​3​e​6​6​c​c​9​2.
The test output contains no begin of test message.
The test output contains no end of test message.
The following table lists an evaluation of the reported test information.

.. raw:: latex

    \\begin{scriptsize}

.. table::
    :class: longtable
    :widths: 42,8,20,20,10

    +-+-+-+-+-+
    | Property | Line | Reported | Expected | Status |
    +=+=+=+=+=+
    | RTEMS Git Commit | ? | ? | 5​8​b​f​f​6​2​2​d​6​1​0​8​6​5​c​7​6​d​a​0​4​5​e​8​c​c​6​7​a​a​5​6​c​3​2​b​7​c​8 | NOK |
    +-+-+-+-+-+
    | RTEMS_DEBUG | ? | ? | not listed | NOK |
    +-+-+-+-+-+
    | RTEMS_MULTIPROCESSING | ? | ? | not listed | NOK |
    +-+-+-+-+-+
    | RTEMS_PARAVIRT | ? | ? | not listed | NOK |
    +-+-+-+-+-+
    | RTEMS_POSIX_API | ? | ? | not listed | NOK |
    +-+-+-+-+-+
    | RTEMS_PROFILING | ? | ? | not listed | NOK |
    +-+-+-+-+-+
    | RTEMS_SMP | ? | ? | not listed | NOK |
    +-+-+-+-+-+
    | GCC Version | ? | ? | 1​3​.​4​.​1​ ​2​0​2​6​0​1​0​8 | NOK |
    +-+-+-+-+-+

.. raw:: latex

    \\end{scriptsize}

.. _a-build-config-key-build-test-programTestOutput:

Test output
***********

The test report was generated from the following test output."""

    assert _get_tr(
        "a-build-config-key-build-testsuites-tmtests-tmfine01.rst"
    ) == """.. _a-build-config-key-build-testsuites-tmtests-tmfine01:

Test program - spec:/​build/​testsuites/​tmtests/​tmfine01
##########################################################

This report was produced by the
:file:`tmfine01.exe`
executable.  The executable file had an SHA512 digest of
4​b​2​3​b​8​c​8​8​d​5​e​5​3​6​b​9​6​c​2​1​b​9​f​7​e​3​b​b​8​7​1​c​a​b​8​3​3​f​8​a​f​7​8​4​3​0​d​1​c​e​c​f​b​e​7​f​b​3​4​b​1​f​4​8​9​2​3​1​d​7​9​7​0​b​a​6​6​4​6​0​9​7​f​5​d​8​6​f​4​c​5​e​f​c​d​3​2​7​4​3​1​9​c​3​4​a​b​6​1​1​4​9​1​6​f​7​e​7​b​f​f​9​9​8​7​2​8.

.. error:: Test runner error

    the error message

There is a valid begin of test message at line :ref:`3
<a-build-config-key-build-testsuites-tmtests-tmfine01Output0>`.
There is a valid end of test message at line :ref:`122
<a-build-config-key-build-testsuites-tmtests-tmfine01Output100>`.  This
indicates that the test program executed without a detected error.
The following table lists an evaluation of the reported test information.

.. raw:: latex

    \\begin{scriptsize}

.. table::
    :class: longtable
    :widths: 42,8,20,20,10

    +-+-+-+-+-+
    | Property | Line | Reported | Expected | Status |
    +=+=+=+=+=+
    | RTEMS Git Commit | :ref:`4 <a-build-config-key-build-testsuites-tmtests-tmfine01Output0>` | 4​e​a​7​f​a​2​9​a​1​1​d​c​9​d​7​c​b​8​1​d​9​9​d​9​a​1​4​7​d​e​e​0​4​6​a​2​f​2​b | 5​8​b​f​f​6​2​2​d​6​1​0​8​6​5​c​7​6​d​a​0​4​5​e​8​c​c​6​7​a​a​5​6​c​3​2​b​7​c​8 | NOK |
    +-+-+-+-+-+
    | RTEMS_DEBUG | :ref:`6 <a-build-config-key-build-testsuites-tmtests-tmfine01Output0>` | not listed | not listed | OK |
    +-+-+-+-+-+
    | RTEMS_MULTIPROCESSING | :ref:`6 <a-build-config-key-build-testsuites-tmtests-tmfine01Output0>` | not listed | not listed | OK |
    +-+-+-+-+-+
    | RTEMS_PARAVIRT | :ref:`6 <a-build-config-key-build-testsuites-tmtests-tmfine01Output0>` | not listed | not listed | OK |
    +-+-+-+-+-+
    | RTEMS_POSIX_API | :ref:`6 <a-build-config-key-build-testsuites-tmtests-tmfine01Output0>` | not listed | not listed | OK |
    +-+-+-+-+-+
    | RTEMS_PROFILING | :ref:`6 <a-build-config-key-build-testsuites-tmtests-tmfine01Output0>` | not listed | not listed | OK |
    +-+-+-+-+-+
    | RTEMS_SMP | :ref:`6 <a-build-config-key-build-testsuites-tmtests-tmfine01Output0>` | listed | not listed | NOK |
    +-+-+-+-+-+
    | GCC Version | :ref:`7 <a-build-config-key-build-testsuites-tmtests-tmfine01Output0>` | 1​5​.​2​.​1​ ​2​0​2​5​0​9​1​6 | 1​3​.​4​.​1​ ​2​0​2​6​0​1​0​8 | NOK |
    +-+-+-+-+-+

.. raw:: latex

    \\end{scriptsize}

.. _a-build-config-key-build-testsuites-tmtests-tmfine01TestOutput:

Test output
***********

The test report was generated from the following test output."""

    assert _get_tr("a-build-config-key-hello.exe.rst"
                   ) == """.. _a-build-config-key-hello.exe:

Other program - hello.exe
#########################

This report was produced by the
:file:`hello.exe`
executable.  The executable file had an SHA512 digest of
5​e​8​2​2​b​7​7​7​b​c​f​0​9​b​9​b​e​e​4​2​5​9​4​c​a​b​3​1​1​8​0​1​5​a​c​b​d​9​4​7​4​c​b​8​0​a​5​5​f​1​6​4​6​9​3​b​4​c​f​e​e​1​2​8​9​e​3​d​1​1​d​2​1​f​2​6​7​c​3​a​4​c​a​5​b​3​1​3​5​6​4​2​9​6​0​7​6​7​0​9​c​8​1​6​e​9​2​4​8​0​d​3​0​2​6​c​2​9​e​5​2​c​d​6​e​6​4.

.. raw:: latex

    \\begin{tiny}

.. _a-build-config-key-hello.exeOutput0:

.. code-block:: none
    :linenos:
    :lineno-start: 1

    ​
    ​ ​S​I​S​ ​-​ ​S​P​A​R​C​/​R​I​S​C​V​ ​i​n​s​t​r​u​c​t​i​o​n​ ​s​i​m​u​l​a​t​o​r​ ​2​.​3​0​,​ ​ ​c​o​p​y​r​i​g​h​t​ ​J​i​r​i​ ​G​a​i​s​l​e​r​ ​2​0​2​0
    ​ ​B​u​g​-​r​e​p​o​r​t​s​ ​t​o​ ​j​i​r​i​@​g​a​i​s​l​e​r​.​s​e
    ​
    ​ ​G​R​7​4​0​/​L​E​O​N​4​ ​e​m​u​l​a​t​i​o​n​ ​e​n​a​b​l​e​d​,​ ​4​ ​c​p​u​s​ ​o​n​l​i​n​e​,​ ​d​e​l​t​a​ ​5​0​ ​c​l​o​c​k​s
    ​
    ​ ​L​o​a​d​e​d​ ​h​e​l​l​o​.​e​x​e​,​ ​e​n​t​r​y​ ​0​x​0​0​0​0​0​0​0​0
    ​
    ​
    ​*​*​*​ ​B​E​G​I​N​ ​O​F​ ​T​E​S​T​ ​H​E​L​L​O​ ​W​O​R​L​D​ ​*​*​*
    ​*​*​*​ ​T​E​S​T​ ​V​E​R​S​I​O​N​:​ ​6​.​0​.​0​.​5​8​b​f​f​6​2​2​d​6​1​0​8​6​5​c​7​6​d​a​0​4​5​e​8​c​c​6​7​a​a​5​6​c​3​2​b​7​c​8
    ​*​*​*​ ​T​E​S​T​ ​S​T​A​T​E​:​ ​E​X​P​E​C​T​E​D​_​P​A​S​S
    ​*​*​*​ ​T​E​S​T​ ​B​U​I​L​D​:​ ​R​T​E​M​S​_​S​M​P
    ​*​*​*​ ​T​E​S​T​ ​T​O​O​L​S​:​ ​1​3​.​4​.​1​ ​2​0​2​6​0​1​0​8
    ​H​e​l​l​o​ ​W​o​r​l​d
    ​
    ​*​*​*​ ​E​N​D​ ​O​F​ ​T​E​S​T​ ​H​E​L​L​O​ ​W​O​R​L​D​ ​*​*​*
    ​
    ​c​p​u​ ​0​ ​i​n​ ​e​r​r​o​r​ ​m​o​d​e​ ​(​t​t​ ​=​ ​0​x​8​0​)
    ​ ​ ​ ​ ​6​6​5​0​0​ ​ ​0​0​0​0​2​0​8​0​:​ ​ ​9​1​d​0​2​0​0​0​ ​ ​ ​t​a​ ​ ​0​x​0

.. raw:: latex

    \\end{tiny}"""

    assert _get_tr("a-build-config-key-testsuites-performance-no-clock-0.rst"
                   ) == """.. _ABuildConfigKeyTestsuitesPerformanceNoClock0:

Test suite - spec:/​testsuites/​performance-no-clock-0
######################################################

This report was produced by the
:file:`ts-performance-no-clock-0.exe`
executable.  The executable file had an SHA512 digest of
1​2​0​a​9​7​6​2​6​4​1​3​2​9​3​f​1​a​9​c​9​8​d​0​0​a​c​e​c​e​5​b​8​4​b​9​d​4​a​b​4​a​7​3​8​7​a​8​1​a​2​e​4​6​e​b​2​f​1​0​f​d​9​6​a​4​5​5​6​1​8​2​c​b​f​6​1​f​d​9​5​b​b​1​3​2​0​2​1​5​0​c​6​7​a​5​8​f​2​a​e​1​8​a​7​e​f​a​0​8​d​a​6​9​4​a​0​f​d​3​f​d​8​f​a​9​9​7.
This test suite is specified by ``spec:/​testsuites/​performance-no-clock-0``.
There is a valid begin of test message at line :ref:`85
<ABuildConfigKeyTestsuitesPerformanceNoClock0Output0>`.
There is a valid end of test message at line :ref:`2444
<ABuildConfigKeyTestsuitesPerformanceNoClock0Output2400>`.  This indicates that
the test program executed without a detected error.
The following table lists an evaluation of the reported test information.

.. raw:: latex

    \\begin{scriptsize}

.. table::
    :class: longtable
    :widths: 42,8,20,20,10

    +-+-+-+-+-+
    | Property | Line | Reported | Expected | Status |
    +=+=+=+=+=+
    | RTEMS Git Commit | :ref:`86 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output0>` | 8​c​9​a​5​d​0​e​1​e​a​e​4​5​0​d​d​2​8​3​4​4​b​e​9​3​9​0​9​3​6​a​4​5​7​3​7​4​0​d | 5​8​b​f​f​6​2​2​d​6​1​0​8​6​5​c​7​6​d​a​0​4​5​e​8​c​c​6​7​a​a​5​6​c​3​2​b​7​c​8 | NOK |
    +-+-+-+-+-+
    | RTEMS_DEBUG | :ref:`88 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output0>` | not listed | not listed | OK |
    +-+-+-+-+-+
    | RTEMS_MULTIPROCESSING | :ref:`88 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output0>` | not listed | not listed | OK |
    +-+-+-+-+-+
    | RTEMS_PARAVIRT | :ref:`88 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output0>` | not listed | not listed | OK |
    +-+-+-+-+-+
    | RTEMS_POSIX_API | :ref:`88 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output0>` | not listed | not listed | OK |
    +-+-+-+-+-+
    | RTEMS_PROFILING | :ref:`88 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output0>` | not listed | not listed | OK |
    +-+-+-+-+-+
    | RTEMS_SMP | :ref:`88 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output0>` | not listed | not listed | OK |
    +-+-+-+-+-+
    | GCC Version | :ref:`89 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output0>` | 1​3​.​2​.​0 | 1​3​.​4​.​1​ ​2​0​2​6​0​1​0​8 | NOK |
    +-+-+-+-+-+

.. raw:: latex

    \\end{scriptsize}

The following table lists an evaluation of the test suite information reported
in lines :ref:`90 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output0>` up to
and including :ref:`2441
<ABuildConfigKeyTestsuitesPerformanceNoClock0Output2400>` of the test output.
The runtime measurements and test cases of this test suite are presented in the
following sections.

.. raw:: latex

    \\begin{scriptsize}

.. table::
    :class: longtable
    :widths: 42,8,20,20,10

    +-+-+-+-+-+
    | Property | Line | Reported | Expected | Status |
    +=+=+=+=+=+
    | GCC Version | :ref:`92 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output0>` | 1​3​.​2​.​0 | 1​3​.​4​.​1​ ​2​0​2​6​0​1​0​8 | NOK |
    +-+-+-+-+-+
    | RTEMS Git Commit | :ref:`93 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output0>` | 8​c​9​a​5​d​0​e​1​e​a​e​4​5​0​d​d​2​8​3​4​4​b​e​9​3​9​0​9​3​6​a​4​5​7​3​7​4​0​d | 5​8​b​f​f​6​2​2​d​6​1​0​8​6​5​c​7​6​d​a​0​4​5​e​8​c​c​6​7​a​a​5​6​c​3​2​b​7​c​8 | NOK |
    +-+-+-+-+-+
    | BSP | :ref:`94 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output0>` | g​r​7​1​2​r​c | g​r​7​1​2​r​c | OK |
    +-+-+-+-+-+
    | Build Label | :ref:`95 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output0>` | s​p​a​r​c​/​g​r​7​1​2​r​c​/​u​n​i​/​6​/​q​u​a​l​-​o​n​l​y | b​u​i​l​d​-​l​a​b​e​l | NOK |
    +-+-+-+-+-+
    | Target Hash | :ref:`96 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output0>` | c​p​I​0​9​J​u​6​o​r​F​2​e​o​J​c​m​J​i​4​i​g​e​I​a​r​y​p​s​R​N​w​U​x​T​r​Z​S​s​9​L​M​g​= | c​p​I​0​9​J​u​6​o​r​F​2​e​o​J​c​m​J​i​4​i​g​e​I​a​r​y​p​s​R​N​w​U​x​T​r​Z​S​s​9​L​M​g​=, o​q​N​H​r​l​F​i​_​j​s​i​c​o​5​y​g​H​k​-​O​c​f​e​M​9​o​a​Y​3​J​M​w​_​z​6​d​m​F​0​9​-​U​= | OK |
    +-+-+-+-+-+
    | RTEMS_DEBUG | :ref:`97 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output0>` | 0 | 0 | OK |
    +-+-+-+-+-+
    | RTEMS_MULTIPROCESSING | :ref:`98 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output0>` | 0 | 0 | OK |
    +-+-+-+-+-+
    | RTEMS_POSIX_API | :ref:`99 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output0>` | 0 | 0 | OK |
    +-+-+-+-+-+
    | RTEMS_PROFILING | :ref:`100 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output0>` | 0 | 0 | OK |
    +-+-+-+-+-+
    | RTEMS_SMP | :ref:`101 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output100>` | 0 | 0 | OK |
    +-+-+-+-+-+
    | Step Count | :ref:`2441 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output2400>` | 4039 | > 0 | OK |
    +-+-+-+-+-+
    | Failed Steps Count | :ref:`2441 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output2400>` | 0 | 0 | OK |
    +-+-+-+-+-+
    | Duration | :ref:`2441 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output2400>` | 56.968s | :math:`\\geq` 0 | OK |
    +-+-+-+-+-+
    | Report Hash | :ref:`2442 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output2400>` | D​7​R​a​0​9​o​3​6​-​R​i​f​r​d​Q​5​T​9​G​7​F​l​k​3​1​H​m​Q​L​9​B​Y​w​6​C​q​4​H​R​O​A​8​= | D​7​R​a​0​9​o​3​6​-​R​i​f​r​d​Q​5​T​9​G​7​F​l​k​3​1​H​m​Q​L​9​B​Y​w​6​C​q​4​H​R​O​A​8​= | OK |
    +-+-+-+-+-+

.. raw:: latex

    \\end{scriptsize}

.. _ABuildConfigKeyTestsuitesPerformanceNoClock0RtemsReqPerf:

Runtime measurement - spec:/​rtems/​req/​perf
*********************************************

For the runtime performance requirement ``spec:/​rtems/​req/​perf``, the
following runtime values were measured on this target and configuration in the
listed measurement environments.

.. image:: ../../../perf-images/a-build-config-key-rtems-req-perf.*
    :align: center
    :width: 50%

.. _ABuildConfigKeyTestsuitesPerformanceNoClock0RtemsReqPerfHotCache:

.. rubric:: Measurement environment - HotCache

The runtime measurement report for this
measurement environment was generated from lines :ref:`118 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output100>` up to and including
:ref:`131 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output100>` of the test output.

.. image:: ../../../perf-images/a-build-config-key-rtems-req-perf-HotCache.*
    :align: center
    :width: 50%

.. raw:: latex

    \\begin{scriptsize}

.. table::
    :class: longtable
    :widths: 15,45,25,15

    +-+-+-+-+
    | Limit Kind | Specified Limits | Actual Value | Status |
    +=+=+=+=+
    | Minimum | 298.000ns :math:`\\leq` Minimum | 275.000ns | NOK |
    +-+-+-+-+
    | Median | 298.000ns :math:`\\leq` Median :math:`\\leq` 1.192μs | 2.750μs | NOK |
    +-+-+-+-+
    | Maximum | Maximum :math:`\\leq` 1.192μs | 275.000ns | OK |
    +-+-+-+-+

.. raw:: latex

    \\end{scriptsize}

.. _ABuildConfigKeyTestsuitesPerformanceNoClock0RtemsReqPerfFullCache:

.. rubric:: Measurement environment - FullCache

The runtime measurement report for this
measurement environment was generated from lines :ref:`103 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output100>` up to and including
:ref:`117 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output100>` of the test output.

.. image:: ../../../perf-images/a-build-config-key-rtems-req-perf-FullCache.*
    :align: center
    :width: 50%

.. raw:: latex

    \\begin{scriptsize}

.. table::
    :class: longtable
    :widths: 15,45,25,15

    +-+-+-+-+
    | Limit Kind | Specified Limits | Actual Value | Status |
    +=+=+=+=+
    | Minimum | 275.000ns :math:`\\leq` Minimum | 275.000ns | OK |
    +-+-+-+-+
    | Median | 275.000ns :math:`\\leq` Median :math:`\\leq` 475.000ns | 275.000ns | OK |
    +-+-+-+-+
    | Maximum | Maximum :math:`\\leq` 475.000ns | 475.000ns | OK |
    +-+-+-+-+

.. raw:: latex

    \\end{scriptsize}

.. _ABuildConfigKeyTestsuitesPerformanceNoClock0RtemsReqPerfDirtyCache:

.. rubric:: Measurement environment - DirtyCache

The runtime measurement report for this
measurement environment was generated from lines :ref:`132 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output100>` up to and including
:ref:`145 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output100>` of the test output.

.. image:: ../../../perf-images/a-build-config-key-rtems-req-perf-DirtyCache.*
    :align: center
    :width: 50%

.. raw:: latex

    \\begin{scriptsize}

.. table::
    :class: longtable
    :widths: 15,45,25,15

    +-+-+-+-+
    | Limit Kind | Specified Limits | Actual Value | Status |
    +=+=+=+=+
    | Minimum | 588.600ns :math:`\\leq` Minimum | 2.125μs | OK |
    +-+-+-+-+
    | Median | 602.100ns :math:`\\leq` Median :math:`\\leq` 10.312μs | 21.250ms | NOK |
    +-+-+-+-+
    | Maximum | Maximum :math:`\\leq` 12.728μs | 2.125μs | OK |
    +-+-+-+-+

.. raw:: latex

    \\end{scriptsize}

.. _ABuildConfigKeyTestsuitesPerformanceNoClock0RtemsReqPerfLoad1:

.. rubric:: Measurement environment - Load/1

The runtime measurement report for this
measurement environment was generated from lines :ref:`146 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output100>` up to and including
:ref:`159 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output100>` of the test output.

.. image:: ../../../perf-images/a-build-config-key-rtems-req-perf-Load-1.*
    :align: center
    :width: 50%

.. raw:: latex

    \\begin{scriptsize}

.. table::
    :class: longtable
    :widths: 15,45,25,15

    +-+-+-+-+
    | Limit Kind | Specified Limits | Actual Value | Status |
    +=+=+=+=+
    | Minimum | 583.200ns :math:`\\leq` Minimum | 106.200ns | NOK |
    +-+-+-+-+
    | Median | 618.300ns :math:`\\leq` Median :math:`\\leq` 15.080μs | 1.062s | NOK |
    +-+-+-+-+
    | Maximum | Maximum :math:`\\leq` 0s | 1.062μs | NOK |
    +-+-+-+-+

.. raw:: latex

    \\end{scriptsize}

.. _ABuildConfigKeyTestsuitesPerformanceNoClock0ScoreCpuValPerf:

Test case - spec:/​score/​cpu/​val/​perf
****************************************

This test case is specified by
``spec:/​score/​cpu/​val/​perf``.

The following table lists an evaluation of
the test case information reported in lines :ref:`102 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output100>` up to and including :ref:`223 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output200>`
of the test output.

.. raw:: latex

    \\begin{scriptsize}

.. table::
    :class: longtable
    :widths: 42,8,20,20,10

    +-+-+-+-+-+
    | Property | Line | Reported | Expected | Status |
    +=+=+=+=+=+
    | Step Count | :ref:`223 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output200>` | 1 | > 0 | OK |
    +-+-+-+-+-+
    | Failed Steps Count | :ref:`223 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output200>` | 0 | 0 | OK |
    +-+-+-+-+-+
    | Duration | :ref:`223 <ABuildConfigKeyTestsuitesPerformanceNoClock0Output200>` | 3.654s | :math:`\\geq` 0 | OK |
    +-+-+-+-+-+

.. raw:: latex

    \\end{scriptsize}

This test case contains the following runtime measurements presented in the
preceeding sections:

- :ref:`spec:/​rtems/​req/​perf
  <ABuildConfigKeyTestsuitesPerformanceNoClock0RtemsReqPerf>`

.. _ABuildConfigKeyTestsuitesPerformanceNoClock0TestOutput:

Test output
***********

The test report was generated from the following test output.

.. raw:: latex

    \\begin{tiny}

.. _ABuildConfigKeyTestsuitesPerformanceNoClock0Output0:

.. code-block:: none
    :linenos:
    :lineno-start: 1

    ​*​*​*​ ​B​E​G​I​N​ ​O​F​ ​T​E​S​T​ ​T​e​s​t​s​u​i​t​e​s​P​e​r​f​o​r​m​a​n​c​e​N​o​C​l​o​c​k​0​ ​*​*​*
    ​*​*​*​ ​T​E​S​T​ ​V​E​R​S​I​O​N​:​ ​6​.​0​.​0​.​8​c​9​a​5​d​0​e​1​e​a​e​4​5​0​d​d​2​8​3​4​4​b​e​9​3​9​0​9​3​6​a​4​5​7​3​7​4​0​d
    ​*​*​*​ ​T​E​S​T​ ​S​T​A​T​E​:​ ​E​X​P​E​C​T​E​D​_​P​A​S​S
    ​*​*​*​ ​T​E​S​T​ ​B​U​I​L​D​:
    ​*​*​*​ ​T​E​S​T​ ​T​O​O​L​S​:​ ​1​3​.​2​.​0
    ​A​:​T​e​s​t​s​u​i​t​e​s​P​e​r​f​o​r​m​a​n​c​e​N​o​C​l​o​c​k​0
    ​S​:​P​l​a​t​f​o​r​m​:​R​T​E​M​S
    ​S​:​C​o​m​p​i​l​e​r​:​1​3​.​2​.​0
    ​S​:​V​e​r​s​i​o​n​:​6​.​0​.​0​.​8​c​9​a​5​d​0​e​1​e​a​e​4​5​0​d​d​2​8​3​4​4​b​e​9​3​9​0​9​3​6​a​4​5​7​3​7​4​0​d
    ​S​:​B​S​P​:​g​r​7​1​2​r​c
    ​S​:​B​u​i​l​d​L​a​b​e​l​:​s​p​a​r​c​/​g​r​7​1​2​r​c​/​u​n​i​/​6​/​q​u​a​l​-​o​n​l​y
    ​S​:​T​a​r​g​e​t​H​a​s​h​:​S​H​A​2​5​6​:​c​p​I​0​9​J​u​6​o​r​F​2​e​o​J​c​m​J​i​4​i​g​e​I​a​r​y​p​s​R​N​w​U​x​T​r​Z​S​s​9​L​M​g​=
    ​S​:​R​T​E​M​S​_​D​E​B​U​G​:​0
    ​S​:​R​T​E​M​S​_​M​U​L​T​I​P​R​O​C​E​S​S​I​N​G​:​0
    ​S​:​R​T​E​M​S​_​P​O​S​I​X​_​A​P​I​:​0
    ​S​:​R​T​E​M​S​_​P​R​O​F​I​L​I​N​G​:​0
    ​S​:​R​T​E​M​S​_​S​M​P​:​0
    ​B​:​S​c​o​r​e​C​p​u​V​a​l​P​e​r​f
    ​M​:​B​:​R​t​e​m​s​R​e​q​P​e​r​f
    ​M​:​V​:​F​u​l​l​C​a​c​h​e
    ​M​:​N​:​1​0​0
    ​M​:​S​:​9​9​:​0​.​0​0​0​0​0​0​2​7​5
    ​M​:​S​:​1​:​0​.​0​0​0​0​0​0​4​7​5
    ​M​:​M​I​:​0​.​0​0​0​0​0​0​2​7​5
    ​M​:​P​1​:​0​.​0​0​0​0​0​0​2​7​5
    ​M​:​Q​1​:​0​.​0​0​0​0​0​0​2​7​5
    ​M​:​Q​2​:​0​.​0​0​0​0​0​0​2​7​5
    ​M​:​Q​3​:​0​.​0​0​0​0​0​0​2​7​5
    ​M​:​P​9​9​:​0​.​0​0​0​0​0​0​4​7​5
    ​M​:​M​X​:​0​.​0​0​0​0​0​0​4​7​5
    ​M​:​M​A​D​:​0​.​0​0​0​0​0​0​0​0​0
    ​M​:​D​:​0​.​0​0​0​0​2​7​6​9​7
    ​M​:​E​:​R​t​e​m​s​R​e​q​P​e​r​f​:​D​:​0​.​0​0​7​1​6​5​3​6​2
    ​M​:​B​:​R​t​e​m​s​R​e​q​P​e​r​f
    ​M​:​V​:​H​o​t​C​a​c​h​e
    ​M​:​N​:​1​0​0
    ​M​:​S​:​1​0​0​:​0​.​0​0​0​0​0​0​2​7​5
    ​M​:​M​I​:​0​.​0​0​0​0​0​0​2​7​5
    ​M​:​P​1​:​0​.​0​0​0​0​0​0​2​7​5
    ​M​:​Q​1​:​0​.​0​0​0​0​0​0​2​7​5
    ​M​:​Q​2​:​0​.​0​0​0​0​0​0​2​7​5
    ​M​:​Q​3​:​0​.​0​0​0​0​0​0​2​7​5
    ​M​:​P​9​9​:​0​.​0​0​0​0​0​0​2​7​5
    ​M​:​M​X​:​0​.​0​0​0​0​0​0​2​7​5
    ​M​:​M​A​D​:​0​.​0​0​0​0​0​0​0​0​0
    ​M​:​D​:​0​.​0​0​0​0​2​7​4​9​7
    ​M​:​E​:​R​t​e​m​s​R​e​q​P​e​r​f​:​D​:​0​.​0​0​0​1​7​8​9​5​0
    ​M​:​B​:​R​t​e​m​s​R​e​q​P​e​r​f
    ​M​:​V​:​D​i​r​t​y​C​a​c​h​e
    ​M​:​N​:​1​0​0
    ​M​:​S​:​1​0​0​:​0​.​0​0​0​0​0​2​1​2​5
    ​M​:​M​I​:​0​.​0​0​0​0​0​2​1​2​5
    ​M​:​P​1​:​0​.​0​0​0​0​0​2​1​2​5
    ​M​:​Q​1​:​0​.​0​0​0​0​0​2​1​2​5
    ​M​:​Q​2​:​0​.​0​0​0​0​0​2​1​2​5
    ​M​:​Q​3​:​0​.​0​0​0​0​0​2​1​2​5
    ​M​:​P​9​9​:​0​.​0​0​0​0​0​2​1​2​5
    ​M​:​M​X​:​0​.​0​0​0​0​0​2​1​2​5
    ​M​:​M​A​D​:​0​.​0​0​0​0​0​0​0​0​0
    ​M​:​D​:​0​.​0​0​0​2​1​2​4​8​1
    ​M​:​E​:​R​t​e​m​s​R​e​q​P​e​r​f​:​D​:​0​.​0​0​5​2​3​1​9​3​7
    ​M​:​B​:​R​t​e​m​s​R​e​q​P​e​r​f
    ​M​:​V​:​L​o​a​d​/​1
    ​M​:​N​:​1​0​0
    ​M​:​S​:​1​0​0​:​0​.​0​0​0​0​0​1​0​6​2
    ​M​:​M​I​:​0​.​0​0​0​0​0​1​0​6​2
    ​M​:​P​1​:​0​.​0​0​0​0​0​1​0​6​2
    ​M​:​Q​1​:​0​.​0​0​0​0​0​1​0​6​2
    ​M​:​Q​2​:​0​.​0​0​0​0​0​1​0​6​2
    ​M​:​Q​3​:​0​.​0​0​0​0​0​1​0​6​2
    ​M​:​P​9​9​:​0​.​0​0​0​0​0​1​0​6​2
    ​M​:​M​X​:​0​.​0​0​0​0​0​1​0​6​2
    ​M​:​M​A​D​:​0​.​0​0​0​0​0​0​0​0​0
    ​M​:​D​:​0​.​0​0​0​1​0​6​2​4​1
    ​M​:​E​:​R​t​e​m​s​R​e​q​P​e​r​f​:​D​:​0​.​0​0​5​6​9​5​0​1​2
    ​E​:​S​c​o​r​e​C​p​u​V​a​l​P​e​r​f​:​N​:​1​:​F​:​0​:​D​:​3​.​6​5​4​4​4​0
    ​Z​:​T​e​s​t​s​u​i​t​e​s​P​e​r​f​o​r​m​a​n​c​e​N​o​C​l​o​c​k​0​:​C​:​7​:​N​:​4​0​3​9​:​F​:​0​:​D​:​5​6​.​9​6​7​5​2​4
    ​Y​:​R​e​p​o​r​t​H​a​s​h​:​S​H​A​2​5​6​:​D​7​R​a​0​9​o​3​6​-​R​i​f​r​d​Q​5​T​9​G​7​F​l​k​3​1​H​m​Q​L​9​B​Y​w​6​C​q​4​H​R​O​A​8​=
    ​
    ​*​*​*​ ​E​N​D​ ​O​F​ ​T​E​S​T​ ​T​e​s​t​s​u​i​t​e​s​P​e​r​f​o​r​m​a​n​c​e​N​o​C​l​o​c​k​0​ ​*​*​*
    ​
    ​ ​ 
    ​ ​ ​C​P​U​ ​0​:​ ​ ​P​r​o​g​r​a​m​ ​e​x​i​t​e​d​ ​n​o​r​m​a​l​l​y​.

.. raw:: latex

    \\end{tiny}"""

    assert _get_tr("a-build-config-key-testsuites-test-suite-fail.rst"
                   ) == """.. _ABuildConfigKeyTestsuitesTestSuiteFail:

Test suite - spec:/​testsuites/​test-suite-fail
###############################################

This report was produced by the
:file:`ts-fail.exe`
executable.  The executable file had an SHA512 digest of
6​4​3​b​3​4​5​9​e​e​1​9​d​9​b​7​f​2​b​a​4​f​a​2​3​2​e​b​a​a​c​f​6​d​5​d​d​d​9​a​e​a​0​a​6​9​0​c​1​e​4​d​d​5​5​a​9​5​6​c​e​d​d​5​5​1​2​7​7​4​3​d​c​f​b​e​8​6​3​6​b​f​b​f​8​8​9​8​0​e​f​9​4​9​7​0​0​4​f​1​2​b​8​c​f​a​2​e​2​0​c​0​2​1​3​7​c​f​6​d​d​8​a​9​d​0​a​0.
This test suite is specified by ``spec:/​testsuites/​test-suite-fail``.
There is a valid begin of test message at line :ref:`10
<ABuildConfigKeyTestsuitesTestSuiteFailOutput0>`.
The test output contains no end of test message.
The following table lists an evaluation of the reported test information.

.. raw:: latex

    \\begin{scriptsize}

.. table::
    :class: longtable
    :widths: 42,8,20,20,10

    +-+-+-+-+-+
    | Property | Line | Reported | Expected | Status |
    +=+=+=+=+=+
    | RTEMS Git Commit | :ref:`11 <ABuildConfigKeyTestsuitesTestSuiteFailOutput0>` | 8​c​9​a​5​d​0​e​1​e​a​e​4​5​0​d​d​2​8​3​4​4​b​e​9​3​9​0​9​3​6​a​4​5​7​3​7​4​0​d | 5​8​b​f​f​6​2​2​d​6​1​0​8​6​5​c​7​6​d​a​0​4​5​e​8​c​c​6​7​a​a​5​6​c​3​2​b​7​c​8 | NOK |
    +-+-+-+-+-+
    | RTEMS_DEBUG | :ref:`13 <ABuildConfigKeyTestsuitesTestSuiteFailOutput0>` | not listed | not listed | OK |
    +-+-+-+-+-+
    | RTEMS_MULTIPROCESSING | :ref:`13 <ABuildConfigKeyTestsuitesTestSuiteFailOutput0>` | not listed | not listed | OK |
    +-+-+-+-+-+
    | RTEMS_PARAVIRT | :ref:`13 <ABuildConfigKeyTestsuitesTestSuiteFailOutput0>` | not listed | not listed | OK |
    +-+-+-+-+-+
    | RTEMS_POSIX_API | :ref:`13 <ABuildConfigKeyTestsuitesTestSuiteFailOutput0>` | not listed | not listed | OK |
    +-+-+-+-+-+
    | RTEMS_PROFILING | :ref:`13 <ABuildConfigKeyTestsuitesTestSuiteFailOutput0>` | not listed | not listed | OK |
    +-+-+-+-+-+
    | RTEMS_SMP | :ref:`13 <ABuildConfigKeyTestsuitesTestSuiteFailOutput0>` | listed | not listed | NOK |
    +-+-+-+-+-+
    | GCC Version | :ref:`14 <ABuildConfigKeyTestsuitesTestSuiteFailOutput0>` | 6​.​0​.​0​.​8​c​9​a​5​d​0​e​1​e​a​e​4​5​0​d​d​2​8​3​4​4​b​e​9​3​9​0​9​3​6​a​4​5​7​3​7​4​0​d | 1​3​.​4​.​1​ ​2​0​2​6​0​1​0​8 | NOK |
    +-+-+-+-+-+

.. raw:: latex

    \\end{scriptsize}

The following table lists an evaluation of the test suite information reported
in lines :ref:`15 <ABuildConfigKeyTestsuitesTestSuiteFailOutput0>` up to and
including ? of the test output.
The test cases of this test suite are presented in the following sections.

.. raw:: latex

    \\begin{scriptsize}

.. table::
    :class: longtable
    :widths: 42,8,20,20,10

    +-+-+-+-+-+
    | Property | Line | Reported | Expected | Status |
    +=+=+=+=+=+
    | GCC Version | :ref:`17 <ABuildConfigKeyTestsuitesTestSuiteFailOutput0>` | 6​.​0​.​0​.​8​c​9​a​5​d​0​e​1​e​a​e​4​5​0​d​d​2​8​3​4​4​b​e​9​3​9​0​9​3​6​a​4​5​7​3​7​4​0​d | 1​3​.​4​.​1​ ​2​0​2​6​0​1​0​8 | NOK |
    +-+-+-+-+-+
    | RTEMS Git Commit | :ref:`18 <ABuildConfigKeyTestsuitesTestSuiteFailOutput0>` | 8​c​9​a​5​d​0​e​1​e​a​e​4​5​0​d​d​2​8​3​4​4​b​e​9​3​9​0​9​3​6​a​4​5​7​3​7​4​0​d | 5​8​b​f​f​6​2​2​d​6​1​0​8​6​5​c​7​6​d​a​0​4​5​e​8​c​c​6​7​a​a​5​6​c​3​2​b​7​c​8 | NOK |
    +-+-+-+-+-+
    | BSP | :ref:`19 <ABuildConfigKeyTestsuitesTestSuiteFailOutput0>` | g​r​7​4​0 | g​r​7​1​2​r​c | NOK |
    +-+-+-+-+-+
    | Build Label | :ref:`20 <ABuildConfigKeyTestsuitesTestSuiteFailOutput0>` | s​p​a​r​c​/​g​r​7​1​2​r​c​/​u​n​i​/​6​/​q​u​a​l​-​o​n​l​y | b​u​i​l​d​-​l​a​b​e​l | NOK |
    +-+-+-+-+-+
    | Target Hash | :ref:`21 <ABuildConfigKeyTestsuitesTestSuiteFailOutput0>` | ​ | c​p​I​0​9​J​u​6​o​r​F​2​e​o​J​c​m​J​i​4​i​g​e​I​a​r​y​p​s​R​N​w​U​x​T​r​Z​S​s​9​L​M​g​=, o​q​N​H​r​l​F​i​_​j​s​i​c​o​5​y​g​H​k​-​O​c​f​e​M​9​o​a​Y​3​J​M​w​_​z​6​d​m​F​0​9​-​U​= | OK |
    +-+-+-+-+-+
    | RTEMS_DEBUG | :ref:`22 <ABuildConfigKeyTestsuitesTestSuiteFailOutput0>` | 0 | 0 | OK |
    +-+-+-+-+-+
    | RTEMS_MULTIPROCESSING | :ref:`23 <ABuildConfigKeyTestsuitesTestSuiteFailOutput0>` | 0 | 0 | OK |
    +-+-+-+-+-+
    | RTEMS_POSIX_API | :ref:`24 <ABuildConfigKeyTestsuitesTestSuiteFailOutput0>` | 0 | 0 | OK |
    +-+-+-+-+-+
    | RTEMS_PROFILING | :ref:`25 <ABuildConfigKeyTestsuitesTestSuiteFailOutput0>` | 0 | 0 | OK |
    +-+-+-+-+-+
    | RTEMS_SMP | :ref:`26 <ABuildConfigKeyTestsuitesTestSuiteFailOutput0>` | 1 | 0 | NOK |
    +-+-+-+-+-+
    | Step Count | :ref:`35 <ABuildConfigKeyTestsuitesTestSuiteFailOutput0>` | ? | > 0 | NOK |
    +-+-+-+-+-+
    | Failed Steps Count | :ref:`35 <ABuildConfigKeyTestsuitesTestSuiteFailOutput0>` | 1 | 0 | NOK |
    +-+-+-+-+-+
    | Duration | :ref:`35 <ABuildConfigKeyTestsuitesTestSuiteFailOutput0>` | 1.407ms | :math:`\\geq` 0 | OK |
    +-+-+-+-+-+
    | Report Hash | :ref:`36 <ABuildConfigKeyTestsuitesTestSuiteFailOutput0>` | 5​q​C​F​a​t​f​P​B​z​G​v​b​b​R​6​c​_​C​n​o​f​H​e​U​W​I​F​Z​R​D​w​e​_​U​R​i​K​6​S​3​l​s​= | 5​q​C​F​a​t​f​P​B​z​G​v​b​b​R​6​c​_​C​n​o​f​H​e​U​W​I​F​Z​R​D​w​e​_​U​R​i​K​6​S​3​l​s​= | OK |
    +-+-+-+-+-+

.. raw:: latex

    \\end{scriptsize}

.. _ABuildConfigKeyTestsuitesTestSuiteFailRtemsValTestCaseFail:

Test case - spec:/​rtems/​val/​test-case-fail
*********************************************

This test case is specified by
``spec:/​rtems/​val/​test-case-fail``.
It runs the following parameterized test cases:

- ``spec:/​req/​root`` reported in line :ref:`31
  <ABuildConfigKeyTestsuitesTestSuiteFailOutput0>`

- ``spec:/​rtems/​req/​func`` reported in line :ref:`32
  <ABuildConfigKeyTestsuitesTestSuiteFailOutput0>`

The following table lists an evaluation of
the test case information reported in lines :ref:`29 <ABuildConfigKeyTestsuitesTestSuiteFailOutput0>` up to and including :ref:`34 <ABuildConfigKeyTestsuitesTestSuiteFailOutput0>`
of the test output.

.. raw:: latex

    \\begin{scriptsize}

.. table::
    :class: longtable
    :widths: 42,8,20,20,10

    +-+-+-+-+-+
    | Property | Line | Reported | Expected | Status |
    +=+=+=+=+=+
    | Step Count | :ref:`34 <ABuildConfigKeyTestsuitesTestSuiteFailOutput0>` | 0 | > 0 | NOK |
    +-+-+-+-+-+
    | Failed Steps Count | :ref:`34 <ABuildConfigKeyTestsuitesTestSuiteFailOutput0>` | ? | 0 | NOK |
    +-+-+-+-+-+
    | Duration | :ref:`34 <ABuildConfigKeyTestsuitesTestSuiteFailOutput0>` | ? | :math:`\\geq` 0 | NOK |
    +-+-+-+-+-+

.. raw:: latex

    \\end{scriptsize}

.. _ABuildConfigKeyTestsuitesTestSuiteFailTestOutput:

Test output
***********

The test report was generated from the following test output.

.. raw:: latex

    \\begin{tiny}

.. _ABuildConfigKeyTestsuitesTestSuiteFailOutput0:

.. code-block:: none
    :linenos:
    :lineno-start: 1

    ​
    ​ ​S​I​S​ ​-​ ​S​P​A​R​C​/​R​I​S​C​V​ ​i​n​s​t​r​u​c​t​i​o​n​ ​s​i​m​u​l​a​t​o​r​ ​2​.​3​0​,​ ​ ​c​o​p​y​r​i​g​h​t​ ​J​i​r​i​ ​G​a​i​s​l​e​r​ ​2​0​2​0
    ​ ​B​u​g​-​r​e​p​o​r​t​s​ ​t​o​ ​j​i​r​i​@​g​a​i​s​l​e​r​.​s​e
    ​
    ​ ​G​R​7​4​0​/​L​E​O​N​4​ ​e​m​u​l​a​t​i​o​n​ ​e​n​a​b​l​e​d​,​ ​1​ ​c​p​u​s​ ​o​n​l​i​n​e​,​ ​d​e​l​t​a​ ​5​0​ ​c​l​o​c​k​s
    ​
    ​ ​L​o​a​d​e​d​ ​/​o​p​t​/​r​t​e​m​s​-​s​p​a​r​c​-​g​r​7​4​0​-​7​/​b​u​i​l​d​/​s​p​a​r​c​-​g​r​7​4​0​-​u​n​i​-​b​s​p​-​q​u​a​l​-​o​n​l​y​/​s​p​a​r​c​/​g​r​7​4​0​-​u​n​i​-​q​u​a​l​-​o​n​l​y​/​t​e​s​t​s​/​t​s​-​f​a​i​l​.​e​x​e​,​ ​e​n​t​r​y​ ​0​x​0​0​0​0​0​0​0​0
    ​
    ​
    ​*​*​*​ ​B​E​G​I​N​ ​O​F​ ​T​E​S​T​ ​T​e​s​t​s​u​i​t​e​s​T​e​s​t​S​u​i​t​e​F​a​i​l​ ​*​*​*
    ​*​*​*​ ​T​E​S​T​ ​V​E​R​S​I​O​N​:​ ​6​.​0​.​0​.​8​c​9​a​5​d​0​e​1​e​a​e​4​5​0​d​d​2​8​3​4​4​b​e​9​3​9​0​9​3​6​a​4​5​7​3​7​4​0​d
    ​*​*​*​ ​T​E​S​T​ ​S​T​A​T​E​:​ ​E​X​P​E​C​T​E​D​_​P​A​S​S
    ​*​*​*​ ​T​E​S​T​ ​B​U​I​L​D​:
    ​*​*​*​ ​T​E​S​T​ ​T​O​O​L​S​:​ ​6​.​0​.​0​.​8​c​9​a​5​d​0​e​1​e​a​e​4​5​0​d​d​2​8​3​4​4​b​e​9​3​9​0​9​3​6​a​4​5​7​3​7​4​0​d
    ​A​:​T​e​s​t​s​u​i​t​e​s​T​e​s​t​S​u​i​t​e​F​a​i​l
    ​S​:​P​l​a​t​f​o​r​m​:​R​T​E​M​S
    ​S​:​C​o​m​p​i​l​e​r​:​6​.​0​.​0​.​8​c​9​a​5​d​0​e​1​e​a​e​4​5​0​d​d​2​8​3​4​4​b​e​9​3​9​0​9​3​6​a​4​5​7​3​7​4​0​d
    ​S​:​V​e​r​s​i​o​n​:​6​.​0​.​0​.​8​c​9​a​5​d​0​e​1​e​a​e​4​5​0​d​d​2​8​3​4​4​b​e​9​3​9​0​9​3​6​a​4​5​7​3​7​4​0​d
    ​S​:​B​S​P​:​g​r​7​4​0
    ​S​:​B​u​i​l​d​L​a​b​e​l​:​s​p​a​r​c​/​g​r​7​1​2​r​c​/​u​n​i​/​6​/​q​u​a​l​-​o​n​l​y
    ​S​:​T​a​r​g​e​t​H​a​s​h​:​S​H​A​2​5​6​:​c​p​I​0​9​J​u​6​o​r​F​2​e​o​J​c​m​J​i​4​i​g​e​I​a​r​y​p​s​R​N​w​U​x​T​r​Z​S​s​9​L​M​g​=
    ​S​:​R​T​E​M​S​_​D​E​B​U​G​:​0
    ​S​:​R​T​E​M​S​_​M​U​L​T​I​P​R​O​C​E​S​S​I​N​G​:​0
    ​S​:​R​T​E​M​S​_​P​O​S​I​X​_​A​P​I​:​0
    ​S​:​R​T​E​M​S​_​P​R​O​F​I​L​I​N​G​:​0
    ​S​:​R​T​E​M​S​_​S​M​P​:​0
    ​B​:​R​t​e​m​s​V​a​l​T​e​s​t​C​a​s​e​N​o​S​p​e​c
    ​E​:​R​t​e​m​s​V​a​l​T​e​s​t​C​a​s​e​N​o​S​p​e​c​:​N​:​1​:​F​:​0​:​D​:​0​.​0​0​0​1​2​1
    ​B​:​R​t​e​m​s​V​a​l​T​e​s​t​C​a​s​e​F​a​i​l
    ​F​:​0​:​0​:​R​U​N​:​t​c​-​f​a​i​l​.​c​:​1​9
    ​R​:​R​e​q​R​o​o​t
    ​R​:​R​t​e​m​s​R​e​q​F​u​n​c
    ​R​:​N​o​S​p​e​c​R​e​m​a​r​k
    ​E​:​R​t​e​m​s​V​a​l​T​e​s​t​C​a​s​e​F​a​i​l​:​N​:​1​:​F​:​1​:​D​:​0​.​0​0​0​4​9​1
    ​Z​:​T​e​s​t​s​u​i​t​e​s​T​e​s​t​S​u​i​t​e​F​a​i​l​:​C​:​2​:​N​:​2​:​F​:​1​:​D​:​0​.​0​0​1​4​0​7
    ​Y​:​R​e​p​o​r​t​H​a​s​h​:​S​H​A​2​5​6​:​5​q​C​F​a​t​f​P​B​z​G​v​b​b​R​6​c​_​C​n​o​f​H​e​U​W​I​F​Z​R​D​w​e​_​U​R​i​K​6​S​3​l​s​=
    ​c​p​u​ ​0​ ​i​n​ ​e​r​r​o​r​ ​m​o​d​e​ ​(​t​t​ ​=​ ​0​x​8​0​)
    ​ ​ ​ ​3​5​8​3​3​0​ ​ ​0​0​0​0​3​0​a​0​:​ ​ ​9​1​d​0​2​0​0​0​ ​ ​ ​t​a​ ​ ​0​x​0

.. raw:: latex

    \\end{tiny}"""

    assert _get_tr("a-build-config-key-testsuites-test-suite-pass.rst"
                   ) == """.. _ABuildConfigKeyTestsuitesTestSuitePass:

Test suite - spec:/​testsuites/​test-suite-pass
###############################################

This report was produced by the
:file:`ts-pass.exe`
executable.  The executable file had an SHA512 digest of
c​5​7​9​3​5​d​c​e​6​5​e​7​b​e​4​8​0​8​3​1​c​6​a​b​b​e​0​3​8​d​0​6​f​e​6​c​7​9​d​d​0​b​d​d​6​b​1​e​f​1​1​8​8​c​9​1​6​9​5​b​8​9​b​f​e​2​9​7​3​d​e​1​f​7​d​0​b​a​0​2​0​5​8​f​7​8​d​f​b​3​1​c​6​f​1​c​c​f​2​7​4​6​d​0​0​0​b​4​8​7​f​5​7​9​6​5​3​4​c​2​9​9​c​9​e​b​a.
This test suite is specified by ``spec:/​testsuites/​test-suite-pass``.
There is a valid begin of test message at line :ref:`10
<ABuildConfigKeyTestsuitesTestSuitePassOutput0>`.
There is a valid end of test message at line :ref:`33
<ABuildConfigKeyTestsuitesTestSuitePassOutput0>`.  This indicates that the test
program executed without a detected error.
The following table lists an evaluation of the reported test information.

.. raw:: latex

    \\begin{scriptsize}

.. table::
    :class: longtable
    :widths: 42,8,20,20,10

    +-+-+-+-+-+
    | Property | Line | Reported | Expected | Status |
    +=+=+=+=+=+
    | RTEMS Git Commit | :ref:`11 <ABuildConfigKeyTestsuitesTestSuitePassOutput0>` | 4​2​6​0​8​4​8​f​3​a​1​6​b​1​5​a​8​e​8​0​7​d​6​d​4​5​f​2​6​8​b​1​0​3​a​e​e​7​9​c | 5​8​b​f​f​6​2​2​d​6​1​0​8​6​5​c​7​6​d​a​0​4​5​e​8​c​c​6​7​a​a​5​6​c​3​2​b​7​c​8 | NOK |
    +-+-+-+-+-+
    | RTEMS_DEBUG | :ref:`13 <ABuildConfigKeyTestsuitesTestSuitePassOutput0>` | not listed | not listed | OK |
    +-+-+-+-+-+
    | RTEMS_MULTIPROCESSING | :ref:`13 <ABuildConfigKeyTestsuitesTestSuitePassOutput0>` | not listed | not listed | OK |
    +-+-+-+-+-+
    | RTEMS_PARAVIRT | :ref:`13 <ABuildConfigKeyTestsuitesTestSuitePassOutput0>` | not listed | not listed | OK |
    +-+-+-+-+-+
    | RTEMS_POSIX_API | :ref:`13 <ABuildConfigKeyTestsuitesTestSuitePassOutput0>` | not listed | not listed | OK |
    +-+-+-+-+-+
    | RTEMS_PROFILING | :ref:`13 <ABuildConfigKeyTestsuitesTestSuitePassOutput0>` | not listed | not listed | OK |
    +-+-+-+-+-+
    | RTEMS_SMP | :ref:`13 <ABuildConfigKeyTestsuitesTestSuitePassOutput0>` | not listed | not listed | OK |
    +-+-+-+-+-+
    | GCC Version | :ref:`14 <ABuildConfigKeyTestsuitesTestSuitePassOutput0>` | 6​.​0​.​0​.​8​c​9​a​5​d​0​e​1​e​a​e​4​5​0​d​d​2​8​3​4​4​b​e​9​3​9​0​9​3​6​a​4​5​7​3​7​4​0​d | 1​3​.​4​.​1​ ​2​0​2​6​0​1​0​8 | NOK |
    +-+-+-+-+-+

.. raw:: latex

    \\end{scriptsize}

The following table lists an evaluation of the test suite information reported
in lines :ref:`15 <ABuildConfigKeyTestsuitesTestSuitePassOutput0>` up to and
including :ref:`30 <ABuildConfigKeyTestsuitesTestSuitePassOutput0>` of the test
output.
The test cases of this test suite are presented in the following sections.

.. raw:: latex

    \\begin{scriptsize}

.. table::
    :class: longtable
    :widths: 42,8,20,20,10

    +-+-+-+-+-+
    | Property | Line | Reported | Expected | Status |
    +=+=+=+=+=+
    | GCC Version | :ref:`17 <ABuildConfigKeyTestsuitesTestSuitePassOutput0>` | 6​.​0​.​0​.​8​c​9​a​5​d​0​e​1​e​a​e​4​5​0​d​d​2​8​3​4​4​b​e​9​3​9​0​9​3​6​a​4​5​7​3​7​4​0​d | 1​3​.​4​.​1​ ​2​0​2​6​0​1​0​8 | NOK |
    +-+-+-+-+-+
    | RTEMS Git Commit | :ref:`18 <ABuildConfigKeyTestsuitesTestSuitePassOutput0>` | 4​2​6​0​8​4​8​f​3​a​1​6​b​1​5​a​8​e​8​0​7​d​6​d​4​5​f​2​6​8​b​1​0​3​a​e​e​7​9​c | 5​8​b​f​f​6​2​2​d​6​1​0​8​6​5​c​7​6​d​a​0​4​5​e​8​c​c​6​7​a​a​5​6​c​3​2​b​7​c​8 | NOK |
    +-+-+-+-+-+
    | BSP | :ref:`19 <ABuildConfigKeyTestsuitesTestSuitePassOutput0>` | g​r​7​4​0 | g​r​7​1​2​r​c | NOK |
    +-+-+-+-+-+
    | Build Label | :ref:`20 <ABuildConfigKeyTestsuitesTestSuitePassOutput0>` | s​p​a​r​c​/​g​r​7​1​2​r​c​/​u​n​i​/​6​/​q​u​a​l​-​o​n​l​y | b​u​i​l​d​-​l​a​b​e​l | NOK |
    +-+-+-+-+-+
    | Target Hash | :ref:`21 <ABuildConfigKeyTestsuitesTestSuitePassOutput0>` | _​x​Q​e​T​N​J​w​S​l​a​2​b​V​b​h​W​P​V​c​I​0​e​m​L​k​2​b​E​_​G​V​Q​f​v​z​t​9​C​N​8​4​k​= | c​p​I​0​9​J​u​6​o​r​F​2​e​o​J​c​m​J​i​4​i​g​e​I​a​r​y​p​s​R​N​w​U​x​T​r​Z​S​s​9​L​M​g​=, o​q​N​H​r​l​F​i​_​j​s​i​c​o​5​y​g​H​k​-​O​c​f​e​M​9​o​a​Y​3​J​M​w​_​z​6​d​m​F​0​9​-​U​= | NOK |
    +-+-+-+-+-+
    | RTEMS_DEBUG | :ref:`22 <ABuildConfigKeyTestsuitesTestSuitePassOutput0>` | 0 | 0 | OK |
    +-+-+-+-+-+
    | RTEMS_MULTIPROCESSING | :ref:`23 <ABuildConfigKeyTestsuitesTestSuitePassOutput0>` | 0 | 0 | OK |
    +-+-+-+-+-+
    | RTEMS_POSIX_API | :ref:`24 <ABuildConfigKeyTestsuitesTestSuitePassOutput0>` | 0 | 0 | OK |
    +-+-+-+-+-+
    | RTEMS_PROFILING | :ref:`25 <ABuildConfigKeyTestsuitesTestSuitePassOutput0>` | 0 | 0 | OK |
    +-+-+-+-+-+
    | RTEMS_SMP | :ref:`26 <ABuildConfigKeyTestsuitesTestSuitePassOutput0>` | 0 | 0 | OK |
    +-+-+-+-+-+
    | Step Count | :ref:`30 <ABuildConfigKeyTestsuitesTestSuitePassOutput0>` | 1 | > 0 | OK |
    +-+-+-+-+-+
    | Failed Steps Count | :ref:`30 <ABuildConfigKeyTestsuitesTestSuitePassOutput0>` | 0 | 0 | OK |
    +-+-+-+-+-+
    | Duration | :ref:`30 <ABuildConfigKeyTestsuitesTestSuitePassOutput0>` | 532.000μs | :math:`\\geq` 0 | OK |
    +-+-+-+-+-+
    | Report Hash | :ref:`31 <ABuildConfigKeyTestsuitesTestSuitePassOutput0>` | x​N​Q​k​Z​p​l​2​T​5​x​S​d​K​_​f​Z​m​9​3​6​g​z​D​F​2​Y​t​Y​M​z​N​5​N​5​7​y​P​Z​h​u​o​M​= | x​N​Q​k​Z​p​l​2​T​5​x​S​d​K​_​f​Z​m​9​3​6​g​z​D​F​2​Y​t​Y​M​z​N​5​N​5​7​y​P​Z​h​u​o​M​= | OK |
    +-+-+-+-+-+

.. raw:: latex

    \\end{scriptsize}

.. _ABuildConfigKeyTestsuitesTestSuitePassRtemsValTestCasePass:

Test case - spec:/​rtems/​val/​test-case-pass
*********************************************

This test case is specified by
``spec:/​rtems/​val/​test-case-pass``.
It runs the parameterized test case
``spec:/​rtems/​req/​func`` reported in line :ref:`28 <ABuildConfigKeyTestsuitesTestSuitePassOutput0>`.

The following table lists an evaluation of
the test case information reported in lines :ref:`27 <ABuildConfigKeyTestsuitesTestSuitePassOutput0>` up to and including :ref:`29 <ABuildConfigKeyTestsuitesTestSuitePassOutput0>`
of the test output.

.. raw:: latex

    \\begin{scriptsize}

.. table::
    :class: longtable
    :widths: 42,8,20,20,10

    +-+-+-+-+-+
    | Property | Line | Reported | Expected | Status |
    +=+=+=+=+=+
    | Step Count | :ref:`29 <ABuildConfigKeyTestsuitesTestSuitePassOutput0>` | 1 | > 0 | OK |
    +-+-+-+-+-+
    | Failed Steps Count | :ref:`29 <ABuildConfigKeyTestsuitesTestSuitePassOutput0>` | 0 | 0 | OK |
    +-+-+-+-+-+
    | Duration | :ref:`29 <ABuildConfigKeyTestsuitesTestSuitePassOutput0>` | 56.000μs | :math:`\\geq` 0 | OK |
    +-+-+-+-+-+

.. raw:: latex

    \\end{scriptsize}

.. _ABuildConfigKeyTestsuitesTestSuitePassTestOutput:

Test output
***********

The test report was generated from the following test output.

.. raw:: latex

    \\begin{tiny}

.. _ABuildConfigKeyTestsuitesTestSuitePassOutput0:

.. code-block:: none
    :linenos:
    :lineno-start: 1

    ​
    ​ ​S​I​S​ ​-​ ​S​P​A​R​C​/​R​I​S​C​V​ ​i​n​s​t​r​u​c​t​i​o​n​ ​s​i​m​u​l​a​t​o​r​ ​2​.​3​0​,​ ​ ​c​o​p​y​r​i​g​h​t​ ​J​i​r​i​ ​G​a​i​s​l​e​r​ ​2​0​2​0
    ​ ​B​u​g​-​r​e​p​o​r​t​s​ ​t​o​ ​j​i​r​i​@​g​a​i​s​l​e​r​.​s​e
    ​
    ​ ​G​R​7​4​0​/​L​E​O​N​4​ ​e​m​u​l​a​t​i​o​n​ ​e​n​a​b​l​e​d​,​ ​1​ ​c​p​u​s​ ​o​n​l​i​n​e​,​ ​d​e​l​t​a​ ​5​0​ ​c​l​o​c​k​s
    ​
    ​ ​L​o​a​d​e​d​ ​/​o​p​t​/​r​t​e​m​s​-​s​p​a​r​c​-​g​r​7​4​0​-​7​/​b​u​i​l​d​/​s​p​a​r​c​-​g​r​7​4​0​-​u​n​i​-​b​s​p​-​q​u​a​l​-​o​n​l​y​/​s​p​a​r​c​/​g​r​7​4​0​-​u​n​i​-​q​u​a​l​-​o​n​l​y​/​t​e​s​t​s​/​t​s​-​p​a​s​s​.​e​x​e​,​ ​e​n​t​r​y​ ​0​x​0​0​0​0​0​0​0​0
    ​
    ​
    ​*​*​*​ ​B​E​G​I​N​ ​O​F​ ​T​E​S​T​ ​T​e​s​t​s​u​i​t​e​s​T​e​s​t​S​u​i​t​e​P​a​s​s​ ​*​*​*
    ​*​*​*​ ​T​E​S​T​ ​V​E​R​S​I​O​N​:​ ​6​.​0​.​0​.​4​2​6​0​8​4​8​f​3​a​1​6​b​1​5​a​8​e​8​0​7​d​6​d​4​5​f​2​6​8​b​1​0​3​a​e​e​7​9​c
    ​*​*​*​ ​T​E​S​T​ ​S​T​A​T​E​:​ ​E​X​P​E​C​T​E​D​_​P​A​S​S
    ​*​*​*​ ​T​E​S​T​ ​B​U​I​L​D​:
    ​*​*​*​ ​T​E​S​T​ ​T​O​O​L​S​:​ ​6​.​0​.​0​.​8​c​9​a​5​d​0​e​1​e​a​e​4​5​0​d​d​2​8​3​4​4​b​e​9​3​9​0​9​3​6​a​4​5​7​3​7​4​0​d
    ​A​:​T​e​s​t​s​u​i​t​e​s​T​e​s​t​S​u​i​t​e​P​a​s​s
    ​S​:​P​l​a​t​f​o​r​m​:​R​T​E​M​S
    ​S​:​C​o​m​p​i​l​e​r​:​6​.​0​.​0​.​8​c​9​a​5​d​0​e​1​e​a​e​4​5​0​d​d​2​8​3​4​4​b​e​9​3​9​0​9​3​6​a​4​5​7​3​7​4​0​d
    ​S​:​V​e​r​s​i​o​n​:​6​.​0​.​0​.​4​2​6​0​8​4​8​f​3​a​1​6​b​1​5​a​8​e​8​0​7​d​6​d​4​5​f​2​6​8​b​1​0​3​a​e​e​7​9​c
    ​S​:​B​S​P​:​g​r​7​4​0
    ​S​:​B​u​i​l​d​L​a​b​e​l​:​s​p​a​r​c​/​g​r​7​1​2​r​c​/​u​n​i​/​6​/​q​u​a​l​-​o​n​l​y
    ​S​:​T​a​r​g​e​t​H​a​s​h​:​S​H​A​2​5​6​:​_​x​Q​e​T​N​J​w​S​l​a​2​b​V​b​h​W​P​V​c​I​0​e​m​L​k​2​b​E​_​G​V​Q​f​v​z​t​9​C​N​8​4​k​=
    ​S​:​R​T​E​M​S​_​D​E​B​U​G​:​0
    ​S​:​R​T​E​M​S​_​M​U​L​T​I​P​R​O​C​E​S​S​I​N​G​:​0
    ​S​:​R​T​E​M​S​_​P​O​S​I​X​_​A​P​I​:​0
    ​S​:​R​T​E​M​S​_​P​R​O​F​I​L​I​N​G​:​0
    ​S​:​R​T​E​M​S​_​S​M​P​:​0
    ​B​:​R​t​e​m​s​V​a​l​T​e​s​t​C​a​s​e​P​a​s​s
    ​R​:​R​t​e​m​s​R​e​q​F​u​n​c
    ​E​:​R​t​e​m​s​V​a​l​T​e​s​t​C​a​s​e​P​a​s​s​:​N​:​1​:​F​:​0​:​D​:​0​.​0​0​0​0​5​6
    ​Z​:​T​e​s​t​s​u​i​t​e​s​T​e​s​t​S​u​i​t​e​P​a​s​s​:​C​:​1​:​N​:​1​:​F​:​0​:​D​:​0​.​0​0​0​5​3​2
    ​Y​:​R​e​p​o​r​t​H​a​s​h​:​S​H​A​2​5​6​:​x​N​Q​k​Z​p​l​2​T​5​x​S​d​K​_​f​Z​m​9​3​6​g​z​D​F​2​Y​t​Y​M​z​N​5​N​5​7​y​P​Z​h​u​o​M​=
    ​
    ​*​*​*​ ​E​N​D​ ​O​F​ ​T​E​S​T​ ​T​e​s​t​s​u​i​t​e​s​T​e​s​t​S​u​i​t​e​P​a​s​s​ ​*​*​*
    ​
    ​c​p​u​ ​0​ ​i​n​ ​e​r​r​o​r​ ​m​o​d​e​ ​(​t​t​ ​=​ ​0​x​8​0​)
    ​ ​ ​ ​1​7​3​3​5​2​ ​ ​0​0​0​0​2​2​6​0​:​ ​ ​9​1​d​0​2​0​0​0​ ​ ​ ​t​a​ ​ ​0​x​0

.. raw:: latex

    \\end{tiny}"""

    assert _get_tr("a-build-config-key-testsuites-test-suite-xfail.rst"
                   ) == """.. _ABuildConfigKeyTestsuitesTestSuiteXfail:

Test suite - spec:/​testsuites/​test-suite-xfail
################################################

This report was produced by the
:file:`ts-xfail.exe`
executable.  The executable file had an SHA512 digest of
2​4​3​2​3​d​d​6​0​5​d​2​5​c​3​3​4​7​4​2​e​e​7​d​a​e​c​a​6​2​9​b​2​5​e​7​6​0​c​3​d​2​2​1​8​c​2​e​b​a​a​d​a​6​8​8​c​5​c​2​d​4​1​1​c​3​b​5​9​d​3​0​2​b​a​0​f​a​3​2​e​3​8​3​6​6​6​e​5​e​5​b​d​1​e​5​3​e​4​9​8​2​a​2​b​9​d​8​d​c​8​d​0​c​3​8​1​5​9​3​1​6​0​4​1​5​1​d.
This test suite is specified by ``spec:/​testsuites/​test-suite-xfail``.
There is a valid begin of test message at line :ref:`10
<ABuildConfigKeyTestsuitesTestSuiteXfailOutput0>`.
The test output contains no end of test message.
The following table lists an evaluation of the reported test information.

.. raw:: latex

    \\begin{scriptsize}

.. table::
    :class: longtable
    :widths: 42,8,20,20,10

    +-+-+-+-+-+
    | Property | Line | Reported | Expected | Status |
    +=+=+=+=+=+
    | RTEMS Git Commit | :ref:`11 <ABuildConfigKeyTestsuitesTestSuiteXfailOutput0>` | 8​c​9​a​5​d​0​e​1​e​a​e​4​5​0​d​d​2​8​3​4​4​b​e​9​3​9​0​9​3​6​a​4​5​7​3​7​4​0​d | 5​8​b​f​f​6​2​2​d​6​1​0​8​6​5​c​7​6​d​a​0​4​5​e​8​c​c​6​7​a​a​5​6​c​3​2​b​7​c​8 | NOK |
    +-+-+-+-+-+
    | RTEMS_DEBUG | :ref:`13 <ABuildConfigKeyTestsuitesTestSuiteXfailOutput0>` | not listed | not listed | OK |
    +-+-+-+-+-+
    | RTEMS_MULTIPROCESSING | :ref:`13 <ABuildConfigKeyTestsuitesTestSuiteXfailOutput0>` | not listed | not listed | OK |
    +-+-+-+-+-+
    | RTEMS_PARAVIRT | :ref:`13 <ABuildConfigKeyTestsuitesTestSuiteXfailOutput0>` | not listed | not listed | OK |
    +-+-+-+-+-+
    | RTEMS_POSIX_API | :ref:`13 <ABuildConfigKeyTestsuitesTestSuiteXfailOutput0>` | not listed | not listed | OK |
    +-+-+-+-+-+
    | RTEMS_PROFILING | :ref:`13 <ABuildConfigKeyTestsuitesTestSuiteXfailOutput0>` | not listed | not listed | OK |
    +-+-+-+-+-+
    | RTEMS_SMP | :ref:`13 <ABuildConfigKeyTestsuitesTestSuiteXfailOutput0>` | not listed | not listed | OK |
    +-+-+-+-+-+
    | GCC Version | :ref:`14 <ABuildConfigKeyTestsuitesTestSuiteXfailOutput0>` | 6​.​0​.​0​.​8​c​9​a​5​d​0​e​1​e​a​e​4​5​0​d​d​2​8​3​4​4​b​e​9​3​9​0​9​3​6​a​4​5​7​3​7​4​0​d | 1​3​.​4​.​1​ ​2​0​2​6​0​1​0​8 | NOK |
    +-+-+-+-+-+

.. raw:: latex

    \\end{scriptsize}

The following table lists an evaluation of the test suite information reported
in lines :ref:`15 <ABuildConfigKeyTestsuitesTestSuiteXfailOutput0>` up to and
including :ref:`30 <ABuildConfigKeyTestsuitesTestSuiteXfailOutput0>` of the
test output.
The test cases of this test suite are presented in the following sections.

.. raw:: latex

    \\begin{scriptsize}

.. table::
    :class: longtable
    :widths: 42,8,20,20,10

    +-+-+-+-+-+
    | Property | Line | Reported | Expected | Status |
    +=+=+=+=+=+
    | GCC Version | :ref:`17 <ABuildConfigKeyTestsuitesTestSuiteXfailOutput0>` | 6​.​0​.​0​.​8​c​9​a​5​d​0​e​1​e​a​e​4​5​0​d​d​2​8​3​4​4​b​e​9​3​9​0​9​3​6​a​4​5​7​3​7​4​0​d | 1​3​.​4​.​1​ ​2​0​2​6​0​1​0​8 | NOK |
    +-+-+-+-+-+
    | RTEMS Git Commit | :ref:`18 <ABuildConfigKeyTestsuitesTestSuiteXfailOutput0>` | 8​c​9​a​5​d​0​e​1​e​a​e​4​5​0​d​d​2​8​3​4​4​b​e​9​3​9​0​9​3​6​a​4​5​7​3​7​4​0​d | 5​8​b​f​f​6​2​2​d​6​1​0​8​6​5​c​7​6​d​a​0​4​5​e​8​c​c​6​7​a​a​5​6​c​3​2​b​7​c​8 | NOK |
    +-+-+-+-+-+
    | BSP | :ref:`19 <ABuildConfigKeyTestsuitesTestSuiteXfailOutput0>` | g​r​7​4​0 | g​r​7​1​2​r​c | NOK |
    +-+-+-+-+-+
    | Build Label | :ref:`20 <ABuildConfigKeyTestsuitesTestSuiteXfailOutput0>` | \\​x​2​0​a​c​s​p​a​r​c​/​g​r​7​1​2​r​c​/​u​n​i​/​6​/​q​u​a​l​-​o​n​l​y | b​u​i​l​d​-​l​a​b​e​l | NOK |
    +-+-+-+-+-+
    | Target Hash | :ref:`21 <ABuildConfigKeyTestsuitesTestSuiteXfailOutput0>` | c​p​I​0​9​J​u​6​o​r​F​2​e​o​J​c​m​J​i​4​i​g​e​I​a​r​y​p​s​R​N​w​U​x​T​r​Z​S​s​9​L​M​g​= | c​p​I​0​9​J​u​6​o​r​F​2​e​o​J​c​m​J​i​4​i​g​e​I​a​r​y​p​s​R​N​w​U​x​T​r​Z​S​s​9​L​M​g​=, o​q​N​H​r​l​F​i​_​j​s​i​c​o​5​y​g​H​k​-​O​c​f​e​M​9​o​a​Y​3​J​M​w​_​z​6​d​m​F​0​9​-​U​= | OK |
    +-+-+-+-+-+
    | RTEMS_DEBUG | :ref:`22 <ABuildConfigKeyTestsuitesTestSuiteXfailOutput0>` | 0 | 0 | OK |
    +-+-+-+-+-+
    | RTEMS_MULTIPROCESSING | :ref:`23 <ABuildConfigKeyTestsuitesTestSuiteXfailOutput0>` | 0 | 0 | OK |
    +-+-+-+-+-+
    | RTEMS_POSIX_API | :ref:`24 <ABuildConfigKeyTestsuitesTestSuiteXfailOutput0>` | 0 | 0 | OK |
    +-+-+-+-+-+
    | RTEMS_PROFILING | :ref:`25 <ABuildConfigKeyTestsuitesTestSuiteXfailOutput0>` | 0 | 0 | OK |
    +-+-+-+-+-+
    | RTEMS_SMP | :ref:`26 <ABuildConfigKeyTestsuitesTestSuiteXfailOutput0>` | 0 | 0 | OK |
    +-+-+-+-+-+
    | Step Count | :ref:`30 <ABuildConfigKeyTestsuitesTestSuiteXfailOutput0>` | 1 | > 0 | OK |
    +-+-+-+-+-+
    | Failed Steps Count | :ref:`30 <ABuildConfigKeyTestsuitesTestSuiteXfailOutput0>` | 1 | 0 | NOK |
    +-+-+-+-+-+
    | Duration | :ref:`30 <ABuildConfigKeyTestsuitesTestSuiteXfailOutput0>` | 774.000μs | :math:`\\geq` 0 | OK |
    +-+-+-+-+-+
    | Report Hash | :ref:`31 <ABuildConfigKeyTestsuitesTestSuiteXfailOutput0>` | G​A​g​4​a​Q​Y​K​W​t​5​F​l​r​m​5​r​n​W​C​Z​5​o​8​J​7​5​z​U​v​W​F​g​K​q​A​9​T​u​2​6​9​I​= | G​A​g​4​a​Q​Y​K​W​t​5​F​l​r​m​5​r​n​W​C​Z​5​o​8​J​7​5​z​U​v​W​F​g​K​q​A​9​T​u​2​6​9​I​= | OK |
    +-+-+-+-+-+

.. raw:: latex

    \\end{scriptsize}

.. _ABuildConfigKeyTestsuitesTestSuiteXfailRtemsValTestCaseXfail:

Test case - spec:/​rtems/​val/​test-case-xfail
**********************************************

This test case is specified by
``spec:/​rtems/​val/​test-case-xfail``.

The following table lists an evaluation of
the test case information reported in lines :ref:`27 <ABuildConfigKeyTestsuitesTestSuiteXfailOutput0>` up to and including :ref:`29 <ABuildConfigKeyTestsuitesTestSuiteXfailOutput0>`
of the test output.

.. raw:: latex

    \\begin{scriptsize}

.. table::
    :class: longtable
    :widths: 42,8,20,20,10

    +-+-+-+-+-+
    | Property | Line | Reported | Expected | Status |
    +=+=+=+=+=+
    | Step Count | :ref:`29 <ABuildConfigKeyTestsuitesTestSuiteXfailOutput0>` | 1 | > 0 | OK |
    +-+-+-+-+-+
    | Failed Steps Count | :ref:`29 <ABuildConfigKeyTestsuitesTestSuiteXfailOutput0>` | 1 | 0 | NOK |
    +-+-+-+-+-+
    | Duration | :ref:`29 <ABuildConfigKeyTestsuitesTestSuiteXfailOutput0>` | ? | :math:`\\geq` 0 | NOK |
    +-+-+-+-+-+

.. raw:: latex

    \\end{scriptsize}

.. _ABuildConfigKeyTestsuitesTestSuiteXfailTestOutput:

Test output
***********

The test report was generated from the following test output.

.. raw:: latex

    \\begin{tiny}

.. _ABuildConfigKeyTestsuitesTestSuiteXfailOutput0:

.. code-block:: none
    :linenos:
    :lineno-start: 1

    ​
    ​ ​S​I​S​ ​-​ ​S​P​A​R​C​/​R​I​S​C​V​ ​i​n​s​t​r​u​c​t​i​o​n​ ​s​i​m​u​l​a​t​o​r​ ​2​.​3​0​,​ ​ ​c​o​p​y​r​i​g​h​t​ ​J​i​r​i​ ​G​a​i​s​l​e​r​ ​2​0​2​0
    ​ ​B​u​g​-​r​e​p​o​r​t​s​ ​t​o​ ​j​i​r​i​@​g​a​i​s​l​e​r​.​s​e
    ​
    ​ ​G​R​7​4​0​/​L​E​O​N​4​ ​e​m​u​l​a​t​i​o​n​ ​e​n​a​b​l​e​d​,​ ​1​ ​c​p​u​s​ ​o​n​l​i​n​e​,​ ​d​e​l​t​a​ ​5​0​ ​c​l​o​c​k​s
    ​
    ​ ​L​o​a​d​e​d​ ​/​o​p​t​/​r​t​e​m​s​-​s​p​a​r​c​-​g​r​7​4​0​-​7​/​b​u​i​l​d​/​s​p​a​r​c​-​g​r​7​4​0​-​u​n​i​-​b​s​p​-​q​u​a​l​-​o​n​l​y​/​s​p​a​r​c​/​g​r​7​4​0​-​u​n​i​-​q​u​a​l​-​o​n​l​y​/​t​e​s​t​s​/​t​s​-​x​f​a​i​l​.​e​x​e​,​ ​e​n​t​r​y​ ​0​x​0​0​0​0​0​0​0​0
    ​
    ​
    ​*​*​*​ ​B​E​G​I​N​ ​O​F​ ​T​E​S​T​ ​T​e​s​t​s​u​i​t​e​s​T​e​s​t​S​u​i​t​e​X​f​a​i​l​ ​*​*​*
    ​*​*​*​ ​T​E​S​T​ ​V​E​R​S​I​O​N​:​ ​6​.​0​.​0​.​8​c​9​a​5​d​0​e​1​e​a​e​4​5​0​d​d​2​8​3​4​4​b​e​9​3​9​0​9​3​6​a​4​5​7​3​7​4​0​d
    ​*​*​*​ ​T​E​S​T​ ​S​T​A​T​E​:​ ​E​X​P​E​C​T​E​D​_​P​A​S​S
    ​*​*​*​ ​T​E​S​T​ ​B​U​I​L​D​:
    ​*​*​*​ ​T​E​S​T​ ​T​O​O​L​S​:​ ​6​.​0​.​0​.​8​c​9​a​5​d​0​e​1​e​a​e​4​5​0​d​d​2​8​3​4​4​b​e​9​3​9​0​9​3​6​a​4​5​7​3​7​4​0​d
    ​A​:​T​e​s​t​s​u​i​t​e​s​T​e​s​t​S​u​i​t​e​X​f​a​i​l
    ​S​:​P​l​a​t​f​o​r​m​:​R​T​E​M​S
    ​S​:​C​o​m​p​i​l​e​r​:​6​.​0​.​0​.​8​c​9​a​5​d​0​e​1​e​a​e​4​5​0​d​d​2​8​3​4​4​b​e​9​3​9​0​9​3​6​a​4​5​7​3​7​4​0​d
    ​S​:​V​e​r​s​i​o​n​:​6​.​0​.​0​.​8​c​9​a​5​d​0​e​1​e​a​e​4​5​0​d​d​2​8​3​4​4​b​e​9​3​9​0​9​3​6​a​4​5​7​3​7​4​0​d
    ​S​:​B​S​P​:​g​r​7​4​0
    ​S​:​B​u​i​l​d​L​a​b​e​l​:​s​p​a​r​c​/​g​r​7​1​2​r​c​/​u​n​i​/​6​/​q​u​a​l​-​o​n​l​y
    ​S​:​T​a​r​g​e​t​H​a​s​h​:​S​H​A​2​5​6​:​c​p​I​0​9​J​u​6​o​r​F​2​e​o​J​c​m​J​i​4​i​g​e​I​a​r​y​p​s​R​N​w​U​x​T​r​Z​S​s​9​L​M​g​=
    ​S​:​R​T​E​M​S​_​D​E​B​U​G​:​0
    ​S​:​R​T​E​M​S​_​M​U​L​T​I​P​R​O​C​E​S​S​I​N​G​:​0
    ​S​:​R​T​E​M​S​_​P​O​S​I​X​_​A​P​I​:​0
    ​S​:​R​T​E​M​S​_​P​R​O​F​I​L​I​N​G​:​0
    ​S​:​R​T​E​M​S​_​S​M​P​:​0
    ​B​:​R​t​e​m​s​V​a​l​T​e​s​t​C​a​s​e​X​f​a​i​l
    ​F​:​0​:​0​:​R​U​N​:​t​c​-​x​f​a​i​l​.​c​:​4
    ​E​:​R​t​e​m​s​V​a​l​T​e​s​t​C​a​s​e​X​f​a​i​l​:​N​:​1​:​F​:​1​:​D​:​0​.​0​0​0​2​3​0
    ​Z​:​T​e​s​t​s​u​i​t​e​s​T​e​s​t​S​u​i​t​e​X​f​a​i​l​:​C​:​1​:​N​:​1​:​F​:​1​:​D​:​0​.​0​0​0​7​7​4
    ​Y​:​R​e​p​o​r​t​H​a​s​h​:​S​H​A​2​5​6​:​G​A​g​4​a​Q​Y​K​W​t​5​F​l​r​m​5​r​n​W​C​Z​5​o​8​J​7​5​z​U​v​W​F​g​K​q​A​9​T​u​2​6​9​I​=
    ​c​p​u​ ​0​ ​i​n​ ​e​r​r​o​r​ ​m​o​d​e​ ​(​t​t​ ​=​ ​0​x​8​0​)
    ​ ​ ​ ​3​2​6​1​3​6​ ​ ​0​0​0​0​3​0​6​0​:​ ​ ​9​1​d​0​2​0​0​0​ ​ ​ ​t​a​ ​ ​0​x​0

.. raw:: latex

    \\end{tiny}"""

    assert _get_tr("a-build-config-key-ts-no-spec.exe.rst"
                   ) == """.. _a-build-config-key-ts-no-spec.exe:

Other program - ts-no-spec.exe
##############################

This report was produced by the
:file:`ts-no-spec.exe`
executable.  The executable file had an SHA512 digest of
a​d​8​5​f​f​d​4​4​b​e​a​6​e​9​d​f​5​d​5​5​8​e​3​1​8​d​a​a​6​6​4​a​d​b​a​3​d​5​b​b​5​c​0​8​b​f​0​4​0​b​c​9​3​a​b​d​c​7​0​f​3​3​1​6​6​e​9​6​6​b​5​3​c​5​a​1​1​3​6​0​f​7​e​a​0​a​4​7​4​d​9​6​d​b​b​6​9​0​1​1​9​e​9​f​7​f​7​c​7​5​9​2​d​0​d​a​2​5​3​2​b​3​f​1​5​4​f.

.. raw:: latex

    \\begin{tiny}

.. _a-build-config-key-ts-no-spec.exeOutput0:

.. code-block:: none
    :linenos:
    :lineno-start: 1

    ​
    ​ ​S​I​S​ ​-​ ​S​P​A​R​C​/​R​I​S​C​V​ ​i​n​s​t​r​u​c​t​i​o​n​ ​s​i​m​u​l​a​t​o​r​ ​2​.​3​0​,​ ​ ​c​o​p​y​r​i​g​h​t​ ​J​i​r​i​ ​G​a​i​s​l​e​r​ ​2​0​2​0
    ​ ​B​u​g​-​r​e​p​o​r​t​s​ ​t​o​ ​j​i​r​i​@​g​a​i​s​l​e​r​.​s​e
    ​
    ​ ​G​R​7​4​0​/​L​E​O​N​4​ ​e​m​u​l​a​t​i​o​n​ ​e​n​a​b​l​e​d​,​ ​1​ ​c​p​u​s​ ​o​n​l​i​n​e​,​ ​d​e​l​t​a​ ​5​0​ ​c​l​o​c​k​s
    ​
    ​ ​L​o​a​d​e​d​ ​/​o​p​t​/​r​t​e​m​s​-​s​p​a​r​c​-​g​r​7​4​0​-​7​/​b​u​i​l​d​/​s​p​a​r​c​-​g​r​7​4​0​-​u​n​i​-​b​s​p​-​q​u​a​l​-​o​n​l​y​/​s​p​a​r​c​/​g​r​7​4​0​-​u​n​i​-​q​u​a​l​-​o​n​l​y​/​t​e​s​t​s​/​t​s​-​n​o​-​s​p​e​c​.​e​x​e​,​ ​e​n​t​r​y​ ​0​x​0​0​0​0​0​0​0​0
    ​
    ​
    ​*​*​*​ ​B​E​G​I​N​ ​O​F​ ​T​E​S​T​ ​T​e​s​t​s​u​i​t​e​s​T​e​s​t​S​u​i​t​e​N​o​S​p​e​c​ ​*​*​*
    ​*​*​*​ ​T​E​S​T​ ​V​E​R​S​I​O​N​:​ ​6​.​0​.​0​.​4​2​6​0​8​4​8​f​3​a​1​6​b​1​5​a​8​e​8​0​7​d​6​d​4​5​f​2​6​8​b​1​0​3​a​e​e​7​9​c
    ​*​*​*​ ​T​E​S​T​ ​S​T​A​T​E​:​ ​E​X​P​E​C​T​E​D​_​P​A​S​S
    ​*​*​*​ ​T​E​S​T​ ​B​U​I​L​D​:
    ​*​*​*​ ​T​E​S​T​ ​T​O​O​L​S​:​ ​6​.​0​.​0​.​8​c​9​a​5​d​0​e​1​e​a​e​4​5​0​d​d​2​8​3​4​4​b​e​9​3​9​0​9​3​6​a​4​5​7​3​7​4​0​d
    ​A​:​T​e​s​t​s​u​i​t​e​s​T​e​s​t​S​u​i​t​e​N​o​S​p​e​c
    ​S​:​P​l​a​t​f​o​r​m​:​R​T​E​M​S
    ​S​:​C​o​m​p​i​l​e​r​:​6​.​0​.​0​.​8​c​9​a​5​d​0​e​1​e​a​e​4​5​0​d​d​2​8​3​4​4​b​e​9​3​9​0​9​3​6​a​4​5​7​3​7​4​0​d
    ​S​:​V​e​r​s​i​o​n​:​6​.​0​.​0​.​4​2​6​0​8​4​8​f​3​a​1​6​b​1​5​a​8​e​8​0​7​d​6​d​4​5​f​2​6​8​b​1​0​3​a​e​e​7​9​c
    ​S​:​B​S​P​:​g​r​7​4​0
    ​S​:​B​u​i​l​d​L​a​b​e​l​:​s​p​a​r​c​/​g​r​7​1​2​r​c​/​u​n​i​/​6​/​q​u​a​l​-​o​n​l​y
    ​S​:​T​a​r​g​e​t​H​a​s​h​:​S​H​A​2​5​6​:​_​x​Q​e​T​N​J​w​S​l​a​2​b​V​b​h​W​P​V​c​I​0​e​m​L​k​2​b​E​_​G​V​Q​f​v​z​t​9​C​N​8​4​k​=
    ​S​:​R​T​E​M​S​_​D​E​B​U​G​:​0
    ​S​:​R​T​E​M​S​_​M​U​L​T​I​P​R​O​C​E​S​S​I​N​G​:​0
    ​S​:​R​T​E​M​S​_​P​O​S​I​X​_​A​P​I​:​0
    ​S​:​R​T​E​M​S​_​P​R​O​F​I​L​I​N​G​:​0
    ​S​:​R​T​E​M​S​_​S​M​P​:​0
    ​B​:​R​t​e​m​s​V​a​l​T​e​s​t​C​a​s​e​N​o​S​p​e​c
    ​E​:​R​t​e​m​s​V​a​l​T​e​s​t​C​a​s​e​N​o​S​p​e​c​:​N​:​1​:​F​:​0​:​D​:​0​.​0​0​0​0​0​9
    ​Z​:​T​e​s​t​s​u​i​t​e​s​T​e​s​t​S​u​i​t​e​N​o​S​p​e​c​:​C​:​1​:​N​:​1​:​F​:​0​:​D​:​0​.​0​0​0​3​7​3
    ​Y​:​R​e​p​o​r​t​H​a​s​h​:​S​H​A​2​5​6​:​_​I​f​g​Z​w​d​l​G​z​B​B​g​f​Z​_​D​V​0​g​B​2​0​s​N​I​j​L​4​_​A​U​w​E​D​J​L​Q​F​p​7​L​4​=
    ​
    ​*​*​*​ ​E​N​D​ ​O​F​ ​T​E​S​T​ ​T​e​s​t​s​u​i​t​e​s​T​e​s​t​S​u​i​t​e​N​o​S​p​e​c​ ​*​*​*
    ​
    ​c​p​u​ ​0​ ​i​n​ ​e​r​r​o​r​ ​m​o​d​e​ ​(​t​t​ ​=​ ​0​x​8​0​)
    ​ ​ ​ ​1​7​4​7​8​3​ ​ ​0​0​0​0​2​5​0​0​:​ ​ ​9​1​d​0​2​0​0​0​ ​ ​ ​t​a​ ​ ​0​x​0

.. raw:: latex

    \\end{tiny}"""

    assert _get_tr("coverage.rst") == """.. _CoverageTargetNameTargetA:

Target - Name Target A
######################

.. _CoverageTargetNameTargetAOverview:

Overview
********

.. raw:: latex

    \\begin{scriptsize}

.. table::
    :class: longtable
    :widths: 34,13,7,13,7,13,7

    +-+-+-+-+-+-+-+
    | Scope | Functions | Status | Lines | Status | Branches | Status |
    +=+=+=+=+=+=+=+
    | Scope | 0/0 (N/A) [13+2/16] | **NOK** | 5+1/6 (100%) [114+3/119] | OK | 2/2 (100%) [12+4/18] | OK |
    +-+-+-+-+-+-+-+
    | Empty | N/A | **NOK** | N/A | **NOK** | N/A | **NOK** |
    +-+-+-+-+-+-+-+
    | Good | 1/1 (100%) | OK | 18/18 (100%) | OK | 4/4 (100%) | OK |
    +-+-+-+-+-+-+-+
    | Overall | 0/1 (0.0%) [1/1] | **NOK** | 3/18 (16.6%) [0/2] | **NOK** | 2/4 (50.0%) | **NOK** |
    +-+-+-+-+-+-+-+

.. raw:: latex

    \\end{scriptsize}

.. _CoverageTargetNameTargetAScopeScope:

Scope - Scope
*************

The following table lists files with unjustified coverage issues.

.. raw:: latex

    \\begin{scriptsize}

.. table::
    :class: longtable
    :widths: 34,13,7,13,7,13,7

    +-+-+-+-+-+-+-+
    | File | Functions | Status | Lines | Status | Branches | Status |
    +=+=+=+=+=+=+=+
    | `cpukit​/score​/src​/threadqenqueue.c </pkg/coverage-html/index.threadqenqueue.c.49433ec925b45a09aa7c6c6f0199f026.html>`__ | 13+1/15 (93.3%) | **NOK** | 113+2/117 (98.2%) | **NOK** | 12+2/16 (87.5%) | OK |
    +-+-+-+-+-+-+-+

.. raw:: latex

    \\end{scriptsize}

The following table lists files with justified coverage issues.

.. raw:: latex

    \\begin{scriptsize}

.. table::
    :class: longtable
    :widths: 34,13,7,13,7,13,7

    +-+-+-+-+-+-+-+
    | File | Functions | Status | Lines | Status | Branches | Status |
    +=+=+=+=+=+=+=+
    | `cpukit​/score​/src​/threadyield.c </pkg/coverage-html/index.threadyield.c.7501fda823bc0449fd657f98b6f927be.html>`__ | N/A | OK | 5+1/6 (100%) | OK | 2/2 (100%) | OK |
    +-+-+-+-+-+-+-+

.. raw:: latex

    \\end{scriptsize}

The following table lists files with coverage issues justified by an excluded test.

.. raw:: latex

    \\begin{scriptsize}

.. table::
    :class: longtable
    :widths: 34,13,7,13,7,13,7

    +-+-+-+-+-+-+-+
    | File | Functions | Status | Lines | Status | Branches | Status |
    +=+=+=+=+=+=+=+
    | `cpukit​/score​/src​/notrun.c </pkg/coverage-html/index.notrun.c.b3a74aeb7ec205001b1ac1ee5ac6e8ac.html>`__ | 0+1/1 (100%) | OK | 1+1/2 (100%) | OK | 0+2/2 (100%) | OK |
    +-+-+-+-+-+-+-+

.. raw:: latex

    \\end{scriptsize}

There are no files without coverage issues.

.. _CoverageTargetNameTargetAScopeEmpty:

Scope - Empty
*************

There is no coverage information available.

.. _CoverageTargetNameTargetAScopeGood:

Scope - Good
************

There are no files with unjustified coverage issues.

There are no files with justified coverage issues.

There are no files with coverage issues justified by an excluded test.

The following table lists files having the expected coverage.

.. raw:: latex

    \\begin{scriptsize}

.. table::
    :class: longtable
    :widths: 34,13,7,13,7,13,7

    +-+-+-+-+-+-+-+
    | File | Functions | Status | Lines | Status | Branches | Status |
    +=+=+=+=+=+=+=+
    | `cpukit​/score​/src​/chain.c </pkg/coverage-good-html/index.chain.c.fb6aee9b3f6ae0998256d52130e2c678.html>`__ | 1/1 (100%) | OK | 15/15 (100%) | OK | 2/2 (100%) | OK |
    +-+-+-+-+-+-+-+
    | `cpukit​/libc​/string​/flsl.c </pkg/coverage-good-html/index.flsl.c.187042b9c864845145c986de5bb93dd5.html>`__ | N/A | OK | 3/3 (100%) | OK | 2/2 (100%) | OK |
    +-+-+-+-+-+-+-+

.. raw:: latex

    \\end{scriptsize}

.. _CoverageTargetNameTargetAScopeOverall:

Scope - Overall
***************

The following table lists files with unjustified coverage issues.

.. raw:: latex

    \\begin{scriptsize}

.. table::
    :class: longtable
    :widths: 34,13,7,13,7,13,7

    +-+-+-+-+-+-+-+
    | File | Functions | Status | Lines | Status | Branches | Status |
    +=+=+=+=+=+=+=+
    | `bsps​/include​/bsp​/fatal.h </pkg/coverage-overall-html/index.fatal.h.7f3bb1e879e3580b41139d705e6b007f.html>`__ | 1/1 (100%) | OK | 0/2 (0.0%) | **NOK** | N/A | OK |
    +-+-+-+-+-+-+-+
    | `cpukit​/score​/src​/chain.c </pkg/coverage-overall-html/index.chain.c.fb6aee9b3f6ae0998256d52130e2c678.html>`__ | 0/1 (0.0%) | **NOK** | 0/15 (0.0%) | **NOK** | 0/2 (0.0%) | **NOK** |
    +-+-+-+-+-+-+-+

.. raw:: latex

    \\end{scriptsize}

There are no files with justified coverage issues.

There are no files with coverage issues justified by an excluded test.

The following table lists files having the expected coverage.

.. raw:: latex

    \\begin{scriptsize}

.. table::
    :class: longtable
    :widths: 34,13,7,13,7,13,7

    +-+-+-+-+-+-+-+
    | File | Functions | Status | Lines | Status | Branches | Status |
    +=+=+=+=+=+=+=+
    | `cpukit​/libc​/string​/flsl.c </pkg/coverage-overall-html/index.flsl.c.187042b9c864845145c986de5bb93dd5.html>`__ | N/A | OK | 3/3 (100%) | OK | 2/2 (100%) | OK |
    +-+-+-+-+-+-+-+

.. raw:: latex

    \\end{scriptsize}

.. _CoverageTargetNameTargetAExcludedTestsScope:

Excluded tests - Scope
**********************

The following table lists the excluded tests of
this target.  The counts state how many coverage gaps the reason of the row
justifies.  A row without a reason justifies no gap.

.. raw:: latex

    \\begin{scriptsize}

.. table::
    :class: longtable
    :widths: 24,8,8,8,52

    +-+-+-+-+-+
    | Tests | Functions | Lines | Branches | Reason |
    +=+=+=+=+=+
    | excluded​-ethernet.exe | 1 | 1 | 2 | The target has no Ethernet device. |
    +-+-+-+-+-+
    | excluded​-ethernet.exe | 0 | 0 | 0 | **This item states no reason.** Another item states one. |
    +-+-+-+-+-+
    | excluded​-second​-board.exe | 0 | 0 | 0 | The test needs a second board. **No other target ran excluded​-second​-board.exe.** |
    +-+-+-+-+-+
    | excluded​-silent.exe | 0 | 0 | 0 | **No item states a reason.** |
    +-+-+-+-+-+

.. raw:: latex

    \\end{scriptsize}

The coverage of these tests comes from the
following targets: spec:​/rtems​/target​-b.

.. _CoverageTargetNameTargetAExcludedTestsEmpty:

Excluded tests - Empty
**********************

No test is excluded from this target.

.. _CoverageTargetNameTargetAExcludedTestsGood:

Excluded tests - Good
*********************

No test is excluded from this target.

.. _CoverageTargetNameTargetAExcludedTestsOverall:

Excluded tests - Overall
************************

No test is excluded from this target.

.. _CoverageCoverageAcrossTheTargets:

Coverage across the targets
###########################

.. raw:: latex

    \\begin{scriptsize}

.. table::
    :class: longtable
    :widths: 40,20,20,20

    +-+-+-+-+
    | Target | Excluded tests | Unjustified issues | Complete evidence |
    +=+=+=+=+
    | `Name Target A <reports.html#a>`__ | 3 | 3 | no |
    +-+-+-+-+

.. raw:: latex

    \\end{scriptsize}

**No target meets its coverage limits with the
tests it runs.**  The coverage evidence of this variant is incomplete."""

    def _get_tr2(name):
        return _get_content("/pkg/build/doc-djf-tr-2", name)

    assert _get_tr2("index.rst") == """.. SPDX-License-Identifier: CC-BY-SA-4.0

.. Copyright (C) 2025 embedded brains GmbH & Co. KG

.. reports begin
.. _B:

Target - Name Target B
######################

.. _BBuildConfigKey:

Configuration - build-config-key
********************************

.. toctree::

    b-build-config-key-testsuites-test-suite-pass

.. _CoverageData:

Coverage data
#############

.. toctree::

    coverage

.. _ListOfExpectedTestFailures:

List of expected test failures
##############################

There were no expected test errors found in the test outputs.

.. _ListOfUnexpectedTestFailures:

List of unexpected test failures
################################

.. _ListOfUnexpectedTestFailuresTargetNameTargetB:

Target - Name Target B
**********************

.. _ListOfUnexpectedTestFailuresTargetNameTargetBSpecRtemsReqAction:

spec:/​rtems/​req/​action
=========================

There are no test results available for this target.

.. _ListOfUnexpectedTestFailuresTargetNameTargetBSpecRtemsReqAction2:

spec:/​rtems/​req/​action-2
===========================

There are no test results available for this target.

.. _ListOfUnexpectedTestFailuresTargetNameTargetBSpecRtemsReqPerf:

spec:/​rtems/​req/​perf
=======================

There are no test results available for this target.

.. _ListOfUnexpectedTestFailuresTargetNameTargetBSpecRtemsReqPerfNoResults:

spec:/​rtems/​req/​perf-no-results
==================================

There are no test results available for this target.

.. _ListOfUnexpectedTestFailuresTargetNameTargetBSpecRtemsValTestCase:

spec:/​rtems/​val/​test-case
============================

There are no test results available for this target.

.. _ListOfUnexpectedTestFailuresTargetNameTargetBSpecRtemsValTestCaseFail:

spec:/​rtems/​val/​test-case-fail
=================================

There are no test results available for this target.

.. _ListOfUnexpectedTestFailuresTargetNameTargetBSpecRtemsValTestCaseRun:

spec:/​rtems/​val/​test-case-run
================================

There are no test results available for this target.

.. _ListOfUnexpectedTestFailuresTargetNameTargetBSpecRtemsValTestCaseUnit:

spec:/​rtems/​val/​test-case-unit
=================================

There are no test results available for this target.

.. _ListOfUnexpectedTestFailuresTargetNameTargetBSpecRtemsValTestCaseXfail:

spec:/​rtems/​val/​test-case-xfail
==================================

There are no test results available for this target.

.. _ListOfUnexpectedTestFailuresTargetNameTargetBSpecScoreCpuValPerf:

spec:/​score/​cpu/​val/​perf
============================

There are no test results available for this target.

.. _ListOfUnexpectedTestFailuresTargetNameTargetBSpecTestsuitesTestSuitePass:

spec:/​testsuites/​test-suite-pass
==================================

- :ref:`Configuration - build-config-key
  <BBuildConfigKeyTestsuitesTestSuitePass>`:

  - The BSP has not the expected name.

  - The RTEMS Git commit has not the expected value.

  - The build label has not the expected value.

  - The target hash has not the expected value.

  - The tools version has not the expected value.
.. reports end"""

    # Target B runs every test and meets its coverage limits, so it
    # carries the coverage evidence of the variant
    assert _get_tr2("coverage.rst") == """.. _CoverageTargetNameTargetB:

Target - Name Target B
######################

.. _CoverageTargetNameTargetBOverview:

Overview
********

.. raw:: latex

    \\begin{scriptsize}

.. table::
    :class: longtable
    :widths: 34,13,7,13,7,13,7

    +-+-+-+-+-+-+-+
    | Scope | Functions | Status | Lines | Status | Branches | Status |
    +=+=+=+=+=+=+=+
    | Scope | 1/1 (100%) | OK | 18/18 (100%) | OK | 4/4 (100%) | OK |
    +-+-+-+-+-+-+-+

.. raw:: latex

    \\end{scriptsize}

.. _CoverageTargetNameTargetBScopeScope:

Scope - Scope
*************

There are no files with unjustified coverage issues.

There are no files with justified coverage issues.

There are no files with coverage issues justified by an excluded test.

The following table lists files having the expected coverage.

.. raw:: latex

    \\begin{scriptsize}

.. table::
    :class: longtable
    :widths: 34,13,7,13,7,13,7

    +-+-+-+-+-+-+-+
    | File | Functions | Status | Lines | Status | Branches | Status |
    +=+=+=+=+=+=+=+
    | `cpukit​/score​/src​/chain.c </pkg/coverage-b-html/index.chain.c.fb6aee9b3f6ae0998256d52130e2c678.html>`__ | 1/1 (100%) | OK | 15/15 (100%) | OK | 2/2 (100%) | OK |
    +-+-+-+-+-+-+-+
    | `cpukit​/libc​/string​/flsl.c </pkg/coverage-b-html/index.flsl.c.187042b9c864845145c986de5bb93dd5.html>`__ | N/A | OK | 3/3 (100%) | OK | 2/2 (100%) | OK |
    +-+-+-+-+-+-+-+

.. raw:: latex

    \\end{scriptsize}

.. _CoverageTargetNameTargetBExcludedTestsScope:

Excluded tests - Scope
**********************

No test is excluded from this target.

.. _CoverageCoverageAcrossTheTargets:

Coverage across the targets
###########################

.. raw:: latex

    \\begin{scriptsize}

.. table::
    :class: longtable
    :widths: 40,20,20,20

    +-+-+-+-+
    | Target | Excluded tests | Unjustified issues | Complete evidence |
    +=+=+=+=+
    | `Name Target B <reports.html#b>`__ | 0 | 0 | yes |
    +-+-+-+-+

.. raw:: latex

    \\end{scriptsize}

The coverage evidence of this variant rests on
the following targets: Name Target B.  Each of them meets its coverage limits with
the tests it runs."""

    def _get_tr3(name):
        return _get_content("/pkg/build/doc-djf-tr-3", name)

    # The third aggregator gathers a test log and no coverage at all, so the
    # report states this and produces no coverage page
    assert "There is no coverage data available." in _get_tr3("index.rst")
    assert _get_tr3("coverage.rst") == ""
