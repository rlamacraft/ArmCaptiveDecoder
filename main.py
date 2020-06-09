import itertools
from parser import parseAllFiles
from decoder import EncodingsSet, findCommonBitsAndSplitRecursively


if __name__ == "__main__":
    instructions = parseAllFiles()
    print("Parsed", len(instructions), "instructions.")

    encodings = list(itertools.chain(*[inst.encodings for inst in instructions]))
    encoding_set = EncodingsSet(set(encodings), {})
    [print(str(encoding_set)) for encoding_set in findCommonBitsAndSplitRecursively(encoding_set)]
