#!/usr/bin/env python3

"""
Date: Dec 25, 2021
Author: Hosein Hadipour
"""

from argparse import ArgumentParser, RawTextHelpFormatter
from truncboom import TruncatedBoomerang
from diff import Diff
from plotdistinguisher import *
import time

def main():

    # # 9 rounds
    # r0, rm, r1 = 0, 9, 0
    # w0, wm, w1 = 1, 1, 1

    # 14 rounds
    #r0, rm, r1 = 2, 10, 2
    #w0, wm, w1 = 6, 3, 6

    # 15 rounds
    # r0, rm, r1 = 2, 10, 3
    # w0, wm, w1 = 6, 2, 6

    # 16 rounds
    # r0, rm, r1 = 3, 10, 3
    # w0, wm, w1 = 2, 2, 5

    # 20 rounds:
    # r0, rm, r1 = 5, 10, 5
    # w0, wm, w1 = 6, 3, 6

    # 21 rounds:
    # r0, rm, r1 = 5, 10, 6
    # w0, wm, w1 = 2, 1, 3

    # # 22 rounds:
    # r0, rm, r1 = 6, 10, 6
    # w0, wm, w1 = 2, 1, 2

    # 23 rounds
    # r0, rm, r1 = 6, 10, 7
    # w0, wm, w1 = 2, 1, 2

    parser = ArgumentParser(description="This tool finds the nearly optimum boomerang distinguisher\n"
                                         "Example:\n"
                                         "python3 boom.py -r0 6 -rm 10 -r1 7 -w0 2 -wm 1 -w1 2 --timelimit 1200",
                            formatter_class=RawTextHelpFormatter)
                        
    parser.add_argument('-i', '--inputfile', type=str, help="Use an input file in yaml format")
    parser.add_argument('-r0', '--r0', type=int,
                        help="number of rounds covered by E0")
    parser.add_argument('-rm', '--rm', type=int,
                        help="number of rounds covered by Em")
    parser.add_argument('-r1', '--r1', type=int,
                        help="number of rounds covered by E1")
    parser.add_argument('-w0', '--w0', type=int,
                        help="cost of active S-boxes in E0")
    parser.add_argument('-wm', '--wm', type=int,
                        help="cost of active S-boxes in Em")
    parser.add_argument('-w1', '--w1', type=int,
                        help="cost of active S-boxes in E1")
    parser.add_argument('-tl', '--timelimit', type=int,
                        help="time limit in seconds")
    parser.add_argument('-ns', '--numofsols', type=int,
                        help="number of solutions (currently disabled)")

    # Parse command line arguments and construct parameter list.
    args = parser.parse_args()
    params = loadparameters(args)
    r0, rm, r1 = params["r0"], params["rm"], params["r1"]
    w0, wm, w1 = params["w0"], params["wm"], params["w1"]

    assert(rm > 0)
    tex_content = tex_init()
    start_time = time.time()
    ##############################################################################################
    ##############################################################################################
    # Step1- Find a truncated boomerang trail
    bm = TruncatedBoomerang(r0=r0, r1=r1, rm=rm, w0=w0, w1=w1, wm=wm)
    bm.iterative = False
    bm.find_truncated_boomerang_trail()
    upper_trail, middle_part, lower_trail = bm.parse_solver_output()
    ##############################################################################################
    ##############################################################################################
    # Step2- Instantiate the upper/lower truncated trails with real differential trails
    diff_upper_trail = None
    diff_effect_upper = None
    if r0 != 0:
        time_limit = params["timelimit"]
        params = {"nrounds" : bm.r0,
                  "mode" : 0,
                  "startweight" : 0,
                  "endweight" : 128,
                  "timelimit" : time_limit,
                  "numberoftrails" : 1,
                  "fixedVariables" : {}}
        bin_of_0xa = ["1", "0", "1", "0"]
        for nibble in range(32):
            if upper_trail[f"x_0"][nibble] == "0":
                for bit in range(4):
                    params["fixedVariables"][f"x_{0}_{nibble}_{bit}"] = "0"
            if upper_trail[f"x_{bm.r0}"][nibble] == "0":
                for bit in range(4):
                    params["fixedVariables"][f"x_{bm.r0}_{nibble}_{bit}"] = "0"
            if upper_trail[f"x_{bm.r0}"][nibble] == "1":
                for bit in range(4):
                    params["fixedVariables"][f"x_{bm.r0}_{nibble}_{bit}"] = bin_of_0xa[bit]
        diff = Diff(params)
        diff.make_model()
        diff_upper_trail = diff.solve()
        params["fixedVariables"] = {"x_0": diff_upper_trail["x_0"], f"x_{bm.r0}": diff_upper_trail[f"x_{bm.r0}"]}
        params["mode"] = 2
        diff = Diff(params)
        diff.make_model()
        diff_effect_upper = diff.solve()
    ##############################################################################################
    diff_lower_trail = None
    diff_effect_lower = None
    if r1 != 0:
        time_limit = params["timelimit"]
        params = {"nrounds" : bm.r1,
                  "mode" : 0,
                  "startweight" : 0,
                  "endweight" : 128,
                  "timelimit" : time_limit,
                  "numberoftrails" : 1,
                  "fixedVariables" : {}}
        for nibble in range(32):
            if lower_trail[f"x_{bm.rm}"][nibble] == "0":
                for bit in range(4):
                    params["fixedVariables"][f"x_{0}_{nibble}_{bit}"] = "0"
            if lower_trail[f"x_{bm.rm}"][nibble] == "1":
                for bit in range(4):
                    params["fixedVariables"][f"x_{0}_{nibble}_{bit}"] = bin_of_0xa[bit]
            if lower_trail[f"x_{bm.R1}"][nibble] == "0":
                for bit in range(4):
                    params["fixedVariables"][f"x_{bm.r1}_{nibble}_{bit}"] = "0"
        diff = Diff(params)
        diff.make_model()
        diff_lower_trail = diff.solve()
        params["fixedVariables"] = {"x_0": diff_lower_trail["x_0"], f"x_{bm.r1}": diff_lower_trail[f"x_{bm.r1}"]}
        params["mode"] = 2
        diff = Diff(params)
        diff.make_model()
        diff_effect_lower = diff.solve()
    ##############################################################################################
    ##############################################################################################
    elapsed_time = time.time() - start_time
    # print out a summary of result in terminal
    print("#"*55)
    print("Summary of the results:")
    print("A differential trail for E0:")
    if diff_upper_trail != None:
        diff.print_trail(diff_trail=diff_upper_trail)
    print("#"*55)
    mactive_sboxes = middle_part["as"]
    print(f"Sandwich {rm} rounds in the middle with {mactive_sboxes} active S-boxes")
    print("#"*55)
    print("A differential trail for E1:")
    if diff_lower_trail != None:
        diff.print_trail(diff_trail=diff_lower_trail)
    print("-"*55)
    total_probability = 0
    if diff_effect_upper != None:
        print("differential effect of the upper trail: 2^(%0.02f)" % diff_effect_upper)
        total_probability += diff_effect_upper*2
    if diff_effect_lower != None:
        print("differential effect of the lower trail: 2^(%0.02f)" % diff_effect_lower)
        total_probability += diff_effect_lower*2
    upper_bound =  total_probability + (-1.5)*mactive_sboxes
    lower_bound = total_probability + (-2)*mactive_sboxes
    print("Total probability = p^2*q^2*r = 2^({:.2f}) x 2^({:.2f}) x r".format(diff_effect_upper*2, diff_effect_lower*2))
    print("2^({:.2f}) <= Total probability <= 2^({:.2f})".format(lower_bound, upper_bound))
    print("To compute the accurate value of total probability, r should be evaluated experimentally or using the (F)BCT framework")

    ##############################################################################################
    ##############################################################################################
    # plot distinguisher
    if diff_upper_trail != None:
        active_input_bits = diff.flatten_state([[4*i + j for j in range(4)] for i in range(32) if diff_upper_trail["x_0"][i] != "0"])
        tex_content += tikz_mark_input_bits(active_input_bits, color="red")
        tex_content += tex_diff_trail(trail=diff_upper_trail, markpattern="markupperpath", direction="->")
    else:
        active_input_bits = []
        for i in range(32):
            if upper_trail[f"x_{0}"][i] != "0":
                active_input_bits.extend([j for j in range(4*i, 4*(i + 1))])
        tex_content += tikz_mark_input_bits(active_input_bits, color="red")

    tex_content += tex_middle(upper_trail=upper_trail, midd_trail=middle_part, lower_trail=lower_trail, r0=r0, rm=rm, r1=r1)

    # tex_content += tex_diff_trail(trail=diff_lower_trail, markpattern="marklowerpath", direction="<-")
    if diff_lower_trail != None:
        tex_content += tex_diff_lower_trail(trail=diff_lower_trail, \
                                            upper_crossing_difference=[str(i) for i in range(32) if upper_trail[f"x_{r0 + rm}"][i] != "0"],\
                                            markpattern="marklowerpath",\
                                            direction="<-")
        active_output_bits = diff.flatten_state([[4*i + j for j in range(4)] for i in range(32) if diff_lower_trail[f"x_{r1}"][i] != "0"])
        tex_content += tikz_mark_output_bits(active_output_bits, color="blue")
    else:
        active_output_bits = []
        for i in range(32):
            if lower_trail[f"x_{rm + r1}"][i] != "0":
                active_output_bits.extend([j for j in range(4*i, 4*(i + 1))])
        tex_content += tikz_mark_output_bits(active_output_bits, color="blue")

    tex_content += tex_fin(r0 + rm + r1)
    with open("bmd.tex", "w") as texfile:
        texfile.write(tex_content)
    # print the elapsed time
    print("Elapsed time: %0.02f seconds" % elapsed_time)

