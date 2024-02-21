import argparse
from io import BufferedReader
from typing import Optional
import os

parser = argparse.ArgumentParser()
parser.add_argument(
    'filename', 
    type=str, 
    help = 'filename: the binary file you want to read data from'
)
parser.add_argument(
    '-s', 
    '--size', 
    type=int, 
    default=8, 
    help = 'number size: how big is the number we are reading from the file (in bits)'
) 
parser.add_argument(
    '-m', 
    '--mask', 
    type=int, 
    default=8, 
    help = 'mask size: how many bits we want to extract from the `--size` bits that we read'
) 
parser.add_argument(
    '-o', 
    '--offset', 
    type=int, 
    default=0, 
    help = 'offset: how many bits we want the mask to be offset from the less significative bit'
) 
parser.add_argument(
    '-d', 
    '--directory', 
    type=str, 
    default='./filtered', 
    help = 'output directory: where the filtered files will be placed'
) 
parser.add_argument(
    '-D', 
    '--input-directory', 
    type=str, 
    default='./original', 
    help = 'input directory: `filename`\'s directory'
)

args = parser.parse_args()
assert(args.offset <= (args.size - args.mask + 1))

def read_bytes_to_int(file: BufferedReader, bytes_no: int) -> Optional[int]:
    read_number = 0
    times = int(bytes_no / 8)
    for time in range(0, times):
        """
            since python3 can only read one byte at a time, we need to do more reads if the bit number is greater than 8
        """ 
        res = file.read(1) # we read one byte
        if not res:
            return None # we reached EOF
        
        int_res = int.from_bytes(res, "big")
        shift_no = times - time - 1 # we calculate the number of shifts 
        """
            if, for example, we have:
            0x895e = b10001001 b01011110 => 16 bits:
                - times = 2 (we have to read two times to extract)
                - the first time, shift_no = 1 (we shift one byte), the second time shift_no = 0 (we don't shift)
                - read_number will be = 1000100101011110
        """
        read_number += int_res << shift_no * 8

    return read_number

def create_bitmask(bits: int) -> int:
    bitmask = 0
    for bit in range(0, bits):
        bitmask += 1 << bit

    return bitmask

if __name__ == '__main__':
    source = os.path.join(args.input_directory, args.filename)
    with open(source, 'rb') as file:
        out_path = os.path.join(args.directory, f'{args.filename}.filtered-mask{args.mask}-offset{args.offset}.raw')
        with open(out_path, 'wb') as output_file:
            count = 0
            while True:
                number = read_bytes_to_int(file, args.size)
                if number is None:
                    break
                mask = create_bitmask(args.mask) << args.offset # we move our mask by `offset` bits to the left
                masked_number = int(number & mask) >> args.offset # we finally filter our number

                # .to_bytes(length=x), where x is the number of bytes required to store the int we are printing to the file
                output_file.write(masked_number.to_bytes(length=int(args.size / 8), byteorder='big'))

