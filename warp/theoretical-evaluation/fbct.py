# -*- coding: utf-8 -*-
"""
Created on Dec 27 2021
Author: Hosein Hadipour
"""

import math

class FBCTFramework:
    def __init__(self, S):
        self.size = len(S)
        print(f"S-box:\t{S}")
        self.ddt = self.gen_ddt(S)
        self.fbct = self.gen_fbct(S)

    def gen_ddt(self, S):
        ddt = []
        for i in range(self.size):
            ddt.append( [0 for j in range(self.size)] )
        for inDiff in range(self.size):
            for x in range(self.size):
                ddt[inDiff][S[x]^S[x^inDiff]] += 1
        # print2Dlist(ddt)
        return ddt

    def gen_bct(self, S, Sinv):
        bct = []
        for i in range(self.size):
            bct.append( [0 for j in range(self.size)] )
        for inDiff in range(self.size):
            for outDiff in range(self.size):
                for x in range(self.size):
                    y1 = S[x]
                    y2 = S[x^inDiff]
                    x3 = Sinv[y1^outDiff]
                    x4 = Sinv[y2^outDiff]
                    if x3^x4 == inDiff:
                        bct[inDiff][outDiff] += 1
        # print2Dlist(bct)
        return bct

    def gen_fbct(self, S):
        """
        Compute the Feistel boomerang connectivity table
        """

        fbct = [[0 for i in range(self.size)] for j in range(self.size)]
        for di in range(self.size):
            for do in range(self.size):
                for x in range(self.size):
                    t1 = S[x]
                    t2 = S[x ^ di]
                    t3 = S[x ^ do]
                    t4 = S[x ^ di ^ do]
                    if t1 ^ t2 ^ t3 ^ t4 == 0:
                        fbct[di][do] += 1
        # print2Dlist(fbct)
        return fbct

    def get_fbct_uniformity(self):
        """
        Compute the Feistel boomerang uniformity of S-box
        """

        funiformity = 0
        for di in range(1, self.size):
            for do in range(1, self.size):
                if di != do:
                    tmp = self.fbct[di][do]
                    if funiformity < tmp:
                        funiformity = tmp
        return funiformity

    def get_good_ios(self):
        """
        Find those input/output differences working better for boomerang attack
        """

        list_of_worths = [0]*self.size
        for dx in range(self.size):
            for dy in range(self.size):
                list_of_worths[dx] += self.fbct[dx][dy]
        mx = max(list_of_worths[1:])
        good_ios = ["{:02x}".format(i) for i in range(0, self.size) if list_of_worths[i] == mx]
        if len(good_ios) == (self.size - 1):
            good_ios = "Doesn't have a good IO! ;-)"
        return good_ios, list_of_worths


    def gen_fbdt(self, S):
        """
        Compute the Feistel boomerang difference table
        """

        fbdt = [[[0 for _ in range(self.size)] for _ in range(self.size)] for _ in range(self.size)]
        for di in range(self.size):
            for do in range(self.size):
                for x in range(self.size):
                    y1 = S[x]
                    y2 = S[x ^ di]
                    y3 = S[x ^ do]
                    y4 = S[x ^ di ^ do]
                    delta = y1 ^ y2
                    if y1 ^ y2 ^ y3 ^ y4 == 0:
                        fbdt[di][delta][do] += 1
        return fbdt


    def compute_F(self):
        self.F = [[0 for _ in range(self.size)] for _ in range(self.size)]
        for a_3_6 in range(self.size):
            for b_12_4 in range(self.size):
                for b_3_6 in range(self.size):
                    self.F[a_3_6][b_12_4] += self.fbct[a_3_6][b_3_6] * self.ddt[b_12_4][b_3_6]

    def compute_G(self):
        self.G = [[[0 for _ in range(self.size)] for _ in range(self.size)] for _ in range(self.size)]
        for a_3_6 in range(self.size):
            for a_6_20 in range(self.size):
                for b_7_28 in range(self.size):
                    for a_7_28 in range(self.size):
                        self.G[a_3_6][a_6_20][b_7_28] += self.fbct[a_7_28][b_7_28] * self.ddt[a_3_6][a_6_20] * self.ddt[a_6_20][a_7_28]

    def compute_H(self):
        self.H = [[0 for _ in range(self.size)] for _ in range(self.size)]
        for b_10_19 in range(self.size):
            for b_7_28 in range(self.size):
                for b_8_8 in range(self.size):
                    self.H[b_10_19][b_7_28] += self.ddt[b_10_19][b_8_8] * self.ddt[b_8_8][b_7_28]

    def compute_I(self):
        self.I = [[[0 for _ in range(self.size)] for _ in range(self.size)] for _ in range(self.size)]
        for a_6_20 in range(self.size):
            for b_10_19 in range(self.size):
                for b_12_4 in range(self.size):
                    for a_9_24 in range(self.size):
                        for a_10_18 in range(self.size):
                            self.I[a_6_20][b_10_19][b_12_4] += self.ddt[a_6_20][a_9_24] * self.ddt[a_9_24][a_10_18] * self.fbdt[b_12_4][b_10_19][a_10_18]

    def compute_boomerang_switch(self, a_3_6, b_12_4):
        """
        Compute the boomerang switch for our 14-round sandwich distinguisher for WARP
        """

        self.fbdt = self.gen_fbdt(S)
        self.compute_F()
        self.compute_G()
        self.compute_H()
        self.compute_I()

        output = 0
        for a_6_20 in range(self.size):
            for b_7_28 in range(self.size):
                for b_10_19 in range(self.size):
                    output += self.F[a_3_6][b_12_4] * self.G[a_3_6][a_6_20][b_7_28] * self.H[b_10_19][b_7_28] * self.I[a_6_20][b_10_19][b_12_4]
        denominator_log2 = 4*10
        print(f"pr = {output}/2^-{(denominator_log2)}")
        if output != 0:
            return (math.log(output, 2) - (denominator_log2))
        else:
            return '-inf'

