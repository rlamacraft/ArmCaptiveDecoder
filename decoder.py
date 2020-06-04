#!/usr/bin/python

import os
import itertools
from parser import *

class EncodingsSet():

    def __init__(self, encodings, shared_bits):
        self.encodings = encodings
        self.shared_bits = shared_bits
        # NOTE: the invariant that all encodings do share such bits is not asserted

    def __len__(self):
        return(len(self.encodings))

    def __str__(self):
        out = f"{len(self.encodings)} instructions share the bits: "
        for bit in range(0,32):
            out += strBitValue((BitValueType.Bound, self.shared_bits[bit]) if bit in self.shared_bits else (BitValueType.Unbound, None))
        out += "\n"
        for encoding in self.encodings:
            out += f"- {str(encoding)} [{encoding.instruction.name}]({encoding.instruction.fileName})\n"
        return(out)

    def append(self, encoding):
        self.encodings |= {encoding}

    # returns two new encoding sets
    def split(self, common_bit_position):
        if common_bit_position in self.shared_bits.keys():
            raise ValueError(common_bit_position, "is already shared by all members of this encoding set")

        zeros_shared_bits = self.shared_bits.copy()
        zeros_shared_bits[common_bit_position] = Bit.Zero
        zeros = EncodingsSet(set(), zeros_shared_bits)

        ones_shared_bits = self.shared_bits.copy()
        ones_shared_bits[common_bit_position] = Bit.One
        ones = EncodingsSet(set(), ones_shared_bits)

        for encoding in self.encodings:
            (bit_type, bit_value) = encoding.getBit(common_bit_position)
            if   (bit_type == BitValueType.Unbound) \
              or (bit_type == BitValueType.Bound and bit_value == Bit.Zero) \
              or (bit_type == BitValueType.Unpredictably_bound and bit_value == Bit.Zero):
                zeros.append(encoding)
            if   (bit_type == BitValueType.Unbound) \
              or (bit_type == BitValueType.Bound and bit_value == Bit.One) \
              or (bit_type == BitValueType.Unpredictably_bound and bit_value == Bit.One):
                ones.append(encoding)
        return({zeros, ones})

    # returns 2 ** n new encoding sets by splitting on n bit positions
    def splitMany(self, common_bit_positions):
        sets = {self}
        for bit_position in common_bit_positions:
            new_set = set()
            for each_set in sets:
                new_set |= each_set.split(bit_position)
            sets = new_set
        return(sets)

    # in addition to the bits listed by self.shared_bits, there may be other bits that are commonly bound - split on those
    def findOtherCommonlyBoundBits(self):
        other_bits = set(range(32)) - set(self.shared_bits.keys())
        unbound_in_an_instruction = set()
        for position in other_bits:
            for encoding in self.encodings:
                (bitValueType, _) = encoding.getBit(position)
                if bitValueType == BitValueType.Unbound:
                    unbound_in_an_instruction |= {position}
                    break
        return(other_bits - unbound_in_an_instruction)

    def splitOnCommonBoundBits(self):
        return(self.splitMany(self.findOtherCommonlyBoundBits()))

    def findDifferentBoundValue(self):
       other_bits = set(range(32)) - set(self.shared_bits.keys())
       different = set()
       for position in other_bits:
           values = set()
           for encoding in self.encodings:
               (bitValueType, bitValue) = encoding.getBit(position)
               if bitValueType != BitValueType.Unbound:
                   values |= {bitValue}
           if len(values) == 2:
                different |= {position}
       return(different)

    def splitOnDifferentBoundValue(self):
       return(self.splitMany(self.findDifferentBoundValue()))

def findCommonBitsAndSplitRecursively(encoding_set, depth):
    if depth > 7:  # prevents infinite loops as some instructions appear to be indistinguishable
        return {encoding_set}
    encoding_subsets = encoding_set.splitOnCommonBoundBits()
    encoding_subsubsets = set()
    for subset in encoding_subsets:
        if len(subset) > 1:      # i.e. more sub-dividing may be possible
            encoding_subsubsets |= findCommonBitsAndSplitRecursively(subset, depth + 1)
        else:
            encoding_subsubsets |= {subset}
    return(encoding_subsubsets)

if __name__ == "__main__":
    instructions = parseAllFiles()
    print("Parsed", len(instructions), "instructions.")

    # encodings = list(itertools.chain(*[inst.encodings for inst in instructions]))
    # encoding_set = EncodingsSet(set(encodings), {})
    # [print(str(encoding_set)) for encoding_set in list(findCommonBitsAndSplitRecursively(encoding_set, 0)) if len(encoding_set) > 0]
