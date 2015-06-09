#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "common.h"

/* mp_task_sim -- simulate multi-processor task run
 *
 * This program simulate an execution of a multi-processor task by
 * consuming a number of defined CPU cores by an user defined
 * number of iterations. Run calculate_loop_time first to obtain
 * the number of iterations to run.
 *
 * This program uses pthreads to busy-wait the CPU in multiple
 * cores. */

void usage()
{
   fprintf(stderr, "usage: mp_task_sim ITERATIONS\n");
   exit(EXIT_FAILURE);
}

void *consume_cpu(void *iterations)
{
   long *it = (long *)iterations;
   long sum;
   struct timespec start, finish;
   double elapsed;

   clock_gettime(CLOCK_MONOTONIC_RAW, &start);
   /* Busy wait the CPU until a pre-determined number of
    * iterations. */
   for (long i = 0; i < (*it) * ITERATIONS_PER_LOOP; ++i) {
      ++sum;
   }

   /* This method only works on Linux from version 2.6.28 onwards,
    * but it's the most precise way to measure time.
    * See "man 2 clock_gettime" and http://stackoverflow.com/a/2962914
    * for details. */
   clock_gettime(CLOCK_MONOTONIC_RAW, &finish);
   elapsed = (finish.tv_sec - start.tv_sec);
   elapsed += (finish.tv_nsec - start.tv_nsec) / 1000000000.0;
   /* Just print a hexadecimal representation of the thread id,
    * does not matter what that actually is.
    * http://stackoverflow.com/a/1759846 */
   printf("Thread %02x finished after %g seconds\n",
         (unsigned char*) pthread_self(), elapsed);
   pthread_exit(NULL);
}

int main(int argc, char *argv[])
{
   long iterations = 0;

   if (argc < 2) {
      usage();
   } else {
      iterations = atoi(argv[1]);
      if (iterations <= 0) {
         usage();
      }
   }
   printf("Using %d threads during %ld iterations\n",
         THREADS,
         iterations * ITERATIONS_PER_LOOP);

   pthread_t threads[THREADS];
   /* Run consume_cpu() function in the number of threads and time
    * defined by the user. */
   for (int i = 0; i < THREADS; i++) {
      pthread_create(&threads[i], NULL, consume_cpu, (void *) &iterations);
   }
   /* Needs to join threads here or the main program will exit before
    * the threads finish their job. */
   for (int i = 0; i < THREADS; i++) {
      pthread_join(threads[i], NULL);
   }

   pthread_exit(NULL);
   exit(EXIT_SUCCESS);
}

