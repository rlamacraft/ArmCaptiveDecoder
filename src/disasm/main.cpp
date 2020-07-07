#include <iostream>
#include <stdio.h>
#include "../../out/arm64-decode.cpp"
using namespace captive::arch::aarch64;
int main() {

  captive::arch::aarch64::aarch64_decode_a64 thing;
  thing.isa_mode = aarch64_decode_a64::aarch64_a64;
  uint64_t pc = 0x0000000000000000;
  uint32_t ir = 0x11000000;
  uint32_t* ptr = &ir;
  bool is_valid = thing.decode(0, pc, ptr);
  if(thing.opcode == aarch64_decode_a64::op_aarch64_a64_add_addsub_imm_no_s) {
    printf("add imm\n");
  }

  return 0;
}
