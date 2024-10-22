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
        self.psname = regDiagram.getAttribute("psname")
        self.id = xmlNode.getAttribute("id")
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

    # NOTE: inverted bit sequences are treated as unbound for uniquely distinguishing encodings
    # NOTE: this is indexed from the left, where 0 corresponds to the highest position (leftmost)
    def getBit(self, index):
        sequence = self.getSequenceByBitIndex(index)
        if sequence.inverted:
            return((BitValueType.Unbound, None))
        return(sequence.constants[index - (31 - sequence.high_bit)])

    def getBitRange(self, lower, upper):
        return([self.getBit(i) for i in range(lower, upper)])

    def getBitMany(self, set_of_positions):
        return(dict([(i,self.getBit(i)) for i in set_of_positions]))

    def unbound_count(self):
        count = 0
        for i in range(0,32):
            (bitType, _) = self.getBit(i)
            if bitType == BitValueType.Unbound:
                count += 1
        return(count)

    def named_bit_sequences(self):
        return([bs for bs in self.bitSequences if bs.name != "_"])

    def get_size_of_unbound_sequences(self):
        size_dict = dict()
        current_count = 0
        for (_, (_, bitValue)) in self.getBitMany(range(32)).items():
            if bitValue != None:
                size_dict[current_count] = size_dict.get(current_count, 0) + 1
                current_count = 0
            else:
                current_count += 1
        if current_count > 0:
            size_dict[current_count] = size_dict.get(current_count, 0) + 1
        return(size_dict)


class Instruction(XmlDecoder):

    def __init__(self, fileName, xmlNode):
        self.fileName = fileName
        self.parse(xmlNode)

    @staticmethod
    def parse_docvars(instNode):
        docvars_node = instNode.getElementsByTagName("docvars")[0]
        docvars = dict()
        for docvar_node in docvars_node.getElementsByTagName("docvar"):
            k = docvar_node.getAttribute("key")
            v = docvar_node.getAttribute("value")
            docvars[k] = v
        return(docvars)

    def parse(self, xmlNode):
        instNode = xmlNode.getElementsByTagName("instructionsection")[0]
        self.name = instNode.getElementsByTagName("heading")[0].childNodes[0].data
        self.id = getAttr(instNode, "id", None)
        docvars = Instruction.parse_docvars(instNode)
        self.mnemonic = docvars["mnemonic"] if "mnemonic" in docvars else instNode.getAttribute('id')
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
    try:
        xml_data = xml.dom.minidom.parse(path)
    except xml.parsers.expat.ExpatError:
        raise ValueError("Failed to parse", xmlFile)
    try:
        inst = Instruction(xmlFile, xml_data)
        return(inst)
    except:
        raise ValueError("Missing data in", xmlFile)

def xmlFileNames(indexFilePath):
    indexXml = xml.dom.minidom.parse(indexFilePath)
    iforms = indexXml.getElementsByTagName('iform')
    return([iform.getAttribute('iformfile') for iform in iforms])

def parseAllFiles(include_aliases = False):
    xmlDir = "../../spec/ISA_v82A_A64_xml_00bet3.1/"

    baseInstructions_indexFile = xmlDir + "index.xml"
    baseInstructions_xmlFilePaths = xmlFileNames(baseInstructions_indexFile)

    fpsimdInstructions_indexFile = xmlDir + "fpsimdindex.xml"
    fpsimdInstructions_xmlFilePaths = xmlFileNames(fpsimdInstructions_indexFile)

    xmlFiles = baseInstructions_xmlFilePaths + fpsimdInstructions_xmlFilePaths

    instructions_and_aliases = dict([(xmlFile, parseInstruction(xmlDir, xmlFile)) for xmlFile in xmlFiles])

    if(include_aliases):
        return(instructions_and_aliases.values())

    # Convert alias filenames to object references
    just_instructions = set()
    for filename, inst in instructions_and_aliases.items():
        if not inst.is_alias:
            just_instructions |= {inst}
        inst.update_alias_references(instructions_and_aliases)

    return(just_instructions)

