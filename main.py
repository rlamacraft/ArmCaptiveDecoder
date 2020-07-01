import itertools
from parser import parseAllFiles
from decoder import EncodingsSet, findCommonBitsAndSplitRecursively
from code_generator import generate_code

def pop_many(count, initial_set):
    output_set = set()
    for i in range(0,count):
        output_set |= {initial_set.pop()}
    return(output_set)

def frequency_of_length_of_unbound_bit_sequences(encodings):
    aggregate_dict = dict([(i,0) for i in range(32)])
    for enc in encodings:
        for (k,v) in enc.get_size_of_unbound_sequences().items():
            aggregate_dict[k] += v
    for k,v in aggregate_dict.items():
        print(k,",",v)

if __name__ == "__main__":
    instructions = parseAllFiles()
    # print("Parsed", len(instructions), "instructions.")

    encodings = list(itertools.chain(*[inst.encodings for inst in instructions]))
    # print(len(encodings), "encodings found.")

    # encoding_set = EncodingsSet(set(encodings), {})
    # encodings_sets = set(list(findCommonBitsAndSplitRecursively(encoding_set)))

    # [print(str(es)) for es in encodings_sets]

    # generate_code(encodings_sets, instructions)

    # for enc in [e for e in encodings if "branch" in e.psname]:
    #     print(enc.instruction.fileName, enc.psname)
    #     print(enc)

    # frequency_of_length_of_unbound_bit_sequences(encodings)
