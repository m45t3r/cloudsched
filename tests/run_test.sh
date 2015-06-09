#!/bin/bash

TMPDIR=`mktemp -d`
NUMBER_OF_CORES=32

function clean_up() {
    rm -rf $TMPDIR/count $TMPDIR/lock
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

function sub() {
    sleep 2
    increasecount 1
}

trap "clean_up; kill 0" SIGTERM SIGINT

clean_up
echo $NUMBER_OF_CORES > $TMPDIR/count

while true; do
	echo "Number of process `ps aux | grep "[s]leep 2" | wc -l`"
    if [ `readcount` -gt 0 ]; then
        decreasecount 1
        sub &
    else
        wait -n
    fi
done
