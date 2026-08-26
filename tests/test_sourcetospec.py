# SPDX-License-Identifier: BSD-2-Clause
""" Tests for the sourcetospec module. """

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

from pathlib import Path
import re
from xml.etree import ElementTree

import pytest

from specmake import DoxygenContext
from specmake import sourcetospec
from specmake.sourcetospec import _append_element_text, _Scope, DoxygenItem

_GF_0_EXPECTED_RESULT = {
    "SPDX-License-Identifier":
    "CC-BY-SA-4.0 OR BSD-2-Clause",
    "brief":
    "Brief gf_0().",
    "copyrights": ["Copyright (C) 2024 embedded brains GmbH & Co. KG"],
    "definition": {
        "default": {
            "attributes":
            None,
            "body":
            None,
            "params": [
                "const int *${.:/params[0]/name}", "int *${.:/params[1]/name}",
                "int *${.:/params[2]/name}", "int ${.:/params[3]/name}"
            ],
            "return":
            "int"
        },
        "variants": []
    },
    "description":
    "Description gf_0().",
    "enabled-by":
    True,
    "index-entries": [],
    "interface-type":
    "function",
    "links": [{
        "role": "interface-placement",
        "uid": "header-header"
    }, {
        "role": "interface-ingroup",
        "uid": "group"
    }],
    "name":
    "gf_0",
    "notes":
    None,
    "params": [{
        "description": "gf_0() in description.",
        "dir": "in",
        "name": "in"
    }, {
        "description": "gf_0() out description.",
        "dir": "out",
        "name": "out"
    }, {
        "description": "gf_0() inout description.",
        "dir": "inout",
        "name": "inout"
    }, {
        "description": "gf_0() none description.",
        "dir": None,
        "name": "none"
    }],
    "return": {
        "return":
        "gf_0() return description.",
        "return-values": [{
            "description": "gf_0() retval description.",
            "value": "retval"
        }]
    },
    "type":
    "interface"
}

_F_0_EXPECTED_RESULT = {
    "SPDX-License-Identifier":
    "CC-BY-SA-4.0 OR BSD-2-Clause",
    "brief":
    "Brief f_0().",
    "copyrights": ["Copyright (C) 2024 embedded brains GmbH & Co. KG"],
    "definition": {
        "default": {
            "attributes":
            None,
            "body":
            None,
            "params": [
                "const int *${.:/params[0]/name}", "int *${.:/params[1]/name}",
                "int *${.:/params[2]/name}", "int ${.:/params[3]/name}",
                "int *(*${.:/params[4]/name})(int i, int *, int *(*f2)(void))"
            ],
            "return":
            "int"
        },
        "variants": []
    },
    "description":
    "Description f_0().",
    "enabled-by":
    True,
    "index-entries": [],
    "interface-type":
    "function",
    "links": [{
        "role": "interface-placement",
        "uid": "header-header"
    }, {
        "role": "interface-ingroup",
        "uid": "group"
    }],
    "name":
    "f_0",
    "notes":
    None,
    "params": [{
        "description": "f_0() in description.",
        "dir": "in",
        "name": "in"
    }, {
        "description": "f_0() out description.",
        "dir": "out",
        "name": "out"
    }, {
        "description": "f_0() inout description.",
        "dir": "inout",
        "name": "inout"
    }, {
        "description": "f_0() none description.",
        "dir": None,
        "name": "none"
    }, {
        "description": "f_0() function pointer description.",
        "dir": None,
        "name": "f"
    }],
    "return": {
        "return":
        "* f_0() return description list item 0\n\n"
        "* f_0() return description list item 1",
        "return-values": [{
            "description": "f_0() retval description.",
            "value": "retval"
        }]
    },
    "type":
    "interface"
}

_GF_1_EXPECTED_RESULT = {
    "SPDX-License-Identifier":
    "CC-BY-SA-4.0 OR BSD-2-Clause",
    "brief":
    "Brief gf_1().",
    "copyrights": ["Copyright (C) 2024 embedded brains GmbH & Co. KG"],
    "definition": {
        "default": {
            "attributes": None,
            "body": None,
            "params": [],
            "return": None
        },
        "variants": []
    },
    "description":
    "Description gf_1().",
    "enabled-by":
    True,
    "index-entries": [],
    "interface-type":
    "function",
    "links": [{
        "role": "interface-placement",
        "uid": "header-header"
    }, {
        "role": "interface-ingroup",
        "uid": "group"
    }],
    "name":
    "gf_1",
    "notes":
    None,
    "params": [],
    "return":
    None,
    "type":
    "interface"
}

_F_1_EXPECTED_RESULT = {
    "SPDX-License-Identifier":
    "CC-BY-SA-4.0 OR BSD-2-Clause",
    "brief":
    "Brief f_1().",
    "copyrights": ["Copyright (C) 2024 embedded brains GmbH & Co. KG"],
    "definition": {
        "default": {
            "attributes": None,
            "body": None,
            "params": [],
            "return": None
        },
        "variants": []
    },
    "description":
    "Description f_1().",
    "enabled-by":
    True,
    "index-entries": [],
    "interface-type":
    "function",
    "links": [{
        "role": "interface-placement",
        "uid": "header-header"
    }, {
        "role": "interface-ingroup",
        "uid": "group"
    }],
    "name":
    "f_1",
    "notes":
    None,
    "params": [],
    "return":
    None,
    "type":
    "interface"
}

_GF_2_EXPECTED_RESULT = {
    "SPDX-License-Identifier":
    "CC-BY-SA-4.0 OR BSD-2-Clause",
    "brief":
    "Brief gf_2().",
    "copyrights": ["Copyright (C) 2024 embedded brains GmbH & Co. KG"],
    "definition": {
        "default": {
            "attributes": None,
            "body": None,
            "params": ["int ${.:/params[0]/name}", "int ${.:/params[1]/name}"],
            "return": "int"
        },
        "variants": []
    },
    "description":
    "Description gf_2().",
    "enabled-by":
    True,
    "index-entries": [],
    "interface-type":
    "function",
    "links": [{
        "role": "interface-placement",
        "uid": "header-header"
    }, {
        "role": "interface-ingroup",
        "uid": "group"
    }],
    "name":
    "gf_2",
    "notes":
    None,
    "params": [{
        "description": "gf_2() x description.",
        "dir": "in",
        "name": "x"
    }, {
        "description": "gf_2() y description.",
        "dir": "in",
        "name": "y"
    }],
    "return": {
        "return":
        "gf_2() return description.",
        "return-values": [{
            "description": "gf_2() retval description.",
            "value": "retval"
        }]
    },
    "type":
    "interface"
}

_F_2_EXPECTED_RESULT = {
    "SPDX-License-Identifier":
    "CC-BY-SA-4.0 OR BSD-2-Clause",
    "brief":
    "Brief f_2().",
    "copyrights": ["Copyright (C) 2024 embedded brains GmbH & Co. KG"],
    "definition": {
        "default": {
            "attributes": None,
            "body": None,
            "params": ["int ${.:/params[0]/name}", "int ${.:/params[1]/name}"],
            "return": "int"
        },
        "variants": []
    },
    "description":
    "Description f_2().",
    "enabled-by":
    True,
    "index-entries": [],
    "interface-type":
    "function",
    "links": [{
        "role": "interface-placement",
        "uid": "header-header"
    }, {
        "role": "interface-ingroup",
        "uid": "group"
    }],
    "name":
    "f_2",
    "notes":
    None,
    "params": [{
        "description": "f_2() x description.",
        "dir": "in",
        "name": "x"
    }, {
        "description": "f_2() y description.",
        "dir": "in",
        "name": "y"
    }],
    "return": {
        "return":
        "f_2() return description.",
        "return-values": [{
            "description": "f_2() retval description.",
            "value": "retval"
        }]
    },
    "type":
    "interface"
}

_GF_3_EXPECTED_RESULT = {
    "SPDX-License-Identifier":
    "CC-BY-SA-4.0 OR BSD-2-Clause",
    "brief":
    "Brief TODO.\n",
    "copyrights": ["Copyright (C) 2024 embedded brains GmbH & Co. KG"],
    "definition": {
        "default": {
            "attributes": None,
            "body": None,
            "params": ["int ${.:/params[0]/name}", "int ${.:/params[1]/name}"],
            "return": None
        },
        "variants": []
    },
    "description":
    None,
    "enabled-by":
    True,
    "index-entries": [],
    "interface-type":
    "function",
    "links": [{
        "role": "interface-placement",
        "uid": "header-header"
    }, {
        "role": "interface-ingroup",
        "uid": "group"
    }],
    "name":
    "gf_3",
    "notes":
    None,
    "params": [{
        "description": None,
        "dir": None,
        "name": "x",
    }, {
        "description": None,
        "dir": None,
        "name": "y",
    }],
    "return":
    None,
    "type":
    "interface"
}

_GF_4_EXPECTED_RESULT = {
    "SPDX-License-Identifier":
    "CC-BY-SA-4.0 OR BSD-2-Clause",
    "brief":
    "Brief gf_4().",
    "copyrights": ["Copyright (C) 2024 embedded brains GmbH & Co. KG"],
    "definition": {
        "default": {
            "attributes":
            None,
            "body":
            None,
            "params": [
                "const ${/gt_0:/name} *${.:/params[0]/name}",
                "${/gt_0:/name} *${.:/params[1]/name}"
            ],
            "return":
            "int"
        },
        "variants": []
    },
    "description":
    "Description gf_4().",
    "enabled-by":
    True,
    "index-entries": [],
    "interface-type":
    "function",
    "links": [{
        "role": "interface-placement",
        "uid": "header-header"
    }, {
        "role": "interface-ingroup",
        "uid": "group"
    }],
    "name":
    "gf_4",
    "notes":
    None,
    "params": [{
        "description": "gf_4() in description.",
        "dir": "in",
        "name": "in"
    }, {
        "description": "gf_4() out description.",
        "dir": "out",
        "name": "out"
    }],
    "return": {
        "return": "gf_4() return description.",
        "return-values": []
    },
    "type":
    "interface"
}

