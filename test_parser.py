import unittest
from xml.dom.minidom import parseString
from parser import *

class TestBitValue(unittest.TestCase):

    def test_readBitValue(self):
         self.assertEqual(readBitValue('x'), (BitValueType.Unbound, None))
         self.assertEqual(readBitValue('0'), (BitValueType.Bound, Bit.Zero))
         self.assertEqual(readBitValue('1'), (BitValueType.Bound, Bit.One))

    def test_strBitValue(self):
        self.assertEqual(strBitValue((BitValueType.Unbound, None)), 'x')
        self.assertEqual(strBitValue((BitValueType.Bound, Bit.Zero)), '0')
        self.assertEqual(strBitValue((BitValueType.Bound, Bit.One)), '1')

    def test_strBitValue_readBitValue(self):
        f = lambda str: strBitValue(readBitValue(str))
        self.assertEqual(f('x'), 'x')
        self.assertEqual(f('0'), '0')
        self.assertEqual(f('1'), '1')

def parseSingleNode(xmlString):
    return(parseString(xmlString).childNodes[0])

class TestBitSequence(unittest.TestCase):

    def unbound(self):
        return(BitSequence(parseSingleNode('<box hibit="31" name="sf"><c></c></box>'), False))

    def bound(self):
        return(BitSequence(parseSingleNode('<box hibit="31" name="sf" width="2"><c>0</c><c>1</c></box>'), False))

    def test_parse(self):
        unbound = self.unbound()
        self.assertEqual(unbound.name, "sf")
        self.assertEqual(unbound.high_bit, 31)
        self.assertEqual(unbound.width, 1)
        self.assertEqual(unbound.low_bit, 31)
        self.assertEqual(unbound.constants, [
            (BitValueType.Unbound, None)
        ])

        bound = self.bound()
        self.assertEqual(bound.name, "sf")
        self.assertEqual(bound.high_bit, 31)
        self.assertEqual(bound.width, 2)
        self.assertEqual(bound.low_bit, 30)
        self.assertEqual(bound.constants, [
            (BitValueType.Bound, Bit.Zero),
            (BitValueType.Bound, Bit.One)
        ])

    def test_str(self):
        unbound = self.unbound()
        self.assertEquals(str(unbound), "x")
        bound = self.bound()
        self.assertEquals(str(bound), "01")

class TestEncoding(unittest.TestCase):

    @staticmethod
    def xml():
        return("""
        <iclass isa="A64">
          <regdiagram form="32">
            <box hibit="31" name="sf" width="32">
              <c>0</c>
              <c>0</c>
              <c>0</c>
              <c>0</c>
              <c>0</c>
              <c>0</c>
              <c>0</c>
              <c>0</c>
              <c>0</c>
              <c>0</c>
              <c>0</c>
              <c>0</c>
              <c>0</c>
              <c>0</c>
              <c>0</c>
              <c>0</c>
              <c>0</c>
              <c>0</c>
              <c>0</c>
              <c>0</c>
              <c>0</c>
              <c>0</c>
              <c>0</c>
              <c>0</c>
              <c>0</c>
              <c>0</c>
              <c>0</c>
              <c>0</c>
              <c>0</c>
              <c>0</c>
              <c>0</c>
              <c>0</c>
            </box>
          </regdiagram>
        </iclass>
        """)

    def test_parse(self):
        encoding = Encoding(parseSingleNode(TestEncoding.xml()), None)
        self.assertEqual(encoding.instruction_set, "A64")

        zero = (BitValueType.Bound, Bit.Zero)
        self.assertEqual(encoding.getBit(0), zero)
        self.assertEqual(encoding.getBitRange(0,3), [zero] * 3)

class TestInstruction(unittest.TestCase):

    @staticmethod
    def instruction_without_alias_xml():
        return("""
        <instructionsection type="instruction">
          <heading>Example</heading>
          <alias_list howmany="0">
          </alias_list>
          <classes>""" +
               TestEncoding.xml() +
          """
          </classes>
        </instructionsection>""")

    @staticmethod
    def instruction_with_alias_xml():
        return("""
        <instructionsection type="instruction">
          <heading>Example</heading>
          <alias_list howmany="1">
            <aliasref aliasfile="alias.xml"></aliasref>
          </alias_list>
          <classes>""" +
               TestEncoding.xml() +
          """
          </classes>
        </instructionsection>""")

    @staticmethod
    def alias_xml():
        return("""
        <instructionsection type="alias">
          <heading>Alias</heading>
          <aliasto refiform="example.xml"></aliasto>
          <classes>""" +
               TestEncoding.xml() +
          """
          </classes>
        </instructionsection>""")

    def test_parse(self):
        # No aliases
        instruction = Instruction("example.xml",
                                  parseSingleNode(TestInstruction.instruction_without_alias_xml()))
        self.assertEqual(instruction.name, "Example")
        self.assertEqual(len(instruction.encodings), 1)
        instruction.update_alias_references(dict([("example.xml", instruction)]))
        self.assertEqual(instruction.aliaslist, set([]))

        # With aliases
        aliased_instruction = Instruction("example.xml",
                                          parseSingleNode(TestInstruction.instruction_with_alias_xml()))
        alias = Instruction("alias.xml",
                            parseSingleNode(TestInstruction.alias_xml()))
        filename_inst_dict = dict([
            ("example.xml", aliased_instruction),
            ("alias.xml", alias)
        ])
        aliased_instruction.update_alias_references(filename_inst_dict)
        self.assertEqual(aliased_instruction.aliaslist, set([alias]))
        alias.update_alias_references(filename_inst_dict)
        self.assertEqual(alias.aliasto, aliased_instruction)

def main():
    unittest.main()

if __name__ == "__main__":
    main()
