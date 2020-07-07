#include <iostream>
#include <stdio.h>
#include "../../out/disasm.cpp"

using namespace captive::arch::aarch64;

int main() {

  uint32_t ir = 0x11000000;
  disasm(ir);

  return 0;
}
