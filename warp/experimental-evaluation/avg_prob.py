#!/usr/bin/env python3
import numpy as np
from math import log2

if __name__ == '__main__':
    trials = {}
    with open('Results/middle_verification.txt', 'r') as f:
        for line in f:
            _, key, _, prob_txt = line.split()
            success, total = prob_txt[1:-1].split('/')
            trials[key] = (int(success), int(total))

    prob = np.zeros((len(trials),), dtype=np.double)
    total_successful = 0;
    total_trials = 0;
    for i, (success, total) in enumerate(trials.values()):
        prob[i] = success / total
        total_successful += success
        total_trials += total

    log_prob = np.log2(prob)
    total_prob = total_successful / total_trials
    print(f"overall probability: 2^{log2(total_prob):.2f} (2^{np.max(log_prob):.2f} ... 2^{np.min(log_prob):.2f})")



