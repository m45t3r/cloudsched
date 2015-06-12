#!/usr/bin/env python

import sys

from backports import statistics

with open(sys.argv[1], 'r') as result_file:
    results = [float(x) for x in result_file]
    mean = round(statistics.mean(results), ndigits=2)
    stdev = round(statistics.stdev(results), ndigits=2)
    print("{0:.2f},{1:.2f}".format(mean, stdev))