_GM_0_EXPECTED_RESULT = {
    "SPDX-License-Identifier":
    "CC-BY-SA-4.0 OR BSD-2-Clause",
    "brief":
    "Brief GM_0().",
    "copyrights": ["Copyright (C) 2024 embedded brains GmbH & Co. KG"],
    "definition": {
        "default": {
            "attributes": None,
            "body": "((a) > (b) ? (a) : (b))",
            "params": ["${.:/params[0]/name}", "${.:/params[1]/name}"],
            "return": None
        },
        "variants": []
    },
    "description":
    "Description GM_0().",
    "enabled-by":
    True,
    "index-entries": [],
    "interface-type":
    "macro",
    "links": [{
        "role": "interface-placement",
        "uid": "header-header"
    }, {
        "role": "interface-ingroup",
        "uid": "group"
    }],
    "name":
    "GM_0",
    "notes":
    None,
    "params": [{
        "description": "GM_0() a description.",
        "dir": "in",
        "name": "a"
    }, {
        "description": "GM_0() b description.",
        "dir": "in",
        "name": "b"
    }],
    "return": {
        "return": "GM_0() return description.",
        "return-values": []
    },
    "type":
    "interface"
}

_FOO_GROUP_EXPECTED_RESULT = {
    "SPDX-License-Identifier": "CC-BY-SA-4.0 OR BSD-2-Clause",
    "brief": "This group contains example items.",
    "copyrights": [
        "Copyright (C) 2024 embedded brains GmbH & Co. KG",
    ],
    "description": None,
    "enabled-by": True,
    "index-entries": [],
    "links": [],
    "name": "Example Group",
    "notes": None,
    "type": "interface",
    "interface-type": "group",
    "identifier": "FooGroup",
}

_HEADER_H_EXPECTED_RESULT = {
    "SPDX-License-Identifier":
    "CC-BY-SA-4.0 OR BSD-2-Clause",
    "brief":
    "This header file declares various C constructs with Doxygen comments.",
    "copyrights": [
        "Copyright (C) 2024 embedded brains GmbH & Co. KG",
    ],
    "description":
    "This file contains examples of functions, macros, typedefs, defines, "
    "structs, unions, and enums with Doxygen comments. Some of these are group "
    "members, and some are not.",
    "enabled-by":
    True,
    "index-entries": [],
    "links": [
        {
            "role": "interface-ingroup",
            "uid": "group",
        },
    ],
    "notes":
    None,
    "type":
    "interface",
    "interface-type":
    "header-file",
    "path":
    "header.h",
    "prefix":
    "",
}

_M_0_EXPECTED_RESULT = {
    "SPDX-License-Identifier":
    "CC-BY-SA-4.0 OR BSD-2-Clause",
    "brief":
    "Brief M_0().",
    "copyrights": ["Copyright (C) 2024 embedded brains GmbH & Co. KG"],
    "definition": {
        "default": {
            "attributes": None,
            "body": "((a) < (b) ? (a) : (b))",
            "params": ["${.:/params[0]/name}", "${.:/params[1]/name}"],
            "return": None
        },
        "variants": []
    },
    "description":
    "Description M_0().",
    "enabled-by":
    True,
    "index-entries": [],
    "interface-type":
    "macro",
    "links": [{
        "role": "interface-placement",
        "uid": "header-header"
    }, {
        "role": "interface-ingroup",
        "uid": "group"
    }],
    "name":
    "M_0",
    "notes":
    None,
    "params": [{
        "description": "M_0() a description.",
        "dir": "in",
        "name": "a"
    }, {
        "description": "M_0() b description.",
        "dir": "in",
        "name": "b"
    }],
    "return": {
        "return": "M_0() return description.",
        "return-values": []
    },
    "type":
    "interface"
}

_GD_1_EXPECTED_RESULT = {
    "SPDX-License-Identifier":
    "CC-BY-SA-4.0 OR BSD-2-Clause",
    "brief":
    "Brief GD_1.",
    "copyrights": ["Copyright (C) 2024 embedded brains GmbH & Co. KG"],
    "definition": {
        "default": "4096",
        "variants": []
    },
    "description":
    None,
    "enabled-by":
    True,
    "index-entries": [],
    "interface-type":
    "define",
    "links": [{
        "role": "interface-placement",
        "uid": "header-header"
    }, {
        "role": "interface-ingroup",
        "uid": "group"
    }],
    "name":
    "GD_1",
    "notes":
    None,
    "type":
    "interface"
}

_D_1_EXPECTED_RESULT = {
    "SPDX-License-Identifier":
    "CC-BY-SA-4.0 OR BSD-2-Clause",
    "brief":
    "Brief D_1.",
    "copyrights": ["Copyright (C) 2024 embedded brains GmbH & Co. KG"],
    "definition": {
        "default": "1024",
        "variants": []
    },
    "description":
    None,
    "enabled-by":
    True,
    "index-entries": [],
    "interface-type":
    "define",
    "links": [{
        "role": "interface-placement",
        "uid": "header-header"
    }, {
        "role": "interface-ingroup",
        "uid": "group"
    }],
    "name":
    "D_1",
    "notes":
    None,
    "type":
    "interface"
}

_GT_0_EXPECTED_RESULT = {
    "SPDX-License-Identifier":
    "CC-BY-SA-4.0 OR BSD-2-Clause",
    "brief":
    "Brief gt_0.",
    "copyrights": ["Copyright (C) 2024 embedded brains GmbH & Co. KG"],
    "definition": [{
        "default": {
            "brief": "Brief TODO.\n",
            "definition": "int ${.:name}",
            "description": None,
            "kind": "member",
            "name": "x"
        },
        "variants": []
    }, {
        "default": {
            "brief": "Brief TODO.\n",
            "definition": "int ${.:name}",
            "description": None,
            "kind": "member",
            "name": "y"
        },
        "variants": []
    }],
    "definition-kind":
    "typedef-only",
    "description":
    "Description gt_0.",
    "enabled-by":
    True,
    "index-entries": [],
    "interface-type":
    "struct",
    "links": [{
        "role": "interface-placement",
        "uid": "header-header"
    }, {
        "role": "interface-ingroup",
        "uid": "group"
    }],
    "name":
    "gt_0",
    "notes":
    None,
    "type":
    "interface"
}

_T_0_EXPECTED_RESULT = {
    "SPDX-License-Identifier":
    "CC-BY-SA-4.0 OR BSD-2-Clause",
    "brief":
    "Brief t_0.",
    "copyrights": ["Copyright (C) 2024 embedded brains GmbH & Co. KG"],
    "definition": [{
        "default": {
            "brief": "Brief TODO.\n",
            "definition": "int ${.:name}",
            "description": None,
            "kind": "member",
            "name": "x"
        },
        "variants": []
    }, {
        "default": {
            "brief": "Brief TODO.\n",
            "definition": "int ${.:name}",
            "description": None,
            "kind": "member",
            "name": "y"
        },
        "variants": []
    }],
    "definition-kind":
    "typedef-only",
    "description":
    "Description t_0.",
    "enabled-by":
    True,
    "index-entries": [],
    "interface-type":
    "struct",
    "links": [{
        "role": "interface-placement",
        "uid": "header-header"
    }, {
        "role": "interface-ingroup",
        "uid": "group"
    }],
    "name":
    "t_0",
    "notes":
    None,
    "type":
    "interface"
}

_GS_0_EXPECTED_RESULT = {
    "SPDX-License-Identifier":
    "CC-BY-SA-4.0 OR BSD-2-Clause",
    "brief":
    "Brief gs_0.",
    "copyrights": ["Copyright (C) 2024 embedded brains GmbH & Co. KG"],
    "definition": [{
        "default": {
            "brief": "Brief TODO.\n",
            "definition": "int ${.:name}",
            "description": None,
            "kind": "member",
            "name": "a"
        },
        "variants": []
    }, {
        "default": {
            "brief": "Brief TODO.\n",
            "definition": "int ${.:name}",
            "description": None,
            "kind": "member",
            "name": "b"
        },
        "variants": []
    }],
    "definition-kind":
    "struct-only",
    "description":
    "Description gs_0.",
    "enabled-by":
    True,
    "index-entries": [],
    "interface-type":
    "struct",
    "links": [{
        "role": "interface-placement",
        "uid": "header-header"
    }, {
        "role": "interface-ingroup",
        "uid": "group"
    }],
    "name":
    "gs_0",
    "notes":
    None,
    "type":
    "interface"
}

