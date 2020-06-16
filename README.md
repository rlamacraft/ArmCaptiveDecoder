# ArmCaptiveDecoder
Program for generating an instruction decoder for Captive derived from the ARM ISA specification

# ARM Specification
This program will be fed by the machine readable ARM spec, which can be downloaded from [this link](https://developer.arm.com/-/media/developer/products/architecture/armv8-a-architecture/ARMv82A-SysReg-00bet3.1.tar.gz). This should then be stored, within this project, in the directory "spec".

# Project Structure

TODO

## Scripts

### instruction_types.awk
For determining the number of instruction types from the Captive project's decode file - obviously should not be considered a complete set. 

Example
```sh
awk -f instruction_types.awk <<captive/arch/aarch64/aarch64-decode.cpp>>
```

This script is purely for development purposes and should be removed when no longer needed.
