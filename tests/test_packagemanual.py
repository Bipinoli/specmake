# SPDX-License-Identifier: BSD-2-Clause
""" Tests for the packagemanual module. """

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

import logging
import os
from pathlib import Path
import pickle
import subprocess

import specitems
from specitems import ItemGetValueContext

import specmake
from specmake import PackageComponent, TestReporter

from .util import create_package

TestReporter.__test__ = False


class _DummyTestReporter(TestReporter):

    def run(self) -> None:
        pass


def _set_enabled_set(component: PackageComponent,
                     enabled_set: list[str]) -> None:
    logging.critical("%s: set enabled set: %s", component.uid, enabled_set)
    if "subcomponent-target-b" in component.selection.enabled_set:
        enabled_set = enabled_set + ["subcomponent-target-b"]
    component["enabled-set"] = enabled_set
    component.selection.reset(enabled_set)
    for link in component.item.links_to_children("input"):
        child = component.director[link.item.uid]
        if isinstance(child, PackageComponent):
            _set_enabled_set(child, enabled_set)


def _run_command(args, cwd=None, stdout=None):
    logging.info("run command: %s", " ".join(args))
    if args == ["python3", "-msphinx", "-M", "clean", "source", "build"]:
        return 0
    if args == ["python3", "-msphinx", "-M", "latexpdf", "source", "build"]:
        os.makedirs(os.path.join(cwd, "build/latex"))
        open(os.path.join(cwd, "build/latex/document.pdf"), "w+").close()
        return 0
    if args == ["python3", "-msphinx", "-M", "html", "source", "build"]:
        os.makedirs(os.path.join(cwd, "build/html"))
        open(os.path.join(cwd, "build/html/index.html"), "w+").close()
        return 0
    if "pkg-config" in args:
        stdout.append(" ".join(args))
        return 0
    if "git" in args:
        stdout.append(" ".join(args))
        return 0
    return 1


def _repository_state_lazy_verify(self):
    return True


def _package_manual_generate(content, sections_by_uid, root, table_pivots,
                             mapper):
    content.add([root.uid] + table_pivots + list(sections_by_uid.keys()))


def _subprocess_run(args, stdin, stdout, stderr, shell, cwd, check, encoding):
    cp = subprocess.CompletedProcess(args, 0)
    if isinstance(args, list):
        args = " ".join(args)
    if args.startswith("no-output"):
        cp.stdout = None
    elif args.startswith("error"):
        raise subprocess.CalledProcessError()
    elif encoding is None:
        cp.stdout = b"no encoding"
    else:
        cp.stdout = str(args.encode(encoding))
    if not isinstance(stderr, int):
        stderr.write("\nstderr\n".encode("latin-1"))
    if not isinstance(stdout, int):
        stdout.write("\nstdout\n".encode("latin-1"))
    if not isinstance(stdin, int):
        assert isinstance(cp.stdout, bytes)
        cp.stdout += stdin.read()
    return cp


def _clear_copyrights_by_license(ctx: ItemGetValueContext) -> str:
    ctx.item.cache["/pkg/source/a"]["copyrights-by-license"] = {}
    return "clear copyrights by license"


def _format_path(tmp_dir: Path, path: str) -> str:
    path_2 = str(tmp_dir / path)
    for char in "/-_.":
        path_2 = path_2.replace(char, f"{char}\u200b")
    return f":file:`{path_2}`"


def _add_invisible(line: str) -> str:
    return "\u200b".join(char for char in line)


