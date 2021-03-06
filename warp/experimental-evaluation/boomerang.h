#include <stdio.h>
#include <stdlib.h>  // rand(), srand()
#include <math.h>
#include <stdint.h>
#include <string.h>
#include <omp.h>
#include <time.h>    // time()
#include <stdbool.h>
#include <sys/random.h>

#define Nthreads 1
#define STEP ((1 << 10) - 1)

typedef unsigned long long int UINT64;

void print_state(int *m);
UINT64 boomerang(int R, int N3, int* dp, int* dc);
double send_boomerangs(int R, int N1, UINT64 N2, UINT64 N3, int *dp, int *dc);
void convert_hexstr_to_statearray(char hex_str[], int dx[32]);
unsigned int init_prng(unsigned int offset);


// #######################################################################################################
// #######################################################################################################
// ############################## User must change only the following lines ##############################
const int DEG1 = 10;
const int DEG2 = 28;
const int NUMBER_OF_EXPERIMENTS = 10;   // Number of independent experiments
const int NUMBER_OF_ROUNDS = 10;   // Number of rounds

char DP_STR[] = "0a000000000000000000000000000000";
char DC_STR[] = "0000a000000000000000000000000000";
// #######################################################################################################
// #######################################################################################################
