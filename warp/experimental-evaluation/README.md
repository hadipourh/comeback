# Experimental Verification

## Boomerang Distinguishers

We have provided the required codes to verify the probability of our boomerang distinguishers experimentally. To specify the input/output differences, the number of rounds for boomerang distinguisher, and the number of boomerang queries open [`boomerang.h`](boomerang.h) and adjust the corresponding variables. For example, the setting of the experimental verification for the 10-round middle part in our 14-round boomerang distinguisher is as follows:

```c
const int DEG1 = 13;
const int DEG2 = 13;
const int NUMBER_OF_EXPERIMENTS = 10;   // Number of independent experiments
const int NUMBER_OF_ROUNDS = 10;   // Number of rounds

char DP_STR[] = "0a000000000000000000000000000000";
char DC_STR[] = "0000a000000000000000000000000000";
```

`DEG1` and `DEG2` specify the total number of boomerang queries $2^{(DEG1 + DEG2)}$. More precisely, the code performs $2^{DEG1}$ bunch of boomerang queries, including $2^{DEG2}$ boomerang queries each, such that a new random master key is used for each bunch. This experiment is repeated 10 times to compute the average number of returned boomerangs. To compile the code and then perform the experimental evaluation, run the following commands:

```sh
make
./boomerang 0
```

## Differential Distinguishers

We have also prepared a code to experimentally verify the differential probability of differential hulls. For example, to experimentally verify the differential probability of the 6-round differential for $E_{0}$ in our 23-round boomerang distinguisher for WARP, you can open [`boomerang.h`](boomerang.h) and modify it as follows:

```c
const int DEG1 = 2;
const int DEG2 = 27;
const int NUMBER_OF_EXPERIMENTS = 5;   // Number of independent experiments
const int NUMBER_OF_ROUNDS = 6;   // Number of rounds

char DP_STR[] = "00000000aaaaaaaa0a00aa00000a000a";
char DC_STR[] = "a0000000000000000000000000000000";
```

To compile the code and then perform the experimental evaluation use the following commands:

```sh
make
./diff 0
```
