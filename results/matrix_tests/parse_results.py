#!/usr/bin/env python3

import csv
import glob
import statistics

fieldnames = ["n", "mean", "stdev"]

with open("results.csv", 'w') as csv_file:
    csv_writer = csv.DictWriter(csv_file, fieldnames)
    csv_writer.writeheader()
    for n, filename in enumerate(sorted(glob.glob("*.log")), 1):
        with open(filename, 'r') as log_file:
            results = [float(x) for x in log_file]
            mean = statistics.mean(results)
            stdev = 0.95 * statistics.stdev(results)
            csv_writer.writerow({"n": n, "mean": mean, "stdev": stdev})
