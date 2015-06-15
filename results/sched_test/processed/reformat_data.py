#!/usr/bin/env python

import csv
import sys

fieldnames = ['Algorithms', 'Time', 'Operation']

try:
    filename = sys.argv[1]
except IndexError:
    sys.exit("usage: {} CSV_FILE".format(sys.argv[0]))

with open(sys.argv[1], 'r') as original_file, open('reformated.csv', 'wb') as result_file:
    csv_reader = csv.DictReader(original_file)
    csv_writer = csv.DictWriter(result_file, fieldnames=fieldnames)
    csv_writer.writeheader()
    for row in csv_reader:
        csv_writer.writerow({'Algorithms': row['algorithm'], 'Time': row['expected'], 'Operation': 'Expected'})
        csv_writer.writerow({'Algorithms': row['algorithm'], 'Time': row['calculated'], 'Operation': 'Calculated'})
