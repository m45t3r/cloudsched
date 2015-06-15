#!/usr/bin/env python2

from __future__ import division

import csv
import glob
import math
import os
import sys

import numpy

N=32
fieldnames = ["n", "expected", "mean", "ci95"]
try:
    folder = sys.argv[1]
except IndexError:
    sys.exit("usage: {} RESULTS_FOLDER".format(sys.argv[0]))

with open(os.path.join(folder, 'result32.log')) as base_file:
    results = []
    for line_number, line in enumerate(base_file, 1):
        if line_number > 10:
            break
        results.append(float(line))
    base_mean = round(numpy.mean(results), ndigits=2)

with open("summary_{}.csv".format(folder), 'wb') as csv_file:
    csv_writer = csv.DictWriter(csv_file, fieldnames)
    csv_writer.writeheader()

    os.chdir(folder)
    for n, filename in enumerate(sorted(glob.glob("*.log")), 1):
        with open(filename, 'r') as log_file:
            results = []
            base = None
            for line_number, line in enumerate(log_file, 1):
                if line_number > 10:
                    break
                results.append(float(line))
            mean = numpy.mean(results)
            stdev = numpy.std(results)
            csv_writer.writerow({"n": n, "expected": "{0:.2f}".format(math.ceil(N/n) * base_mean),
                "mean": "{0:.2f}".format(round(mean, 2)), "ci95": "{0:.2f}".format(1.96 * stdev/math.sqrt(len(results)))})
