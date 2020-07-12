# ArmCaptiveDecoder
Program for generating an instruction decoder for [Captive](https://github.com/tspink/captive) derived from the ARM ISA specification.

# Installation and Executing 

1. Install `python3`
2. Install the following with pip
    1. [Jinja2](https://jinja.palletsprojects.com/en/2.11.x/intro/#installation)
3. Then, clone the repo
4. Decompressed [ARM spec](https://developer.arm.com/-/media/developer/products/architecture/armv8-a-architecture/A64_v82A_ISA_xml_00bet3.1.tar.gz) and symlink the `A64_v82A_ISA_xml_00bet3.1` directory to `spec/`
5. Run `main.py` 
6. Output c++ files can be found in `out/` directory

# Project Structure

## Scripts

General development scripts

### instruction_types.awk
For determining the number of instruction types from the Captive project's decode file - obviously should not be considered a complete set. 

Example
```sh
awk -f instruction_types.awk <<captive/arch/aarch64/aarch64-decode.cpp>>
```

### end_of_block.awk
For finding all of the instructions that trigger the end of a block, so that it can be determined what property of the instructions in the XML spec files determines this.

To execute,
```sh
awk -f end_of_block.awk <<captive/arch/aarch64/aarch64-decode.cpp>> | sort | uniq | grep "true"
```

## Src

Source Code

### Disasm

A standalone disassembler that uses the generated decoder to disasemble a given ARM binary

#### Compile

```sh
gcc main.cpp -o decode.o -lstdc++ -Wno-c++11-extensions
```

### Generate Decoder

The code for parsing the ISA spec's XML files, generated decoder, and outputing that as C++ code in a created root-level "out" directory

#### main.py

This is what parses the XML files, builds the decoder, and generates the C++ files in the /out directory

#### query_parsed_instruction_data.py

A simple program for querying the parsed instruction data - useful for when the output of the generated code, disassembler, or other part of the system outputs a piece of info about an instructions but not enough to aid with the debugging process e.g. the mnemonic is printed by the disassembler but the filename from which the decode is derived from is useful to know.

The command line args are explorable through the standard usage and help mechanics

#### Other files

All other files in this directory are modules that are called by the above scripts.

## Templates

These are the files that Jinja2 uses to generated the output C++ files.

## Tests

Unit tests