_S_0_EXPECTED_RESULT = {
    "SPDX-License-Identifier":
    "CC-BY-SA-4.0 OR BSD-2-Clause",
    "brief":
    "Brief s_0.",
    "copyrights": ["Copyright (C) 2024 embedded brains GmbH & Co. KG"],
    "definition": [{
        "default": {
            "brief": "Brief TODO.\n",
            "definition": "int ${.:name}",
            "description": None,
            "kind": "member",
            "name": "a"
        },
        "variants": []
    }, {
        "default": {
            "brief": "Brief TODO.\n",
            "definition": "int ${.:name}",
            "description": None,
            "kind": "member",
            "name": "b"
        },
        "variants": []
    }],
    "definition-kind":
    "struct-only",
    "description":
    "Description s_0.",
    "enabled-by":
    True,
    "index-entries": [],
    "interface-type":
    "struct",
    "links": [{
        "role": "interface-placement",
        "uid": "header-header"
    }, {
        "role": "interface-ingroup",
        "uid": "group"
    }],
    "name":
    "s_0",
    "notes":
    None,
    "type":
    "interface"
}

_GU_0_EXPECTED_RESULT = {
    "SPDX-License-Identifier":
    "CC-BY-SA-4.0 OR BSD-2-Clause",
    "brief":
    "Brief gu_0.",
    "copyrights": ["Copyright (C) 2024 embedded brains GmbH & Co. KG"],
    "definition": [{
        "default": {
            "brief": "Brief TODO.\n",
            "definition": "int ${.:name}",
            "description": None,
            "kind": "member",
            "name": "i"
        },
        "variants": []
    }, {
        "default": {
            "brief": "Brief TODO.\n",
            "definition": "float ${.:name}",
            "description": None,
            "kind": "member",
            "name": "f"
        },
        "variants": []
    }],
    "definition-kind":
    "typedef-only",
    "description":
    "Description gu_0.",
    "enabled-by":
    True,
    "index-entries": [],
    "interface-type":
    "union",
    "links": [{
        "role": "interface-placement",
        "uid": "header-header"
    }, {
        "role": "interface-ingroup",
        "uid": "group"
    }],
    "name":
    "gu_0",
    "notes":
    None,
    "type":
    "interface"
}

_U_0_EXPECTED_RESULT = {
    "SPDX-License-Identifier":
    "CC-BY-SA-4.0 OR BSD-2-Clause",
    "brief":
    "Brief u_0.",
    "copyrights": ["Copyright (C) 2024 embedded brains GmbH & Co. KG"],
    "definition": [{
        "default": {
            "brief": "Brief TODO.\n",
            "definition": "char ${.:name}",
            "description": None,
            "kind": "member",
            "name": "c"
        },
        "variants": []
    }, {
        "default": {
            "brief": "Brief TODO.\n",
            "definition": "int ${.:name}",
            "description": None,
            "kind": "member",
            "name": "i"
        },
        "variants": []
    }],
    "definition-kind":
    "typedef-only",
    "description":
    "Description u_0.",
    "enabled-by":
    True,
    "index-entries": [],
    "interface-type":
    "union",
    "links": [{
        "role": "interface-placement",
        "uid": "header-header"
    }, {
        "role": "interface-ingroup",
        "uid": "group"
    }],
    "name":
    "u_0",
    "notes":
    None,
    "type":
    "interface"
}

_GU_1_EXPECTED_RESULT = {
    "SPDX-License-Identifier":
    "CC-BY-SA-4.0 OR BSD-2-Clause",
    "brief":
    "Brief gu_1.",
    "copyrights": ["Copyright (C) 2024 embedded brains GmbH & Co. KG"],
    "definition": [{
        "default": {
            "brief": "Brief TODO.\n",
            "definition": "int ${.:name}",
            "description": None,
            "kind": "member",
            "name": "i"
        },
        "variants": []
    }, {
        "default": {
            "brief": "Brief TODO.\n",
            "definition": "float ${.:name}",
            "description": None,
            "kind": "member",
            "name": "f"
        },
        "variants": []
    }],
    "definition-kind":
    "union-only",
    "description":
    "Description gu_1.",
    "enabled-by":
    True,
    "index-entries": [],
    "interface-type":
    "union",
    "links": [{
        "role": "interface-placement",
        "uid": "header-header"
    }, {
        "role": "interface-ingroup",
        "uid": "group"
    }],
    "name":
    "gu_1",
    "notes":
    None,
    "type":
    "interface"
}

_U_1_EXPECTED_RESULT = {
    "SPDX-License-Identifier":
    "CC-BY-SA-4.0 OR BSD-2-Clause",
    "brief":
    "Brief u_1.",
    "copyrights": ["Copyright (C) 2024 embedded brains GmbH & Co. KG"],
    "definition": [{
        "default": {
            "brief": "Brief TODO.\n",
            "definition": "char ${.:name}",
            "description": None,
            "kind": "member",
            "name": "c"
        },
        "variants": []
    }, {
        "default": {
            "brief": "Brief TODO.\n",
            "definition": "int ${.:name}",
            "description": None,
            "kind": "member",
            "name": "i"
        },
        "variants": []
    }],
    "definition-kind":
    "union-only",
    "description":
    "Description u_1.",
    "enabled-by":
    True,
    "index-entries": [],
    "interface-type":
    "union",
    "links": [{
        "role": "interface-placement",
        "uid": "header-header"
    }, {
        "role": "interface-ingroup",
        "uid": "group"
    }],
    "name":
    "u_1",
    "notes":
    None,
    "type":
    "interface"
}

_GE_0_EXPECTED_RESULT = {
    "SPDX-License-Identifier":
    "CC-BY-SA-4.0 OR BSD-2-Clause",
    "brief":
    "Brief ge_0.",
    "copyrights": ["Copyright (C) 2024 embedded brains GmbH & Co. KG"],
    "definition-kind":
    "typedef-only",
    "description":
    "Description ge_0.",
    "enabled-by":
    True,
    "index-entries": [],
    "interface-type":
    "enum",
    "links": [{
        "role": "interface-placement",
        "uid": "header-header"
    }, {
        "role": "interface-ingroup",
        "uid": "group"
    }, {
        "role": "interface-enumerator",
        "uid": "ge-0-a"
    }, {
        "role": "interface-enumerator",
        "uid": "ge-0-b"
    }, {
        "role": "interface-enumerator",
        "uid": "ge-0-c"
    }],
    "name":
    "ge_0",
    "notes":
    None,
    "type":
    "interface"
}

_E_0_EXPECTED_RESULT = {
    "SPDX-License-Identifier":
    "CC-BY-SA-4.0 OR BSD-2-Clause",
    "brief":
    "Brief e_0.",
    "copyrights": ["Copyright (C) 2024 embedded brains GmbH & Co. KG"],
    "definition-kind":
    "typedef-and-enum",
    "description":
    "Description e_0.",
    "enabled-by":
    True,
    "index-entries": [],
    "interface-type":
    "enum",
    "links": [{
        "role": "interface-placement",
        "uid": "header-header"
    }, {
        "role": "interface-ingroup",
        "uid": "group"
    }, {
        "role": "interface-enumerator",
        "uid": "e-0-a"
    }],
    "name":
    "e_0",
    "notes":
    None,
    "type":
    "interface"
}

_E_1_EXPECTED_RESULT = {
    "SPDX-License-Identifier":
    "CC-BY-SA-4.0 OR BSD-2-Clause",
    "brief":
    "Brief e_1.",
    "copyrights": ["Copyright (C) 2024 embedded brains GmbH & Co. KG"],
    "definition-kind":
    "enum-only",
    "description":
    "Description e_1.",
    "enabled-by":
    True,
    "index-entries": [],
    "interface-type":
    "enum",
    "links": [{
        "role": "interface-placement",
        "uid": "header-header"
    }, {
        "role": "interface-ingroup",
        "uid": "group"
    }, {
        "role": "interface-enumerator",
        "uid": "e-1-a"
    }],
    "name":
    "e_1",
    "notes":
    None,
    "type":
    "interface"
}


def _enumvalue(name: str) -> dict:
    return {
        "SPDX-License-Identifier": "CC-BY-SA-4.0 OR BSD-2-Clause",
        "brief": f"Brief {name}.",
        "copyrights": [
            "Copyright (C) 2024 embedded brains GmbH & Co. KG",
        ],
        "definition": {
            "default": None,
            "variants": [],
        },
        "description": f"Description {name}.",
        "enabled-by": True,
        "index-entries": [],
        "interface-type": "enumerator",
        "links": [],
        "name": name,
        "notes": None,
        "type": "interface"
    }


_RESULTS = {
    "define": {
        "M_0": _M_0_EXPECTED_RESULT,
        "GM_0": _GM_0_EXPECTED_RESULT,
        "D_1": _D_1_EXPECTED_RESULT,
        "GD_1": _GD_1_EXPECTED_RESULT,
    },
    "enum": {
        "e_0": _E_0_EXPECTED_RESULT,
        "ge_0": _GE_0_EXPECTED_RESULT,
        "e_1": _E_1_EXPECTED_RESULT,
    },
    "enumvalue": {
        "GE_0_A": _enumvalue("GE_0_A"),
        "GE_0_B": _enumvalue("GE_0_B"),
        "GE_0_C": _enumvalue("GE_0_C"),
        "E_0_A": _enumvalue("E_0_A"),
        "E_1_A": _enumvalue("E_1_A")
    },
    "function": {
        "f_0": _F_0_EXPECTED_RESULT,
        "f_1": _F_1_EXPECTED_RESULT,
        "f_2": _F_2_EXPECTED_RESULT,
        "gf_0": _GF_0_EXPECTED_RESULT,
        "gf_1": _GF_1_EXPECTED_RESULT,
        "gf_2": _GF_2_EXPECTED_RESULT,
        "gf_3": _GF_3_EXPECTED_RESULT,
        "gf_4": _GF_4_EXPECTED_RESULT,
    },
    "group": {
        "FooGroup": _FOO_GROUP_EXPECTED_RESULT,
    },
    "file": {
        "header.h": _HEADER_H_EXPECTED_RESULT,
    },
    "struct": {
        "s_0": _S_0_EXPECTED_RESULT,
        "gs_0": _GS_0_EXPECTED_RESULT,
        "t_0": _T_0_EXPECTED_RESULT,
        "gt_0": _GT_0_EXPECTED_RESULT,
    },
    "union": {
        "u_0": _U_0_EXPECTED_RESULT,
        "gu_0": _GU_0_EXPECTED_RESULT,
        "u_1": _U_1_EXPECTED_RESULT,
        "gu_1": _GU_1_EXPECTED_RESULT,
    },
}


