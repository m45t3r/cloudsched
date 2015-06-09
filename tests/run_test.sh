#!/bin/bash

set -e

TMPDIR=`mktemp -d`
NUMBER_OF_CORES=32
ONE_SECOND=500

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
    count=$(( `readcount` + $1 ))
    echo $count > $TMPDIR/count
    unlock
}

function decreasecount() {
    lock
    count=$(( `readcount` - $1 ))
    echo $count > $TMPDIR/count
    unlock
}

function task() {
    echo "Running process for $1 seconds with $2 CPUs"
    ./mp_task_sim $(( $1 * $ONE_SECOND )) $2 2>/dev/null
    increasecount $2
}

function calculate_one_second() {
    ./calculate_loop_time | grep -oP 'Input=\K([0-9]*)'
}

function run_tasks() {
    while read -r run_time n_procs; do
        if [ `readcount` -gt $n_procs ]; then
            decreasecount $n_procs
            task $run_time $n_procs &
        else
            wait -n
        fi
    done < "$1"
}

if [[ "$BASH_SOURCE" == "$0" ]]; then
    trap "clean_up; kill_children" SIGTERM SIGINT EXIT

    echo "Calculating one second of processing time"
    #ONE_SECOND=`calculate_one_second`
    echo "One second is equals to $ONE_SECOND of iterations"

    echo $NUMBER_OF_CORES > $TMPDIR/count

    echo "Starting tasks"
    run_tasks $1
fi
