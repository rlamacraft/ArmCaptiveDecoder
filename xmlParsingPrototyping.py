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

    def __init__(self, xmlNode):
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
        # index_of_remainder = index
        # for bitSequence in self.bitSequences:
        #     if index_of_remainder < bitSequence.width:
        #         return bitSequence.constants[index_of_remainder]
        #     index_of_remainder -= bitSequence.width
        # raise ValueError("index (" + index + ") > length of instruction (" + self.total_bit_sequence_length)

    def getBitRange(self, lower, upper):
        return([self.getBit(i) for i in range(lower, upper)])

class Instruction(XmlDecoder):

    def __init__(self, xmlNode):
        self.parse(xmlNode)

    def parse(self, instNode):
        self.name = instNode.getElementsByTagName("heading")[0].childNodes[0].data
        self.encodings = [Encoding(iclass) for iclass in instNode.getElementsByTagName("iclass")]

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

def splitInstructionsByBitPosition(encoding_instructions_mapping, position, prefix):
    """Attempt 1: Split on each bit, producing binary tree of depth 32. Takes too long."""
    if position > 31:
        return(encoding_instructions_mapping.values())
    if len(encoding_instructions_mapping.items()) < 2:
        return(encoding_instructions_mapping.values())
    indent = " " * position
    print(indent, "Comparing bits at position", position, "( prefix:", prefix, ")")
    zeros = dict()
    ones = dict()
    for encoding, inst in encoding_instructions_mapping.items():
        (bit_type, bit_value) = encoding.getBit(position)
        if   (bit_type == BitValueType.Unbound) \
          or (bit_type == BitValueType.Bound and bit_value == Bit.Zero) \
          or (bit_type == BitValueType.Unpredictably_bound and bit_value == bit.Zero):
            zeros[encoding] = inst
        if   (bit_type == BitValueType.Unbound) \
          or (bit_type == BitValueType.Bound and bit_value == Bit.One) \
          or (bit_type == BitValueType.Unpredictably_bound and bit_value == Bit.One):
            ones[encoding] = inst
    print(indent, len(zeros.items()), " items in the zeros set")
    print(indent, len(ones.items()), " items in the ones set")
    return((splitInstructionsByBitPosition(zeros, position + 1, prefix + '0'), \
            splitInstructionsByBitPosition(ones, position + 1, prefix + '1')))

def splitInstructionsByBitSequence(encoding_instructions_mapping, position):
    """Attempt 2: (WIP) split on bit sequences"""
    if position > 31:
        return(encoding_instruction_mapping)
    next_sequence_upper_bound = 31 - list(encoding_instruction_mapping.keys())[0].getSequenceByBitIndex(position).low_bit
    print("next_sequence_upper_bound", next_sequence_upper_bound)
    branches = dict()
    for encoding, inst in encoding_instruction_mapping.items():
        print("instruction", inst.name)
        print("encoding", str(encoding))
        sub_sequence = "".join([strBitValue(x) for x in encoding.getBitRange(position, next_sequence_upper_bound + 1)])
        if sub_sequence not in branches:
            branches[sub_sequence] = []
        branches[sub_sequence] += (encoding, inst)
    return(branches)

instructions = parseAllFiles()
print("Parsed", len(instructions), "instructions.")
encoding_instruction_mapping = dict(list(itertools.chain(*[[(encoding, inst) for encoding in inst.encodings] for inst in instructions[0:-1]])))
print("\n".join([str(enc) for enc in list(encoding_instruction_mapping.keys())]))
print("Built mapping from encodings to instructions.")
# decode_binary_tree = splitInstructionsByBitPosition(encoding_instruction_mapping, 0, "")

# print(splitInstructionsByBitSequence(encoding_instruction_mapping, 2))

# bit positions 3, 4, and 5 are bound for all instructions
always_bound = [True] * 32
always_unbound = [True] * 32
for position in range(0, 32):
    for encoding in list(encoding_instruction_mapping.keys()):
        (bitValueType, _) = encoding.getBit(position)
        if bitValueType == BitValueType.Unbound:
            always_bound[position] = False
        if bitValueType == BitValueType.Bound or bitValueType == BitValueType.Unpredictably_bound:
            always_unbound[position] = False
print("always_bound  ", "".join(["T" if b else "F" for b in always_bound]))
print("always_unbound", "".join(["T" if b else "F" for b in always_unbound]))


