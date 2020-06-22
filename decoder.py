#!/usr/bin/python

import os
import itertools
from parser import *

class EncodingsSet():

    def __init__(self, encodings, shared_bits):
        for encoding in encodings:
            for position, bit in shared_bits.items():
                (_, bitValue) = encoding.getBit(position)
                assert bitValue == bit
        self.encodings = encodings
        self.shared_bits = shared_bits

    def __len__(self):
        return(len(self.encodings))

    def is_singleton(self):
        return(len(self) == 1)

    def __str__(self):
        out = f"{len(self.encodings)} instructions share the bits: "
        for bit in range(0,32):
            out += strBitValue((BitValueType.Bound, self.shared_bits[bit])
                               if bit in self.shared_bits
                               else (BitValueType.Unbound, None))
        out += "\n"
        for encoding in self.encodingsOrderedByIncreasingUnbound():
            out += f"- {str(encoding)} [{encoding.instruction.name}]({encoding.instruction.fileName})\n"
            for bit_sequence in encoding.bitSequences:
                if not bit_sequence.name == "_":
                    out += f"  - {bit_sequence.name}: [{bit_sequence.high_bit}..{bit_sequence.low_bit}]\n"
        return(out)

    def ordered_shared_bits(self):
        for bit in sorted(self.shared_bits):
            yield (bit, self.shared_bits[bit])

    def append(self, encoding):
        for position, bit in self.shared_bits.items():
            (_, bitValue) = encoding.getBit(position)
            assert bitValue == bit
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

    def findUncommonlyBoundBits(self):
        """These are the bit positions where at least one of the encodings has a bound bit"""
        all_bound = set()
        for enc in self.encodings:
            for i in range(0,32):
                (bitType, _) = enc.getBit(i)
                if bitType == BitValueType.Bound:
                    all_bound |= {i}
        return(all_bound - set(self.shared_bits.keys()))

    def splitOnCommonBoundBits(self):
        return(self.splitMany(self.findOtherCommonlyBoundBits()))

    def encodingsOrderedByIncreasingUnbound(self):
        unbound_count = dict([(i,set()) for i in range(0,32)])
        for enc in self.encodings:
            unbound_count[enc.unbound_count()] |= {enc}
        ret = []
        for i in range(0,32):
            ret += unbound_count[i]
        return(ret)

    def _remove_repeated_none_and_leading_none(self, elements):
        no_repeat_none = []
        for elem in elements:
            if not elem == None:
                no_repeat_none.append(elem)
            else:
                if no_repeat_none != [] and no_repeat_none[-1] != None:
                    no_repeat_none.append(None)
        return(no_repeat_none)

    def shared_bits_as_list_of_ranges(self):
        if len(self.shared_bits) == 0:
            return([])
        none_separated_bit_data = self._remove_repeated_none_and_leading_none([
            {'v':self.shared_bits[i].value,'high':i,'low':i}
            if i in self.shared_bits else None for i in range(0,32)])
        data = []
        initial = {'v':0,'high':None,'low':None}
        accumulator = initial
        for datum in none_separated_bit_data:
            if datum is None:
                data.append(accumulator)
                accumulator = initial
            else:
                accumulator = {
                    'v': (accumulator['v'] * 2) + datum['v'],
                    'high': accumulator['high'] if accumulator['high'] is not None else 31 - datum['high'],
                    'low': 31 - datum['low']
                }
        return(data)

def findCommonBitsAndSplitRecursively(encoding_set):
    encoding_subsets = encoding_set.splitOnCommonBoundBits()
    if len(encoding_subsets) == 1:
        # stop when splitting does nothing but apply singleton function
        return {encoding_set}
    encoding_subsubsets = set()
    for subset in encoding_subsets:
        if len(subset) == 0:
            # we don't care about empty encoding sets
            pass
        elif len(subset) == 1:
            # don't split singletons sets to keep the minimum shared_bits set
            encoding_subsubsets |= {subset}
        else:
            encoding_subsubsets |= findCommonBitsAndSplitRecursively(subset)
    return(encoding_subsubsets)