def test_null_item_to_group_is_treated_as_absent():
    config = {
        "data": {},
        "groups": {},
        "item-to-group": None,
        "spec-directory": "spec",
    }
    ctx = DoxygenContext(config)
    assert not ctx.item_to_group


def test_missing_spec_directory_defaults_but_explicit_value_is_respected():
    ctx = DoxygenContext({"data": {}, "groups": {}})
    assert ctx.spec_directory == Path("spec")

    # An explicit, if unusual, falsy value must not be silently replaced by
    # the default. Only an absent/null attribute should default.
    ctx_2 = DoxygenContext({"data": {}, "groups": {}, "spec-directory": ""})
    assert ctx_2.spec_directory == Path("")


def test_item_to_group_naming_unknown_group_raises_clear_error():
    xml_files = [
        _get_path("source-to-spec/xml/bad_8c.xml"),
        _get_path("source-to-spec/xml/default_8h.xml"),
        _get_path("source-to-spec/xml/header_8h.xml"),
        _get_path("source-to-spec/xml/foobar_8h.xml"),
        _get_path("source-to-spec/xml/group__DefaultGroup.xml"),
        _get_path("source-to-spec/xml/group__FooGroup.xml"),
        _get_path("source-to-spec/xml/source_8c.xml"),
        _get_path("source-to-spec/xml/structs__0.xml"),
        _get_path("source-to-spec/xml/structgs__0.xml"),
        _get_path("source-to-spec/xml/structt__0.xml"),
        _get_path("source-to-spec/xml/structgt__0.xml"),
        _get_path("source-to-spec/xml/unionu__0.xml"),
        _get_path("source-to-spec/xml/uniongu__0.xml"),
        _get_path("source-to-spec/xml/unionu__1.xml"),
        _get_path("source-to-spec/xml/uniongu__1.xml"),
    ]
    config = {
        "data": {},
        "groups": {
            "FooGroup": {
                "uid": "/if/group"
            }
        },
        "item-to-group": {
            "bad_8c_1a8cc687906d3e4964fc993ca1bf18472e": "NoSuchGroup"
        },
        "spec-directory": "spec",
    }
    ctx = DoxygenContext(config)
    with pytest.raises(ValueError,
                       match="cannot associate item .* with group "
                       "'NoSuchGroup'"):
        ctx.doxygen_xml_to_spec(xml_files)


def test_inline_commands_do_not_truncate_text():
    # inline-markup/inline.h's brief uses @a, @b, @c, @p and a line break,
    # each followed by more words: none of that trailing text must be
    # dropped, only the @a/@b/@c/@p markup itself needs not survive.
    config = {
        "data": {},
        "groups": {
            "InlineAPI": {
                "uid": "/if/group"
            }
        },
        "spec-directory": "spec",
    }
    ctx = DoxygenContext(config)
    ctx.doxygen_xml_to_spec([
        _get_path("source-to-spec/inline-markup/xml/group__InlineAPI.xml"),
        _get_path("source-to-spec/inline-markup/xml/inline_8h.xml"),
    ])
    brief = ctx.items_by_name["function"]["inline_use"][0].brief
    assert brief is not None
    for word in (
            "Sets",
            "w to a value, uses",
            "bold text, code",
            "text, and param",
            "references, followed by a break",
            "after the break, all with trailing words after each command.",
    ):
        assert word in brief, f"{word!r} missing from brief: {brief!r}"


def test_parameternamelist_does_not_leak_into_parameter_description():
    # <parameternamelist> is an unhandled wrapper around <parametername>
    # that shares its scope with the sibling <parameterdescription>: it
    # must not fall through to the generic tail-capturing fallback that
    # preserves inline-markup text, or its (whitespace) text/tail pollutes
    # every @param description.
    config = {
        "data": {},
        "groups": {
            "WidgetAPI": {
                "uid": "/if/group"
            }
        },
        "spec-directory": "spec",
    }
    ctx = DoxygenContext(config)
    ctx.doxygen_xml_to_spec([
        _get_path(
            "source-to-spec/null-item-to-group/xml/group__WidgetAPI.xml"),
        _get_path("source-to-spec/null-item-to-group/xml/widget_8h.xml"),
    ])
    item = ctx.items_by_name["function"]["widget_set_size"][0]
    # Deliberately not .strip()'d: the leak this guards against is a
    # leading "\n\n" that only a raw comparison would still catch, since
    # add_function_like_attributes() strips the final exported value
    # regardless of whether this fix is in place.
    description = item.data["param"][0]["description"]
    assert description == " is the pointer to the widget object.  "


def test_xrefsect_is_ignored():
    # @todo (and @bug, @deprecated, ...) render as <xrefsect>, which carries
    # its own labelled text (for example "Todo") via further unhandled
    # child tags.
    # It must be ignored outright rather than leaking into whatever
    # brief/description field is the ambient text scope at that point.
    config = {
        "data": {},
        "groups": {
            "TodoAPI": {
                "uid": "/if/group"
            }
        },
        "spec-directory": "spec",
    }
    ctx = DoxygenContext(config)
    ctx.doxygen_xml_to_spec([
        _get_path("source-to-spec/inline-markup/xml/group__TodoAPI.xml"),
        _get_path("source-to-spec/inline-markup/xml/todo_8h.xml"),
    ])
    item = ctx.items_by_name["function"]["todo_use"][0]
    assert item.brief == "Uses the widget after setup finishes."
    assert item.description is None


def test_append_element_text_ignores_wholly_empty_element():
    # An inline element with neither its own text nor a tail (for example
    # a <linebreak/> at the very end of a paragraph) must leave the
    # accumulated text untouched rather than appending an empty word.
    scope = _Scope(
        DoxygenItem(
            DoxygenContext({
                "data": {},
                "groups": {},
                "spec-directory": "spec",
            }), "root", "", ""), {"brief": "Existing text"}, "brief")
    elem = ElementTree.Element("linebreak")
    result = _append_element_text(elem, scope)
    assert result.data["brief"] == "Existing text"


def _types_api_xml_files() -> list[str]:
    return [
        _get_path(f"source-to-spec/typedef-generation/xml/{name}")
        for name in ("group__TypesAPI.xml", "types_8h.xml")
    ]


def test_typedef_export_shape():
    config = {
        "data": {},
        "groups": {
            "TypesAPI": {
                "uid": "/if/group"
            }
        },
        "spec-directory": "spec",
    }
    ctx = DoxygenContext(config)
    ctx.doxygen_xml_to_spec(_types_api_xml_files())
    widget_size_t = ctx.items_by_name["typedef"]["widget_size_t"][0]
    data = widget_size_t.export()
    assert data["interface-type"] == "typedef"
    assert data["params"] == []
    assert data["return"] is None
    assert data["definition"] == {
        "default": "_ImplementationDefined",
        "variants": []
    }
    # Placed like any other item, with relative links via its group, not
    # a flat root or absolute UIDs.
    assert widget_size_t.uid == "/if/widget-size-t"
    assert data["links"] == [{
        "role": "interface-placement",
        "uid": "header-types"
    }, {
        "role": "interface-ingroup",
        "uid": "group"
    }]


def test_typedef_aliases_compound():
    config = {
        "data": {},
        "groups": {
            "TypesAPI": {
                "uid": "/if/group"
            }
        },
        "spec-directory": "spec",
    }
    ctx = DoxygenContext(config)
    ctx.doxygen_xml_to_spec(_types_api_xml_files())
    typedefs = ctx.items_by_name["typedef"]
    assert typedefs["widget_size_t"][0].aliases_compound is False
    assert typedefs["widget_handle"][0].aliases_compound is False
    assert typedefs["tagged_enum"][0].aliases_compound is True


def _get_path(path: str) -> str:
    test_dir = Path(__file__).parent
    return str(test_dir / f"{path}")


