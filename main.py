import itertools
from parser import parseAllFiles
from decoder import EncodingsSet, findCommonBitsAndSplitRecursively
from code_generator import generate_code

def pop_many(count, initial_set):
    output_set = set()
    for i in range(0,count):
        output_set |= {initial_set.pop()}
    return(output_set)

if __name__ == "__main__":
    instructions = parseAllFiles()
    # print("Parsed", len(instructions), "instructions.")

    encodings = list(itertools.chain(*[inst.encodings for inst in pop_many(3, instructions)]))
    encoding_set = EncodingsSet(set(encodings), {})
    encodings_sets = set(list(findCommonBitsAndSplitRecursively(encoding_set)))
    # [print(str(es)) for es in encodings_sets]

    print(generate_code(encodings_sets))
