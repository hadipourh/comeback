#!/usr/bin/env python3

"""
Date: Feb 1, 2022
"""

from copyreg import constructor
from truncdiff import WordClefia
import time
from gurobipy import *

class TruncatedBoomerang(WordClefia):
    """
    This class is used to find a truncated boomerang trail for CLEFIA block cipher
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
        self.lp_file_name = f"clefia_{r0}_{rm}_{r1}.lp"
        self.r0 = r0
        self.R0 = r0 + rm
        self.r1 = r1
        self.R1 = r1 + rm
        self.rm = rm
        self.w0 = w0
        self.w1 = w1
        self.wm = wm

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

    def constraints_by_mds_prob_one(self, dx, dy):
        """
        Generate constraints describing the propagation of truncated
        differential trail through the MDS matrix with probability one

        :param dx list[4]: input of MDS
        :param dy list[4]: output of MDS
        """

        constraints = ""
        for y in dy:
            for x in dx:
                constraints += f"{y} - {x} >= 0\n"
        self.mds_counter += 1
        return constraints

    def generate_upper_constraints(self):
        """
        Generate the constraints describing the propagation of
        upper differential trail
        """
        constraints = ""
        for rn in range(self.R0):
            x_in = self.generate_round_x_variables(rn, "u")
            x_out = self.generate_round_x_variables(rn + 1, "u")
            x_middle = self.apply_inv_permutation(x_out)
            z = self.generate_round_z_variables(rn, "u")
            constraints += self.constraints_by_mds(dx=x_in[0], dy=z[0])
            constraints += self.constraints_by_mds(dx=x_in[2], dy=z[1])
            for n in range(4):
                if rn < self.r0:
                    constraints += self.constraint_by_trunc_xor(z[0][n], x_in[1][n], x_middle[1][n])
                    constraints += self.constraint_by_trunc_xor(z[1][n], x_in[3][n], x_middle[3][n])
                else:
                    constraints += self.constraint_by_xor(z[0][n], x_in[1][n], x_middle[1][n])
                    constraints += self.constraint_by_xor(z[1][n], x_in[3][n], x_middle[3][n])
                constraints += self.constraints_by_equality(x_in[0][n], x_middle[0][n])
                constraints += self.constraints_by_equality(x_in[2][n], x_middle[2][n])
            if rn >= 4:
                constraints += self.diffusion_switching_mechanism(rn, "u")
                pass
        return constraints

    def generate_lower_constraints(self):
        """
        Generate the constraints describing the propagation of
        lower differential trail
        """

        constraints = ""
        for rn in range(self.R1):
            x_in = self.generate_round_x_variables(rn, "l")
            x_out = self.generate_round_x_variables(rn + 1, "l")
            x_middle = self.apply_inv_permutation(x_out)
            z = self.generate_round_z_variables(rn, "l")
            constraints += self.constraints_by_mds(dx=x_in[0], dy=z[0])
            constraints += self.constraints_by_mds(dx=x_in[2], dy=z[1])
            for n in range(4):
                if rn < self.rm:
                    constraints += self.constraint_by_xor(z[0][n], x_middle[1][n], x_in[1][n])
                    constraints += self.constraint_by_xor(z[1][n], x_middle[3][n], x_in[3][n])
                else:
                    constraints += self.constraint_by_trunc_xor(z[0][n], x_in[1][n], x_middle[1][n])
                    constraints += self.constraint_by_trunc_xor(z[1][n], x_in[3][n], x_middle[3][n])
                constraints += self.constraints_by_equality(x_in[0][n], x_middle[0][n])
                constraints += self.constraints_by_equality(x_in[2][n], x_middle[2][n])
            if rn >= 4:
                constraints += self.diffusion_switching_mechanism(rn, "l")
                pass
        return constraints

    def generate_linking_vars(self, rn):
        """
        Generate linking variables to model the common active
        S-boxes between upper and lower trails
        """

        s = [[f"s_{rn}_{bn}_{n}" for n in range(4)] for bn in range(2)]
        self.milp_variables.extend(self.flatten_byte_state(s))
        return s

    def generate_objective_function(self):
        """
        Generate objective function of MILP model
        """

        upper_active_sboxes = []

        for r in range(0, self.r0):
            xu = self.generate_round_x_variables(rn=r, ul="u")
            for i in range(4):
                if i % 2 == 0:
                    upper_active_sboxes.append(f"{self.w0*4.67} {xu[0][i]}")
                    upper_active_sboxes.append(f"{self.w0*6} {xu[2][i]}")
                else:
                    upper_active_sboxes.append(f"{self.w0*6} {xu[0][i]}")
                    upper_active_sboxes.append(f"{self.w0*4.67} {xu[2][i]}")
        lower_active_sboxes = []
        for r in range(self.rm, self.R1):
            xl = self.generate_round_x_variables(rn=r, ul="l")
            for i in range(4):
                if i % 2 == 0:
                    lower_active_sboxes.append(f"{self.w1*4.67} {xl[0][i]}")
                    lower_active_sboxes.append(f"{self.w1*6} {xl[2][i]}")
                else:
                    lower_active_sboxes.append(f"{self.w1*6} {xl[0][i]}")
                    lower_active_sboxes.append(f"{self.w1*4.67} {xl[2][i]}")
        common_active_sboxes = []
        for r in range(self.rm):
            s = self.generate_linking_vars(r)
            for i in range(4):
                if i % 2 == 0:
                    common_active_sboxes.append(f"{self.wm*4.67} {s[0][i]}")
                    common_active_sboxes.append(f"{self.wm*6} {s[1][i]}")
                else:
                    common_active_sboxes.append(f"{self.wm*6} {s[0][i]}")
                    common_active_sboxes.append(f"{self.wm*4.67} {s[1][i]}")
        if upper_active_sboxes == [] and lower_active_sboxes == []:
            objective  = " + ".join(common_active_sboxes)
        elif upper_active_sboxes == [] and lower_active_sboxes != [] and common_active_sboxes != []:
            objective  = " + ".join(lower_active_sboxes) + " + " + \
                         " + ".join(common_active_sboxes)
        elif lower_active_sboxes == [] and upper_active_sboxes != [] and common_active_sboxes != []:
            objective  = " + ".join(upper_active_sboxes) + " + " + \
                         " + ".join(common_active_sboxes)
        elif common_active_sboxes == [] and upper_active_sboxes != [] and lower_active_sboxes != []:
            objective  = " + ".join(upper_active_sboxes) + " + " + \
                         " + ".join(lower_active_sboxes)
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
            for i in range(4):
                constraints += f"{xu[0][i]} - {s[0][i]} >= 0\n"
                constraints += f"{xu[2][i]} - {s[1][i]} >= 0\n"
                constraints += f"{xl[0][i]} - {s[0][i]} >= 0\n"
                constraints += f"{xl[2][i]} - {s[1][i]} >= 0\n"
                constraints += f"- {xu[0][i]} - {xl[0][i]} + {s[0][i]} >= -1\n"
                constraints += f"- {xu[2][i]} - {xl[2][i]} + {s[1][i]} >= -1\n"
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

        # self.milp_model.Params.PoolSearchMode = 2
        # # Limit number of solutions
        # self.milp_model.Params.PoolSolutions = 2
        # # Choose solution number 1
        # self.milp_model.Params.SolutionNumber = 0

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
        get_value_str = lambda t: str(int(self.milp_model.getVarByName(t).Xn)).zfill(2)
        get_value_int = lambda t: int(self.milp_model.getVarByName(t).Xn)

        print("\nUpper Truncated Trail:\n")
        for r in range(self.R0 + 1):
            x_name = self.generate_round_x_variables(rn=r, ul="u")
            x_name = self.flatten_byte_state(x_name)
            x_value = ''.join(list(map(get_value_str, x_name)))
            self.upper_trail[f"x_{r}"] = x_value
            print(x_value)
        print("\n%s\n%s" % ("+"*32, "#"*32))
        print("Lower Truncated Trail:\n")
        for r in range(self.R1 + 1):
            x_name = self.generate_round_x_variables(rn=r, ul="l")
            x_name = self.flatten_byte_state(x_name)
            x_value = ''.join(list(map(get_value_str, x_name)))
            self.lower_trail[f"x_{r}"] = x_value
            print(x_value)
        print("\n%s\n%s" % ("#"*32, "#"*32))
        print("Middle Part:\n")
        for r in range(self.rm):
            s_name = self.generate_linking_vars(r)
            s_name = self.flatten_byte_state(s_name)
            s_value = ''.join(list(map(get_value_str, s_name[0:4]))) + "*"*8 + \
                      ''.join(list(map(get_value_str, s_name[4::]))) + "*"*8
            self.middle_part[f"s_{r}"] = s_value
            print(s_value)
        s = []
        for r in range(self.rm):
            s.extend(self.flatten_byte_state(self.generate_linking_vars(r)))
        ncs = sum(list(map(get_value_int, s)))
        print(f"\nNumber of common active S-boxes: {ncs}")
        self.middle_part["as"] = ncs
        return self.upper_trail, self.middle_part, self.lower_trail

if __name__ == "__main__":
    r0, rm, r1 = 3, 2, 3
    w0, wm, w1 = 1, 1, 1
    bm = TruncatedBoomerang(r0=r0, r1=r1, rm=rm, w0=w0, w1=w1, wm=wm)
    bm.find_truncated_boomerang_trail()
    bm.parse_solver_output()