MPICC=mpicc
CFLAGS=-O0 -Wall -std=gnu11
LDFLAGS=-lm -pthread

all: matrix_mul

matrix_mul: matrix_mul.c
	$(MPICC) $(CFLAGS) -o matrix_mul matrix_mul.c

clean:
	rm -rf matrix_mul
