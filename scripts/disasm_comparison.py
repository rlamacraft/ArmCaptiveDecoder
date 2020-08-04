# This is script is for generating comparison statistics between the disassemble outputs of objdump, capstone, and my disassembler.

import sys

directory = sys.argv[1]
# files = [f for f in os.listdir(directory) if isfile(join(directory, f)) and os.access(join(directory, f), os.X_OK)]

all_different = 0
d_and_c_and_not_o = 0
d_and_o_and_not_c = 0
o_and_c_and_not_d = 0
all_same = 0

with open(directory + 'my_disasm.txt', 'r') as my_disasm:
    with open(directory + 'capstone.txt', 'r') as capstone:
        with open(directory + 'objdump.txt', 'r') as objdump:
           for i in range(109):
               d = my_disasm.readline()
               c = capstone.readline()
               o = objdump.readline()
               if c == d == o:
                   all_same += 1
               elif c == d != o:
                   d_and_c_and_not_o += 1
               elif d == o != c:
                   d_and_o_and_not_c += 1
               elif c == o != d:
                   o_and_c_and_not_d += 1
               else:
                   all_different += 1

print("all_different:", all_different, all_different / 109)
print("d + c - o:", d_and_c_and_not_o, d_and_c_and_not_o / 109)
print("d + o - c:", d_and_o_and_not_c, d_and_o_and_not_c / 109)
print("o + c - d:", o_and_c_and_not_d, o_and_c_and_not_d / 109)
print("all_same:", all_same, all_same / 109)
