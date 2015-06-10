#!/bin/bash

BASE_NAME=cloudsched
IMAGE_NAME=bsptest # Needs any image with MPI installed!
ZONE=us-central1-a
MACHINE_TYPE=n1-standard-1
NUMBER_OF_INSTANCES=32
REPETITIONS=30

alias SSH="ssh"
alias SCP="scp"

function get_ips() {
    cat hostfile.txt | cut -d" " -f1
}

function copy_file_all() {
    local src="$1" dst="$2"
    for ip in `get_ips`; do
        SCP "$src" "$ip":"$dst"
    done
}

function compile() {
    for ip in `get_ips`; do
        SSH "$ip" "mpicc -std=gnu11 ~/matrix_mul.c -o matrix_mul"
    done
}

function run_matrix_test() {
    for i in `seq 30`; do
        echo "Test $i/$REPETITIONS" | tee -a result.log
        mpirun -np $NUMBER_OF_INSTANCES -hostfile hostfile.txt ./matrix_mul | tee -a result.log
        sleep 5
    done
}

if [[ "$BASH_SOURCE" == "$0" ]]; then
    copy_file_all matrix_mul.c ~/
    compile
    run_matrix_test
fi
