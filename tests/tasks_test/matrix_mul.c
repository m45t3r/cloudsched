#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>
#include <assert.h>

#define MASTER 0
#define FROM_MASTER 1
#define FROM_WORKER 2
#define DEFAULT_SIZE 512

long **init_long_matrix(int rows, int cols);
void fprintf_matrix(FILE *stream, long** matrix, int rows, int cols);
void usage(char* program_name);

int main(int argc, char *argv[])
{
  /* Get square matrix size */
  int N = DEFAULT_SIZE;

  if(argc == 2) {
    N = atoi(argv[1]);
    if(N <= 0) {
      usage(argv[0]);
    }
  }

  /* The variables below represent the matrices. a and b are the matrices to
   * be multiplied, while c is the result matrix. */
  long **a = NULL, **b = NULL, **c = NULL;

  /* The variable below is used to initialize the matrix with values. */
  const int mul = 2;

  /* The variables below are used to calculate elapsed time. */
  double t_start = 0, t_end = 0;

  /* MPI related variables. */
  int my_rank, nproc;

  /* Initialize MPI. */
  MPI_Init(&argc, &argv);

  /* Get MPI info. */
  MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);
  MPI_Comm_size(MPI_COMM_WORLD, &nproc);

  /* Initialize matrices. */
  a = init_long_matrix(N, N);
  b = init_long_matrix(N, N);
  c = init_long_matrix(N, N);

  /* Initializing data. */
  for(int i = 0; i < N; ++i) {
    for (int j = 0; j < N; ++j) {
      a[i][j] = i * mul;
      b[i][j] = i;
    }
  }

  /* Synchronization barrier */
  MPI_Barrier(MPI_COMM_WORLD);

  if(my_rank == MASTER) {
    t_start = MPI_Wtime();
  } 

  /* Compute matrix multiplication */
  for(int k = 0; k < N; ++k) {
    for(int i = 0; i < N; ++i) {
      for(int j = 0; j < N; ++j) {
        c[i][k] += a[i][j] * b[j][k];
      }
    }
  }

  /* Synchronization barrier */
  MPI_Barrier(MPI_COMM_WORLD);

  if(my_rank == MASTER) {
    t_end = MPI_Wtime();
    printf("%lf\n", t_end - t_start);
  }

  const long col_sum = N * (N-1) / 2;
  if(my_rank == MASTER) {
    for (int i = 0; i < N; ++i) {
      for (int j = 0; j < N; ++j) {
        assert(c[i][j] == i * mul * col_sum);
      }
    }
    printf("Matrix checking sucessful!\n");
  }

  MPI_Finalize();
  exit(EXIT_SUCCESS);
}

long **init_long_matrix(int rows, int cols)
{
  long *data = (long *) malloc(rows * cols * sizeof(long));
  long **array= (long **) malloc(rows * sizeof(long*));
  if(data == NULL || array == NULL) {
    fprintf(stderr, "Could not allocate sufficient memory!");
    exit(EXIT_FAILURE);
  }
  for (int i = 0; i < rows; ++i) {
    array[i] = &(data[cols*i]);
  }
  return array;
}

void fprintf_matrix(FILE *stream, long** matrix, int rows, int cols)
{
  for(int i = 0; i < rows; ++i) {
    for(int j = 0; j < cols; ++j) {
      if(j == cols - 1) {
        fprintf(stream, "%4ld", matrix[i][j]);
      } else {
        fprintf(stream, "%4ld,", matrix[i][j]);
      }
    }
    fprintf(stream, "\n");
  }
  fprintf(stream, "\n");
}

void usage(char* program_name)
{
  fprintf(stderr, "usage: %s MATRIX_SIZE\n", program_name);
  exit(EXIT_FAILURE);
}

