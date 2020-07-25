#include <fstream>
#include <iostream>
#include <stdio.h>
#include <time.h>
#include "../../out/arm64-decode.cpp"

using namespace captive::arch::aarch64;

#define ONE_MB_INST_DATA 25 * 10 * 1000
#define LINUX_TEXT 3485966
#define NUM_OF_INSTRUCTIONS LINUX_TEXT
// #define NUM_OF_INSTRUCTIONS ONE_MB_INST_DATA

bool just_decode(uint32_t ir) {
  captive::arch::aarch64::aarch64_decode_a64 decoder;
  decoder.isa_mode = aarch64_decode_a64::aarch64_a64;
  uint64_t pc = 0x0000000000000000;
  uint32_t* ptr = &ir;
  bool is_valid = decoder.decode(0, pc, ptr);
  return is_valid;
}

int main(int argc, char *argv[]) {

  if(argc != 2) {
    printf("Insufficient args. Specify binary instructions.\n");
    return 1;
  }

  unsigned char bytes[4];
  int sum = 0;
  FILE *fp = fopen(argv[1], "rb");
  int index = 0;

  clock_t begin = clock();

  while( fread(bytes, 4, 1, fp) != 0) {
    if(index == NUM_OF_INSTRUCTIONS) {
      printf("Reading more instructions than expected\n");
      return 1;
    }
    just_decode(bytes[0] | (bytes[1]<<8) | (bytes[2]<<16) | (bytes[3]<<24));
    index++;
  }
  if(index != NUM_OF_INSTRUCTIONS) {
    printf("Didn't read enough data\n");
    return 1;
  }

  clock_t end = clock();
  double time_spent = (double)(end - begin) / CLOCKS_PER_SEC;
  printf("%f\n", time_spent);

  return 0;
}
