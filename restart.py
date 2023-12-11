#!/usr/bin/env python
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

# This script runs a restart test according to SP800-90B

import os 
import sys
import tempfile
import time

# This script needs to be run as root

if os.geteuid() != 0:
    sys.stderr.write("This script needs to be run as root\n")
    sys.exit(1)

SYNTAX = f"{sys.argv[0]} <bits to extract> <output filename>\n"

if len(sys.argv) < 3:
    sys.stderr.write(SYNTAX)
    sys.exit(1)

bits_to_extract = int(sys.argv[1])
outfilename = sys.argv[2]

if bits_to_extract not in [1,2,4,8]:
    sys.stderr.write("The number of bits to extract must be either 1, 2, 4 or 8\n")
    sys.exit(1)

o = open(outfilename, "wb")

# Ensure the module is not loaded
os.system("rmmod deltats")

# Start to collect noise
sys.stderr.write("Start noise collection in 3 seconds\n")
time.sleep(3)

# Run extractor to extract noisy data
for _ in range(1000):
    os.system("insmod ./deltats.ko")
    sleepns = open("/sys/kernel/deltats/sleepns", "wt")
    sleepns.write("0")
    sleepns.close()
    tf = tempfile.NamedTemporaryFile('w+b')
    os.system(f"python3 extractor.py {bits_to_extract} 1000 0 {tf.name} delta > /dev/null 2> /dev/null")
    tf.seek(0) 
    o.write(tf.read())
    tf.close()
    os.system("rmmod deltats")
