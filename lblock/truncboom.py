#!/usr/bin/env python3

"""
Date: Feb 1, 2022
"""

from truncdiff import WordLBlock
import time
from gurobipy import *

class TruncatedBoomerang(WordLBlock):
    """
    This class is used to find a truncated boomerang trail for LBlock block cipher
    """

    count = 0
    def __init__(self, r0, r1, rm, w0=1, w1=1, wm=1):
        """
        Initialize the main parameters of the boomerang trails

        :param r0 int: number of rounds covered by only the upper trail
        :param r1 int: number of rounds covered by only the lower trail
        :param rm int: number of rounds covered by both the lower and upper trails (middle part)
        :param w0 int: cost of active S-boxes in the upper trail
        :param w1 int: cost of active S-boxes in the lower trail
        :param wm int: cost of common active S-boxes between the upper and lower trails
        """

        super().__init__()
        self.lp_file_name = f"lblock_{r0}_{rm}_{r1}.lp"
        self.r0 = r0
        self.R0 = r0 + rm
        self.r1 = r1
        self.R1 = r1 + rm
        self.rm = rm
        self.w0 = w0
        self.w1 = w1
        self.wm = wm
        self.iterative = False

    def constraint_by_xor(self, a, b, c):
        """
        operation:
        (a, b) |----> c = a + b
        model:
        c - a >= 0
        c - b >= 0
        a + b - c >= 0
        """

        constraints = ""
        constraints += f"{c} - {a} >= 0\n"
        constraints += f"{c} - {b} >= 0\n"
        constraints += f"{a} + {b} - {c} >= 0\n"
        return constraints

    def generate_upper_constraints(self):
        """
        Generate the constraints describing the propagation of
        upper differential trail
        """
        constraints = ""
        for rn in range(self.R0):
            x_in = self.generate_round_x_variables(rn, ul="u")
            x_out = self.generate_round_x_variables(rn + 1, ul="u")
            x_middle = self.swap(x_out)
            sbo = self.apply_permutation(x_in[0:8])
            for n in range(8):
                constraints += self.constraints_by_equality(x_in[n], x_middle[n])
                if rn < self.r0:
                    constraints += self.constraint_by_trunc_xor(sbo[n], x_in[8 + (n + 2)%8], x_middle[8 + n])
                else:
                    constraints += self.constraint_by_xor(sbo[n], x_in[8 + (n + 2)%8], x_middle[8 + n])
                    # constraints += self.constraint_by_trunc_xor(sbo[n], x_in[8 + (n + 2)%8], x_middle[8 + n])
        return constraints

    def generate_lower_constraints(self):
        """
        Generate the constraints describing the propagation of
        lower differential trail
        """

        constraints = ""
        for rn in range(self.R1):
            x_in = self.generate_round_x_variables(rn, ul="l")
            x_out = self.generate_round_x_variables(rn + 1, ul="l")
            x_middle = self.swap(x_out)
            sbo = self.apply_permutation(x_in[0:8])
            for n in range(8):
                constraints += self.constraints_by_equality(x_in[n], x_middle[n])
                if rn < self.rm:
                    constraints += self.constraint_by_xor(sbo[n], x_middle[8 + n], x_in[8 + (n + 2)%8])
                    # constraints += self.constraint_by_trunc_xor(sbo[n], x_in[8 + (n + 2)%8], x_middle[8 + n])
                else:
                    constraints += self.constraint_by_trunc_xor(sbo[n], x_in[8 + (n + 2)%8], x_middle[8 + n])
        return constraints

    def generate_linking_vars(self, rn):
        """
        Generate linking variables to model the common active
        S-boxes between upper and lower trails
        """

        s = [f"s_{rn}_{n}" for n in range(8)]
        self.milp_variables.extend(s)
        return s

    def generate_objective_function(self):
        """
        Generate objective function of MILP model
        """

        upper_active_sboxes = []

        for r in range(0, self.r0):
            xu = self.generate_round_x_variables(rn=r, ul="u")
            for i in range(8):
                upper_active_sboxes.append(f"{self.w0} {xu[i]}")
        lower_active_sboxes = []
        for r in range(self.rm, self.R1):
            xl = self.generate_round_x_variables(rn=r, ul="l")
            for i in range(8):
                lower_active_sboxes.append(f"{self.w1} {xl[i]}")
        common_active_sboxes = []
        for r in range(self.rm):
            s = self.generate_linking_vars(r)
            for i in range(8):
                common_active_sboxes.append(f"{self.wm} {s[i]}")
        if upper_active_sboxes == [] and lower_active_sboxes == []:
            objective  = " + ".join(common_active_sboxes)
        elif upper_active_sboxes == []:
            objective  = " + ".join(lower_active_sboxes) + " + " + \
                         " + ".join(common_active_sboxes)
        elif lower_active_sboxes == []:
            objective  = " + ".join(upper_active_sboxes) + " + " + \
                         " + ".join(common_active_sboxes)
        else:
            objective  = " + ".join(upper_active_sboxes) + " + " + \
                         " + ".join(lower_active_sboxes) + " + " + \
                         " + ".join(common_active_sboxes)
        return objective


    def make_model(self):
        """
        Generate the main constrain of our MILP model
        describing the propagation of differential trails in upper and
        lower parts
        """

        constraints = "minimize\n"
        constraints += self.generate_objective_function()
        constraints += "\nsubject to\n"
        constraints += self.generate_upper_constraints()
        constraints += self.exclude_trivial_solution(ul="u")
        constraints += self.generate_lower_constraints()
        constraints += self.exclude_trivial_solution(ul="l")

        for rn in range(self.rm):
            s = self.generate_linking_vars(rn)
            xu = self.generate_round_x_variables(rn + self.r0, ul="u")
            xl = self.generate_round_x_variables(rn, ul="l")
            for i in range(8):
                constraints += f"{xu[i]} - {s[i]} >= 0\n"
                constraints += f"{xl[i]} - {s[i]} >= 0\n"
                constraints += f"- {xu[i]} - {xl[i]} + {s[i]} >= -1\n"
        if self.iterative == True:
            x_in = self.generate_round_x_variables(0, ul="u")
            # x_out = self.generate_round_x_variables(self.R1, ul="l")
            x_out = self.generate_round_x_variables(self.rm, ul="u")
            for i in range(16):
                constraints += f"{x_in[i]} - {x_out[i]} = 0\n"
        constraints += self.declare_binary_vars()
        constraints += "end"
        with open(self.lp_file_name, "w") as lpfile:
            lpfile.write(constraints)

    def find_truncated_boomerang_trail(self):
        """
        Solve the constructed model minimizing the number of active S-boxes
        """

        self.make_model()
        self.milp_model = read(self.lp_file_name)
        os.remove(self.lp_file_name)
        self.milp_model.setParam(GRB.Param.OutputFlag, True)

        self.milp_model.Params.PoolSearchMode = 2
        # Limit number of solutions
        self.milp_model.Params.PoolSolutions = 10
        # Choose solution number 1
        self.milp_model.Params.SolutionNumber = 0

        start_time = time.time()
        ###################
        self.milp_model.optimize()
        ###################
        elapsed_time = time.time() - start_time
        time_line = "Total time to find the trail: %0.02f seconds\n".format(elapsed_time)
        objective_function = self.milp_model.getObjective()
        objective_value = objective_function.getValue()
        print(f"Number of active S-boxes: {objective_value}")

    def parse_solver_output(self):
        '''
        Extract the truncated differential characteristic from the solver output
        '''

        self.upper_trail = dict()
        self.lower_trail = dict()
        self.middle_part = dict()
        get_value_str = lambda t: str(int(self.milp_model.getVarByName(t).Xn))
        get_value_int = lambda t: int(self.milp_model.getVarByName(t).Xn)

        print("\nUpper Truncated Trail:\n")
        for r in range(self.R0 + 1):
            x_name = self.generate_round_x_variables(rn=r, ul="u")
            x_value = ''.join(list(map(get_value_str, x_name)))
            self.upper_trail[f"x_{r}"] = x_value
            print(x_value)
        print("\n%s\n%s" % ("+"*16, "#"*16))
        print("Lower Truncated Trail:\n")
        for r in range(self.R1 + 1):
            x_name = self.generate_round_x_variables(rn=r, ul="l")
            x_value = ''.join(list(map(get_value_str, x_name)))
            self.lower_trail[f"x_{r}"] = x_value
            print(x_value)
        print("\n%s\n%s" % ("#"*16, "#"*16))
        print("Middle Part:\n")
        for r in range(self.rm):
            s_name = self.generate_linking_vars(r)
            s_value = '*'.join(list(map(get_value_str, s_name))) + "*"
            self.middle_part[f"s_{r}"] = s_value
            print(s_value)
        s = []
        for r in range(self.rm):
            s.extend(self.generate_linking_vars(r))
        ncs = sum(list(map(get_value_int, s)))
        print(f"\nNumber of common active S-boxes: {ncs}")
        self.middle_part["as"] = ncs
        return self.upper_trail, self.middle_part, self.lower_trail

if __name__ == "__main__":
    r0, rm, r1 = 0, 6, 0
    w0, wm, w1 = 1, 1, 1
    bm = TruncatedBoomerang(r0=r0, r1=r1, rm=rm, w0=w0, w1=w1, wm=wm)
    bm.iterative = False
    bm.find_truncated_boomerang_trail()
    bm.parse_solver_output()