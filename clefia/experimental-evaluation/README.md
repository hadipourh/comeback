# Experimental Verification

## Boomerang Distinguishers

We have provided the required codes to verify the probability of our boomerang distinguishers experimentally. To specify the input/output differences, the number of rounds for boomerang distinguisher, as well as the number of boomerang queries open [`boomerang.h`](boomerang.h) and adjust the corresponding variables. Next, to compile the code and then perform the experimental evaluation, run the following commands:

```sh
make
./boomerang 0
```

To see more details about the parameters in [`boomerang.h`](boomerang.h) please refer to [the README of WARP](warp/experimental-evaluation/README.md).

## Differential Distinguishers

We have also prepared a code to experimentally verify the differential probability of differential hulls. For example, to experimentally verify the differential probability of the 2-round differential for $E_{0}$ in our 8-round boomerang distinguisher for CLEFIA, you can open [`boomerang.h`](boomerang.h) and modify it as follows:

```c
const int DEG1 = 14;
const int DEG2 = 15;
int NUMBER_OF_EXPERIMENTS = 5;   // Number of independent experiments
int NUMBER_OF_ROUNDS = 2;   // Number of rounds

char DP_STR[] = "2bfcd77e9d96be910000000000000008";
char DC_STR[] = "00000000000000080000000000000000";
```

Next, to compile the code and evaluate the probability of the corresponding differential hull experimentally, run the following commands:

```
make
./diff 0
```