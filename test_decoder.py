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
        return(Encoding(parseSingleNode(TestEncoding.xml().replace('0','1',1)).childNodes[0], None))

    @staticmethod
    def two_encoding():
        """All zeros, except 0th and 1st which are 1"""
        return(Encoding(parseSingleNode(TestEncoding.xml().replace('0','1',2)).childNodes[0], None))

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

    def test_split_many(self):
        encoding_set = TestEncodingsSet.zero_and_one()
        encoding_set.append(TestEncodingsSet.two_encoding())

        sets = [set for set in encoding_set.splitMany([0,1]) if len(set) > 0]
        self.assertEqual(len(sets), 3)

        encoding_set = TestEncodingsSet.zero_and_one()
        sets = [set for set in encoding_set.splitMany([0,1]) if len(set) > 0]
        self.assertEqual(len(sets), 2)

    def test_encodingsOrderedByIncreasingUnbound(self):
        encoding_zero = Encoding(parseSingleNode(TestEncoding.xml()).childNodes[0], None)
        encoding_one = Encoding(parseSingleNode(TestEncoding.xml().replace('0','x',1)).childNodes[0], None)
        encoding_set = EncodingsSet(set([encoding_zero, encoding_one]), {})
        self.assertEqual(encoding_set.encodingsOrderedByIncreasingUnbound(), [encoding_zero, encoding_one])

def main():
    unittest.main()

if __name__ == "__main__":
    main()
