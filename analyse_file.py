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
import matplotlib.pyplot as plt
import numpy as np
from math import log2

SYNTAX = f"{sys.argv[0]} <length of a word in bits> <filename> <whole length: true|false>"
bitlen = int(sys.argv[1])
filename = sys.argv[2]
whole_length = True if sys.argv[3].lower() == "true" else False

if not int(log2(bitlen)) == log2(bitlen) or bitlen < 1 or bitlen > 8:
    sys.stderr.write(f"{bitlen} is not a power of 2 or is invalid\n")
    sys.exit(1)

f = open(filename, 'rb')
l = []
masks = {1: 0x80, 2: 0xC0, 4: 0xF0, 8: 0xFF}

while (len(r := f.read(1)) > 0):
    cr = int.from_bytes(r, 'big')    # Copy r

    if whole_length:
        mask = (1<<bitlen) - 1
        l.append(cr & mask)
    else: 
        cm = masks[bitlen]
        loops = int(8 / bitlen)
        for b in range(loops-1,-1,-1):
           cn = cr & cm
           l.append(cn >> b)
           cm >>= bitlen


# Compute Shannon's entropy
la = np.array(l)
dn = {i: la[la == i].shape[0] for i in range(1<<bitlen)}

ent = -sum([(dn[i] / len(l)) * (log2(dn[i] / len(l)) if dn[i] != 0 else 0) for i in dn])
ment = -log2(max([dn[i] / len(l) for i in dn]))

print(f"Shannon entropy: {ent}")
print(f"Min-entropy: {ment}")

plt.bar(list(dn.keys()), list(dn.values()))
plt.show()
