#!/bin/bash

set -eu

TMPDIR=`mktemp -d`
NUMBER_OF_CORES=32
ONE_SECOND=500
RESULT_FILE="$(basename "$1" .trace)-result.csv"

function clean_up() {
    rm -rf $TMPDIR/count $TMPDIR/lock
}

function kill_children() {
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
    local job_number=$1
    local run_time=$2
    local n_procs=$3
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
        if [ `readcount` -gt $n_procs ]; then
            decreasecount $n_procs
            task $job_number $run_time $n_procs &
        else
            wait -n
        fi
    done < "$1"
    wait
}

if [[ "$BASH_SOURCE" == "$0" ]]; then
    trap "clean_up; kill_children" SIGTERM SIGINT EXIT

    echo "Calculating one second of processing time"
    ONE_SECOND=`calculate_one_second`
    echo "ONE_SECOND=$ONE_SECOND"

    echo $NUMBER_OF_CORES > $TMPDIR/count

    echo "Starting tasks"
    echo "=========================================="
    echo "job_number,run_time,n_procs" |& tee $RESULT_FILE
    time run_tasks $1 |& tee -a $RESULT_FILE
fi