def generate_latex_code(D):
    """
    Print the latex code of the given 2-dimensional table for our paper
    """
    size = len(D[0])
    row_to_nice_str = lambda entry : "{:2d}".format(entry)
    for i in range(size):
        row = D[i]
        row = list(map(row_to_nice_str, row))
        row = " & ".join(row)
        row = r"\texttt{" + hex(i)[2:] + r"\,} & " + row + r"\\"
        print(row)

def print2dlist(D):
    size = len(D[0])
    row_to_nice_str = lambda entry : "{:2d}".format(entry)
    topline = list(range(size))
    topline = list(map(row_to_nice_str, topline))
    topline = " "*4 + " ".join(topline)
    print("#"*(3*(size) + 3))
    print(topline)
    print("#"*(3*(size) + 3))
    for i in range(size):
        print("{:02x}: ".format(i), end = "")
        row = D[i]
        row = list(map(row_to_nice_str, row))
        row = " ".join(row)
        print(row)

if __name__ == "__main__":
    # WARP
    # S-box of WARP
    S = [0xc, 0xa, 0xd, 0x3, 0xe, 0xb, 0xf, 0x7, 0x8, 0x9, 0x1, 0x5, 0x0, 0x2, 0x4, 0x6]
    ######################################################################################
    ######################################################################################

    # LBlock
    # S-box S0 of LBlock
    # S = [14, 9, 15, 0, 13, 4, 10, 11, 1, 2, 8, 3, 7, 6, 12, 5]
    ######################################################################################
    # S-box S1 of LBlock
    # S = [4, 11, 14, 9, 15, 13, 0, 10, 7, 12, 5, 6, 2, 8, 1, 3]
    ######################################################################################
    # S-box S2 of LBlock
    # S = [1, 14, 7, 12, 15, 13, 0, 6, 11, 5, 9, 3, 2, 4, 8, 10]
    ######################################################################################
    # S-box S3 of LBlock
    # S = [7, 6, 8, 11, 0, 15, 3, 14, 9, 10, 12, 13, 5, 2, 4, 1]
    ######################################################################################
    # S-box S4 of LBlock
    # S = [14, 5, 15, 0, 7, 2, 12, 13, 1, 8, 4, 9, 11, 10, 6, 3]
    ######################################################################################
    # S-box S5 of LBlock
    # S = [2, 13, 11, 12, 15, 14, 0, 9, 7, 10, 6, 3, 1, 8, 4, 5]
    ######################################################################################
    # S-box S6 of LBlock
    # S = [11, 9, 4, 14, 0, 15, 10, 13, 6, 12, 5, 7, 3, 8, 1, 2]
    ######################################################################################
    # S-box S7 of LBlock
    # S = [13, 10, 15, 0, 14, 4, 9, 11, 2, 1, 8, 3, 7, 5, 12, 6]
    ######################################################################################
    ######################################################################################

    # CLEFIA
    # S-box S0 of CLEFIA
    #S = [87, 73, 209, 198, 47, 51, 116, 251, 149, 109, 130, 234, 14, 176, 168, 28, 40, 208, 75, 146, 92, 238, 133, 177, 196, 10, 118, 61, 99, 249, 23, 175, 191, 161, 25, 101, 247, 122, 50, 32, 6, 206, 228, 131, 157, 91, 76, 216, 66, 93, 46, 232, 212, 155, 15, 19, 60, 137, 103, 192, 113, 170, 182, 245, 164, 190, 253, 140, 18, 0, 151, 218, 120, 225, 207, 107, 57, 67, 85, 38, 48, 152, 204, 221, 235, 84, 179, 143, 78, 22, 250, 34, 165, 119, 9, 97, 214, 42, 83, 55, 69, 193, 108, 174, 239, 112, 8, 153, 139, 29, 242, 180, 233, 199, 159, 74, 49, 37, 254, 124, 211, 162, 189, 86, 20, 136, 96, 11, 205, 226, 52, 80, 158, 220, 17, 5, 43, 183, 169, 72, 255, 102, 138, 115, 3, 117, 134, 241, 106, 167, 64, 194, 185, 44, 219, 31, 88, 148, 62, 237, 252, 27, 160, 4, 184, 141, 230, 89, 98, 147, 53, 126, 202, 33, 223, 71, 21, 243, 186, 127, 166, 105, 200, 77, 135, 59, 156, 1, 224, 222, 36, 82, 123, 12, 104, 30, 128, 178, 90, 231, 173, 213, 35, 244, 70, 63, 145, 201, 110, 132, 114, 187, 13, 24, 217, 150, 240, 95, 65, 172, 39, 197, 227, 58, 129, 111, 7, 163, 121, 246, 45, 56, 26, 68, 94, 181, 210, 236, 203, 144, 154, 54, 229, 41, 195, 79, 171, 100, 81, 248, 16, 215, 188, 2, 125, 142]
    ######################################################################################
    # S-box S1 of CLEFIA
    # S = [108, 218, 195, 233, 78, 157, 10, 61, 184, 54, 180, 56, 19, 52, 12, 217, 191, 116, 148, 143, 183, 156, 229, 220, 158, 7, 73, 79, 152, 44, 176, 147, 18, 235, 205, 179, 146, 231, 65, 96, 227, 33, 39, 59, 230, 25, 210, 14, 145, 17, 199, 63, 42, 142, 161, 188, 43, 200, 197, 15, 91, 243, 135, 139, 251, 245, 222, 32, 198, 167, 132, 206, 216, 101, 81, 201, 164, 239, 67, 83, 37, 93, 155, 49, 232, 62, 13, 215, 128, 255, 105, 138, 186, 11, 115, 92, 110, 84, 21, 98, 246, 53, 48, 82, 163, 22, 211, 40, 50, 250, 170, 94, 207, 234, 237, 120, 51, 88, 9, 123, 99, 192, 193, 70, 30, 223, 169, 153, 85, 4, 196, 134, 57, 119, 130, 236, 64, 24, 144, 151, 89, 221, 131, 31, 154, 55, 6, 36, 100, 124, 165, 86, 72, 8, 133, 208, 97, 38, 202, 111, 126, 106, 182, 113, 160, 112, 5, 209, 69, 140, 35, 28, 240, 238, 137, 173, 122, 75, 194, 47, 219, 90, 77, 118, 103, 23, 45, 244, 203, 177, 74, 168, 181, 34, 71, 58, 213, 16, 76, 114, 204, 0, 249, 224, 253, 226, 254, 174, 248, 95, 171, 241, 27, 66, 129, 214, 190, 68, 41, 166, 87, 185, 175, 242, 212, 117, 102, 187, 104, 159, 80, 2, 1, 60, 127, 141, 26, 136, 189, 172, 247, 228, 121, 150, 162, 252, 109, 178, 107, 3, 225, 46, 125, 20, 149, 29]
    ######################################################################################
    # S-box of TWINE
    # S = [12, 0, 15, 10, 2, 11, 9, 5, 8, 3, 13, 7, 1, 14, 6, 4]

    sb = FBCTFramework(S)
    funiformity = sb.get_fbct_uniformity()
    print(f"F-Boomerang Uniformity: {funiformity}")
    good_ios, list_of_worths = sb.get_good_ios()
    print(good_ios)
    list_of_worths.sort(reverse=True)
    # print(list_of_worths[0:10])

    # print2dlist(sb.fbct)
    # generate_latex_code(sb.fbct)

    pr_log2 = sb.compute_boomerang_switch(0xa, 0xa)
    print(f"pr = 2^{pr_log2}")
