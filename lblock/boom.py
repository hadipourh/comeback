#!/usr/bin/env python3

"""
Date: Feb 9, 2022
"""

from argparse import ArgumentParser, RawTextHelpFormatter
from truncboom import TruncatedBoomerang
from diff import Diff
from plotdistinguisher import *

def main():

    # 13 rounds
    # r0, rm, r1 = 3, 8, 2
    # w0, wm, w1 = 6, 3, 6

    # r0, rm, r1 = 2, 9, 2
    # w0, wm, w1 = 5, 4, 5


    # 14 rounds
    # r0, rm, r1 = 3, 8, 3
    # w0, wm, w1 = 5, 4.1, 5

    # 15 rounds
    # r0, rm, r1 = 4, 8, 3
    # w0, wm, w1 = 6, 3, 6

    # 16 rounds
    r0, rm, r1 = 4, 8, 4
    w0, wm, w1 = 6, 3, 6
    # r0, rm, r1 = 3, 9, 4
    # w0, wm, w1 = 5, 3, 5

    parser = ArgumentParser(description="This tool finds the nearly optimum boomerang distinguisher\n"
                                         "Example:\n"
                                         "python3 boom.py -r0 4 -rm 8 -r1 4 -w0 6 -wm 3 -w1 6",
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
    diff_effect_upper = 0
    if r0 != 0:
        time_limit = 18000
        params = {"nrounds" : bm.r0,
                  "mode" : 0,
                  "startweight" : 0,
                  "endweight" : 128,
                  "timelimit" : time_limit,
                  "numberoftrails" : 1,
                  "fixedVariables" : {}}
        for nibble in range(16):
            if upper_trail[f"x_0"][nibble] == "0":
                for bit in range(4):
                    params["fixedVariables"][f"x_{0}_{nibble}_{bit}"] = "0"
            if upper_trail[f"x_{bm.r0}"][nibble] == "0":
                for bit in range(4):
                    params["fixedVariables"][f"x_{bm.r0}_{nibble}_{bit}"] = "0"
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
    diff_effect_lower = 0
    if r1 != 0:
        time_limit = 18000
        params = {"nrounds" : bm.r1,
                  "mode" : 0,
                  "startweight" : 0,
                  "endweight" : 128,
                  "timelimit" : time_limit,
                  "numberoftrails" : 1,
                  "fixedVariables" : {}}
        for nibble in range(16):
            if lower_trail[f"x_{bm.rm}"][nibble] == "0":
                for bit in range(4):
                    params["fixedVariables"][f"x_{0}_{nibble}_{bit}"] = "0"
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
    # print out a summary of result on terminal
    print("#"*27)
    print("Summary of the results:")
    print("Upper trail:")
    if diff_upper_trail != None:
        diff.print_trail(diff_trail=diff_upper_trail)
    print("#"*27)
    mactive_sboxes = middle_part["as"]
    print(f"Sandwich {rm} rounds in the middle with {mactive_sboxes} active S-boxes")
    print("#"*27)
    print("Lower trail:")
    if diff_lower_trail != None:
        diff.print_trail(diff_trail=diff_lower_trail)
    print("-"*27)
    total_weight = 0
    if diff_effect_upper != 0:
        print("differential effect of the upper trail: 2^(%0.02f)" % diff_effect_upper)
        total_weight += diff_effect_upper*2
    if diff_effect_lower != 0:
        print("differential effect of the lower trail: 2^(%0.02f)" % diff_effect_lower)
        total_weight += diff_effect_lower*2
    upper_bound =  total_weight + (-2)*mactive_sboxes
    lower_bound = total_weight + (-2.5)*mactive_sboxes
    print("Total probability = p^2*q^2*r = 2^({:.2f}) x 2^({:.2f}) x r".format(diff_effect_upper*2, diff_effect_lower*2))
    print("2^({:.2f}) <= Total probability <= 2^({:.2f})".format(lower_bound, upper_bound))
    print("To compute the accurate value of total probability, r should be evaluated experimentally or using the (F)BCT framework")

    ##############################################################################################
    ##############################################################################################
    # plot distinguisher
    if diff_upper_trail != None:
        active_input_bits = diff.flatten_state([[4*i + j for j in range(4)] for i in range(16) if diff_upper_trail["x_0"][i] != "0"])
        tex_content += tikz_mark_input_bits(active_input_bits, color="red")
        tex_content += tex_diff_trail(trail=diff_upper_trail, markpattern="markupperpath", direction="->")
    else:
        active_input_bits = []
        for i in range(16):
            if upper_trail[f"x_{0}"][i] != "0":
                active_input_bits.extend([j for j in range(4*i, 4*(i + 1))])
        tex_content += tikz_mark_input_bits(active_input_bits, color="red")

    tex_content += tex_middle(upper_trail=upper_trail, midd_trail=middle_part, lower_trail=lower_trail, r0=r0, rm=rm, r1=r1)

    # tex_content += tex_diff_trail(trail=diff_lower_trail, markpattern="marklowerpath", direction="<-")
    if diff_lower_trail != None:
        tex_content += tex_diff_lower_trail(trail=diff_lower_trail, \
                                            upper_crossing_difference=[str(i) for i in range(16) if upper_trail[f"x_{r0 + rm}"][i] != "0"],\
                                            markpattern="marklowerpath",\
                                            direction="<-")
        active_output_bits = diff.flatten_state([[4*i + j for j in range(4)] for i in range(16) if diff_lower_trail[f"x_{r1}"][i] != "0"])
        tex_content += tikz_mark_output_bits(active_output_bits, color="blue")
    else:
        active_output_bits = []
        for i in range(16):
            if lower_trail[f"x_{rm + r1}"][i] != "0":
                active_output_bits.extend([j for j in range(4*i, 4*(i + 1))])
        tex_content += tikz_mark_output_bits(active_output_bits, color="blue")

    tex_content += tex_fin(r0 + rm + r1)
    with open("bmd.tex", "w") as texfile:
        texfile.write(tex_content)

def loadparameters(args):
    """
    Get parameters from the argument list and inputfile.
    """

    # Load default values
    params = {"inputfile": "./input.yaml",
                "r0" : 4,
                "rm" : 8,
                "r1" : 4,
                "w0" : 6,
                "wm" : 3,
                "w1" : 6,
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
    
    if args.r0 != None:
        params["r0"] = args.r0

    if args.rm != None:
        params["rm"] = args.rm

    if args.r1 != None:
        params["r1"] = args.r1

    if args.w0 != None:
        params["w0"] = args.w0

    if args.wm != None:
        params["wm"] = args.wm

    if args.w1 != None:
        params["w1"] = args.w1
    
    if args.timelimit != None:
        params["timelimit"] = args.timelimit

    if args.numofsols != None:
        params["numofsols"] = args.numofsols

    return params

if __name__ == "__main__":
    main()