def test_doxygen_xml_to_spec(tmp_path):
    xml_files = [
        _get_path("source-to-spec/xml/bad_8c.xml"),
        _get_path("source-to-spec/xml/default_8h.xml"),
        _get_path("source-to-spec/xml/header_8h.xml"),
        _get_path("source-to-spec/xml/foobar_8h.xml"),
        _get_path("source-to-spec/xml/group__DefaultGroup.xml"),
        _get_path("source-to-spec/xml/group__FooGroup.xml"),
        _get_path("source-to-spec/xml/source_8c.xml"),
        _get_path("source-to-spec/xml/structs__0.xml"),
        _get_path("source-to-spec/xml/structgs__0.xml"),
        _get_path("source-to-spec/xml/structt__0.xml"),
        _get_path("source-to-spec/xml/structgt__0.xml"),
        _get_path("source-to-spec/xml/unionu__0.xml"),
        _get_path("source-to-spec/xml/uniongu__0.xml"),
        _get_path("source-to-spec/xml/unionu__1.xml"),
        _get_path("source-to-spec/xml/uniongu__1.xml")
    ]
    config = {
        "data": {
            "copyrights": ["Copyright (C) 2024 embedded brains GmbH & Co. KG"]
        },
        "groups": {
            "FooGroup": {
                "uid": "/if/group",
                "remove-prefix": "foobar-"
            }
        },
        "type-map": {
            "gt_0": "${/gt_0:/name}"
        },
        "spec-directory": str(tmp_path)
    }
    ctx = DoxygenContext(config)
    ctx.doxygen_xml_to_spec(xml_files)
    for kind, name_result in _RESULTS.items():
        for name, result in name_result.items():
            assert result == ctx.items_by_name[kind][name][0].export()

    # Check union
    u_0 = ctx.items["unionu__0"]
    assert u_0 < ctx.items["unionu__1"]
    assert not u_0.is_header
    assert u_0.uid == "/if/u-0"
    u_0_file = tmp_path / "if" / "u-0.yml"
    assert not u_0_file.exists()
    u_0.save()
    assert u_0_file.is_file()

    # Check header
    header = ctx.items["header_8h"]
    assert header.is_header
    assert header.uid == "/if/header-header"
    foobar = ctx.items["foobar_8h"]
    assert foobar.is_header
    assert foobar.uid == "/if/header"
    source = ctx.items["source_8c"]
    assert not source.is_header
    assert source.uid == "/if/source-c"

    # Check bad function
    bad_f = ctx.items["bad_8c_1a8cc687906d3e4964fc993ca1bf18472e"]
    with pytest.raises(ValueError):
        bad_f.group
    assert not bad_f.is_header

    # Check default group association
    config["default-group-name"] = "DefaultGroup"
    config["item-to-group"] = {"bad_8c": "FooGroup"}
    ctx_2 = DoxygenContext(config)
    ctx_2.doxygen_xml_to_spec(xml_files)
    assert sorted(
        item.uid
        for item in ctx_2.items_by_name["group"]["DefaultGroup"][0].members()
        if item.kind == "file") == ["/header-default"]


def test_doxygen_context_treats_a_null_type_map_as_absent(tmp_path):
    # A bare 'type-map:' attribute in the configuration parses as null.
    # The attribute is optional, so validation lets it through, and it
    # then reaches _map_types() on every declaration.
    config = {
        "data": {},
        "groups": {
            "FooGroup": {
                "uid": "/if/group"
            }
        },
        "type-map": None,
        "spec-directory": str(tmp_path)
    }
    ctx = DoxygenContext(config)
    ctx.doxygen_xml_to_spec([
        _get_path("source-to-spec/xml/bad_8c.xml"),
        _get_path("source-to-spec/xml/default_8h.xml"),
        _get_path("source-to-spec/xml/header_8h.xml"),
        _get_path("source-to-spec/xml/foobar_8h.xml"),
        _get_path("source-to-spec/xml/group__DefaultGroup.xml"),
        _get_path("source-to-spec/xml/group__FooGroup.xml"),
        _get_path("source-to-spec/xml/source_8c.xml"),
        _get_path("source-to-spec/xml/structs__0.xml"),
        _get_path("source-to-spec/xml/structgs__0.xml"),
        _get_path("source-to-spec/xml/structt__0.xml"),
        _get_path("source-to-spec/xml/structgt__0.xml"),
        _get_path("source-to-spec/xml/unionu__0.xml"),
        _get_path("source-to-spec/xml/uniongu__0.xml"),
        _get_path("source-to-spec/xml/unionu__1.xml"),
        _get_path("source-to-spec/xml/uniongu__1.xml")
    ])
    for item in ctx.items.values():
        item.export()
    assert ctx.type_map == {}


_EXTRA_LINKS_XML_FILES = [
    "source-to-spec/xml/bad_8c.xml",
    "source-to-spec/xml/default_8h.xml",
    "source-to-spec/xml/header_8h.xml",
    "source-to-spec/xml/foobar_8h.xml",
    "source-to-spec/xml/group__DefaultGroup.xml",
    "source-to-spec/xml/group__FooGroup.xml",
    "source-to-spec/xml/source_8c.xml",
    "source-to-spec/xml/structs__0.xml",
    "source-to-spec/xml/structgs__0.xml",
    "source-to-spec/xml/structt__0.xml",
    "source-to-spec/xml/structgt__0.xml",
    "source-to-spec/xml/unionu__0.xml",
    "source-to-spec/xml/uniongu__0.xml",
    "source-to-spec/xml/unionu__1.xml",
    "source-to-spec/xml/uniongu__1.xml",
]


def _foo_group_context(tmp_path, **group):
    group.setdefault("uid", "/if/group")
    ctx = DoxygenContext({
        "data": {},
        "groups": {
            "FooGroup": group
        },
        "spec-directory": str(tmp_path)
    })
    ctx.doxygen_xml_to_spec(
        [_get_path(path) for path in _EXTRA_LINKS_XML_FILES])
    return ctx


def _extra_links_context(tmp_path, extra_links):
    if extra_links is None:
        return _foo_group_context(tmp_path)
    return _foo_group_context(tmp_path, **{"extra-links": extra_links})


def _saved_links(ctx, kind, name):
    item = ctx.items_by_name[kind][name][0]
    data = item.export()
    item.add_extra_links(data)
    return data["links"]


def test_a_bare_extra_links_attribute_adds_no_link(tmp_path):
    # A bare 'extra-links:' attribute parses as null.  Every attribute
    # of the configuration treats that as absent, so a run must not stop
    # on it.
    ctx = DoxygenContext({
        "data": {},
        "groups": {
            "FooGroup": {
                "uid": "/if/group",
                "extra-links": None
            }
        },
        "spec-directory": str(tmp_path)
    })
    ctx.doxygen_xml_to_spec(
        [_get_path(path) for path in _EXTRA_LINKS_XML_FILES])
    assert [link["role"] for link in _saved_links(ctx, "function", "gf_1")
            ] == ["interface-placement", "interface-ingroup"]


def test_extra_links_are_added_to_the_selected_interface_types(tmp_path):
    # The constraint link of a directive cannot be derived from the
    # source, but it must survive a regeneration.
    ctx = _extra_links_context(tmp_path, [{
        "role": "constraint",
        "uid": "/constraint/directive-ctx-any",
        "interface-types": ["function"]
    }])
    constraint = {"role": "constraint", "uid": "/constraint/directive-ctx-any"}
    assert constraint in _saved_links(ctx, "function", "gf_1")
    assert constraint not in _saved_links(ctx, "define", "GD_1")
    assert constraint not in _saved_links(ctx, "group", "FooGroup")


def test_extra_links_without_interface_types_apply_to_every_item(tmp_path):
    ctx = _extra_links_context(tmp_path, [{
        "role": "constraint",
        "uid": "/constraint/any"
    }])
    constraint = {"role": "constraint", "uid": "/constraint/any"}
    assert constraint in _saved_links(ctx, "function", "gf_1")
    assert constraint in _saved_links(ctx, "define", "GD_1")


def test_extra_links_are_absent_without_configuration(tmp_path):
    ctx = _extra_links_context(tmp_path, None)
    for link in _saved_links(ctx, "function", "gf_1"):
        assert link["role"] in ["interface-placement", "interface-ingroup"]


def test_saved_item_contains_the_extra_links(tmp_path):
    ctx = _extra_links_context(tmp_path, [{
        "role": "constraint",
        "uid": "/constraint/directive-ctx-any",
        "interface-types": ["function"]
    }])
    ctx.items_by_name["function"]["gf_1"][0].save()
    content = (tmp_path / "if" / "gf-1.yml").read_text(encoding="utf-8")
    assert "role: constraint" in content
    assert "uid: /constraint/directive-ctx-any" in content


@pytest.mark.parametrize("extra_links,expected", [
    ("not-a-list", "/groups/FooGroup/extra-links must be a list"),
    ([["role"]], "/groups/FooGroup/extra-links[0] must be a dict"),
    ([{
        "uid": "/constraint/x"
    }], "extra-links[0]/role is missing"),
    ([{
        "role": "constraint"
    }], "extra-links[0]/uid is missing"),
    ([{
        "role": 1,
        "uid": "/constraint/x"
    }], "extra-links[0]/role must be a string"),
    ([{
        "role": "constraint",
        "uid": "/constraint/x",
        "interface-types": "function"
    }], "extra-links[0]/interface-types must be a list"),
    ([{
        "role": "constraint",
        "uid": "/constraint/x",
        "interface-types": [1]
    }], "extra-links[0]/interface-types[0] must be a string"),
    ([{
        "role": "constraint",
        "uid": "/constraint/x",
        "names": "gf_*"
    }], "extra-links[0]/names must be a list"),
    ([{
        "role": "constraint",
        "uid": "/constraint/x",
        "names": [1]
    }], "extra-links[0]/names[0] must be a string"),
])
def test_invalid_extra_links_are_rejected(extra_links, expected):
    with pytest.raises(ValueError, match=re.escape(expected)):
        DoxygenContext({
            "data": {},
            "groups": {
                "FooGroup": {
                    "uid": "/if/group",
                    "extra-links": extra_links
                }
            },
            "spec-directory": "spec"
        })


_IN_BODY_MEMBERDEF = """<memberdef kind="function" id="m_0">
  <name>f</name>
  <briefdescription><para>Brief f().</para></briefdescription>
  <detaileddescription><para>Description f().</para></detaileddescription>
  <inbodydescription><para>Body comment of f().</para></inbodydescription>
</memberdef>"""


