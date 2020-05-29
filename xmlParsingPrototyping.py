#!/usr/bin/python

from enum import Enum
import os
import re
from xml.dom.minidom import parse
import xml.dom.minidom

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
    else:
        raise ValueError("Unknown bit value: " + string)

class BitSequence(XmlDecoder):

    def __init__(self, xmlNode, isT16):
        self.parse(xmlNode, isT16)

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
        constants = [c.childNodes[0].data for c in xmlNode.getElementsByTagName("c") if len(c.childNodes) > 0 is not None]
        self.parse_values(constants)

    def __str__(self):
        return "BitSequence{high_bit=" + str(self.high_bit) + ",width=" + str(self.width) + ",low_bit=" + str(self.low_bit) + ",name=" + self.name + ",constant=" + self.constants + "}"
class Encoding(XmlDecoder):

    def __init__(self, xmlNode):
        self.parse(xmlNode)

    def parse(self, xmlNode):
        regDiagram = xmlNode.getElementsByTagName("regdiagram")[0]
        isT16 = regDiagram.getAttribute("form") == "16"
        self.instruction_set = "T16" if isT16 else xmlNode.getAttribute("isa")
        self.bitSequences = [BitSequence(boxNode, isT16) for boxNode in regDiagram.getElementsByTagName("box")]
        self.total_bit_sequence_length = sum([seq.width for seq in self.bitSequences])

class Instruction(XmlDecoder):

    def __init__(self, xmlNode):
        self.parse(xmlNode)

    def parse(self, instNode):
        self.name = instNode.getElementsByTagName("heading")[0]
        self.encodings = [Encoding(iclass) for iclass in instNode.getElementsByTagName("iclass")]

def parseInstruction(xmlDir, xmlFile):
    print(xmlFile)
    path = xmlDir + xmlFile
    xml_data = xml.dom.minidom.parse(path)
    return(Instruction(xml_data))

xmlDir = "spec/ISA_v82A_A64_xml_00bet3.1/"
indexFile = xmlDir + "index.xml"
indexXml = xml.dom.minidom.parse(indexFile)
iforms = indexXml.getElementsByTagName('iform')
xmlFiles = [iform.getAttribute('iformfile') for iform in iforms]
instructions = [parseInstruction(xmlDir, xmlFile) for xmlFile in xmlFiles]
