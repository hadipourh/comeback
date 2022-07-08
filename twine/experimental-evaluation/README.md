# Experimental Verification

We have provided the required codes to verify the probability of our boomerang distinguishers experimentally. To specify the input/output differences, the number of rounds for boomerang distinguisher, as well as the number of boomerang queries open [`boomerang.h`](boomerang.h) and adjust the corresponding variables. Next, to compile the code and then perform the experimental evaluation, run the following commands:

```sh
make
./boomerang 0
```

To see more details about the parameters in [`boomerang.h`](boomerang.h) please refer to [the README of WARP](warp/experimental-evaluation/README.md).