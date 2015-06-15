#!/bin/bash

RESULT_DIR="split"
BASE_NAME=`basename -s .log "$1"`
REPETITIONS_PER_TEST=10

mkdir -p "$RESULT_DIR"
grep 'real' "$1" | cut -f2 | awk -F 'm' '{ print ($1 * 60 + $2) }' | split -l $REPETITIONS_PER_TEST

mv 'xaa' "${RESULT_DIR}/${BASE_NAME}_fifo_mcm.results"
mv 'xab' "${RESULT_DIR}/${BASE_NAME}_fifo_rr.results"
mv 'xac' "${RESULT_DIR}/${BASE_NAME}_ltf_mcm.results"
mv 'xad' "${RESULT_DIR}/${BASE_NAME}_ltf_rr.results"
mv 'xae' "${RESULT_DIR}/${BASE_NAME}_rit_mcm.results"
mv 'xaf' "${RESULT_DIR}/${BASE_NAME}_rit_rr.results"
