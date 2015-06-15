#!/usr/bin/env python

import glob
import re
import sys

import numpy

algorithms = ['fifo-mcm', 'fifo-rr', 'ltf-mcm', 'ltf-rr', 'rit-mcm', 'rit-rr']

with open(glob.glob("schedule_n*.log")[0], 'r') as schedule_file: 
    makespans = re.findall("makespan=(.*)", schedule_file.read())

print("algorithm,expected,calculated,stdev")
for i, filename in enumerate(sorted(glob.glob("*.results"))):
    with open(filename, 'r') as result_file:
        results = [float(x) for x in result_file]
        mean = round(numpy.mean(results), ndigits=2)
        stdev = round(numpy.std(results), ndigits=2)
        print("{0},{1},{2:.2f},{3:.2f}".format(algorithms[i],makespans[i], mean, stdev))
