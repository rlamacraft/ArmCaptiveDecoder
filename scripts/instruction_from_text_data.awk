# Given the .text contents of a binary file (using objdump), we want to extract just the 32-bit instruction data for passing through our own disassembler.
$1 ~ /[0-9a-f]{3}:/ { print $2, $3 }
