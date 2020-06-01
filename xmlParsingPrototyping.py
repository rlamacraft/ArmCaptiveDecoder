#!/usr/bin/python

from enum import Enum
import os
import re
from xml.dom.minidom import parse
import xml.dom.minidom
import itertools

def getAttr(element, name, default):
    """Similar API to getAttr, but for DOM Elements"""
    return element.getAttribute(name) if element.hasAttribute(name) else default

class XmlDecoder:

    def parse(_xmlNode):
        raise NotImplementedError("Object that can be instantiated from the XML should implement this")

class Bit(Enum):
    Zero = 0
    One = 1

    def __str__(self):
        if self == Bit.Zero:
            return "0"
        if self == Bit.One:
            return "1"
        raise ValueError("Impossible")

class BitSequenceType(Enum):
    Sequence = 0
    Inverted_Sequence = 1

class BitValueType(Enum):
    Unbound = 0               # denoted with "x", or an empty string
    Bound = 1                 # denoted with either "0" or "1"
    Unpredictably_bound = 2   # denoted with either "(0)" or "(1)"

def readBitValue(string):
    encodings = {
        "x": (BitValueType.Unbound, None),
        "0": (BitValueType.Bound, Bit.Zero),
        "1": (BitValueType.Bound, Bit.One),
        "(0)": (BitValueType.Unpredictably_bound, Bit.Zero),
        "(1)": (BitValueType.Unpredictably_bound, Bit.One)
    }
    if string in encodings:
        return(encodings[string])
    raise ValueError("Unknown bit value: " + string)

def strBitValue(bitValuePair):
    decodings = {
        (BitValueType.Unbound, None): "x",
        (BitValueType.Bound, Bit.Zero): "0",
        (BitValueType.Bound, Bit.One): "1",
        (BitValueType.Unpredictably_bound, Bit.Zero): "(0)",
        (BitValueType.Unpredictably_bound, Bit.One): "(1)"
    }
    if bitValuePair in decodings:
        return(decodings[bitValuePair])
    raise ValueError("Unknown bit value: " + bitValuePair)

class BitSequence(XmlDecoder):

    def __init__(self, xmlNode, isT16):
        self.parse(xmlNode, isT16)

    def __str__(self):
        ret = ""
        if self.inverted:
            ret += "!"
        # ret += "".join(["(" + str(bitValueType) + ", " + str(bitValue) + ")" for (bitValueType,bitValue) in self.constants])
        ret += "".join([strBitValue(bitValue) for bitValue in self.constants])
        return(ret)

    def parse_values(self, constants):
        if constants == []:
            constants = ["x"] * self.width
        if constants[0].startswith("!="):
            self.inverted = True
            constants = list(re.compile("!= (.*)").match(constants[0])[1])
        else:
            self.inverted = False
        self.constants = [readBitValue(c) for c in constants]

    def parse(self, xmlNode, isT16):
        self.high_bit = int(xmlNode.getAttribute("hibit"))
        if isT16:
            self.high_bit = self.high_bit - 16
        self.width = int(getAttr(xmlNode, "width", 1))
        self.low_bit = self.high_bit - self.width + 1
        self.name = getAttr(xmlNode, "name", "_")
        self.parse_values([c.childNodes[0].data for c in xmlNode.getElementsByTagName("c") if len(c.childNodes) > 0 is not None])

class Encoding(XmlDecoder):

    def __init__(self, xmlNode, instruction):
        self.instruction = instruction
        self.parse(xmlNode)

    def __str__(self):
        return(":".join([str(seq) for seq in self.bitSequences]))

    def parse(self, xmlNode):
        regDiagram = xmlNode.getElementsByTagName("regdiagram")[0]
        isT16 = regDiagram.getAttribute("form") == "16"
        self.instruction_set = "T16" if isT16 else xmlNode.getAttribute("isa")
        self.bitSequences = [BitSequence(boxNode, isT16) for boxNode in regDiagram.getElementsByTagName("box")]
        self.total_bit_sequence_length = sum([seq.width for seq in self.bitSequences])

    # note: doesn't support inverted sequences
    def getSequenceByBitIndex(self, index):
        index_of_remainder = index
        for bitSequence in self.bitSequences:
            if index_of_remainder < bitSequence.width:
                return bitSequence
            index_of_remainder -= bitSequence.width
        raise ValueError("index (" + index + ") > length of instruction (" + self.total_bit_sequence_length)

    def getBit(self, index):
        sequence = self.getSequenceByBitIndex(index)
        return(sequence.constants[index - (31 - sequence.high_bit)]) # TODO: test

    def getBitRange(self, lower, upper):
        return([self.getBit(i) for i in range(lower, upper)])

