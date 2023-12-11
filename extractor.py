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

import sys
import os
import time
from math import log2

SYNTAX = f"{sys.argv[0]} <bits_to_extract> <samples> <time_to_sleep_microseconds> <output_filename> <ticks|delta>\n"

if len(sys.argv) != 6:
    sys.stderr.write(SYNTAX)
    sys.exit(1)

maskbits = int(sys.argv[1])    # How many bits should we extract from the number? -1 means all
samples = int(sys.argv[2])
usleep = int(sys.argv[3])
mask = (1<<maskbits) - 1 if maskbits > 0 else -1


f = '/sys/kernel/deltats/ticks'
bits = 32    # How many decimal digits is the number returned expected to have
outfile = sys.argv[4]
out = open(outfile, "wb")
if sys.argv[5].lower() == "ticks":
    delta = False
elif sys.argv[5].lower() == "delta":
    delta = True
else:
    sys.stderr.write(SYNTAX)
    sys.exit(1)

for _ in range(samples):
    D = 0
    lastn = -1
    for i in range(delta+1):
        e = os.open(f, os.O_RDONLY)
        n = os.read(e, 32)
        n = n.decode("utf-8")
        n = int(n)
        if delta and lastn == -1:
            lastn = n
        elif delta and lastn > 0:
            D = n - lastn
        else:
            D = n
        os.close(e)
    
    try:
        gg = (int(log2(D & mask)) + 1)
    except:
        gg = 1

    out.write((D & mask).to_bytes(length=max(maskbits >> 3 if maskbits > 0 else gg // 8 + (1 if gg % 8 > 0 else 0), 1), byteorder='big'))

    if usleep != 0:
        time.sleep(usleep/1000000.)
