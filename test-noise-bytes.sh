#!/bin/bash
#
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

# This test is for computing the entropy in each byte of the computed delta.

SYNTAX="$0 <repetitions> <samples per test> <output directory>"

if [ $# -ne 3 ]; then
    >&2 echo "$SYNTAX"
    exit 1
fi

if [ "$EUID" -ne 0 ]; then
    echo "This script must be run as root"
    exit 1
fi

REP=$1
SAMPLES=$2
OUTPUT=$3

# Make sure the kernel module is running
if [ ! -d "/sys/kernel/deltats" ]; then
    insmod ./deltats.ko
fi

if [ ! -d "/sys/kernel/deltats" ]; then
    >&2 echo "Unable to start kernel module"
    exit 1
fi

echo "0" > /sys/kernel/deltats/sleepns

>&2 echo "Starting entropy collection in 3 seconds"
sleep 3
>&2 echo "Starting entropy collection"

for i in $(seq 1 $REP)
do
    python3 extractor.py 24 $SAMPLES 0 $OUTPUT/$i.bin delta
    >&2 echo "Entropy collected for $i-th sample"
done

# Splitting files into subfiles
for i in $(seq 1 $REP)
do
    python3 splitter.py 3 "$OUTPUT/$i.bin" "$i-"
done

# Now call ea_non_iid on all the created files
for i in $(seq 0 2); do
    min=1000
    max=0
    sum=0
    for j in $(seq 1 $REP); do
        out=$(./ea_non_iid $OUTPUT/$j-$i.bin | grep -Po "(?<=min\(H_original, 8 X H_bitstring\): )[\d\.]+")
        if [ -z $out ]; then
            out=0
        fi

        if (( $(echo "$out < $min" | bc -l) )); then
            min=$out
        fi
        if (( $(echo "$out > $max" | bc -l) )); then
            max=$out
        fi
        sum=$(bc -l <<< $sum+$out)
    done
    echo "(min, max, avg) entropy for $i-th byte: ($min, $max, $(bc -l <<< $sum/$REP))"
done
