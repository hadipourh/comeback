# An Efficient Automatic Tool to Search for Boomerang Distinguishers

This repository includes the source code of tools we used in our paper entitled [*Throwing Boomerangs into Feistel Structures: Application to CLEFIA, WARP, LBlock, LBlock-s and TWINE*](https://eprint.iacr.org/2022/745).

![logo](./miscellaneous/logo.svg)

---

- [An Efficient Automatic Tool to Search for Boomerang Distinguishers](#an-efficient-automatic-tool-to-search-for-boomerang-distinguishers)
  - [Prerequisites](#prerequisites)
  - [Usage](#usage)
  - [S-box Analyzer](#s-box-analyzer)
  - [Paper](#paper)
  - [License](#license)

---

## Prerequisites

Our tool to find distinguishers is written in Python3 and requires the following software:

- [Gurobi](https://www.gurobi.com/)
- [Tex Live](https://www.tug.org/texlive/)

## Usage

Our tool is written in [Python3](https://www.python.org/downloads/) and follows the modular design paradigm. For instance, one module provides a simple user interface for the user, one module finds the truncated differential trails according to the method described in our paper, and another module instantiates the discovered truncated trails and computes the differential effect. There is also another module that generates the shape of the discovered distinguisher. For the experimental evaluations we have employed the C implementations provided by the designers of targeted ciphers.

The usage of our tool is the same for all applications. Thus we only show its usage for WARP. Our tool for WARP is located [here](warp). To see a brief documentation of parameters, run the following command:

```sh
python3 boom.py --help
```

For example to reproduce our distinguisher for 14 rounds of WARP, you can use the following command:

```sh
python3 boom.py -r0 2 -rm 10 -r1 2 -w0 6 -wm 3 -w1 6
```

Running this command, leaves a `.tex` file named `bmd.tex` within the working directory. By compiling `bmd.tex` using the following command, you can generate the shape of the discovered distinguisher in PDF format:

```sh
latexmk -pdf bmd.tex
```

The result of running the above command is a shape like this:

![bmd.svg](miscellaneous/bmdwarp14r.svg)

To compute the probability of boomerang switch in our 14-round boomerang distinguisher for WARP based on the FBCT framework, refer to [warp/theoretical-evaluation](warp/theoretical-evaluation) and see the [README](warp/theoretical-evaluation/README.md). For experimental verifications refer to [warp/experimental-evaluation](warp/experimental-evaluation) and see the [README](warp/experimental-evaluation/README.md).

---

As another example, to reproduce our distinguisher for 23 rounds of WARP, you can run the following command:

```sh
python3 boom.py -r0 6 -rm 10 -r1 7 -w0 2 -wm 1 -w1 2
```

Running the above command leaves a `bmd.tex` file in the working directory. By compiling this file using `latexmk -pdf bmd.tex` command you can generate the shape of the distinguisher in PDF format.

![bmd.svg](miscellaneous/bmdwarp23r.svg)

## S-box Analyzer

Our tool for encoding the DDT, LAT and the [MPT]() of S-boxes is available [here](https://github.com/hadipourh/sboxanalyzer).

## Paper

If you use our codes in a project resulting in an academic publication, please acknowledge it by citing our paper:

```txt
@misc{cryptoeprint:2022/745,
      author = {Hosein Hadipour and Marcel Nageler and Maria Eichlseder},
      title = {Throwing Boomerangs into Feistel Structures: Application to CLEFIA, WARP, LBlock, LBlock-s and TWINE},
      howpublished = {Cryptology ePrint Archive, Paper 2022/745},
      year = {2022},
      note = {\url{https://eprint.iacr.org/2022/745}},
      url = {https://eprint.iacr.org/2022/745}
}
```

---

## License
[![license](./miscellaneous/license-MIT-informational.svg)](https://en.wikipedia.org/wiki/MIT_License)

Our tool is released under the [MIT](./LICENSE.txt) license.
