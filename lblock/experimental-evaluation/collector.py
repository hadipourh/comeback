import sys
from math import log2
if __name__ == "__main__":
    assert(len(sys.argv) > 1)
    nr = sys.argv[1]
    ntasks = int(sys.argv[2])
    total_num_of_boomerangs = 0
    num_of_returned_boomerangs = 0
    for i in range(ntasks):
        with open(f"result_{nr}_{i}") as result:
            total_num_of_boomerangs += int(result[-2].split(" = ")[1].split("^")[1])
            num_of_returned_boomerangs += int(result[-1].split(" = ")[1][:-1])
    avg_pr = log2(num_of_returned_boomerangs) - log2(ntasks) - log2(total_num_of_boomerangs)
    print("Average probability: 2^-({%0.02f})".format(avg_pr))
