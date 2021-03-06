#include <stdio.h>
#include <stdlib.h>  // rand(), srand()
#include <math.h>
#include <stdint.h>
#include <string.h>
#include <omp.h>
#include <time.h>    // time()
#include <stdbool.h>
#include <sys/random.h>
#include "clefia.c"

#define Nthreads 1
#define STEP ((1 << 10) - 1)

typedef unsigned long long int UINT64;
void print_state(unsigned char *data, int bytelen);
UINT64 diff(int R, int N3, unsigned char *dp, unsigned char *dc);
double send_diff(int R, int N1, UINT64 N2, UINT64 N3, unsigned char *dp, unsigned char *dc);
void convert_hexstr_to_statearray(char hex_str[], unsigned char dx[8]);
unsigned int init_prng(unsigned int offset);

// #######################################################################################################
// #######################################################################################################
// ############################## User must change only the following lines ##############################
const int DEG1 = 14;
const int DEG2 = 15;
int NUMBER_OF_EXPERIMENTS = 5;   // Number of independent experiments
int NUMBER_OF_ROUNDS = 2;   // Number of rounds

char DP_STR[] = "2bfcd77e9d96be910000000000000008";
char DC_STR[] = "00000000000000080000000000000000";
// #######################################################################################################
// #######################################################################################################
