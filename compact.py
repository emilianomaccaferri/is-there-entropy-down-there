#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) Gianmarco Lusvardi, 2023
#
# This software has been produced in fulfilment of the requirements of the
# kernel hacking university exam
#
# THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY APPLICABLE
# LAW. EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT HOLDER PROVIDE THE
# PROGRAM "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS FOR A PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE QUALITY AND
# PERFORMANCE OF THE PROGRAM IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE,
# YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR OR CORRECTION.  
#
# IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING WILL
# ANY COPYRIGHT HOLDER, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY GENERAL,
# SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OR
# INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR
# DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES OR
# A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF SUCH
# HOLDER HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.  
#
# If the disclaimer of warranty and limitation of liability provided above
# cannot be given local legal effect according to their terms, reviewing courts
# shall apply local law that most closely approximates an absolute waiver of
# all civil liability in connection with the Program, unless a warranty or
# assumption of liability accompanies a copy of the Program in return for a
# fee.


# This script takes 4-bit deltas and put every delta in an 8-bit number.
# For instance, it converts the two bytes 05 0a into 5a

import sys

SYNTAX = f"{sys.argv[0]} <filename> <output filename>\n"
if len(sys.argv) != 3:
    sys.stderr.write(SYNTAX)
    sys.exit(1)

filename = sys.argv[1]
output = sys.argv[2]

f = open(filename, "rb")
o = open(output, "wb")

r = 0
rn = 0

while len(n := f.read(1)) > 0:
    nn = int.from_bytes(n, 'big')
    if rn == 0:
        r |= nn
        rn += 1
    else:
        r = (r << 4) | nn
        o.write(r.to_bytes(1, 'big'))
        rn = 0
        r = 0
