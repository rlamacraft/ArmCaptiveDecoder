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

    def has_shared_bits(self):
        return(len(self.shared_bits) > 0)

    def __len__(self):
        return(len(self.encodings))

    def is_singleton(self):
        return(len(self) == 1)

    def get_singleton(self):
        if(self.is_singleton()):
            [ret] = self.encodings
            return(ret)
        raise ValueError("Only call if this EncodingsSet is unknown to be a singleton")

    @staticmethod
    def make_singleton(enc):
        shared_bits = dict()
        for i in range(0,32):
            (bitType, bitValue) = enc.getBit(i)
            if bitType == BitValueType.Bound:

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

    # returns 2 ** n new sets of encodings by splitting on n bit positions
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
        for index, elem in enumerate(elements):
            if not elem['v'] == None:
                no_repeat_none.append((BitValueType.Bound,elem))
            else:
                if    index > 0                           \
                  and index < len(elements) - 1           \
                  and elements[index - 1]['v'] is not None\
                  and elements[index + 1]['v'] is not None:
                    no_repeat_none.append((BitValueType.Unbound, elem))
                elif no_repeat_none != [] and no_repeat_none[-1] != None:
                    # only add a None if something else has been added first
                    #   and the last element isn't a None to drop repeat None
                    no_repeat_none.append(None)
        return(no_repeat_none)

    def shared_bits_as_list_of_ranges(self):
        if len(self.shared_bits) == 0:
            return([])
        none_separated_bit_data = self._remove_repeated_none_and_leading_none([
            {'v':self.shared_bits[i].value,'high':i,'low':i}
            if i in self.shared_bits else
            {'v': None, 'high': i, 'low': i}
            for i in range(0,32)])
        conjunctive = []
        initial = [{'v':0,'high':None,'low':None}]
        disjunctive = initial
        for datum in none_separated_bit_data:
            if datum is None:
                conjunctive.append(disjunctive)
                disjunctive = initial
            else:
                (t, value) = datum
                if t == BitValueType.Bound:
                    disjunctive = [{
                        'v': (acc['v'] * 2) + value['v'],
                        'high': acc['high'] if acc['high'] is not None else 31 - value['high'],
                        'low': 31 - value['low']
                    } for acc in disjunctive]
                else:
                    new_disjunctive = []
                    for dis in disjunctive:
                        new_disjunctive.append({
                            'v': (dis['v'] * 2) + 0,
                            'high': dis['high'] if dis['high'] is not None else 31 - value['high'],
                            'low': 31 - value['low']
                        })
                        new_disjunctive.append({
                            'v': (dis['v'] * 2) + 1,
                            'high': dis['high'] if dis['high'] is not None else 31 - value['high'],
                            'low': 31 - value['low']
                        })
                    disjunctive = new_disjunctive
        if(disjunctive != initial):
            conjunctive.append(disjunctive)
        return(conjunctive)

# The nodes of a decode tree, where the leaves at EncodingsSets
class EncodingsTree():

    def __init__(self, encoding_set, depth = 0):
        self.source_enc_set = encoding_set
        encoding_subsets = encoding_set.splitOnCommonBoundBits() # set of EncodingsSets
        no_empty_enc_sets = set([x for x in encoding_subsets if len(x) > 0])
        if(len(no_empty_enc_sets) == 1):
            self.leaf = encoding_set
            self.children = None
        else:
            self.leaf = None
            self.children = set()
            for subset in no_empty_enc_sets:
                if(subset.is_singleton()):
                    # produce the most precise singleton encodings set to ensure that
                    # the unbound bit hopping is used minimally i.e. only hop unbound
                    # bits that are actually unbound in the encoding and not simply
                    # because they are not necessary to uniquely identify the
                    # instruction; see "UCVTF"
                    subset = EncodingsSet.make_singleton(subset.get_singleton())
                self.children |= {EncodingsTree(subset)}

    def is_leaf(self):
        return(self.leaf is not None)

    def number_of_children(self):
        if(self.is_leaf()):
            return(0)
        else:
            return(len(self.children))
