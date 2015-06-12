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
pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;

void *calculate_loop_time()
{
   struct timespec start, finish;
   double elapsed;
   long sum = 0;

   clock_gettime(CLOCK_MONOTONIC_RAW, &start);

   /* This main loop will run until we used all the time asked
    * by the user. */
   for (;;) {
      /* Busy wait the CPU until a pre-determined number of
       * iterations. */
      for (long i = 0; i < ITERATIONS_PER_LOOP; ++i) {
         ++sum;
      }

      /* This method only works on Linux from version 2.6.28 onwards,
       * but it's the most precise way to measure time.
       * See "man 2 clock_gettime" and http://stackoverflow.com/a/2962914
       * for details. */
      clock_gettime(CLOCK_MONOTONIC_RAW, &finish);
      elapsed = (finish.tv_sec - start.tv_sec);
      elapsed += (finish.tv_nsec - start.tv_nsec) / 1000000000.0;

      if (elapsed >= SECONDS) {
         pthread_mutex_lock(&lock);
         PARTIAL_SUM += sum;
         pthread_mutex_unlock(&lock);
         pthread_exit(NULL);
      }
   }
}

int main(void)
{
   printf("Running for %d threads with %d repetitions for %lf second(s)\n",
         THREADS, REPETITIONS, SECONDS);

   long final_sum = 0;
   pthread_t threads[THREADS];
   for (int i = 1; i <= REPETITIONS; ++i) {
      PARTIAL_SUM = 0;
      printf("(%d/%d) ", i, REPETITIONS);
      for (int t = 0; t < THREADS; ++t) {
         pthread_create(&threads[t], NULL, calculate_loop_time, NULL);
      }
      for (int t = 0; t < THREADS; ++t) {
         pthread_join(threads[t], NULL);
      }
      printf("Number of iterations=%ld\n", PARTIAL_SUM / THREADS);
      final_sum += PARTIAL_SUM;
   }
   long result = final_sum / REPETITIONS / THREADS;
   printf("Mean iterations=%ld\nInput=%ld\n", result, result / ITERATIONS_PER_LOOP);
   exit(EXIT_SUCCESS);
}
