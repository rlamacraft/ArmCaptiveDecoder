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

## Templates

These are the files that Jinja2 uses to generated the output C++ files.

## Tests

Unit tests
