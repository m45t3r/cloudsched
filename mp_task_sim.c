#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

/* mp_task_sim -- simulate multi-processor task run
 *
 * This program simulate an execution of a multi-processor task by
 * consuming a number of defined CPU cores by an user defined
 * time (in seconds).
 *
 * This program uses pthreads to  busy-wait the CPU in multiple
 * cores. */

const int ITERATIONS_PER_LOOP=1000000;

void usage()
{
   fprintf(stderr, "usage: mp_task_sim TIME_LIMIT THREADS\n");
   exit(EXIT_FAILURE);
}

void *consume_cpu(void *time_limit)
{
   long sum;
   struct timespec start, finish;
   double elapsed;

   clock_gettime(CLOCK_MONOTONIC_RAW, &start);
   /* This main loop will run until we used all the time asked
    * by the user. */
   for (;;) {
      /* Busy wait the CPU until a pre-determined number of
       * iterations. */
      for (int i = 0; i < ITERATIONS_PER_LOOP; ++i) {
         ++sum;
      }


      /* This method only works on Linux from version 2.6.28 onwards,
       * but it's the most precise way to measure time.
       * See "man 2 clock_gettime" and http://stackoverflow.com/a/2962914
       * for details. */
      clock_gettime(CLOCK_MONOTONIC_RAW, &finish);
      elapsed = (finish.tv_sec - start.tv_sec);
      elapsed += (finish.tv_nsec - start.tv_nsec) / 1000000000.0;
      if (elapsed > *((double *) time_limit)) {
         /* Just print a hexadecimal representation of the thread id,
          * does not matter what that actually is.
          * http://stackoverflow.com/a/1759846 */
         printf("Thread %02x finished after %g seconds\n",
               (unsigned char*) pthread_self(), elapsed);
         pthread_exit(NULL);
      }
   }
}

int main(int argc, char *argv[])
{
   double time_limit = 0.0;
   int num_threads = 0;

   if (argc < 3) {
      usage();
   } else {
      time_limit = atof(argv[1]);
      num_threads = atoi(argv[2]);
      if (time_limit <= 0.0 || num_threads <= 0) {
         usage();
      }
   }
   printf("Using %d threads during %g seconds\n", num_threads, time_limit);

   pthread_t threads[num_threads];
   /* Run consume_cpu() function in the number of threads and time
    * defined by the user. */
   for (int i = 0; i < num_threads; i++) {
      pthread_create(&threads[i], NULL, consume_cpu, (void *) &time_limit);
   }
   /* Needs to join threads here or the main program will exit before
    * the threads finish their job. */
   for (int i = 0; i < num_threads; i++) {
      pthread_join(threads[i], NULL);
   }

   pthread_exit(NULL);
   exit(EXIT_SUCCESS);
}

