# Generates a count of all of the types of instructions
#  where we define type to be the pointer type that the
#  operands are assigned to in the Captive project's
#  decode file (arch/aarch64/aarch64-decode.cpp) e.g.
#  "((aarch64_decode_a64_SYSTEM&)*this)..." -> SYSTEM
# Just run this AWK script with that file as arg
$1 == "opcode" { opcode = $3 }
$1 ~ /aarch/ {
    match($0, / *\(\(aarch64_decode_a64_/);
    prefix_length = RLENGTH + 1;
    category_length = match($0, "&") - prefix_length ;
    opcode_category[opcode] = substr($0, prefix_length, category_length);
}
END {
    for (opcode in opcode_category){
        category = opcode_category[opcode];
        category_inst_count[category] += 1;
    }
    for (category in category_inst_count)
        print category, category_inst_count[category];
}
