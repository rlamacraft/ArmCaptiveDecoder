#!/usr/bin/python

from xml.dom.minidom import parse
import xml.dom.minidom

def getAttr(element, name, default):
    """Similar API to getAttr, but for DOM Elements"""
    return element.getAttribute(name) if element.hasAttribute(name) else default

class XmlDecoder:

    def parse(_xmlNode):
        raise NotImplementedError("Object that can be instantiated from the XML should implement this")

class Box(XmlDecoder):

    def __init__(self, xmlNode, isT16):
        self.parse(xmlNode, isT16)

    def parse(self, xmlNode, isT16):
        self.high_bit = int(xmlNode.getAttribute("hibit"))
        if isT16:
            self.high_bit = self.high_bit - 16
        self.width = int(getAttr(xmlNode, "width", 1))
        self.low_bit = self.high_bit - self.width + 1
        self.name = getAttr(xmlNode, "name", "_")
        self.constants = "".join([c.childNodes[0].data for c in xmlNode.getElementsByTagName("c") if len(c.childNodes) > 0 is not None])
        if self.constants == "" or self.constants.startswith('!='):
            self.constants = 'x' * self.width 

    def __str__(self):
        return "Box{high_bit=" + str(self.high_bit) + ",width=" + str(self.width) + ",low_bit=" + str(self.low_bit) + ",name=" + self.name + ",constant=" + self.constants + "}"

class Encoding(XmlDecoder):

    def __init__(self, xmlNode):
        self.parse(xmlNode)

    def parse(self, xmlNode):
        regDiagram = xmlNode.getElementsByTagName("regdiagram")[0]
        isT16 = regDiagram.getAttribute("form") == "16"
        self.instruction_set = "T16" if isT16 else xmlNode.getAttribute("isa")
        self.boxes = [Box(boxNode, isT16) for boxNode in regDiagram.getElementsByTagName("box")]

class Instruction(XmlDecoder):

    def __init__(self, xmlNode):
        self.parse(xmlNode)

    def parse(self, instNode):
        self.name = instNode.getElementsByTagName("heading")[0]
        if len(instNode.getElementsByTagName('iclass')) > 1:
            raise NotImplementedError("Multiple instruction encodings are not yet supported.")
        self.encoding = Encoding(instNode.getElementsByTagName("iclass")[0])

xmlFile = "spec/ISA_v82A_A64_xml_00bet3.1/add_addsub_imm.xml" 
instruction = Instruction(xml.dom.minidom.parse(xmlFile).documentElement)

for box in instruction.encoding.boxes:
    print box
