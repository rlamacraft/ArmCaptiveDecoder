# This is for measuring how different decoder optimisations end up affecting the disassembler that
#  they are used within. This script will execute all binaries in a given directory, passing each
#  a provided 1 MB file of random data. This is not expected to reflect the actual time to
#  disassemble an actual executable of such a size given that the vast majority of instructions
#  will be "unknown" and thus take much longer to decode -- we're simply interested in the
#  relative performance to identify which optimisations are best

import sys
import os
from os.path import isfile, join
import subprocess

directory = sys.argv[1]
files = [f for f in os.listdir(directory) if isfile(join(directory, f)) and os.access(join(directory, f), os.X_OK)]

binary_file = sys.argv[2]
iterations = 3

for file in files:
    sum = 0
    for i in range(0,iterations):
        res = subprocess.run("%s%s %s" % (directory, file, binary_file), shell=True, capture_output=True)
        if(res.stderr != b''):
            print(res.stderr)
            exit()
        sum += float(res.stdout)
    print("%20s" % file, str(sum / iterations)) # currently prints the mean average
