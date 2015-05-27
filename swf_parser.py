#!/usr/bin/env python

from __future__ import print_function, division

import csv
from pprint import pprint

swf_data_fields = ['job_number',  # field 1
                   'submit_time',  # field 2
                   'wait_time',  # field 3
                   'run_time',  # field 4
                   'number_of_allocated_processors',  # field 5
                   'average_cpu_time_used',  # field 6
                   'used_memory',  # field 7
                   'requested_number_of_processors',  # field 8
                   'requested_time',  # field 9
                   'requested_memory',  # field 10
                   'status',  # field 11
                   'used_id',  # field 12
                   'group_id',  # field 13
                   'executable_number',  # field 14
                   'queue_number',  # field 15
                   'partition_number',  # field 16
                   'preceding_job_number',  # field 17
                   'think_time_from_preceding_job',  # field 18
                   ]


def parse_swf_file(filename):
    """Parses swf file information and return it as a dictionary

    See 'swf_data_fields' and the website below for details:
    http://www.cs.huji.ac.il/labs/parallel/workload/swf.html

    Warning: all data are converted to floats, even if the data is
    actually an integer.

    Keyword arguments:
    filename -- name of the file
    """
    with open(filename, 'r') as swf_file:
        # Remove comments (lines starting with ';')
        clean_file = [n for n in swf_file.readlines() if not n.startswith(';')]
        # SWF uses whitespace as delimiters, and can contain a arbitrary
        # number of trailing spaces, so we need to ignore it by setting
        # skipinitialspace to True.
        result_data = csv.DictReader(clean_file, fieldnames=swf_data_fields,
                                     delimiter=' ', skipinitialspace=True,
                                     quoting=csv.QUOTE_NONNUMERIC)
    return result_data


if __name__ == "__main__":
    # Testing program with an arbitrary .swf file
    total_time = 0
    count = 0
    for trace_data in parse_swf_file("UniLu-Gaia-2014-2.swf"):
        # Using only 500 tasks
        if count >= 500:
            break
        task_time = trace_data['run_time'] * trace_data['number_of_allocated_processors']
        # Only show tasks that completed sucessful with up-to
        # 5 minutes of duration
        if trace_data['status'] == 1 and task_time <= 300:
            pprint(trace_data)
            total_time += task_time
            count += 1
    print("Number of entries:", count)
    print("Total run-time in hours:", total_time/32/3600)
