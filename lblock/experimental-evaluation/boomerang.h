#include <stdio.h>
#include <stdlib.h>  // rand(), srand()
#include <math.h>
#include <stdint.h>
#include <string.h>
#include <omp.h>
#include <time.h>    // time()
#include <stdbool.h>
#include <sys/random.h>
#include "lblock.h"

#define Nthreads 1
#define STEP ((1 << 10) - 1)

typedef unsigned long long int UINT64;
void print_state(u8 *m);
UINT64 boomerang(int R, int N3, u8 *dp, u8 *dc);
double send_boomerangs(int R, int N1, UINT64 N2, UINT64 N3, u8 *dp, u8 *dc);
void convert_hexstr_to_statearray(char hex_str[], u8 dx[8]);
unsigned int init_prng(unsigned int offset);

// #######################################################################################################
// #######################################################################################################
// ############################## User must change only the following lines ##############################
const int DEG1 = 13;
const int DEG2 = 13;
int NUMBER_OF_EXPERIMENTS = 4;   // Number of independent experiments
int NUMBER_OF_ROUNDS = 8;   // Number of rounds

char DP_STR[] = "0000010000000000";
char DC_STR[] = "0000000030000000";

// #######################################################################################################
// #######################################################################################################
