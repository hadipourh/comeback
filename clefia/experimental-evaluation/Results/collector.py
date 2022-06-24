import sys
from math import log2
if __name__ == "__main__":
    assert(len(sys.argv) > 1)
    nr = sys.argv[1]
    ntasks = int(sys.argv[2])
    total_num_of_boomerangs = 0
    num_of_returned_boomerangs = 0
    for i in range(ntasks):
        with open(f"result_{nr}_{i}.txt") as fl:
            result = fl.readlines()
            total_num_of_boomerangs += 2**int(result[-2].split(" = ")[1].split("^")[1])
            num_of_returned_boomerangs += int(result[-1].split(" = ")[1][:-1])
    if num_of_returned_boomerangs != 0:
        avg_pr_log2 = log2(num_of_returned_boomerangs) - log2(total_num_of_boomerangs)
    else:
        avg_pr_log2 = "-inf"
    print("Total number of returned boomerangs: %d" % num_of_returned_boomerangs)
    print("Total number of queries: 2^(%0.02f)" % log2(total_num_of_boomerangs))
    if num_of_returned_boomerangs != 0:
        print("Average probability: 2^(%.02f)" % avg_pr_log2)
    else:
        print("Average probability: 2^(-inf)")