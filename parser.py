from enum import Enum
from xml.dom.minidom import parse
import xml.dom.minidom
import re

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
        "x"  : (BitValueType.Unbound, None),
        "0"  : (BitValueType.Bound, Bit.Zero),
        "1"  : (BitValueType.Bound, Bit.One),
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

def getAttr(element, name, default):
    """Similar API to getAttr, but for DOM Elements"""
    return element.getAttribute(name) if element.hasAttribute(name) else default

class XmlDecoder:

    def parse(_xmlNode):
        raise NotImplementedError("Object that can be instantiated from the XML should implement this")

class BitSequence(XmlDecoder):

    def __init__(self, xmlNode, isT16):
        self.parse(xmlNode, isT16)

    def __str__(self):
        ret = ""
        if self.inverted:
            ret += "!"
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

    def getSequenceByBitIndex(self, index):
        index_of_remainder = index
        for bitSequence in self.bitSequences:
            if index_of_remainder < bitSequence.width:
                return bitSequence
            index_of_remainder -= bitSequence.width
        raise ValueError("index (" + index + ") > length of instruction (" + self.total_bit_sequence_length)

    # NOTE: doesn't support inverted sequences
    #   because only alias have inverted bit sequences and the decoder doesn't care about aliases
    def getBit(self, index):
        sequence = self.getSequenceByBitIndex(index)
        if sequence.inverted:
            raise ValueError("getBit does not support inverted bit sequences")
        return(sequence.constants[index - (31 - sequence.high_bit)])

    def getBitRange(self, lower, upper):
        return([self.getBit(i) for i in range(lower, upper)])

class Instruction(XmlDecoder):

    def __init__(self, fileName, xmlNode):
        self.fileName = fileName
        self.parse(xmlNode)

    def parse(self, xmlNode):
        instNode = xmlNode.getElementsByTagName("instructionsection")[0]
        self.name = instNode.getElementsByTagName("heading")[0].childNodes[0].data
        self.is_alias = getAttr(instNode, "type", "instruction") == "alias"
        self.encodings = [Encoding(iclass, self) for iclass in instNode.getElementsByTagName("iclass")]
        if self.is_alias:
            self.aliasto_filename = instNode.getElementsByTagName('aliasto')[0].getAttribute('refiform')
        else:
            alias_list_node = instNode.getElementsByTagName('alias_list')[0]
            self.aliaslist_filenames = set([aliasref.getAttribute('aliasfile') for aliasref
                                        in alias_list_node.getElementsByTagName('aliasref')])

    def update_alias_references(self, filename_inst_mapping):
        if self.is_alias:
            self.aliasto = filename_inst_mapping[self.aliasto_filename]
        else:
            self.aliaslist = set([filename_inst_mapping[filename] for filename in self.aliaslist_filenames])

def parseInstruction(xmlDir, xmlFile):
    path = xmlDir + xmlFile
    xml_data = xml.dom.minidom.parse(path)
    return(Instruction(xmlFile, xml_data))

def parseAllFiles():
    xmlDir = "spec/ISA_v82A_A64_xml_00bet3.1/"
    indexFile = xmlDir + "index.xml"
    indexXml = xml.dom.minidom.parse(indexFile)
    iforms = indexXml.getElementsByTagName('iform')
    xmlFiles = [iform.getAttribute('iformfile') for iform in iforms]
    instructions_and_aliases = dict([(xmlFile, parseInstruction(xmlDir, xmlFile)) for xmlFile in xmlFiles])

    # Convert alias filenames to object references
    just_instructions = set()
    for filename, inst in instructions_and_aliases.items():
        if not inst.is_alias:
            just_instructions |= {inst}
        inst.update_alias_references(instructions_and_aliases)

    return(just_instructions)