def _new_item():
    return DoxygenItem(
        DoxygenContext({
            "data": {},
            "groups": {},
            "spec-directory": "spec"
        }), "function", "m_0", "f")


def test_in_body_description_does_not_reach_the_documentation():
    # A comment inside a function body documents the implementation.  It
    # must not end up in the brief or the description, and it must not
    # crash the run through the text scope of the enclosing item, which
    # has no text key.
    item = _new_item()
    item.data["brief"] = ""
    item.data["description"] = ""
    scope = _Scope(item, item.data, "")
    for child in ElementTree.fromstring(_IN_BODY_MEMBERDEF).findall("*"):
        # pylint: disable=protected-access
        sourcetospec._fill_items(child, scope)
    assert "Brief f()." in item.data["brief"]
    assert "Description f()." in item.data["description"]
    assert "Body comment" not in item.data["brief"]
    assert "Body comment" not in item.data["description"]


def test_text_of_an_unhandled_container_is_dropped():
    # The ambient scope of an item has no text key.  A paragraph reaching
    # it belongs to no documented field and must not raise a KeyError.
    item = _new_item()
    scope = _Scope(item, item.data, "")
    # pylint: disable=protected-access
    result = sourcetospec._tag_add_text(
        ElementTree.fromstring("<para>Loose text.</para>"), scope)
    assert result is scope
    assert "" not in item.data


def test_extra_links_are_added_to_the_group_item_itself(tmp_path):
    # A group item carries the configuration of its own name.  Its link
    # to the design group is not derivable from the source.
    ctx = _extra_links_context(tmp_path, [{
        "role": "interface-ingroup",
        "uid": "../req/group",
        "interface-types": ["group"]
    }])
    assert {
        "role": "interface-ingroup",
        "uid": "../req/group"
    } in _saved_links(ctx, "group", "FooGroup")
    assert {
        "role": "interface-ingroup",
        "uid": "../req/group"
    } not in _saved_links(ctx, "function", "gf_1")


def _filter_context(tmp_path, rules):
    config = {
        "data": {},
        "groups": {
            "FooGroup": {
                "uid": "/if/group"
            }
        },
        "spec-directory": str(tmp_path)
    }
    if rules is not None:
        config["filter"] = rules
    ctx = DoxygenContext(config)
    ctx.doxygen_xml_to_spec(
        [_get_path(path) for path in _EXTRA_LINKS_XML_FILES])
    return ctx


def test_a_filter_excludes_an_item(tmp_path):
    ctx = _filter_context(tmp_path, [{"exclude": ["GD_1"]}])
    assert ctx.items_by_name["define"]["GD_1"][0].is_excluded
    assert not ctx.items_by_name["define"]["D_1"][0].is_excluded
    assert not ctx.items_by_name["function"]["gf_1"][0].is_excluded


def test_a_filter_pattern_is_an_fnmatch_pattern(tmp_path):
    ctx = _filter_context(tmp_path, [{"exclude": ["GD_*", "gf_[13]"]}])
    assert ctx.items_by_name["define"]["GD_1"][0].is_excluded
    assert ctx.items_by_name["function"]["gf_1"][0].is_excluded
    assert not ctx.items_by_name["function"]["gf_2"][0].is_excluded


def test_a_filter_pattern_is_case_sensitive(tmp_path):
    # A C identifier is case sensitive, so a pattern must not match a
    # declaration which merely differs in case.
    ctx = _filter_context(tmp_path, [{"exclude": ["gd_*"]}])
    assert not ctx.items_by_name["define"]["GD_1"][0].is_excluded


def test_the_first_matching_filter_rule_decides(tmp_path):
    ctx = _filter_context(tmp_path, [{
        "exclude": ["gf_2"]
    }, {
        "include": ["gf_*"]
    }, {
        "exclude": ["*"]
    }])
    assert not ctx.items_by_name["function"]["gf_1"][0].is_excluded
    assert ctx.items_by_name["function"]["gf_2"][0].is_excluded
    assert ctx.items_by_name["define"]["GD_1"][0].is_excluded


def test_an_item_no_filter_rule_matches_stays(tmp_path):
    for rules in [None, [], [{"exclude": ["nothing"]}]]:
        ctx = _filter_context(tmp_path, rules)
        assert not ctx.items_by_name["define"]["GD_1"][0].is_excluded


def test_a_filter_leaves_a_header_and_a_group_alone(tmp_path):
    # A header file and a group are structural rather than declarations,
    # so that an interface placement still resolves.
    ctx = _filter_context(tmp_path, [{"exclude": ["*"]}])
    assert not ctx.items_by_name["file"]["header.h"][0].is_excluded
    assert not ctx.items_by_name["group"]["FooGroup"][0].is_excluded
    assert ctx.items_by_name["function"]["gf_1"][0].is_excluded


def test_a_filter_must_be_a_list_of_one_action_rules(tmp_path):
    bad_rules = [
        "gf_*",
        ["gf_*"],
        [{
            "include": ["gf_*"],
            "exclude": ["gf_2"]
        }],
        [{
            "keep": ["gf_*"]
        }],
        [{}],
        [{
            "include": "gf_*"
        }],
        [{
            "include": [1]
        }],
    ]
    for bad in bad_rules:
        with pytest.raises(sourcetospec.ConfigError) as error:
            _filter_context(tmp_path, bad)
        assert "filter" in str(error.value), bad


def test_a_filter_error_names_its_attribute_path(tmp_path):
    # The rule which is wrong is named by its place in the
    # configuration, so that a filter of many rules needs no counting.
    with pytest.raises(sourcetospec.ConfigError) as error:
        _filter_context(tmp_path, [{"include": ["gf_*"]}, {"keep": ["gf_2"]}])
    assert "/filter[1] must have exactly one" in str(error.value)


def test_a_filter_pattern_error_names_its_attribute_path(tmp_path):
    # A pattern sits three levels down, so the path names the rule, the
    # action and the pattern to point at the one which is wrong.
    with pytest.raises(sourcetospec.ConfigError) as error:
        _filter_context(tmp_path, [{"include": ["gf_*", 7]}])
    assert "/filter[0]/include[1] must be a string" in str(error.value)


def _define_in_header(name, header_name, initializer=None):
    # Doxygen omits an undocumented include guard, so a guard only
    # reaches the generator when it carries a comment, as in the Xilinx
    # headers.  Build that shape directly.
    ctx = DoxygenContext({"data": {}, "groups": {}, "spec-directory": "spec"})
    header = sourcetospec.DoxygenFile(ctx, "file", "f_0", header_name)
    ctx.items["f_0"] = header
    define = sourcetospec.DoxygenDefine(ctx, "define", "d_0", name)
    if initializer is not None:
        define.data["initializer"] = initializer
    define.file_ids.add("f_0")
    ctx.items["d_0"] = define
    return define


def test_the_include_guard_of_a_header_is_excluded():
    guard = _define_in_header("XWDTPS_H", "xwdtps.h")
    assert guard.is_include_guard
    assert guard.is_excluded


def test_an_include_guard_of_a_nested_name_is_excluded():
    guard = _define_in_header("XWDTPS_HW_H", "xwdtps_hw.h")
    assert guard.is_include_guard


def test_a_guard_followed_by_a_comment_is_still_a_guard():
    # A guard is often written as `#define X /* why */` and Doxygen
    # reports the comment as the value of the define.
    for comment in ["/* by using protection macros */", "// guard", ""]:
        guard = _define_in_header("XUARTLITE_H",
                                  "xuartlite.h",
                                  initializer=comment)
        assert guard.is_include_guard, comment
        assert guard.is_excluded, comment


def test_a_define_with_a_value_is_not_an_include_guard():
    define = _define_in_header("XWDTPS_H", "xwdtps.h", initializer="1")
    assert not define.is_include_guard
    assert not define.is_excluded


def test_a_define_not_named_after_its_header_is_not_a_guard():
    define = _define_in_header("XWDTPS_ZMR_OFFSET", "xwdtps.h")
    assert not define.is_include_guard


def test_a_define_of_a_source_file_is_not_an_include_guard():
    define = _define_in_header("XWDTPS_C", "xwdtps.c")
    assert not define.is_include_guard


def test_a_define_without_a_file_is_not_an_include_guard():
    ctx = DoxygenContext({"data": {}, "groups": {}, "spec-directory": "spec"})
    define = sourcetospec.DoxygenDefine(ctx, "define", "d_0", "XWDTPS_H")
    assert not define.is_include_guard


def test_an_item_without_a_group_gets_no_extra_links():
    # An item which reached no group has no group configuration to take
    # extra links from.
    ctx = DoxygenContext({
        "data": {},
        "groups": {
            "FooGroup": {
                "uid": "/if/group",
                "extra-links": [{
                    "role": "constraint",
                    "uid": "/constraint/x"
                }]
            }
        },
        "spec-directory": "spec"
    })
    item = DoxygenItem(ctx, "function", "m_0", "f")
    data = {"links": [], "interface-type": "function"}
    item.add_extra_links(data)
    assert not data["links"]


def _header_item(tmp_path, **group):
    return _foo_group_context(tmp_path,
                              **group).items_by_name["file"]["header.h"][0]


def test_a_header_item_is_a_header_file_by_default(tmp_path):
    header = _header_item(tmp_path)
    assert header.header_interface_type == "header-file"
    data = header.export()
    assert data["interface-type"] == "header-file"
    assert data["path"] == "header.h"
    assert data["prefix"] == ""
    assert "references" not in data
    for key in ("brief", "description", "notes"):
        assert key in data


