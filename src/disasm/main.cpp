#include <fstream>
#include <iostream>
#include <stdio.h>
#include "../../out/disasm.cpp"

using namespace captive::arch::aarch64;

int main(int argc, char *argv[]) {

  if(argc != 2) {
    printf("Insufficient args. Specify binary instructions.\n");
    return 1;
  }

  unsigned char bytes[4];
  int sum = 0;
  FILE *fp = fopen(argv[1], "rb");
  while( fread(bytes, 4, 1, fp) != 0) {
    sum = bytes[0] | (bytes[1]<<8) | (bytes[2]<<16) | (bytes[3]<<24);
    printf("%08x ", sum);
    disasm(sum);
  }

  return 0;
}