class Instruction(XmlDecoder):

    def __init__(self, xmlNode):
        self.parse(xmlNode)

    def parse(self, instNode):
        self.name = instNode.getElementsByTagName("heading")[0].childNodes[0].data
        self.encodings = [Encoding(iclass, self) for iclass in instNode.getElementsByTagName("iclass")]

# PARSE XML FILES

def parseInstruction(xmlDir, xmlFile):
    path = xmlDir + xmlFile
    xml_data = xml.dom.minidom.parse(path)
    return(Instruction(xml_data))

def parseAllFiles():
	xmlDir = "spec/ISA_v82A_A64_xml_00bet3.1/"
	indexFile = xmlDir + "index.xml"
	indexXml = xml.dom.minidom.parse(indexFile)
	iforms = indexXml.getElementsByTagName('iform')
	xmlFiles = [iform.getAttribute('iformfile') for iform in iforms]
	instructions = [parseInstruction(xmlDir, xmlFile) for xmlFile in xmlFiles]
	return(instructions)

# BUILD ABSTRACT DECODER

# def splitInstructionsByBitPosition(encoding_instructions_mapping, position, prefix):
#     """Attempt 1: Split on each bit, producing binary tree of depth 32. Takes too long."""
#     if position > 31:
#         return(encoding_instructions_mapping.values())
#     if len(encoding_instructions_mapping.items()) < 2:
#         return(encoding_instructions_mapping.values())
#     indent = " " * position
#     print(indent, "Comparing bits at position", position, "( prefix:", prefix, ")")
#     zeros = dict()
#     ones = dict()
#     for encoding, inst in encoding_instructions_mapping.items():
#         (bit_type, bit_value) = encoding.getBit(position)
#         if   (bit_type == BitValueType.Unbound) \
#           or (bit_type == BitValueType.Bound and bit_value == Bit.Zero) \
#           or (bit_type == BitValueType.Unpredictably_bound and bit_value == bit.Zero):
#             zeros[encoding] = inst
#         if   (bit_type == BitValueType.Unbound) \
#           or (bit_type == BitValueType.Bound and bit_value == Bit.One) \
#           or (bit_type == BitValueType.Unpredictably_bound and bit_value == Bit.One):
#             ones[encoding] = inst
#     print(indent, len(zeros.items()), " items in the zeros set")
#     print(indent, len(ones.items()), " items in the ones set")
#     return((splitInstructionsByBitPosition(zeros, position + 1, prefix + '0'), \
#             splitInstructionsByBitPosition(ones, position + 1, prefix + '1')))

# def splitInstructionsByBitSequence(encoding_instructions_mapping, position):
#     """Attempt 2: (WIP) split on bit sequences"""
#     if position > 31:
#         return(encoding_instruction_mapping)
#     next_sequence_upper_bound = 31 - list(encoding_instruction_mapping.keys())[0].getSequenceByBitIndex(position).low_bit
#     print("next_sequence_upper_bound", next_sequence_upper_bound)
#     branches = dict()
#     for encoding, inst in encoding_instruction_mapping.items():
#         print("instruction", inst.name)
#         print("encoding", str(encoding))
#         sub_sequence = "".join([strBitValue(x) for x in encoding.getBitRange(position, next_sequence_upper_bound + 1)])
#         if sub_sequence not in branches:
#             branches[sub_sequence] = []
#         branches[sub_sequence] += (encoding, inst)
#     return(branches)

def findPositionsBoundForAll(encodings):
    always_bound = [True] * 32
    for position in range(0, 32):
        for encoding in encodings:
            (bitValueType, _) = encoding.getBit(position)
            if bitValueType == BitValueType.Unbound:
                always_bound[position] = False
    always_bound_positions = []
    for i, b in enumerate(always_bound):
        if b:
            always_bound_positions.append(i)
    return(always_bound_positions)

