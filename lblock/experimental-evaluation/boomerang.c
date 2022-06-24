/*
Boomerang Analysis of LBlock
Date: Feb 10, 2020
 */

#include "boomerang.h"

FILE *fic;

unsigned int init_prng(unsigned int offset) {
    unsigned int initial_seed = 0;
    ssize_t temp;
    temp = getrandom(&initial_seed, sizeof(initial_seed), 0);
    if (temp == -1) perror("error!");
    initial_seed += offset;
    srand(initial_seed);
	printf("[+] PRNG initialized to 0x%08X\n", initial_seed);
    return initial_seed;
}

void print_state(u8 *m)
{
    for (int i = 0; i < 8; i++)
    {
        printf("%x ", m[i]&0xff);
    }
    printf("\n");
};

bool test()
{
    int R = 10;
    u8 p[8];
    u8 temp[8];
    u8 subkeys[R][4];
    u8 k[10];    
    for(int i = 0; i < 10; i++) 
    {
        k[i] = rand() & 0xff;
    }
    for(int i = 0; i < 8; i++) p[i] = rand() & 0xff;
    for(int i = 0; i < 8; i++) temp[i] = p[i];
    EncryptKeySchedule(R, k, subkeys);    
    Encrypt(R, p, subkeys);
    Decrypt(R, p, subkeys);    
    bool flag = true;
    for(int i = 0; i < 8; i++)
    {
        if (p[i] != temp[i])
        {
            flag = false;
            break;
        }
    }
    return flag;
}

UINT64 boomerang(int R, int N3, u8* dp, u8* dc)
{
    UINT64 num = 0;    
    for(int i = 0; i < 8; i++) dp[i] = dp[i] & 0xff;    
    for(int i = 0; i < 8; i++) dc[i] = dc[i] & 0xff;
    u8 k[10];
    u8 subkeys[R][4];
    u8 p1[8],p2[8];
    u8 c3[8],c4[8];
    // Randomly choose the master key
    for(int i = 0; i < 10; i++) 
    {
        k[i] = rand() & 0xff;
    }
    EncryptKeySchedule(R, k, subkeys);
	for (int t = 0; t < N3; t++){
        bool flag;
		// randomly choose p1
		for(int i = 0; i < 8; i++) p1[i] = rand() & 0xff;
        // compute p2
        for(int i = 0; i < 8; i++) p2[i] = p1[i] ^ dp[i];
        // compute c1 and c2 by encrypting p1 and p2, respectively
        Encrypt(R, p1, subkeys);
        Encrypt(R, p2, subkeys);
        // Derive c3 and c4
        for(int i = 0; i < 8; i++) c3[i] = p1[i] ^ dc[i];
        for(int i = 0; i < 8; i++) c4[i] = p2[i] ^ dc[i];
        // Compute p3 and p4 by decrypting c3 and c4, respectively
        Decrypt(R, c3, subkeys);
        Decrypt(R, c4, subkeys);
		flag = true;
        for (int i = 0; i < 8; i++)
        {
            if ((c3[i] ^ c4[i]) != dp[i])
            {
                flag = 0;
            }
        }
		if (flag) {num ++;}
	}
	return num;
}

double send_boomerangs(int R, int N1, UINT64 N2, UINT64 N3, u8 *dp, u8 *dc)
{
    // Parallel execution
    int NUM[N1];
    printf("#Rounds: %d rounds\n", R);
    printf("#Total Queries = (#Parallel threads) * (#Bunches per thread) * (#Queries per bunch) = %d * %llu * %llu = 2^(%f)\n", N1, N2, N3, log(N1 * N2 * N3) / log(2));
    printf("#Queries per thread = (#Bunches per thread) * (#Queries per bunch) = %llu * %llu = 2^(%f)\n", N2, N3, log(N2 * N3) / log(2));
    clock_t clock_timer;
    double wall_timer;
    clock_timer = clock();
    wall_timer = omp_get_wtime();
    omp_set_num_threads(N1);
    #pragma omp parallel for
    for (int counter = 0; counter < N1; counter++)
    {
        int num = 0;
        int ID = omp_get_thread_num();
        //init_prng(ID);
        for (UINT64 j = 0; j < N2; j++)
        {
            num += boomerang(R, N3, dp, dc);
            if ((j & STEP) == 0){
                printf("PID: %d  \t Bunch Number: %llu/%llu\n", ID, j, N2);
            }    
        } 
        NUM[ID] = num;
    }
    double elapsed_time = (double)(clock() - clock_timer) / CLOCKS_PER_SEC;
    printf("%s: %0.4f\n", "time on clock", elapsed_time);
    printf("%s: %0.4f\n", "time on wall", omp_get_wtime() - wall_timer);
    double sum = 0;
    double sum_temp = 1;
    for (int i = 0; i < N1; i++)
        sum += NUM[i];
    printf("sum = %f\n", sum);
    sum_temp = (double)(N1 * N2 * N3) / sum;

    printf("2^(-%f)\n", log(sum_temp) / log(2));
    printf("####################################\n");
    return sum;
}

void convert_hexstr_to_statearray(char hex_str[], u8 dx[8])
{
    for (int i = 0; i < 8; i++)
    {
        char hex[3];
        hex[0] = hex_str[2*i];
        hex[1] = hex_str[2*i + 1];
        hex[2] = '\0';
        dx[7 - i] = (u8)(strtol(hex, NULL, 16) & 0xff);
    }
}

int main(int argc, char *argv[])
{
    unsigned int task_id;
    task_id = atoi(argv[1]);
    unsigned int initial_seed;
    initial_seed = init_prng(task_id);
    u8 dp[8];
    u8 dc[8];
    bool check;
    check = test();
    printf("%s: %s\n", "Check decryption", check ? "true" : "false");
    convert_hexstr_to_statearray(DP_STR, dp);
    convert_hexstr_to_statearray(DC_STR, dc);
    //########################## Number of queries #########################
    int N1 = Nthreads;             // Number of parallel threads :  N1
    UINT64 N2 = (UINT64)1 << DEG1; // Number of bunches per thread: N2 = 2^(DEG1)
    UINT64 N3 = (UINT64)1 << DEG2; // Number of queries per bunch:  N3 = 2^(DEG2)
    //################### Number of total queries : N1*N2*N3 ###############
    double sum = 0;
    for (int i = 0; i < NUMBER_OF_EXPERIMENTS; i++)
    {
        sum += send_boomerangs(NUMBER_OF_ROUNDS, N1, N2, N3, dp, dc);
    }
    double temp = log(NUMBER_OF_EXPERIMENTS) + log(N1) + log(N2) + log(N3);
    char name[30];
    sprintf(name, "result_%d_%d.txt", NUMBER_OF_ROUNDS, task_id);
    fic = fopen(name, "w");
    fprintf(fic, "Initial seed 0x%08X\n", initial_seed);
    fprintf(fic, "Boomerang distinguisher for %d rounds of LBlock\n", NUMBER_OF_ROUNDS);
    fprintf(fic, "Input difference: \t %s\n", DP_STR);
    fprintf(fic, "Output difference: \t %s\n", DC_STR);
    double avg_pr = (temp - log(sum))/log(2);
    fprintf(fic, "Average probability = 2^(-%0.4f)\n", avg_pr);
    fprintf(fic, "Number of boomerangs thrown = 2^%d\n", (int)(temp/log(2)));
    fprintf(fic, "Number of boomerangs returned = %d\n", (int)sum);
    fclose(fic);
    printf("\nAverage probability = 2^(-%0.4f)\n", avg_pr);
    return 0;
}
