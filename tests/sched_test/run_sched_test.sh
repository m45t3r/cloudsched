#!/bin/bash

set -eu

TMPDIR=`mktemp -d`
NUMBER_OF_CORES=`nproc`
ONE_SECOND=500
REPETITIONS=10

function clean_up() {
    rm -rf $TMPDIR/count $TMPDIR/lock
}

function kill_children() {
    local proc
    for proc in `jobs -p`; do
        kill $proc
    done
}

function lock() {
    while ! mkdir $TMPDIR/lock 2>/dev/null; do :; done
}

function unlock() {
    rm -rf $TMPDIR/lock
}

function readcount() {
    while ! cat $TMPDIR/count; do :; done
}

function increasecount() {
    lock
    local count=$(( `readcount` + $1 ))
    echo $count > $TMPDIR/count
    unlock
}

function decreasecount() {
    lock
    local count=$(( `readcount` - $1 ))
    echo $count > $TMPDIR/count
    unlock
}

function task() {
    local job_number=$1 run_time=$2 n_procs=$3
    local iterations=$(( $run_time * $ONE_SECOND ))
    ./mp_task_sim $job_number $iterations $n_procs
    increasecount $n_procs
}

function calculate_one_second() {
    ./calculate_loop_time | grep -oP 'Input=\K([0-9]*)'
}

function run_tasks() {
    local job_number run_time n_procs
    while read -r job_number run_time n_procs; do
        while true; do
            if [ `readcount` -ge $n_procs ]; then
                decreasecount $n_procs
                task $job_number $run_time $n_procs &
                break
            else
                wait -n
            fi
        done
    done < "$1"
    wait
}

function run_test() {
    local trace_file=$1
    local test_number=$2

    echo $NUMBER_OF_CORES > $TMPDIR/count

    echo "Starting tasks from $trace_file"
    echo "=========================================="
    echo "job_number,run_time,n_procs"
    time run_tasks $1
    echo ""
}

if [[ "$BASH_SOURCE" == "$0" ]]; then
    trap "clean_up; kill_children" SIGTERM SIGINT EXIT

    echo "Running tests with $NUMBER_OF_CORES CPUs"

    echo "Calculating one second of processing time"
    #ONE_SECOND=`calculate_one_second`
    echo "ONE_SECOND=$ONE_SECOND"

    for trace_file in *.trace; do
        result_file="$(basename "$trace_file" .trace).log"
	for i in `seq $REPETITIONS`; do
            run_test $trace_file $i |& tee -a "$result_file"
	done
	mv $trace_file ${trace_file}.ok
    done
fi
