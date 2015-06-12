#!/usr/bin/env python2

import csv
import glob

from backports import statistics

fieldnames = ["n", "mean", "ci95"]

with open("summary.csv", 'w') as csv_file:
    csv_writer = csv.DictWriter(csv_file, fieldnames)
    csv_writer.writeheader()
    for n, filename in enumerate(sorted(glob.glob("*.log")), 1):
        with open(filename, 'r') as log_file:
            results = [float(x) for x in log_file]
            mean = round(statistics.mean(results), ndigits=2)
            ci95 = round(0.95 * statistics.stdev(results), ndigits=2)
            csv_writer.writerow({"n": n, "mean": "{0:.2f}".format(mean), "ci95": "{0:.2f}".format(ci95)})
