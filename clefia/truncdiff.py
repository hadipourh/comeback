"""
Date: Feb 15, 2022

This module can be used to find truncated differential trail
with minimum number of active S-boxes for CLEFIA block cipher.
"""

import io
from statistics import mode
import time
import os
from xml.dom import minidom
from gurobipy import *

class WordClefia:
    """
    This class can be used to find a truncated differential trail
    with minimum number of active S-boxes for CLEFIA block cipher.

    x_roundNumber_branchNumber_byteNumber

    Variable mapping:

    ... x_r_0                                   --- x_r_1 ...
    ... |                                       |     |
    ... |--------> | S |---|4*4 MDS|--- z_r_0---+---->+    ...
    ... |                                       |    ...
    """
    count = 0

    def __init__(self, nrounds=1) -> None:
        WordClefia.count += 1
        self.xor_counter = 0
        self.mds_counter = 0
        self.DSM_counter = 0
        self.dummy_var = "d"
        self.nrounds = nrounds
        self.milp_variables = []
        self.lp_file_name = f"clefia_{nrounds}r.lp"
        self.permute_branches = [3, 0, 1, 2]

    @staticmethod
    def ordered_set(seq):
        """
        This method eliminates duplicated elements in a given list,
        and returns a list in which each elements appears only once
        """

        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))]

    def apply_permutation(self, state):
        """
        Apply the permute branches on the state array
        """

        output = [0]*4
        for i in range(4):
            output[self.permute_branches[i]] = state[i]
        return output

    def apply_inv_permutation(self, state):
        """
        Apply the inverse of branch permutation on the state array
        """

        output = [0]*4
        for i in range(4):
            output[i] = state[self.permute_branches[i]]
        return output

    @staticmethod
    def flatten_byte_state(s):
        state_bytes = [s[bn][byten] for bn in range(len(s)) for byten in range(len(s[0]))]
        return state_bytes

    def generate_round_x_variables(self, rn, ul="u"):
        """
        Generate the input variables of rn'th round

        :param rn int: round number
        :param ul str: 'u' or 'l' denoting whether it is a variable in upper or lower trail
        """

        x = [[f"x{ul}_{rn}_{bn}_{byten}" for byten in range(4)] for bn in range(4)]
        self.milp_variables.extend(self.flatten_byte_state(x))
        return x

    def generate_round_z_variables(self, rn, ul="u"):
        """
        Generate the variables representing the activeness at the output of MDS matrix

        :param rn int: round number
        :param ul str: 'u' or 'l' denoting whether it is a variable in upper or lower trail
        """

        z = [[f"z{ul}_{rn}_{bn}_{byten}" for byten in range(4)] for bn in range(2)]
        self.milp_variables.extend(self.flatten_byte_state(z))
        return z

    def constraint_by_trunc_xor(self, a, b, c, model=1):
        """
        operation:
        (a, b) |----> c = a + b
        model 1:
        a + b + c >= 2 d
        d >= a
        d >= b
        d >= c
        model 2:
        a + b - c >= 0
        a - b + c >= 0
        - a + b + c >= 0
        """

        constraints = ""
        if model == 1:
            d = f"{self.dummy_var}_{self.xor_counter}"
            self.milp_variables.append(d)
            constraints += f"{a} + {b} + {c} -  2 {d} >= 0\n"
            constraints += f"{d} - {a} >= 0\n"
            constraints += f"{d} - {b} >= 0\n"
            constraints += f"{d} - {c} >= 0\n"
            self.xor_counter += 1
        elif model == 2:
            constraints += f"{a} + {b} - {c} >= 0\n"
            constraints += f"{a} - {b} + {c} >= 0\n"
            constraints += f"- {a} + {b} + {c} >= 0\n"
        return constraints

    def constraints_by_equality(self, a, b):
        """
        a = b
        """

        constraint = f"{a} - {b} = 0\n"
        return constraint

    def constraints_by_mds(self, dx, dy):
        """
        Generate constraints describing the propagation of truncated
        differential trail through the MDS matrix with branch number 5

        :param dx list[4]: input of MDS
        :param dy list[4]: output of MDS
        """

        iodiffs = dx + dy
        iodiffs_sum = " + ".join(iodiffs)
        constraints = f"{iodiffs_sum} - 5 dm_{self.mds_counter} >= 0\n"

        for x in iodiffs:
            constraints += f"dm_{self.mds_counter} - {x} >= 0\n"
        self.mds_counter += 1

        # Model the propagation of differential through the MDS with probability one
        for y in dy:
            for x in dx:
                constraints += f"{y} - {x} >= 0\n"
        return constraints

    def diffusion_switching_mechanism(self, rn, ul="u"):
        """
        Generate some conditions to model the diffusion switching mechanism (DSM)
        in CLEFIA. Switching between two different MDS matrices in the diffusion layer of
        CLEFIA makes it stronger against the differential and linear attacks, since the concatenation of
        these two MDS matrices satisfies an special property which guarantess a certain number of active S-boxes
        over 6 consecutive rounds of CLEFIA.

        Reference:
        - On Feistel Structures Using a Diffusion Switching Mechanism (https://www.iacr.org/archive/fse2006/40470042/40470042.pdf)

        :param rn int: round number
        :rtype: string
        :return: constraints modeling the DSM in rounds rn - 5, ..., rn:
        """

        constraints = ""

        x_0 = self.generate_round_x_variables(rn - 4, ul)
        x_1 = self.generate_round_x_variables(rn - 3, ul)
        x_2 = self.generate_round_x_variables(rn - 2, ul)
        x_3 = self.generate_round_x_variables(rn - 1, ul)
        x_4 = self.generate_round_x_variables(rn, ul)

        temp0 = " + ".join(x_3[0] + x_1[2])
        constraints += f"{temp0} - 8 dsm_{self.DSM_counter} <= 0\n"        
        constraints += f"{temp0} - dsm_{self.DSM_counter} >= 0\n"
        temp1 = " + ".join(x_3[0] + x_1[2] + x_4[0] + x_0[0])
        constraints += f"{temp1} - 5 dsm_{self.DSM_counter} >= 0\n"
        self.milp_variables.append(f"dsm_{self.DSM_counter}")

        self.DSM_counter += 1

        temp0 = " + ".join(x_3[2] + x_1[0])
        constraints += f"{temp0} - 8 dsm_{self.DSM_counter} <= 0\n"        
        constraints += f"{temp0} - dsm_{self.DSM_counter} >= 0\n"
        temp1 = " + ".join(x_4[2] + x_3[2] + x_1[0] + x_0[2])
        constraints += f"{temp1} - 5 dsm_{self.DSM_counter} >= 0\n"
        self.milp_variables.append(f"dsm_{self.DSM_counter}")

        self.DSM_counter += 1

        return constraints

    def generate_constraints(self, ul="u"):
        """
        Generate the constraints of MILP model
        """

        constraints = ""
        for rn in range(self.nrounds):
            x_in = self.generate_round_x_variables(rn, ul)
            x_out = self.generate_round_x_variables(rn + 1, ul)
            x_middle = self.apply_inv_permutation(x_out)
            z = self.generate_round_z_variables(rn)
            constraints += self.constraints_by_mds(dx=x_in[0], dy=z[0])
            constraints += self.constraints_by_mds(dx=x_in[2], dy=z[1])
            for n in range(4):
                constraints += self.constraint_by_trunc_xor(z[0][n], x_in[1][n], x_middle[1][n])
                constraints += self.constraint_by_trunc_xor(z[1][n], x_in[3][n], x_middle[3][n])
                constraints += self.constraints_by_equality(x_in[0][n], x_middle[0][n])
                constraints += self.constraints_by_equality(x_in[2][n], x_middle[2][n])
            if rn >= 4:
                constraints += self.diffusion_switching_mechanism(rn)
        return constraints

    def declare_binary_vars(self):
        """
        Declare binary variables of MILP model
        """

        self.milp_variables = self.ordered_set(self.milp_variables)
        for n in range(self.xor_counter):
            self.milp_variables.append(f"d_{n}")
        for n in range(self.mds_counter):
            self.milp_variables.append(f"dm_{n}")
        constraints = "Binary\n"
        constraints += "\n".join(self.milp_variables) + "\n"
        return constraints

    def generate_objective_function(self):
        """
        Generate the objective function of MILP model
        """

        sbox_inputs = []
        for r in range(self.nrounds):
            round_input = self.generate_round_x_variables(r)
            sbox_inputs.extend(round_input[0] + round_input[2])
        objective = " + ".join(sbox_inputs) + "\n"
        return objective

    def exclude_trivial_solution(self, ul="u"):
        """
        Exclude all-zero solution from the solutions space
        """
        x_0 = self.generate_round_x_variables(0, ul)
        x_0 = self.flatten_byte_state(x_0)
        constraint = " + ".join(x_0) + " >= 1\n"
        return constraint

    def make_model(self):
        """
        Generate the MILP model describing propagation of a truncated differential
        trail through CLEFIA block cipher
        """

        lp_contents = f"\\ Truncated differential trail for {self.nrounds} rounds of CLEFIA\n"
        lp_contents = "minimize\n"
        lp_contents += self.generate_objective_function()
        lp_contents += "subject to\n"
        lp_contents += self.generate_constraints()
        lp_contents += self.exclude_trivial_solution()
        lp_contents += self.declare_binary_vars()
        lp_contents += "End"
        with open(self.lp_file_name, "w") as lp_file:
            lp_file.write(lp_contents)

    def find_truncated_differential_trail(self):
        """
        Solve the constructed model minimizing the number of active S-boxes
        """

        self.make_model()
        milp_model = read(self.lp_file_name)
        os.remove(self.lp_file_name)
        milp_model.setParam(GRB.Param.OutputFlag, True)
        start_time = time.time()
        ###################
        milp_model.optimize()
        ###################
        elapsed_time = time.time() - start_time
        time_line = "Total time to find the trail: %0.02f seconds\n".format(elapsed_time)
        objective_function = milp_model.getObjective()
        objective_value = objective_function.getValue()
        print(f"Number of active S-boxes: {objective_value}")

if __name__ == "__main__":
    nrounds = 3
    clefia_upper = WordClefia(nrounds=nrounds)
    clefia_upper.find_truncated_differential_trail()