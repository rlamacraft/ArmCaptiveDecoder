# Listes all of the instructions that set the `end_of_block` variable
#  To list the instructions that trigger the end of a block, run this AWK
#  script and then pipe into sort, uniq, and grep "true"
$1 == "opcode" { print(opcode, end_of_block); opcode = $3; end_of_block = "false"; }
$1 ~ "end_of_block" { end_of_block = $3; }
