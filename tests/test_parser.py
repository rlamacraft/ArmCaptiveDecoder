import os
import sys
sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '..') ))

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
    return(parseString(xmlString))

class TestBitSequence(unittest.TestCase):

    def unbound(self):
        return(BitSequence(parseSingleNode('<box hibit="31" name="sf"><c></c></box>').childNodes[0], False))

    def bound(self):
        return(BitSequence(parseSingleNode('<box hibit="31" name="sf" width="2"><c>0</c><c>1</c></box>').childNodes[0], False))

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
        self.assertEqual(str(unbound), "x")
        bound = self.bound()
        self.assertEqual(str(bound), "01")

class TestEncoding(unittest.TestCase):

    @staticmethod
    def xml_specified(specified_bit_dict):
        out = ""
        out += '<iclass isa="A64">\n'
        out += '<regdiagram form="32">\n'
        out += '<box hibit="31" name="sf" width="32">'
        for i in range(0,32):
            if i in specified_bit_dict:
                out += '<c>' + specified_bit_dict[i] + '</c>'
            else:
                out += '<c>x</c>'
        out += '</box>'
        out += '</regdiagram>'
        out += '</iclass>'
        return(out)

    @staticmethod
    def xml():
        return TestEncoding.xml_specified(dict([(i,'0') for i in range(0,32)]))

    def test_parse(self):
        encoding = Encoding(parseSingleNode(TestEncoding.xml()).childNodes[0], None)
        self.assertEqual(encoding.instruction_set, "A64")

        zero = (BitValueType.Bound, Bit.Zero)
        self.assertEqual(encoding.getBit(0), zero)
        self.assertEqual(encoding.getBitRange(0,3), [zero] * 3)

    def test_named_bit_sequences(self):
        encoding = Encoding(parseSingleNode(TestEncoding.xml()).childNodes[0], None)
        bit_sequences = encoding.named_bit_sequences()
        self.assertEqual(len(bit_sequences), 1)
        self.assertEqual(bit_sequences[0].name, "sf")

        modified_xml = re.sub(r'name="sf" ',"",TestEncoding.xml())
        encoding = Encoding(parseSingleNode(modified_xml).childNodes[0], None)
        bit_sequences = encoding.named_bit_sequences()
        self.assertEqual(len(bit_sequences), 0)

    def test_get_size_of_unbound_sequences(self):
        encoding = Encoding(parseSingleNode(TestEncoding.xml_specified({
            3: '0',
            7: '1'
        })).childNodes[0], None)
        self.assertEqual(encoding.get_size_of_unbound_sequences(), {
            3: 2,
            24: 1
        })

        encoding = Encoding(parseSingleNode(TestEncoding.xml_specified({
            31: '0',
        })).childNodes[0], None)
        self.assertEqual(encoding.get_size_of_unbound_sequences(), {
            31: 1,
        })

class TestInstruction(unittest.TestCase):

    @staticmethod
    def instruction_without_alias_xml():
        return("""
        <instructionsection type="instruction">
          <docvars></docvars>
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
          <docvars></docvars>
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
          <docvars></docvars>
          <heading>Alias</heading>
          <aliasto refiform="example.xml"></aliasto>
          <classes>""" +
               TestEncoding.xml() +
          """
          </classes>
        </instructionsection>""")

    def test_parse_docvars(self):
        docvars = Instruction.parse_docvars(parseString("""
        <inst>
        <docvars>
          <docvar key="foo" value="bar" />
        </docvars>
        </inst>
        """))
        self.assertEqual(docvars['foo'], 'bar')

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
