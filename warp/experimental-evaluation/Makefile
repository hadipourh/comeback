# -*- MakeFile -*-
# Feb 9, 2022

# compiler
# define the C compiler to use
# for C++ define  CC = g++
CC = g++
CFLAGS  = -g -Wall -fopenmp -O3 --std=c++11


all: boomerang middle_verification diff

boomerang: boomerang.c warp.c warp.h
	$(CC) $(CFLAGS) -o boomerang boomerang.c warp.c

diff: diff.c warp.c warp.h
	$(CC) $(CFLAGS) -o diff diff.c warp.c

middle_verification: middle_verification.cpp warp.c warp.h
	$(CC) $(CFLAGS) -o middle_verification middle_verification.cpp warp.c

clean:
	rm -f boomerang middle_verification diff
