#!/usr/bin/env python
## @ SingleSign.py
# Single signing script
#
# Copyright (c) 2020, Intel Corporation. All rights reserved.<BR>
# SPDX-License-Identifier: BSD-2-Clause-Patent
#
##

##
# Import Modules
#
import os
import sys


def get_fsp_name_from_path (bsf_file):
    name = 'Soc'
    parts = bsf_file.split(os.sep)
    for part in parts:
        if part.endswith ('FspBinPkg'):
            name = part[:-9]
            break
    return name

print (get_fsp_name_from_path (sys.argv[1]))