def test_an_unspecified_header_item_specifies_no_content(tmp_path):
    # The header itself is the source of truth, so the item carries
    # neither documentation nor a prefix of its own.
    header = _header_item(
        tmp_path, **{"header-interface-type": "unspecified-header-file"})
    assert header.header_interface_type == "unspecified-header-file"
    data = header.export()
    assert data["interface-type"] == "unspecified-header-file"
    assert data["path"] == "header.h"
    assert data["references"] == []
    for key in ("brief", "description", "notes", "prefix", "name"):
        assert key not in data


def test_extra_links_select_an_unspecified_header_file(tmp_path):
    # The interface placement of an unspecified header file is not
    # derivable from the source and comes from the configuration.
    ctx = _foo_group_context(
        tmp_path, **{
            "header-interface-type":
            "unspecified-header-file",
            "extra-links": [{
                "role": "interface-placement",
                "uid": "/dev/if/domain",
                "interface-types": ["unspecified-header-file"]
            }]
        })
    placement = {"role": "interface-placement", "uid": "/dev/if/domain"}
    assert placement in _saved_links(ctx, "file", "header.h")
    assert placement not in _saved_links(ctx, "function", "gf_1")


def _undocumented_header_named(name, **group):
    """ Build an undocumented header file item of the FooGroup. """
    group.setdefault("uid", "/if/group")
    ctx = DoxygenContext({
        "data": {},
        "groups": {
            "FooGroup": group
        },
        "spec-directory": "spec"
    })
    ctx.items["g_0"] = sourcetospec.DoxygenGroup(ctx, "group", "g_0",
                                                 "FooGroup")
    header = sourcetospec.DoxygenFile(ctx, "file", "f_0", name)
    header.group_ids.append("g_0")
    ctx.items["f_0"] = header
    return header


def _undocumented_header(**group):
    return _undocumented_header_named("some.h", **group)


def test_a_header_named_after_its_directory_is_the_header_of_it():
    header = _undocumented_header_named("foo.h", uid="/dev/foo/if/group")
    assert header.uid == "/dev/foo/if/header"


def test_a_header_named_after_no_directory_keeps_its_name():
    # The name occurs in the directory /if as the letter of "if", so a
    # substring test made this header the header of that directory.
    assert _undocumented_header_named("f.h").uid == "/if/header-f"


def test_an_undocumented_header_file_needs_a_brief():
    assert _undocumented_header().review_gaps == ["placeholder brief"]


def test_an_unspecified_header_file_has_no_brief_to_complete():
    # The item type has no brief attribute, so there is nothing for a
    # human to write here.
    header = _undocumented_header(
        **{"header-interface-type": "unspecified-header-file"})
    assert not header.review_gaps


def _foo_group(tmp_path, **group):
    return _foo_group_context(tmp_path,
                              **group).items_by_name["group"]["FooGroup"][0]


def test_a_group_item_is_generated_by_default(tmp_path):
    assert _foo_group(tmp_path).generate_item


def test_the_group_item_generation_can_be_suppressed(tmp_path):
    assert not _foo_group(tmp_path, **{
        "generate-group-item": False
    }).generate_item


@pytest.mark.parametrize("entry,expected", [
    ({
        "generate-group-item": "yes"
    }, "/groups/FooGroup/generate-group-item must be a boolean"),
    ({
        "header-interface-type": "source-file"
    }, "/groups/FooGroup/header-interface-type must be"),
    ({
        "header-interface-type": 1
    }, "/groups/FooGroup/header-interface-type must be"),
    ({
        "data": []
    }, "/groups/FooGroup/data must be a dict or null"),
])
def test_invalid_group_settings_are_rejected(entry, expected):
    with pytest.raises(ValueError, match=expected):
        DoxygenContext({
            "data": {},
            "groups": {
                "FooGroup": dict(entry, uid="/if/group")
            },
            "spec-directory": "spec"
        })


def _group_filter_context(tmp_path, group_rules, config_rules=None):
    group: dict = {"uid": "/if/group"}
    if group_rules is not None:
        group["filter"] = group_rules
    config: dict = {
        "data": {},
        "groups": {
            "FooGroup": group
        },
        "spec-directory": str(tmp_path)
    }
    if config_rules is not None:
        config["filter"] = config_rules
    ctx = DoxygenContext(config)
    ctx.doxygen_xml_to_spec(
        [_get_path(path) for path in _EXTRA_LINKS_XML_FILES])
    return ctx


def test_a_group_filter_selects_the_items_of_its_group(tmp_path):
    ctx = _group_filter_context(tmp_path, [{
        "include": ["gf_*"]
    }, {
        "exclude": ["*"]
    }])
    assert not ctx.items_by_name["function"]["gf_1"][0].is_excluded
    assert ctx.items_by_name["define"]["GD_1"][0].is_excluded
    assert ctx.items_by_name["struct"]["gs_0"][0].is_excluded


def test_a_group_filter_leaves_another_group_alone(tmp_path):
    ctx = _group_filter_context(tmp_path, [{"exclude": ["*"]}])
    assert not ctx.items_by_name["function"]["bad_f"][0].is_excluded


def test_the_configured_filter_is_evaluated_before_the_group_one(tmp_path):
    # The precedence is the order of the rules, so a configured rule
    # which matches decides even when the group would include the item.
    ctx = _group_filter_context(tmp_path, [{
        "include": ["GD_1"]
    }], [{
        "exclude": ["GD_1"]
    }])
    assert ctx.items_by_name["define"]["GD_1"][0].is_excluded


def test_the_group_filter_decides_what_the_configured_one_skips(tmp_path):
    ctx = _group_filter_context(tmp_path, [{
        "exclude": ["GD_1"]
    }], [{
        "exclude": ["nothing"]
    }])
    assert ctx.items_by_name["define"]["GD_1"][0].is_excluded
    assert not ctx.items_by_name["define"]["D_1"][0].is_excluded


def test_an_item_is_kept_without_a_group_filter(tmp_path):
    for rules in [None, []]:
        ctx = _group_filter_context(tmp_path, rules)
        assert not ctx.items_by_name["define"]["GD_1"][0].is_excluded


def test_a_group_filter_leaves_a_header_and_a_group_alone(tmp_path):
    ctx = _group_filter_context(tmp_path, [{"exclude": ["*"]}])
    assert not ctx.items_by_name["file"]["header.h"][0].is_excluded
    assert not ctx.items_by_name["group"]["FooGroup"][0].is_excluded


def test_a_group_filter_must_be_a_list_of_one_action_rules(tmp_path):
    for bad in ["gf_*", [{"keep": ["gf_*"]}], [{"include": "gf_*"}]]:
        with pytest.raises(sourcetospec.ConfigError) as error:
            _group_filter_context(tmp_path, bad)
        assert "filter" in str(error.value), bad


def test_a_group_filter_error_names_its_attribute_path(tmp_path):
    # The path names the group as well, so that a configuration of many
    # groups says which filter is wrong.
    with pytest.raises(sourcetospec.ConfigError) as error:
        _group_filter_context(tmp_path, [{
            "include": ["gf_*"]
        }, {
            "keep": ["gf_2"]
        }])
    assert "/groups/FooGroup/filter[1] must have exactly one" in str(
        error.value)


def test_a_compound_resolves_a_referenced_member():
    # Doxygen documents the member of a struct in the compound of the
    # group when the declaration is inside a group scope, and leaves a
    # reference behind in the compound of the struct.
    xml = ElementTree.fromstring("""<compounddef id="structFoo" kind="struct">
      <compoundname>Foo</compoundname>
      <sectiondef kind="public-attrib">
        <member refid="group__g_1ga0" kind="variable"><name>a</name></member>
        <member refid="group__g_1ga1" kind="variable"><name>b</name></member>
      </sectiondef>
      <listofallmembers>
        <member refid="group__g_1ga0"><name>a</name></member>
      </listofallmembers>
    </compounddef>""")
    ctx = DoxygenContext({"data": {}, "groups": {}, "spec-directory": "spec"})
    item = sourcetospec.DoxygenStruct(ctx, "struct", "structFoo", "Foo")
    sourcetospec._compound_relationships(xml, item)
    # The list of all members repeats every member, so following it too
    # would add one of them twice.
    assert item.member_ids == ["group__g_1ga0", "group__g_1ga1"]


def test_a_compound_with_an_inline_member_gains_nothing():
    # A member definition placed in the section is picked up by the
    # scope while it is parsed, so the handler must leave it alone.
    xml = ElementTree.fromstring("""<compounddef id="structFoo" kind="struct">
      <compoundname>Foo</compoundname>
      <sectiondef kind="public-attrib">
        <memberdef kind="variable" id="structFoo_1a0"><name>a</name></memberdef>
      </sectiondef>
    </compounddef>""")
    ctx = DoxygenContext({"data": {}, "groups": {}, "spec-directory": "spec"})
    item = sourcetospec.DoxygenStruct(ctx, "struct", "structFoo", "Foo")
    sourcetospec._compound_relationships(xml, item)
    assert item.member_ids == []


def _macro_params_context():
    ctx = DoxygenContext({
        "data": {},
        "groups": {
            "MacroAPI": {
                "uid": "/if/group"
            }
        },
        "spec-directory": "spec"
    })
    ctx.doxygen_xml_to_spec([
        _get_path(f"source-to-spec/macro-params/xml/{name}")
        for name in ("group__MacroAPI.xml", "macro_8h.xml")
    ])
    return ctx


def _macro_params(ctx, kind, name):
    return ctx.items_by_name[kind][name][0].export()["params"]


