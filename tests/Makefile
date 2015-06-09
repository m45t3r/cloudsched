# Modified version from the last example of below page
# http://mrbook.org/blog/tutorials/make/

CC=gcc
CFLAGS=-O0 -Wall -std=gnu11
LDFLAGS=-lm -lpthread

all: calculate_loop_time mp_task_sim

calculate_loop_time: calculate_loop_time.c common.h
	$(CC) $(CFLAGS) $(LDFLAGS) -o calculate_loop_time calculate_loop_time.c

mp_task_sim: mp_task_sim.c common.h
	$(CC) $(CFLAGS) $(LDFLAGS) -o mp_task_sim mp_task_sim.c

clean:
	rm -rf calculate_loop_time mp_task_sim
