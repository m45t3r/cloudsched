#!/bin/bash

NUMBER_OF_INSTANCES=32
REPETITIONS=10

function get_ips() {
    cat hostfile.txt | cut -d" " -f1
}

function copy_file_all() {
    local src="$1" dst="$2"
    for ip in `get_ips`; do
        scp "$src" "$ip":"$dst"
    done
}

function compile() {
    for ip in `get_ips`; do
	echo "Compiling $ip"
        ssh "$ip" "make"
    done
}

function run_task_test() {
    local vms=`sed '/^\s*#/d' hostfile.txt | wc -l`
    local result_file="result`printf "%01d" $vms`.log"
    echo "Resulting file: $result_file"

    for i in `seq $REPETITIONS`; do
        echo "Testing $i/$REPETITIONS"
        mpirun -np $NUMBER_OF_INSTANCES -hostfile hostfile.txt ./matrix_mul 1024 | tee -a "$result_file"
        sleep 5
    done
}

if [[ "$BASH_SOURCE" == "$0" ]]; then
    copy_file_all matrix_mul.c ~/
    copy_file_all Makefile ~/
    compile
    run_matrix_test
fi
