#!/usr/bin/env python2

import csv
import glob
import os
import sys

import numpy

fieldnames = ["n", "mean", "ci95"]
try:
    folder = sys.argv[1]
except IndexError:
    sys.exit("usage: {} RESULTS_FOLDER".format(sys.argv[0]))

with open("summary_{}.csv".format(folder), 'wb') as csv_file:
    csv_writer = csv.DictWriter(csv_file, fieldnames)
    csv_writer.writeheader()

    os.chdir(folder)
    for n, filename in enumerate(sorted(glob.glob("*.log")), 1):
        with open(filename, 'r') as log_file:
            results = []
            for line_number, line in enumerate(log_file, 1):
                if line_number > 10:
                    break
                results.append(float(line))
            mean = round(numpy.mean(results), ndigits=2)
            ci95 = round(0.95 * numpy.std(results), ndigits=2)
            csv_writer.writerow({"n": n, "mean": "{0:.2f}".format(mean), "ci95": "{0:.2f}".format(ci95)})
