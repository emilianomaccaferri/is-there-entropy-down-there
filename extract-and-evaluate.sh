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
#
#
# This script extracts random bits using the kernel module and the python
# scripts and then splits the different bytes of the results in different files
# so that they can be analysed by the NIST SP800-90B standard.
#
# This script should be run as root

# Extract parameters

SYNTAX="$0 <bits to extract> <samples> <output filename>"

if [ $# -lt 3 ]; then
    >&2 echo $SYNTAX
    exit 1
fi

BITS_TO_EXTRACT=$1
SAMPLES=$2
OUTPUT_FILENAME=$3

if [ ${BITS_TO_EXTRACT:0:1} = '-' -o ${SAMPLES:0:1} = '-' -o ${OUTPUT_FILENAME:0:1} = '-' ]; then
    >&2 echo $SYNTAX
    exit 1
fi

case $SAMPLES in
    ''|*[!0-9]*) >&2 echo $SYNTAX; exit 1 ;;
    *) ;;
esac

case $BITS_TO_EXTRACT in
    ''|*[!0-9]*) >&2 echo $SYNTAX; exit 1 ;;
    *) ;;
esac

if [ $BITS_TO_EXTRACT -le 8 ]; then
    >&2 echo "This script should collect more than 8 bits to do some useful work"
    exit 1
fi

if [ ! $EUID -eq 0 ]; then
    >&2 echo "This script should be run as root"
    exit 1
fi

SYNC=0
PID=0

if [ $# -gt 4 ]; then
    shift
    shift
    shift
    while [ $# -gt 0 ]; do
        if [ $1 = "-prefix" ]; then
            shift
            PREFIX=$1
            >&2 echo "Prefix set to $PREFIX"
            shift
        elif [ $1 = "-sync" ]; then
            SYNC=1
            trap 'SYNC=2' USR1
            >&2 echo "Set sync. PID = $$"
            shift
        elif [ $1 = "-pid" ]; then
            shift
            PID=$1
            >&2 echo "Will kill PID $PID when ready"
            shift
        fi
    done
else
    PREFIX="f"
fi

TOTAL_FILES=$(( (BITS_TO_EXTRACT + 7) / 8 ))


# Make sure the kernel module is running

if [ ! -d "/sys/kernel/deltats" ]; then
    insmod ./deltats.ko
fi

if [ ! -d "/sys/kernel/deltats" ]; then
    >&2 echo "Unable to start kernel module"
    exit 1
fi

echo "0" > /sys/kernel/deltats/sleepns

if [ $SYNC -eq 0 ]; then
    >&2 echo "Starting collection in 3 seconds"
    sleep 3
    >&2 echo "Starting entropy collection"
    if [ $PID -ne 0 ]; then
        kill -SIGUSR1 $PID
    fi
else
    >&2 echo "Waiting for SIGUSR1. PID is $$"
    while [ $SYNC -ne 2 ]; do
        :
    done
fi

# Start extractor
python3 ./extractor.py $BITS_TO_EXTRACT $SAMPLES 0 $OUTPUT_FILENAME 'delta'

>&2 echo "Splitting files"

# Once extracted, split the file into more files
python3 ./splitter.py $TOTAL_FILES $OUTPUT_FILENAME "$PREFIX-$OUTPUT_FILENAME"

>&2 echo "Computing entropy"

# Now call ea_non_iid on all the created files
for i in $(seq 0 $(( TOTAL_FILES - 1 ))); do
    out=$(./ea_non_iid "$PREFIX$i.bin" | grep -Po "(?<=min\(H_original, \d X H_bitstring\): )[\d\.]+")
    if [ -z $out ]; then
        out=0
    fi

    echo "Entropy for the $(( i + 1))th significant byte is $out"
done

exit 0
