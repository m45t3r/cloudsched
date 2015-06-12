#!/bin/bash

BASE_NAME=`basename -s .log "$1"`
grep 'real' "$1" | cut -f2 | awk -F 'm' '{ print ($1 * 60 + $2) }' | split -l 10

mv 'xaa' "${BASE_NAME}_fifo_mcm"
mv 'xab' "${BASE_NAME}_fifo_rr"
mv 'xac' "${BASE_NAME}_ltf_mcm"
mv 'xad' "${BASE_NAME}_ltf_rr"
mv 'xae' "${BASE_NAME}_rit_mcm"
mv 'xaf' "${BASE_NAME}_rit_rr"
