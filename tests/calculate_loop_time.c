#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "common.h"

/* calculate_loop_time -- calculate number of interations per second
 *
 * This program calculate the number of iterations per second to be run
 * as a parameter by mp_task_sim.
 *
 * This program uses pthreads to busy-wait the CPU in multiple
 * cores. */

long PARTIAL_SUM;

void *calculate_loop_time()
{
   struct timespec start, finish;
   double elapsed;

   clock_gettime(CLOCK_MONOTONIC_RAW, &start);

   /* This main loop will run until we used all the time asked
    * by the user. */
   PARTIAL_SUM = 0;
   for (;;) {
      /* Busy wait the CPU until a pre-determined number of
       * iterations. */
      for (long i = 0; i < ITERATIONS_PER_LOOP; ++i) {
         ++PARTIAL_SUM;
      }

      /* This method only works on Linux from version 2.6.28 onwards,
       * but it's the most precise way to measure time.
       * See "man 2 clock_gettime" and http://stackoverflow.com/a/2962914
       * for details. */
      clock_gettime(CLOCK_MONOTONIC_RAW, &finish);
      elapsed = (finish.tv_sec - start.tv_sec);
      elapsed += (finish.tv_nsec - start.tv_nsec) / 1000000000.0;

      if (elapsed >= SECONDS) {
         printf("Number of iterations=%ld\n", PARTIAL_SUM);
         pthread_exit(NULL);
      }
   }
}

int main(void)
{
   printf("Running for %d repetitions of %lf second(s)\n", REPETITIONS, SECONDS);

   long final_sum = 0;
   pthread_t thread;
   for (int i = 1; i <= REPETITIONS; ++i) {
      printf("(%d/%d) ", i, REPETITIONS);
      void *result = 0;
      pthread_create(&thread, NULL, calculate_loop_time, NULL);
      pthread_join(thread, &result);
      final_sum += PARTIAL_SUM;
   }
   long result = final_sum / REPETITIONS;
   printf("Mean iterations=%ld, Input=%ld\n", result, result / ITERATIONS_PER_LOOP);
   exit(EXIT_SUCCESS);
}
