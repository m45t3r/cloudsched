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
   fprintf(stderr, "usage: mp_task_sim JOB_NUMBER ITERATIONS NUM_THREADS\n");
   exit(EXIT_FAILURE);
}

void *consume_cpu(void *iterations)
{
   long *it = (long *)iterations;
   long sum;

   /* Busy wait the CPU until a pre-determined number of
    * iterations. */
   for (long i = 0; i < (*it) * ITERATIONS_PER_LOOP; ++i) {
      ++sum;
   }
   /* Just print a hexadecimal representation of the thread id,
    * does not matter what that actually is.
    * http://stackoverflow.com/a/1759846 */
   /* printf("Thread %02x finished after %g seconds\n",
         (unsigned char*) pthread_self(), elapsed); */
   pthread_exit(NULL);
}

int main(int argc, char *argv[])
{
   int job_number = 0, iterations = 0, num_threads = 0;
   struct timespec start, finish;
   double elapsed;

   if (argc < 2) {
      usage();
   } else {
      job_number = atoi(argv[1]);
      iterations = atoi(argv[2]);
      num_threads = atoi(argv[3]);
      if (job_number <= 0 || iterations <= 0 || num_threads <= 0) {
         usage();
      }
   }
   /* printf("Using %d threads during %ld iterations\n",
         num_threads,
         iterations * ITERATIONS_PER_LOOP); */

   clock_gettime(CLOCK_MONOTONIC_RAW, &start);

   pthread_t threads[num_threads];
   /* Run consume_cpu() function in the number of threads and time
    * defined by the user. */
   for (int i = 0; i < num_threads; i++) {
      pthread_create(&threads[i], NULL, consume_cpu, (void *) &iterations);
   }
   /* Needs to join threads here or the main program will exit before
    * the threads finish their job. */
   for (int i = 0; i < num_threads; i++) {
      pthread_join(threads[i], NULL);
   }

   /* This method only works on Linux from version 2.6.28 onwards,
    * but it's the most precise way to measure time.
    * See "man 2 clock_gettime" and http://stackoverflow.com/a/2962914
    * for details. */
   clock_gettime(CLOCK_MONOTONIC_RAW, &finish);
   elapsed = (finish.tv_sec - start.tv_sec);
   elapsed += (finish.tv_nsec - start.tv_nsec) / 1000000000.0;

   printf("Job #%d running with %d threads finished after %lf seconds\n",
         job_number, num_threads, elapsed);

   pthread_exit(NULL);
   exit(EXIT_SUCCESS);
}

