import argparse
import distutils.util
from parser import parseAllFiles


parser = argparse.ArgumentParser(description='Query the instruction data parsed from the spec files.')
parser.add_argument('-c', dest='output_count', action='store_const', const=True, default=False,
                    help='Count the number of results and output that only')
parser.add_argument('-a', dest='include_aliases', action='store_const', const=True, default=False,
                    help='Toggle for whether to include aliases.')

parser.add_argument('--q-name', dest='query_name', action='store',
                    help='Filter the instructions by their name')
parser.add_argument('--q-filename', dest='query_filename', action='store',
                    help='Filter the instructions by the specified filename.')
parser.add_argument('--q-mnemonic', dest='query_mnemonic', action='store',
                    help='Filter the instructions by the specified mnemonic.')
parser.add_argument('--q-encoding-count', dest='query_encoding_count', action='store',
                    help='Filter the instructions by the number of encodings that they have,')

args = parser.parse_args()

if(args.query_mnemonic is not None and any(filter(str.islower, args.query_mnemonic))):
   print("Are you sure the query is correct? Mnemonic should be all uppercase.")

instructions = parseAllFiles(include_aliases=args.include_aliases)

filtered_instructions = [i for i in instructions if
                         (args.query_name == None or i.name == args.query_name) and
                         (args.query_filename == None or i.fileName == args.query_filename) and
                         (args.query_mnemonic == None or i.mnemonic == args.query_mnemonic) and
                         (args.query_encoding_count == None or str(len(i.encodings)) == args.query_encoding_count)
]

if(args.output_count):
   print(len(filtered_instructions))
else:
   if(len(filtered_instructions) > 10):
      print("There are", len(filtered_instructions), "results. Print all?")
      if(not distutils.util.strtobool(input())):
         exit()
   print("")
   for inst in filtered_instructions:
      print('---', inst.name, '---')
      print("")
      print("   Filename:", inst.fileName)
      print("   Mnemonic:", inst.mnemonic)
      if(args.include_aliases):
         print("   Is Alias:", inst.is_alias)
      print("   Encodings:")
      for enc in inst.encodings:
         print("    ", enc)
      print("")