def test_packagemanual(caplog, tmpdir, monkeypatch):
    monkeypatch.setattr(specmake.directorystate.RepositoryState, "lazy_verify",
                        _repository_state_lazy_verify)
    monkeypatch.setattr(specmake.packagemanual, "run_command", _run_command)
    monkeypatch.setattr(specmake.packagemanual, "generate",
                        _package_manual_generate)
    monkeypatch.setattr(specitems.getvaluesubprocess.subprocess, "run",
                        _subprocess_run)
    tmp_dir = Path(tmpdir)
    tmp_dir_len = len(str(tmp_dir))
    package = create_package(caplog, tmp_dir, Path("spec-packagebuild"),
                             ["aggregate-test-results", "archive"])
    director = package.director
    director.factory.add_constructor("pkg/directory-state/sphinx/test-report",
                                     _DummyTestReporter)
    director.build_package()

    _set_enabled_set(package,
                     ["aggregate-test-results", "package-manual", "archive-2"])
    director["/pkg/source/test-files"].build()
    dir_state_a = director["/pkg/source/a"]
    dir_state_a.build()
    source_archive = director["/pkg/source/archive"]
    source_archive.item["links"][0]["hash"] = package.digest()
    source_archive.item["links"][1]["hash"] = dir_state_a.digest()
    director["/pkg/deployment/verify-package"].load()
    director["/pkg/source/archive"].load()
    director["/pkg/source/doc-package-manual"].load()
    director["/pkg/test-logs/membench-2"].load()
    pm = director["/pkg/deployment/doc-package-manual"]
    pm.mapper.add_get_value(f"{pm.item.type}:/clear-copyrights-by-license",
                            _clear_copyrights_by_license)
    director.build_package()
    pm_build = Path(director["/pkg/build/doc-package-manual"].directory)
    pm_index = pm_build / "source" / "index.rst"
    hidden = "b'a hidden b c \\\\%()\\x00\\x07\\x08,\\x0c\\n\\r \\t\\x0b'"
    with open(pm_index, "r", encoding="utf-8") as src:
        assert src.read() == f""".. SPDX-License-Identifier: CC-BY-SA-4.0

.. Copyright (C) 2023, 2026 embedded brains GmbH & Co. KG

.. subprocess hide-cwd
.. raw:: latex

    \\begin{{tiny}}

.. code-block:: none
    :linenos:
    :lineno-start: 1

    ​{_add_invisible('$ hide-cwd 1 2')}
    ​{_add_invisible('no encoding')}

.. raw:: latex

    \\end{{tiny}}
.. subprocess hide-output
.. raw:: latex

    \\begin{{tiny}}

.. code-block:: none
    :linenos:
    :lineno-start: 1

    ​{_add_invisible('pkg/build $ hide-output 3 4')}

.. raw:: latex

    \\end{{tiny}}
.. subprocess hide

.. subprocess stderr
.. raw:: latex

    \\begin{{tiny}}

.. code-block:: none
    :linenos:
    :lineno-start: 1

    ​{_add_invisible(str(tmp_dir))}​{_add_invisible('/pkg/build $ stderr')}
    ​{_add_invisible('no encoding')}

.. raw:: latex

    \\end{{tiny}}
.. subprocess stdout
.. raw:: latex

    \\begin{{tiny}}

.. code-block:: none
    :linenos:
    :lineno-start: 1

    ​{_add_invisible(str(tmp_dir))}​{_add_invisible('/pkg/build $ stdout')}
    ​{_add_invisible('no encoding')}

.. raw:: latex

    \\end{{tiny}}
.. subprocess stdin stderr
.. raw:: latex

    \\begin{{tiny}}

.. code-block:: none
    :linenos:
    :lineno-start: 1

    ​{_add_invisible(str(tmp_dir))}​{_add_invisible('/pkg/build $ stdin stderr')}
    ​{_add_invisible('no encoding')}
    ​{_add_invisible('stderr')}

.. raw:: latex

    \\end{{tiny}}
.. subprocess stdin stdout
.. raw:: latex

    \\begin{{tiny}}

.. code-block:: none
    :linenos:
    :lineno-start: 1

    ​{_add_invisible(str(tmp_dir))}​{_add_invisible('/pkg/build $ stdin stdout')}
    ​{_add_invisible('no encoding')}
    ​{_add_invisible('stdout')}

.. raw:: latex

    \\end{{tiny}}
.. subprocess no-output
    .. raw:: latex

        \\begin{{tiny}}

    .. code-block:: none
        :linenos:
        :lineno-start: 1

        ​{_add_invisible(str(tmp_dir))}​{_add_invisible('/pkg/doc-package-manual $ no-output')}

    .. raw:: latex

        \\end{{tiny}}
.. subprocess hidden_args
.. raw:: latex

    \\begin{{tiny}}

.. code-block:: none
    :linenos:
    :lineno-start: 1

    ​{_add_invisible(hidden)}

.. raw:: latex

    \\end{{tiny}}
.. archive basename
archive.tar.xz
.. archive sha512
f​c​a​7​b​5​8​f​f​4​4​0​3​7​1​5​6​6​5​5​f​6​d​6​b​c​b​e​7​2​f​8​7​9​7​d​7​c​8​e​1​6​a​f​e​5​5​2​c​8​2​3​e​c​3​c​e​0​7​2​f​1​0​e​a​4​9​b​e​7​4​3​8​f​6​9​f​1​c​9​f​f​1​a​3​1​f​f​5​6​e​5​a​4​7​1​b​2​9​b​0​4​4​c​c​3​3​9​a​9​b​0​3​5​0​7​e​1​1​f​c​b​2​3​c​f​6​f
.. pkg-config
.. code-block:: none

    $ pkg-config --variable=ABI_FLAGS {tmp_dir}/pkg/lib/pkgconfig/sparc-rtems6-gr712rc-smp-qual-only.pc
    pkg-config --variable=ABI_FLAGS {tmp_dir}/pkg/lib/pkgconfig/sparc-rtems6-gr712rc-smp-qual-only.pc

    $ pkg-config --cflags {tmp_dir}/pkg/lib/pkgconfig/sparc-rtems6-gr712rc-smp-qual-only.pc
    pkg-config --cflags {tmp_dir}/pkg/lib/pkgconfig/sparc-rtems6-gr712rc-smp-qual-only.pc

    $ pkg-config --variable=LDFLAGS {tmp_dir}/pkg/lib/pkgconfig/sparc-rtems6-gr712rc-smp-qual-only.pc
    pkg-config --variable=LDFLAGS {tmp_dir}/pkg/lib/pkgconfig/sparc-rtems6-gr712rc-smp-qual-only.pc
.. verify-package basename
verify_package.py
.. verify-package help
.. raw:: latex

    \\begin{{tiny}}

.. code-block:: none
    :linenos:
    :lineno-start: 1

    ​{_add_invisible(str(tmp_dir))}​{_add_invisible(' $ ./verify_package.py --help')}
    ​{_add_invisible('no encoding')}

.. raw:: latex

    \\end{{tiny}}
.. object-size
4
.. benchmark-variants-list
Name 1
    Description 1

Name 2
    Description 2

Name 3
    Description 3
.. memory-benchmarks
/rtems/req/mem-basic
/rtems/req/mem-smp-1
/rtems/val/mem-basic
.. memory-benchmark-reference
:ref:`spec:/​rtems/​val/​mem-basic <SparcGr712rcSmp4BenchmarkSpecRtemsValMemBasic>`
.. memory-benchmark-based-on-reference
:ref:`spec:/​rtems/​val/​mem-basic <SparcGr712rcSmp4BenchmarksBasedOnSpecRtemsValMemBasic>`
.. memory-benchmark-section
123
.. memory-benchmark-compare-section
+0
.. memory-benchmark-variants-table
.. raw:: latex

    \\begin{{scriptsize}}

.. table::
    :class: longtable
    :widths: 35,20,9,9,9,9,9

    +-------------------------------------------------------------+---------+-------+---------+-------+------+---------+
    | Specification                                               | Variant | .text | .rodata | .data | .bss | .noinit |
    +=============================================================+=========+=======+=========+=======+======+=========+
    | :ref:`/rtems/val/mem-basic <BenchmarkSpecRtemsValMemBasic>` | Name 1  | 123   | 5       | 8     | 0    | 1       |
    +                                                             +---------+-------+---------+-------+------+---------+
    |                                                             | Name 2  | +0    | +0      | +0    | +0   | +0      |
    +-------------------------------------------------------------+---------+-------+---------+-------+------+---------+

.. raw:: latex

    \\end{{scriptsize}}
.. performance-variants-table
.. raw:: latex

    \\begin{{scriptsize}}

.. table::
    :class: longtable
    :widths: 31,14,19,12,12,12

    +----------------------------------------+---------------------------------------------------------------------------------------------+---------+----------+-------------+----------+
    | Specification                          | Environment                                                                                 | Variant | Min [μs] | Median [μs] | Max [μs] |
    +========================================+=============================================================================================+=========+==========+=============+==========+
    | ``spec:/​rtems/​req/​perf``            | `HotCache <doc/ts/srs/requirements.html#spec-req-perf-runtime-environment-hot-cache>`__     | Name 1  | 0.275    | 2.750       | 0.275    |
    +                                        +                                                                                             +---------+----------+-------------+----------+
    |                                        |                                                                                             | Name 2  | +0 %     | +0 %        | +0 %     |
    +                                        +                                                                                             +---------+----------+-------------+----------+
    |                                        |                                                                                             | Name 3  | ?        | ?           | ?        |
    +                                        +---------------------------------------------------------------------------------------------+---------+----------+-------------+----------+
    |                                        | `FullCache <doc/ts/srs/requirements.html#spec-req-perf-runtime-environment-full-cache>`__   | Name 1  | 0.275    | 0.275       | 0.475    |
    +                                        +                                                                                             +---------+----------+-------------+----------+
    |                                        |                                                                                             | Name 2  | +0 %     | +0 %        | +0 %     |
    +                                        +                                                                                             +---------+----------+-------------+----------+
    |                                        |                                                                                             | Name 3  | ?        | ?           | ?        |
    +                                        +---------------------------------------------------------------------------------------------+---------+----------+-------------+----------+
    |                                        | `DirtyCache <doc/ts/srs/requirements.html#spec-req-perf-runtime-environment-dirty-cache>`__ | Name 1  | 2.125    | 21250.000   | 2.125    |
    +                                        +                                                                                             +---------+----------+-------------+----------+
    |                                        |                                                                                             | Name 2  | +0 %     | +0 %        | +0 %     |
    +                                        +                                                                                             +---------+----------+-------------+----------+
    |                                        |                                                                                             | Name 3  | ?        | ?           | ?        |
    +                                        +---------------------------------------------------------------------------------------------+---------+----------+-------------+----------+
    |                                        | `Load/1 <doc/ts/srs/requirements.html#spec-req-perf-runtime-environment-load>`__            | Name 1  | 0.106    | 1062000.000 | 1.062    |
    +                                        +                                                                                             +---------+----------+-------------+----------+
    |                                        |                                                                                             | Name 2  | +0 %     | +0 %        | +0 %     |
    +                                        +                                                                                             +---------+----------+-------------+----------+
    |                                        |                                                                                             | Name 3  | ?        | ?           | ?        |
    +----------------------------------------+---------------------------------------------------------------------------------------------+---------+----------+-------------+----------+
    | ``spec:/​rtems/​req/​perf-no-results`` | `HotCache <doc/ts/srs/requirements.html#spec-req-perf-runtime-environment-hot-cache>`__     | Name 1  | ?        | ?           | ?        |
    +----------------------------------------+---------------------------------------------------------------------------------------------+---------+----------+-------------+----------+
    | ``spec:/​rtems/​req/​perf-no-results`` | `HotCache <doc/ts/srs/requirements.html#spec-req-perf-runtime-environment-hot-cache>`__     | Name 2  | ?        | ?           | ?        |
    +                                        +                                                                                             +---------+----------+-------------+----------+
    |                                        |                                                                                             | Name 3  | ?        | ?           | ?        |
    +                                        +---------------------------------------------------------------------------------------------+---------+----------+-------------+----------+
    |                                        | `FullCache <doc/ts/srs/requirements.html#spec-req-perf-runtime-environment-full-cache>`__   | Name 1  | ?        | ?           | ?        |
    +                                        +---------------------------------------------------------------------------------------------+---------+----------+-------------+----------+
    |                                        | `FullCache <doc/ts/srs/requirements.html#spec-req-perf-runtime-environment-full-cache>`__   | Name 2  | ?        | ?           | ?        |
    +                                        +                                                                                             +---------+----------+-------------+----------+
    |                                        |                                                                                             | Name 3  | ?        | ?           | ?        |
    +                                        +---------------------------------------------------------------------------------------------+---------+----------+-------------+----------+
    |                                        | `DirtyCache <doc/ts/srs/requirements.html#spec-req-perf-runtime-environment-dirty-cache>`__ | Name 1  | ?        | ?           | ?        |
    +                                        +---------------------------------------------------------------------------------------------+---------+----------+-------------+----------+
    |                                        | `DirtyCache <doc/ts/srs/requirements.html#spec-req-perf-runtime-environment-dirty-cache>`__ | Name 2  | ?        | ?           | ?        |
    +                                        +                                                                                             +---------+----------+-------------+----------+
    |                                        |                                                                                             | Name 3  | ?        | ?           | ?        |
    +                                        +---------------------------------------------------------------------------------------------+---------+----------+-------------+----------+
    |                                        | `Load/1 <doc/ts/srs/requirements.html#spec-req-perf-runtime-environment-load>`__            | Name 1  | ?        | ?           | ?        |
    +                                        +---------------------------------------------------------------------------------------------+---------+----------+-------------+----------+
    |                                        | `Load/1 <doc/ts/srs/requirements.html#spec-req-perf-runtime-environment-load>`__            | Name 2  | ?        | ?           | ?        |
    +                                        +                                                                                             +---------+----------+-------------+----------+
    |                                        |                                                                                             | Name 3  | ?        | ?           | ?        |
    +----------------------------------------+---------------------------------------------------------------------------------------------+---------+----------+-------------+----------+

.. raw:: latex

    \\end{{scriptsize}}
.. repositories
.. _GitRepositoryBuildSrcB:

Git Repository: build/src/b
---------------------------

B

The ``pkg``
branch with commit ``52f06822b8921ad825cb593b792eab7640e26cde`` was used to build the
package.  This branch is checked out after unpacking the archive.  It is based
on commit `bcef89f2360b97005e490c92fe624ab9dec789e6 <https://git.rtems.org/rtems/commit/?id=bcef89f2360b97005e490c92fe624ab9dec789e6>`__ of the
``master`` branch of the ``origin`` remote
repository.
.. pre-qualified-interfaces
.. _SparcGr712rcSmp4Blub:

Blub
----

- ``blub()``

.. _SparcGr712rcSmp4UnspecGroup:

UnspecGroup
-----------

- ``UnspecFunction()``

- ``UnspecMacro()``
.. targets
.. _PackageItemRtemsTargetA:

Name Target A
-------------

Brief target A.

Description target A.

.. _PackageItemRtemsTargetB:

Name Target B
-------------

Brief target B.

Description target B.
.. change-list

.. _Name2:

Name 2
------

Description 2.

.. _Name2NewlyOpenIssues:

Newly open issues
^^^^^^^^^^^^^^^^^

At the time when the package of this version was produced, the following newly open issues with respect to the previous package version were present.

.. raw:: latex

    \\begin{{footnotesize}}

.. table::
    :class: longtable
    :widths: 27,14,59

    +--------------+------------------------------------------------+---------------------------------------------------------+
    | Database     | Identifier                                     | Subject                                                 |
    +==============+================================================+=========================================================+
    | RTEMS Ticket | `2548 <https://devel.rtems.org/ticket/2548>`__ | Problematic integer conversion in rtems_clock_get_tod() |
    +--------------+------------------------------------------------+---------------------------------------------------------+

.. raw:: latex

    \\end{{footnotesize}}

.. _Name2AlreadyOpenIssues:

Already open issues
^^^^^^^^^^^^^^^^^^^

At the time when the package of this version was produced, the following open issues which were newly or already open in the previous package version were present.

.. raw:: latex

    \\begin{{footnotesize}}

.. table::
    :class: longtable
    :widths: 27,14,59

    +--------------+------------------------------------------------+------------------------------------------------------------+
    | Database     | Identifier                                     | Subject                                                    |
    +==============+================================================+============================================================+
    | RTEMS Ticket | `2365 <https://devel.rtems.org/ticket/2365>`__ | Task pre-emption disable is broken due to pseudo ISR tasks |
    +--------------+------------------------------------------------+------------------------------------------------------------+

.. raw:: latex

    \\end{{footnotesize}}

.. _Name2ClosedIssues:

Closed issues
^^^^^^^^^^^^^

For this package version, the following issues which were newly or already open in the previous package version were closed.

.. raw:: latex

    \\begin{{footnotesize}}

.. table::
    :class: longtable
    :widths: 27,14,59

    +--------------+------------------------------------------------+------------------------------------------------------+
    | Database     | Identifier                                     | Subject                                              |
    +==============+================================================+======================================================+
    | RTEMS Ticket | `2189 <https://devel.rtems.org/ticket/2189>`__ | Insufficient documentation for rtems_clock_get_tod() |
    +--------------+------------------------------------------------+------------------------------------------------------+

.. raw:: latex

    \\end{{footnotesize}}

.. _Name1:

Name 1
------

Description 1.

.. _Name1NewlyOpenIssues:

Newly open issues
^^^^^^^^^^^^^^^^^

At the time when the package of this version was produced, the following newly open issues with respect to the previous package version were present.

.. raw:: latex

    \\begin{{footnotesize}}

.. table::
    :class: longtable
    :widths: 27,14,59

    +--------------+------------------------------------------------+------------------------------------------------------------+
    | Database     | Identifier                                     | Subject                                                    |
    +==============+================================================+============================================================+
    | RTEMS Ticket | `2189 <https://devel.rtems.org/ticket/2189>`__ | Insufficient documentation for rtems_clock_get_tod()       |
    +--------------+------------------------------------------------+------------------------------------------------------------+
    | RTEMS Ticket | `2365 <https://devel.rtems.org/ticket/2365>`__ | Task pre-emption disable is broken due to pseudo ISR tasks |
    +--------------+------------------------------------------------+------------------------------------------------------------+

.. raw:: latex

    \\end{{footnotesize}}

.. _Name1AlreadyOpenIssues:

Already open issues
^^^^^^^^^^^^^^^^^^^

At the time when the package was produced,
there were no open issues which were newly or already open in the previous package version associated.

.. _Name1ClosedIssues:

Closed issues
^^^^^^^^^^^^^

At the time when the package was produced,
there were no closed associated.

.. _Name0:

Name 0
------

Description 0.

.. _Name0InitiallyOpenIssues:

Initially open issues
^^^^^^^^^^^^^^^^^^^^^

At the time when the package was produced,
there were no open associated.
.. open-issues
.. _OpenIssues:

Open issues
-----------

At the time when the package of this version was produced, the following open issues were present.

.. raw:: latex

    \\begin{{footnotesize}}

.. table::
    :class: longtable
    :widths: 27,14,59

    +--------------+------------------------------------------------+------------------------------------------------------------+
    | Database     | Identifier                                     | Subject                                                    |
    +==============+================================================+============================================================+
    | RTEMS Ticket | `2365 <https://devel.rtems.org/ticket/2365>`__ | Task pre-emption disable is broken due to pseudo ISR tasks |
    +--------------+------------------------------------------------+------------------------------------------------------------+
    | RTEMS Ticket | `2548 <https://devel.rtems.org/ticket/2548>`__ | Problematic integer conversion in rtems_clock_get_tod()    |
    +--------------+------------------------------------------------+------------------------------------------------------------+

.. raw:: latex

    \\end{{footnotesize}}
.. license-info
All directories and file paths in this section are
relative to {_format_path(tmp_dir, 'pkg')}.

.. _Directory:

Directory - ..
--------------

.. _Directory FileDirATxt:

File - dir/a.txt
^^^^^^^^^^^^^^^^

The license file
:file:`.​.​/​dir/​a.​txt`
is applicable to this directory or parts of the directory:

.. raw:: latex

    \\begin{{footnotesize}}

.. code-block:: none

    A

.. raw:: latex

    \\end{{footnotesize}}

.. _BSD2ClauseCopyrights:

BSD-2-Clause copyrights
-----------------------

| © 2023 Alice

.. raw:: latex

    \\begin{{footnotesize}}

.. code-block:: none

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions
    are met:
    1. Redistributions of source code must retain the above copyright
       notice, this list of conditions and the following disclaimer.
    2. Redistributions in binary form must reproduce the above copyright
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
    ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
    LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
    CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
    SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
    INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
    CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
    ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
    POSSIBILITY OF SUCH DAMAGE.

.. raw:: latex

    \\end{{footnotesize}}
.. clear-copyrights-by-license
clear copyrights by license
.. license-info
All directories and file paths in this section are
relative to {_format_path(tmp_dir, 'pkg')}.
.. build-description
.. _PackageItemPkgComponent:

spec:/pkg/component
===================

Support the package build.

.. _PackageItemRtemsTargetA:

spec:/rtems/target-a
====================

Support the package build.

.. _PackageItemPkgStepsRtemsItemCache:

spec:/pkg/steps/rtems-item-cache
================================

Use input :ref:`spec:/pkg/component <PackageItemPkgComponent>`.

Augment the component with an RTEMS-specific
view of the specification items.

.. _PackageItemPkgBuildConfig:

spec:/pkg/build-config
======================

Use input :ref:`spec:/pkg/component <PackageItemPkgComponent>`.

Support the package build.

.. _PackageItemPkgBuildConfigEmpty:

spec:/pkg/build-config-empty
============================

Use input :ref:`spec:/pkg/component <PackageItemPkgComponent>`.

Support the package build.

.. _PackageItemPkgBuildConfigErrors:

spec:/pkg/build-config-errors
=============================

Use input :ref:`spec:/pkg/component <PackageItemPkgComponent>`.

Support the package build.

.. _PackageItemPkgTestLogsMembench2:

spec:/pkg/test-logs/membench-2
==============================

Use input :ref:`spec:/pkg/component <PackageItemPkgComponent>`.

Represent the file {_format_path(tmp_dir, 'pkg/build/src/membench.json')}.

.. _PackageItemPkgPackageChanges:

spec:/pkg/package-changes
=========================

Use input :ref:`spec:/pkg/component <PackageItemPkgComponent>`.

Support the package build.

.. _PackageItemPkgSourceTestFiles:

spec:/pkg/source/test-files
===========================

Use input :ref:`spec:/pkg/component <PackageItemPkgComponent>`.

Represent 83 files in directory
{_format_path(tmp_dir, '')}.

.. _PackageItemPkgCoverageTargetA:

spec:/pkg/coverage/target-a
===========================

Use the following inputs:

- :ref:`spec:/pkg/build-config <PackageItemPkgBuildConfig>`

- :ref:`spec:/pkg/component <PackageItemPkgComponent>`

- :ref:`spec:/rtems/target-a <PackageItemRtemsTargetA>`

Represent the file {_format_path(tmp_dir, 'pkg/coverage.json')}.

.. _PackageItemPkgCoverageTargetAEmpty:

spec:/pkg/coverage/target-a-empty
=================================

Use the following inputs:

- :ref:`spec:/pkg/build-config <PackageItemPkgBuildConfig>`

- :ref:`spec:/pkg/component <PackageItemPkgComponent>`

- :ref:`spec:/rtems/target-a <PackageItemRtemsTargetA>`

Represent the file {_format_path(tmp_dir, 'pkg/coverage-empty.json')}.

.. _PackageItemPkgCoverageTargetAGood:

spec:/pkg/coverage/target-a-good
================================

Use the following inputs:

- :ref:`spec:/pkg/build-config <PackageItemPkgBuildConfig>`

- :ref:`spec:/pkg/component <PackageItemPkgComponent>`

- :ref:`spec:/rtems/target-a <PackageItemRtemsTargetA>`

Represent the file {_format_path(tmp_dir, 'pkg/coverage-good.json')}.

.. _PackageItemPkgCoverageTargetANotRun:

spec:/pkg/coverage/target-a-not-run
===================================

Use the following inputs:

- :ref:`spec:/pkg/build-config <PackageItemPkgBuildConfig>`

- :ref:`spec:/pkg/component <PackageItemPkgComponent>`

- :ref:`spec:/rtems/target-a <PackageItemRtemsTargetA>`

Represent the file {_format_path(tmp_dir, 'pkg/not-run-coverage.json')}.

.. _PackageItemPkgCoverageTargetAOverall:

spec:/pkg/coverage/target-a-overall
===================================

Use the following inputs:

- :ref:`spec:/pkg/build-config <PackageItemPkgBuildConfig>`

- :ref:`spec:/pkg/component <PackageItemPkgComponent>`

- :ref:`spec:/rtems/target-a <PackageItemRtemsTargetA>`

Represent the file {_format_path(tmp_dir, 'pkg/coverage-overall.json')}.

.. _PackageItemPkgTestLogsPerf:

spec:/pkg/test-logs/perf
========================

Use the following inputs:

- :ref:`spec:/pkg/build-config <PackageItemPkgBuildConfig>`

- :ref:`spec:/pkg/component <PackageItemPkgComponent>`

- :ref:`spec:/rtems/target-a <PackageItemRtemsTargetA>`

Represent the file {_format_path(tmp_dir, 'pkg/test-log-perf.json')}.

.. _PackageItemPkgTestLogsSample:

spec:/pkg/test-logs/sample
==========================

Use the following inputs:

- :ref:`spec:/pkg/build-config <PackageItemPkgBuildConfig>`

- :ref:`spec:/pkg/component <PackageItemPkgComponent>`

- :ref:`spec:/rtems/target-a <PackageItemRtemsTargetA>`

Represent the file {_format_path(tmp_dir, 'pkg/test-log-sample.json')}.

.. _PackageItemPkgTestLogsEmpty:

spec:/pkg/test-logs/empty
=========================

Use the following inputs:

- :ref:`spec:/pkg/build-config-empty <PackageItemPkgBuildConfigEmpty>`

- :ref:`spec:/pkg/component <PackageItemPkgComponent>`

- :ref:`spec:/rtems/target-a <PackageItemRtemsTargetA>`

Represent the file {_format_path(tmp_dir, 'pkg/test-log-empty.json')}.

.. _PackageItemPkgTestLogsPerfErrors:

spec:/pkg/test-logs/perf-errors
===============================

Use the following inputs:

- :ref:`spec:/pkg/build-config-errors <PackageItemPkgBuildConfigErrors>`

- :ref:`spec:/pkg/component <PackageItemPkgComponent>`

- :ref:`spec:/rtems/target-a <PackageItemRtemsTargetA>`

Represent the file {_format_path(tmp_dir, 'pkg/test-log-perf-errors.json')}.

.. _PackageItemPkgSourceDocPackageManual:

spec:/pkg/source/doc-package-manual
===================================

Use the following inputs:

- :ref:`spec:/pkg/component <PackageItemPkgComponent>`

- :ref:`spec:/pkg/source/test-files <PackageItemPkgSourceTestFiles>`

Represent the file {_format_path(tmp_dir, 'pkg/build/src/doc-package-manual/source/index.rst')}.

.. _PackageItemPkgSourceA:

spec:/pkg/source/a
==================

Use the following inputs:

- :ref:`spec:/pkg/component <PackageItemPkgComponent>`

- :ref:`spec:/pkg/source/test-files <PackageItemPkgSourceTestFiles>`

Represent the files:

- {_format_path(tmp_dir, 'dir/a.txt')}

- {_format_path(tmp_dir, 'dir/subdir/c.txt')}

- {_format_path(tmp_dir, 'dir/subdir/d.txt')}

.. _PackageItemPkgStepsAggregateTestResults:

spec:/pkg/steps/aggregate-test-results
======================================

Use the following inputs:

- :ref:`spec:/pkg/component <PackageItemPkgComponent>`

- :ref:`spec:/pkg/coverage/target-a <PackageItemPkgCoverageTargetA>`

- :ref:`spec:/pkg/coverage/target-a-empty <PackageItemPkgCoverageTargetAEmpty>`

- :ref:`spec:/pkg/coverage/target-a-good <PackageItemPkgCoverageTargetAGood>`

- :ref:`spec:/pkg/coverage/target-a-not-run
  <PackageItemPkgCoverageTargetANotRun>`

- :ref:`spec:/pkg/coverage/target-a-overall
  <PackageItemPkgCoverageTargetAOverall>`

- :ref:`spec:/pkg/steps/rtems-item-cache <PackageItemPkgStepsRtemsItemCache>`

- :ref:`spec:/pkg/test-logs/empty <PackageItemPkgTestLogsEmpty>`

- :ref:`spec:/pkg/test-logs/perf <PackageItemPkgTestLogsPerf>`

- :ref:`spec:/pkg/test-logs/perf-errors <PackageItemPkgTestLogsPerfErrors>`

- :ref:`spec:/pkg/test-logs/sample <PackageItemPkgTestLogsSample>`

Aggregate test results.

.. _PackageItemPkgSourceArchive:

spec:/pkg/source/archive
========================

Use the following inputs:

- :ref:`spec:/pkg/component <PackageItemPkgComponent>`

- :ref:`spec:/pkg/source/a <PackageItemPkgSourceA>`

Support the package build.

.. _PackageItemPkgDeploymentVerifyPackage:

spec:/pkg/deployment/verify-package
===================================

Use input :ref:`spec:/pkg/component <PackageItemPkgComponent>`.

Represent the file {_format_path(tmp_dir, 'verify_package.py')}.

.. _PackageItemPkgDeploymentDocPackageManual:

spec:/pkg/deployment/doc-package-manual
=======================================

Use the following inputs:

- :ref:`spec:/pkg/component <PackageItemPkgComponent>`

- :ref:`spec:/pkg/deployment/verify-package
  <PackageItemPkgDeploymentVerifyPackage>`

- :ref:`spec:/pkg/package-changes <PackageItemPkgPackageChanges>`

- :ref:`spec:/pkg/source/archive <PackageItemPkgSourceArchive>`

- :ref:`spec:/pkg/source/doc-package-manual
  <PackageItemPkgSourceDocPackageManual>`

- :ref:`spec:/pkg/steps/aggregate-test-results
  <PackageItemPkgStepsAggregateTestResults>`

- :ref:`spec:/pkg/steps/rtems-item-cache <PackageItemPkgStepsRtemsItemCache>`

- :ref:`spec:/pkg/test-logs/empty <PackageItemPkgTestLogsEmpty>`

- :ref:`spec:/pkg/test-logs/membench-2 <PackageItemPkgTestLogsMembench2>`

- :ref:`spec:/pkg/test-logs/perf <PackageItemPkgTestLogsPerf>`

Support the package build.
"""
    package_summary = director["/pkg/deployment/doc-package-summary"]
    with open(package_summary.file, "r", encoding="utf-8") as src:
        assert src.read() == """(PackageSummarySparcGr712rcSmp4)=

# Package summary - sparc/gr712rc/smp/4

(PackageSummarySparcGr712rcSmp4TestStatus)=

## Test status

(PackageSummarySparcGr712rcSmp4TestStatusComponentSparcGr712rcSmp4)=

### Component - sparc/gr712rc/smp/4

- /rtems/target-a

  - /build/test-program

  - /build/testsuites/smptests/smplock01

  - /build/testsuites/smptests/smpopenmp01

  - /build/testsuites/sptests/sptimecounter02

  - /build/testsuites/tmtests/tmcontext01

  - /build/testsuites/tmtests/tmfine01

  - /build/testsuites/tmtests/tmtimer01

  - /rtems/req/action

  - /rtems/req/action-2

  - /rtems/req/perf-no-results

  - /rtems/val/test-case-fail

  - /rtems/val/test-case-run

  - /rtems/val/test-case-unit

  - /rtems/val/test-case-xfail

  - /testsuites/performance-no-clock-0

  - /testsuites/test-suite-fail

  - /testsuites/test-suite-pass

  - /testsuites/test-suite-xfail

(PackageSummarySparcGr712rcSmp4TestStatusComponentSparcGr712rcSmp4)=

### Component - sparc/gr712rc/smp/4

There were no unexpected test errors found in the test outputs.

(PackageSummarySparcGr712rcSmp4CoverageData)=

## Coverage data

(PackageSummarySparcGr712rcSmp4CoverageDataComponentSparcGr712rcSmp4)=

### Component - sparc/gr712rc/smp/4

 | Target        | Configuration    | Scope   | Functions           | Status  | Lines                    | Status  | Branches             | Status  |
 | ------------- | ---------------- | ------- | ------------------- | ------- | ------------------------ | ------- | -------------------- | ------- |
 | Name Target A | build-config-key | Scope   | 0/0 (N/A) [13+2/16] | **NOK** | 5+1/6 (100%) [114+3/119] | OK      | 2/2 (100%) [12+4/18] | OK      |
 | Name Target A | build-config-key | Empty   | N/A                 | **NOK** | N/A                      | **NOK** | N/A                  | **NOK** |
 | Name Target A | build-config-key | Good    | 1/1 (100%)          | OK      | 18/18 (100%)             | OK      | 4/4 (100%)           | OK      |
 | Name Target A | build-config-key | Overall | 0/1 (0.0%) [1/1]    | **NOK** | 3/18 (16.6%) [0/2]       | **NOK** | 2/4 (50.0%)          | **NOK** |

(PackageSummarySparcGr712rcSmp4CoverageDataComponentSparcGr712rcSmp4)=

### Component - sparc/gr712rc/smp/4

 | Target | Configuration | Scope | Functions | Status | Lines | Status | Branches | Status |
 | ------ | ------------- | ----- | --------- | ------ | ----- | ------ | -------- | ------ |

(PackageSummarySparcGr712rcSmp4Repositories)=

## Repositories

(PackageSummarySparcGr712rcSmp4RepositoriesSpec)=

### ../spec

```{code} none
:linenos:
:lineno-start: 1
git log -1
```

(PackageSummarySparcGr712rcSmp4RepositoriesBuildSrcB)=

### build/src/b

```{code} none
:linenos:
:lineno-start: 1
git log -1
```
"""
    pm2_build = Path(director["/pkg/build/doc-package-manual-2"].directory)
    pm2_index = pm2_build / "source" / "index.rst"
    with open(pm2_index, "r", encoding="utf-8") as src:
        assert src.read() == f""".. SPDX-License-Identifier: CC-BY-SA-4.0

.. Copyright (C) 2025 embedded brains GmbH & Co. KG

text
.. raw:: latex

    \\begin{{scriptsize}}

.. table::
    :class: longtable
    :widths: 35,20,9,9,9,9,9

    +---------------+---------+-------+---------+-------+------+---------+
    | Specification | Variant | .text | .rodata | .data | .bss | .noinit |
    +---------------+---------+-------+---------+-------+------+---------+

.. raw:: latex

    \\end{{scriptsize}}
text
There is no performance variants table available.
text
"""
    verify_package_sha512 = pm.substitute("${.:/input/verify-package/sha512}")
    if pickle.DEFAULT_PROTOCOL == 4:
        assert verify_package_sha512 == "6​f​a​c​7​d​c​2​c​6​2​4​1​c​b​3​0​6​b​5​6​a​8​1​5​7​a​c​b​1​3​b​c​5​1​e​a​e​4​e​c​9​3​6​8​5​5​4​0​b​7​a​7​9​3​1​e​1​5​3​3​7​4​7​8​7​0​1​2​e​8​6​8​2​6​8​4​e​6​5​b​9​9​7​7​5​2​a​e​0​a​f​a​e​6​5​7​6​6​a​c​b​b​a​0​e​e​6​5​e​2​9​8​a​0​b​f​7​2​d​d​c​4​6​e​7​0​9"
    else:
        assert verify_package_sha512 == "3​8​9​0​0​3​a​2​4​5​5​4​8​4​4​4​4​a​1​0​e​9​b​8​9​9​9​d​4​2​a​8​2​a​f​5​a​e​9​a​d​e​b​5​b​6​1​f​d​9​1​7​4​e​d​9​2​d​3​4​e​1​3​4​8​1​1​3​6​1​2​e​3​5​e​4​5​8​6​a​a​a​e​1​3​9​9​9​8​c​c​f​0​f​f​6​0​3​6​6​1​9​9​f​6​b​2​8​0​e​a​a​5​7​9​1​6​d​6​8​4​4​a​9​3​0​9​7"
