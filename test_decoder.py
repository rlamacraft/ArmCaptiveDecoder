import unittest
from decoder import *
from test_parser import *

class TestEncodingsSet(unittest.TestCase):

    def test_append(self):
        encoding_set = EncodingsSet(set(), {})
        encoding = Encoding(parseSingleNode(TestEncoding.xml()).childNodes[0], None)
        encoding_set.append(encoding)
        self.assertEqual(encoding_set.encodings, set([encoding]))

    def test_split(self):
        encoding_zero = Encoding(parseSingleNode(TestEncoding.xml()).childNodes[0], None)
        encoding_one = Encoding(parseSingleNode(TestEncoding.xml().replace('0','1',1)).childNodes[0], None)
        encoding_set = EncodingsSet(set([encoding_zero, encoding_one]), {})
        sets = encoding_set.split(0)
        for enc_set in sets:
           shared_bits = enc_set.shared_bits
           self.assertEqual(len(enc_set.encodings), 1)
           encoding = list(enc_set.encodings)[0]
           self.assertEqual(encoding.getBit(0), (BitValueType.Bound, shared_bits[0]))

def main():
    unittest.main()

if __name__ == "__main__":
    main()
