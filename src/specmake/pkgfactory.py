# SPDX-License-Identifier: BSD-2-Clause
""" Provides the default build item factory. """

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

from .archiver import Archiver, IndexGroup, Indexer
from .ctrfcollector import CTRFCollector
from .directorystate import DirectoryState, RepositoryState
from .docbuilder import DocumentBuilder
from .doxyfile import Doxyfile
from .gcdaproducer import GCDAProducer
from .icdbuilder import ICDBuilder
from .itemcachestate import ItemCacheDirectoryState
from .linkhub import LinkHub
from .membenchcollector import MembenchCollector
from .notruncoverage import NotRunCoverage
from .pkgitems import (BuildItemFactory, GenericPackageComponent, Redirection)
from .packagechanges import PackageChanges
from .packagemanual import PackageManualBuilder, PackageSummary
from .perfimages import BuildPerformanceImages
from .reposubset import RepositorySubset
from .rtems import RTEMSItemCache, RTEMSPackageComponent
from .rtemstestsimages import BuildRTEMSTestsImages
from .runactions import RunActions
from .runexecutablecmd import RunExecutableCommand
from .sddlinker import SDDLinker
from .spamrmanager import SpamrManager
from .speccompare import CompareSpecsRegistry
from .sreldbuilder import SRelDBuilder
from .srsbuilder import SRSBuilder
from .stdtailoring import ECSSClause
from .svrbuilder import SVRBuilder
from .testaggregator import TestAggregator
from .testplanbuilder import TestPlanBuilder
from .testreporter import TestReporter
from .testrunner import (TestRunner, GRMONManualTestRunner,
                         SubprocessTestRunner, TestLog)
from .testrunneresa import ESATestRunner
from .testrunnergrpc import GRPCTestRunner


def create_build_item_factory() -> BuildItemFactory:
    """ Create the default build item factory. """
    factory = BuildItemFactory()
    factory.add_constructor("pkg/component/generic", GenericPackageComponent)
    factory.add_constructor("pkg/component/rtems", RTEMSPackageComponent)
    factory.add_constructor("pkg/directory-state/archive", Archiver)
    factory.add_constructor("pkg/directory-state/ctrf", CTRFCollector)
    factory.add_constructor("pkg/directory-state/doxyfile", Doxyfile)
    factory.add_constructor("pkg/directory-state/explicit", DirectoryState)
    factory.add_constructor("pkg/directory-state/gcda-producer", GCDAProducer)
    factory.add_constructor("pkg/directory-state/index", Indexer)
    factory.add_constructor("pkg/directory-state/not-run-coverage",
                            NotRunCoverage)
    factory.add_constructor("pkg/directory-state/item-cache",
                            ItemCacheDirectoryState)
    factory.add_constructor("pkg/directory-state/membench-collector",
                            MembenchCollector)
    factory.add_constructor("pkg/directory-state/package-summary",
                            PackageSummary)
    factory.add_constructor("pkg/directory-state/patterns", DirectoryState)
    factory.add_constructor("pkg/directory-state/performance-images",
                            BuildPerformanceImages)
    factory.add_constructor("pkg/directory-state/repository", RepositoryState)
    factory.add_constructor("pkg/directory-state/repository-subset",
                            RepositorySubset)
    factory.add_constructor("pkg/directory-state/rtems-tests-images",
                            BuildRTEMSTestsImages)
    factory.add_constructor("pkg/directory-state/run-executable-command",
                            RunExecutableCommand)
    factory.add_constructor("pkg/directory-state/sdd-linker", SDDLinker)
    factory.add_constructor("pkg/directory-state/sphinx/ddf-sreld",
                            SRelDBuilder)
    factory.add_constructor("pkg/directory-state/sphinx/djf-svr", SVRBuilder)
    factory.add_constructor("pkg/directory-state/sphinx/generic",
                            DocumentBuilder)
    factory.add_constructor("pkg/directory-state/sphinx/package-manual",
                            PackageManualBuilder)
    factory.add_constructor("pkg/directory-state/sphinx/paf-spamr",
                            SpamrManager)
    factory.add_constructor("pkg/directory-state/sphinx/test-plan",
                            TestPlanBuilder)
    factory.add_constructor("pkg/directory-state/sphinx/test-report",
                            TestReporter)
    factory.add_constructor("pkg/directory-state/sphinx/ts-icd", ICDBuilder)
    factory.add_constructor("pkg/directory-state/sphinx/ts-srs", SRSBuilder)
    factory.add_constructor("pkg/directory-state/test-coverage",
                            DirectoryState)
    factory.add_constructor("pkg/directory-state/test-log", TestLog)
    factory.add_constructor("pkg/directory-state/unpacked-archive",
                            DirectoryState)
    factory.add_constructor("pkg/index-group", IndexGroup)
    factory.add_constructor("pkg/link-hub", LinkHub)
    factory.add_constructor("pkg/package-changes", PackageChanges)
    factory.add_constructor("pkg/redirection", Redirection)
    factory.add_constructor("pkg/rtems-item-cache", RTEMSItemCache)
    factory.add_constructor("pkg/run-actions", RunActions)
    factory.add_constructor("pkg/spec-compare-registry", CompareSpecsRegistry)
    factory.add_constructor("pkg/test-aggregator", TestAggregator)
    factory.add_constructor("pkg/test-runner/esa", ESATestRunner)
    factory.add_constructor("pkg/test-runner/dummy", TestRunner)
    factory.add_constructor("pkg/test-runner/grmon-manual",
                            GRMONManualTestRunner)
    factory.add_constructor("pkg/test-runner/grpc", GRPCTestRunner)
    factory.add_constructor("pkg/test-runner/subprocess", SubprocessTestRunner)
    factory.add_constructor("requirement/non-functional/ecss", ECSSClause)
    return factory
