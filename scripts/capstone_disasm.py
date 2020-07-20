# This script is for comparing this project's generated disassembler against a known good
# comparison. The Python binding for [Capstone](http://www.capstone-engine.org) must be installed.
# The bulk of this script comes from the [Capstone docs](http://www.capstone-engine.org/lang_python.html)

from capstone import *
import sys

if __name__ == "__main__":
   if(len(sys.argv) != 2):
      print("Just the path of binary file must be given.")
      exit

   with open(sys.argv[1], mode='rb') as file:
      CODE = file.read()

   md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
   for i in md.disasm(CODE, 0x1000):
      print("0x%x:\t%s\t%s" %(i.address, i.mnemonic, i.op_str))
