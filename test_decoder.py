import unittest
from decoder import *
from test_parser import *

class TestEncodingsSet(unittest.TestCase):

    @staticmethod
    def zero_encoding():
        """All zeros"""
        return(Encoding(parseSingleNode(TestEncoding.xml()).childNodes[0], None))

    @staticmethod
    def one_encoding():
        """All zeros, except 0th which is 1"""
        return(Encoding(parseSingleNode(TestEncoding.xml_specified(dict([(i,'1' if i == 0 else '0') for i in range(0,32)]))).childNodes[0], None))

    @staticmethod
    def two_encoding():
        """All zeros, except 0th and 1st which are 1"""
        return(Encoding(parseSingleNode(TestEncoding.xml_specified(dict([(i,'1' if i < 2 else '0') for i in range(0,32)]))).childNodes[0], None))

    @staticmethod
    def zero_and_one(shared_bits=dict()):
        return(EncodingsSet(set([
            TestEncodingsSet.zero_encoding(),
            TestEncodingsSet.one_encoding()
        ]), shared_bits))

    def test_init(self):
        try:
            TestEncodingsSet.zero_and_one({0: Bit.Zero})
        except AssertionError:
            pass
        except:
            self.fail("Incorrect error thrown")
        else:
            self.fail("Shared_bits not validated")

    def test_append(self):
        encoding_set = EncodingsSet(set(), {0: Bit.Zero})
        encoding = TestEncodingsSet.zero_encoding()
        encoding_set.append(encoding)
        self.assertEqual(encoding_set.encodings, set([encoding]))

        try:
            encoding_set.append(TestEncodingsSet.one_encoding())
        except AssertionError:
            pass
        except:
            self.fail("Incorrect error thrown")
        else:
            self.fail("Shared_bits not validated")

    def test_split(self):
        sets = TestEncodingsSet.zero_and_one().split(0)
        for enc_set in sets:
           shared_bits = enc_set.shared_bits
           self.assertEqual(len(enc_set.encodings), 1)
           encoding = list(enc_set.encodings)[0]
           self.assertEqual(encoding.getBit(0), (BitValueType.Bound, shared_bits[0]))

    def test_splitMany(self):
        encoding_set = TestEncodingsSet.zero_and_one()
        encoding_set.append(TestEncodingsSet.two_encoding())

        sets = [set for set in encoding_set.splitMany([0,1]) if len(set) > 0]
        self.assertEqual(len(sets), 3)

        encoding_set = TestEncodingsSet.zero_and_one()
        sets = [set for set in encoding_set.splitMany([0,1]) if len(set) > 0]
        self.assertEqual(len(sets), 2)

    def test_findOtherCommonlyBoundBits(self):
        encodings_set = TestEncodingsSet.zero_and_one({1: Bit.Zero})
        self.assertEqual(encodings_set.findOtherCommonlyBoundBits(), set(range(2,32)) | set([0]))

        empty_encodings_set = EncodingsSet(set(), dict())
        self.assertEqual(empty_encodings_set.findOtherCommonlyBoundBits(), set(range(0,32)))

    def test_splitOnCommonBoundBits(self):
        zeros_and_unbound = Encoding(parseSingleNode(TestEncoding.xml_specified({0:'0'})).childNodes[0], None)
        one_and_unbound = Encoding(parseSingleNode(TestEncoding.xml_specified({0:'1'})).childNodes[0], None)
        encodings_set = EncodingsSet(set([zeros_and_unbound, one_and_unbound]), dict())
        sets = encodings_set.splitOnCommonBoundBits()
        self.assertEqual(len(sets), 2)

    def test_encodingsOrderedByIncreasingUnbound(self):
        encoding_zero = Encoding(parseSingleNode(TestEncoding.xml_specified(dict([(i,'0') for i in range(0,32)]))).childNodes[0], None)
        encoding_one = Encoding(parseSingleNode(TestEncoding.xml_specified(dict([(i,'0') for i in range(1,32)]))).childNodes[0], None)
        encoding_set = EncodingsSet(set([encoding_zero, encoding_one]), {})
        self.assertEqual(encoding_set.encodingsOrderedByIncreasingUnbound(), [encoding_zero, encoding_one])

def main():
    unittest.main()

if __name__ == "__main__":
    main()
