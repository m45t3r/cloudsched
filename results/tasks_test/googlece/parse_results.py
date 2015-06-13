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
            results = []
            for line_number, line in enumerate(log_file, 1):
                if line_number > 10:
                    break
                results.append(float(x)
            mean = round(statistics.mean(results), ndigits=2)
            ci95 = round(0.95 * statistics.stdev(results), ndigits=2)
            csv_writer.writerow({"n": n, "mean": "{0:.2f}".format(mean), "ci95": "{0:.2f}".format(ci95)})