def splitEncodingsByCommonBit(encodings, common_bit_position):
    zeros = []
    ones = []
    for encoding in encodings:
        (bit_type, bit_value) = encoding.getBit(common_bit_position)
        if   (bit_type == BitValueType.Unbound) \
          or (bit_type == BitValueType.Bound and bit_value == Bit.Zero) \
          or (bit_type == BitValueType.Unpredictably_bound and bit_value == bit.Zero):
            zeros.append(encoding)
        if   (bit_type == BitValueType.Unbound) \
          or (bit_type == BitValueType.Bound and bit_value == Bit.One) \
          or (bit_type == BitValueType.Unpredictably_bound and bit_value == Bit.One):
            ones.append(encoding)
    return([zeros, ones])

def splitEncodingsByCommonBoundBit(encodings, common_bound_positions):
    sets = [encodings]
    for bit_position in common_bound_positions:
        new_sets = []
        for each_set in sets:
            another_two_sets = splitEncodingsByCommonBit(each_set, bit_position)
            new_sets += another_two_sets
        sets = new_sets
    return(sets)

def printBinaryTree(sets):
    for index, each_set in enumerate(sets):
        print("#####", index, "#####")
        for encoding in each_set:
            print(str(encoding), ":", encoding.instruction.name)

class EncodingsSet():

    def __init__(self, encodings, shared_bits):
        self.encodings = encodings
        self.shared_bits = shared_bits
        # NOTE: the invariant that all encodings do share such bits is not asserted

    def __len__(self):
        return(len(self.encodings))

    def __str__(self):
        out = f"{len(self.encodings)} share the bits "
        out += "{"
        shared_bits_str = []
        shared_bits_items = list(self.shared_bits.items())
        shared_bits_items.sort()
        for shared_bit, shared_value in shared_bits_items:
            shared_value_str = "0" if shared_value == Bit.Zero else "1"
            shared_bits_str.append(f"{shared_bit}:{shared_value_str}")
        out += ", ".join(shared_bits_str)
        out += "}\n"
        for encoding in self.encodings:
            out += f"- {str(encoding)} ({encoding.instruction.name})\n"
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
               (_, bitValue) = encoding.getBit(position)
               if bitValue != None:
                   values |= {bitValue}
           if len(values) == 2:
                different |= {position}
       return(different)

    def splitOnDifferentBoundValue(self):
       return(self.splitMany(self.findDifferentBoundValue()))

def splitOnCommonBoundAndThenDifferentBoundValue(encoding_set):
    sets_from_common_bound = encoding_set.splitOnCommonBoundBits()
    # sets_from_different_bound_value = set()
    # for each_set in sets_from_common_bound:
    #     sets_from_different_bound_value |= each_set.splitOnDifferentBoundValue()
    # return(sets_from_different_bound_value)
    return(sets_from_common_bound)

def findCommonBitsAndSplitRecursively(encoding_set, depth):
    if depth > 6:
        return {encoding_set}
    encoding_subsets = encoding_set.splitOnCommonBoundBits()
    # encoding_subsets = splitOnCommonBoundAndThenDifferentBoundValue(encoding_set)
    encoding_subsubsets = set()
    for subset in encoding_subsets:
        if len(subset) > 1:      # i.e. more sub-dividing is necessary
            # encoding_subsubsets |= subset.splitOnCommonBoundBits()
            encoding_subsubsets |= findCommonBitsAndSplitRecursively(subset, depth + 1)
        else:
            encoding_subsubsets |= {subset}
    return(encoding_subsubsets)

instructions = parseAllFiles()
print("Parsed", len(instructions), "instructions.")

# For purposes of intial prototyping, will we consider the encodings of only a subset of all of the instructions
encodings = list(itertools.chain(*[inst.encodings for inst in instructions[0:-1]]))

# bit positions 3, 4, and 5 are bound for all instructions
# so split all of the instructions into 8 groups (actually 4 groups "010", "100", "101", and "110")
# split = splitEncodingsByCommonBoundBit(encodings, findPositionsBoundForAll(encodings))
# printBinaryTree(split)

# # now repeat
# for subset in [s for s in split if s ]:
#     print("***")
#     printBinaryTree(splitEncodingsByCommonBoundBit(subset, findPositionsBoundForAll(subset)))
encoding_set = EncodingsSet(set(encodings), {})
[print(str(encoding_set)) for encoding_set in list(findCommonBitsAndSplitRecursively(encoding_set, 0)) if len(encoding_set) > 0]