def loadparameters(args):
    """
    Get parameters from the argument list and inputfile.
    """

    # Load default values
    params = {"inputfile": "./input.yaml",
                "r0" : 6,
                "rm" : 10,
                "r1" : 7,
                "w0" : 2,
                "wm" : 1,
                "w1" : 2,
                "timelimit" : 1200,
                "numofsols" : 1}

    # Check if there is an input file specified
    if args.inputfile:
        with open(args.inputfile[0], 'r') as input_file:
            doc = yaml.load(input_file, Loader=yaml.FullLoader)
            params.update(doc)
            if "fixedVariables" in doc:
                fixed_vars = {}
                for variable in doc["fixedVariables"]:
                    fixed_vars = dict(list(fixed_vars.items()) +
                                    list(variable.items()))
                params["fixedVariables"] = fixed_vars

    # Override parameters if they are set on commandline
    
    if args.inputfile:
        params["inputfile"] = args.inputfile

    if args.r0:
        params["r0"] = args.r0

    if args.rm:
        params["rm"] = args.rm

    if args.r1:
        params["r1"] = args.r1

    if args.w0:
        params["w0"] = args.w0

    if args.wm:
        params["wm"] = args.wm

    if args.w1:
        params["w1"] = args.w1

    if args.timelimit:
        params["timelimit"] = args.timelimit

    if args.numofsols:
        params["numofsols"] = args.numofsols

    if args.numofsols:
        params["numofsols"] = args.numofsols

    return params

if __name__ == "__main__":
    main()
