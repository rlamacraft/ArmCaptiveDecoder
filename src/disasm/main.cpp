#include <fstream>
#include <iostream>
#include <stdio.h>
#include <time.h>
#include "../../out/disasm.cpp"

using namespace captive::arch::aarch64;

#define ONE_MB_INST_DATA 25 * 100 * 1000
#define NUM_OF_INSTRUCTIONS ONE_MB_INST_DATA

int main(int argc, char *argv[]) {

  if(argc != 2) {
    printf("Insufficient args. Specify binary instructions.\n");
    return 1;
  }

  unsigned char bytes[4];
  int sum = 0;
  FILE *fp = fopen(argv[1], "rb");
  uint32_t inst_data[NUM_OF_INSTRUCTIONS];
  int index = 0;
  while( fread(bytes, 4, 1, fp) != 0) {
    if(index == NUM_OF_INSTRUCTIONS) {
      printf("Reading more instructions than expected\n");
      return 1;
    }
    inst_data[index++] = bytes[0] | (bytes[1]<<8) | (bytes[2]<<16) | (bytes[3]<<24);
  }

  clock_t begin = clock();

  for(int i = 0; i < NUM_OF_INSTRUCTIONS; i++) {
    // printf("%08x ", inst_data[i]); 
    disasm(inst_data[i]);
  }

  clock_t end = clock();
  double time_spent = (double)(end - begin) / CLOCKS_PER_SEC;
  printf("%f\n", time_spent);

  return 0;
}