def test_a_partly_documented_macro_keeps_its_parameters():
    # Doxygen counts the ... of a variadic macro as a parameter and a
    # vendor rarely documents it.  A macro parameter carries a defname
    # and no type at all.
    params = _macro_params(_macro_params_context(), "define", "MACRO_LOG")
    assert params == [{
        "description": "is the log level.",
        "dir": None,
        "name": "level"
    }, {
        "description": None,
        "dir": None,
        "name": "..."
    }]


def test_one_documentation_block_documents_every_name_it_lists():
    params = _macro_params(_macro_params_context(), "define", "MACRO_MAX")
    assert [param["description"] for param in params
            ] == ["are the two operands.", "are the two operands."]


def test_the_declaration_orders_the_parameters():
    # The documentation blocks come in the reverse order here, so a
    # positional pairing would swap the two descriptions.
    params = _macro_params(_macro_params_context(), "define", "MACRO_ADD")
    assert [(param["name"], param["description"])
            for param in params] == [("a", "is the first operand."),
                                     ("b", "is the second operand.")]


def test_a_documentation_block_of_no_parameter_is_a_stray():
    ctx = _macro_params_context()
    item = ctx.items_by_name["function"]["macro_store"][0]
    assert _macro_params(ctx, "function", "macro_store") == [{
        "description": "is the value to store.",
        "dir": None,
        "name": "value"
    }]
    assert item.review_gaps == ["stray param doc: slot"]


def test_an_unnamed_parameter_takes_the_documented_name():
    # A prototype may name none of its parameters, so the
    # documentation is the only source of a name for them.
    params = _macro_params(_macro_params_context(), "function",
                           "macro_set_size")
    assert [(param["name"], param["description"])
            for param in params] == [("width", "is the width."),
                                     ("height", "is the height.")]


def test_a_retval_block_documents_every_name_it_lists():
    xml = ElementTree.fromstring("""<memberdef kind="function" id="f_0">
      <name>f_0</name>
      <type>int</type>
      <detaileddescription><para><parameterlist kind="retval">
      <parameteritem>
      <parameternamelist>
      <parametername>0</parametername>
      <parametername>1</parametername>
      </parameternamelist>
      <parameterdescription><para>Nothing happens.</para></parameterdescription>
      </parameteritem>
      </parameterlist></para></detaileddescription>
    </memberdef>""")
    ctx = DoxygenContext({"data": {}, "groups": {}, "spec-directory": "spec"})
    item = sourcetospec.DoxygenFunction(ctx, "function", "f_0", "f_0")
    ctx.items["f_0"] = item
    sourcetospec._fill_items(xml, sourcetospec._Scope(item, {}, ""))
    data: dict = {}
    item.add_function_like_attributes("function", data)
    assert data["return"]["return-values"] == [{
        "description": "Nothing happens.",
        "value": "0"
    }, {
        "description": "Nothing happens.",
        "value": "1"
    }]


def test_a_typedef_of_a_function_pointer_has_no_stray_param_doc():
    # The item specifies no parameter of the function it points to, so
    # every documented name of it would count as a stray.
    ctx = DoxygenContext({
        "data": {},
        "groups": {
            "TypesAPI": {
                "uid": "/if/group"
            }
        },
        "spec-directory": "spec"
    })
    ctx.doxygen_xml_to_spec([
        _get_path(f"source-to-spec/typedef-generation/xml/{name}")
        for name in ("group__TypesAPI.xml", "types_8h.xml")
    ])
    item = ctx.items_by_name["typedef"]["widget_handler"][0]
    assert item.export()["params"] == []
    assert item.review_gaps == []


def test_an_empty_parameter_name_documents_nothing():
    # An empty <parametername> names no parameter, so it must not
    # become a parameter of the item under an empty name.
    xml = ElementTree.fromstring("""<memberdef kind="function" id="f_0">
      <name>f_0</name>
      <type>void</type>
      <param><type>int</type><declname>a</declname></param>
      <detaileddescription><para><parameterlist kind="param">
      <parameteritem>
      <parameternamelist>
      <parametername></parametername>
      <parametername>a</parametername>
      </parameternamelist>
      <parameterdescription><para>is the operand.</para></parameterdescription>
      </parameteritem>
      </parameterlist></para></detaileddescription>
    </memberdef>""")
    ctx = DoxygenContext({"data": {}, "groups": {}, "spec-directory": "spec"})
    item = sourcetospec.DoxygenFunction(ctx, "function", "f_0", "f_0")
    ctx.items["f_0"] = item
    sourcetospec._fill_items(xml, sourcetospec._Scope(item, {}, ""))
    data: dict = {}
    item.add_function_like_attributes("function", data)
    assert data["params"] == [{
        "description": "is the operand.",
        "dir": None,
        "name": "a"
    }]
    assert item._stray_param_docs(data) == []


def _copyrights(ctx, kind, name):
    return ctx.items_by_name[kind][name][0].export()["copyrights"]


def _group_data_context(tmp_path, **groups):
    ctx = DoxygenContext({
        "data": {
            "copyrights": ["Copyright (C) 2026 Everyone"],
            "enabled-by": "SOMETHING"
        },
        "groups": groups,
        "spec-directory": str(tmp_path)
    })
    ctx.doxygen_xml_to_spec(
        [_get_path(path) for path in _EXTRA_LINKS_XML_FILES])
    return ctx


def test_the_data_of_a_group_applies_to_its_items(tmp_path):
    # A generated item copies the prose of its header, so it carries
    # the copyright of that header and not the copyright of every
    # header of the run.
    ctx = _group_data_context(
        tmp_path, **{
            "FooGroup": {
                "uid": "/if/group",
                "data": {
                    "copyrights": ["Copyright (C) 2026 Foo"]
                }
            },
            "DefaultGroup": {
                "uid": "/other/group"
            }
        })
    assert _copyrights(ctx, "function", "gf_1") == ["Copyright (C) 2026 Foo"]
    assert _copyrights(ctx, "group",
                       "DefaultGroup") == ["Copyright (C) 2026 Everyone"]


def test_a_group_inherits_what_its_data_leaves_out(tmp_path):
    ctx = _group_data_context(
        tmp_path, **{
            "FooGroup": {
                "uid": "/if/group",
                "data": {
                    "copyrights": ["Copyright (C) 2026 Foo"]
                }
            }
        })
    assert ctx.items_by_name["function"]["gf_1"][0].export(
    )["enabled-by"] == "SOMETHING"


def test_the_data_of_a_group_applies_to_the_group_item(tmp_path):
    ctx = _group_data_context(
        tmp_path, **{
            "FooGroup": {
                "uid": "/if/group",
                "data": {
                    "copyrights": ["Copyright (C) 2026 Foo"]
                }
            }
        })
    assert _copyrights(ctx, "group", "FooGroup") == ["Copyright (C) 2026 Foo"]


def test_extra_links_are_added_to_the_selected_names(tmp_path):
    # A call context constraint holds for one function of a group and
    # not for the next, so the interface type alone cannot address it.
    ctx = _extra_links_context(tmp_path, [{
        "role": "constraint",
        "uid": "/constraint/directive-ctx-any",
        "names": ["gf_1", "gf_3"]
    }])
    constraint = {"role": "constraint", "uid": "/constraint/directive-ctx-any"}
    assert constraint in _saved_links(ctx, "function", "gf_1")
    assert constraint in _saved_links(ctx, "function", "gf_3")
    assert constraint not in _saved_links(ctx, "function", "gf_2")


def test_a_name_pattern_of_an_extra_link_is_case_sensitive(tmp_path):
    # A C identifier is case sensitive, so gf_1 and GF_1 are two
    # different declarations.
    ctx = _extra_links_context(tmp_path, [{
        "role": "constraint",
        "uid": "/constraint/any",
        "names": ["GF_*"]
    }])
    constraint = {"role": "constraint", "uid": "/constraint/any"}
    assert constraint not in _saved_links(ctx, "function", "gf_1")


def test_both_selectors_of_an_extra_link_must_match(tmp_path):
    ctx = _extra_links_context(tmp_path, [{
        "role": "constraint",
        "uid": "/constraint/any",
        "interface-types": ["define"],
        "names": ["gf_*"]
    }])
    constraint = {"role": "constraint", "uid": "/constraint/any"}
    assert constraint not in _saved_links(ctx, "function", "gf_1")
    assert constraint not in _saved_links(ctx, "define", "GD_1")


@pytest.mark.parametrize("name,interface_type,params", [
    ("MACRO_MIN", "macro", ["a", "b"]),
    ("MACRO_NOP", "macro", []),
    ("MACRO_COUNT", "define", None),
])
def test_the_declaration_decides_a_function_like_define(
        name, interface_type, params):
    # MACRO_MIN carries a brief and no documented parameter, which is
    # how a vendor documents most of its macros.  MACRO_NOP writes an
    # empty parameter list, which Doxygen reports as a parameter of
    # neither a name nor a type.
    ctx = _macro_params_context()
    data = ctx.items_by_name["define"][name][0].export()
    assert data["interface-type"] == interface_type
    if params is None:
        assert "params" not in data
    else:
        assert [param["name"] for param in data["params"]] == params


def test_a_define_of_a_brief_alone_reports_its_parameters():
    ctx = _macro_params_context()
    item = ctx.items_by_name["define"]["MACRO_MIN"][0]
    assert item.review_gaps == ["undocumented params"]
    assert item.export()["definition"]["default"]["params"] == [
        "${.:/params[0]/name}", "${.:/params[1]/name}"
    ]
