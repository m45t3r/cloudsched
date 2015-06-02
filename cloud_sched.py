#!/usr/bin/env python

from __future__ import print_function, division

import copy
import logging
import math
import random
from pprint import pprint

import numpy
from matplotlib import pyplot

from swf_parser import parse_swf_file


logging.basicConfig(level=logging.DEBUG,
                    format='%(name)s | %(funcName)s | %(asctime)s | %(levelname)s | %(message)s',
                    filename='cloud_sched.log',
                    filemode='w')
# define a Handler which writes DEBUG messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
# set a format which is simpler for console use
formatter = logging.Formatter('%(funcName)-20s| %(levelname)-8s| %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)
logger = logging.getLogger("cloud_sched")


class CloudSchedException(Exception):
    pass


def filter_tasks(self, task_limit=500, time_limit=300, status_code=None, shuffle=None):
    count = 0
    filtered_tasks = []
    if shuffle:
        random.seed(shuffle)
        random.shuffle(tasks)
    for task in tasks:
        if count >= task_limit:
            break
        if status_code and status_code != task['status']:
            continue
        total_time = task['run_time'] * task['number_of_allocated_processors']
        if total_time <= time_limit:
            count += 1
            filtered_tasks.append(task)

    return filtered_tasks


def pre_process_tasks(tasks, max_n_procs=1):
    processed_tasks = []
    count = 0
    for task in tasks:
        if task['number_of_allocated_processors'] > max_n_procs:
            count += 1
            task['run_time'] = \
                math.ceil(task['number_of_allocated_processors'] /
                          max_n_procs) * task['run_time']
            task['number_of_allocated_processors'] = max_n_procs
        processed_tasks.append(task)
    logger.debug("{} reshaped tasks with n_procs={}".format(count, max_n_procs))

    return processed_tasks


def tasks_statistics(tasks, field):
    data = []
    count_data = 0
    for task in tasks:
        count_data += 1
        data.append(task[field])

    sum_data = sum(data)
    mean_data = numpy.mean(data)
    stdev_data = numpy.std(data)

    return {"count": count_data,
            "sum": sum_data,
            "mean": mean_data,
            "stdev": stdev_data}


def tasks_histogram(tasks, field, bins=10):
    data = []
    for task in tasks:
        data.append(task[field])

    pyplot.hist(data, bins)
    pyplot.title("{} histogram".format(field))
    pyplot.xlabel("Value")
    pyplot.ylabel("Frequency")
    pyplot.show()


def calculate_makespan(tasks, n_procs):
    procs = [0] * n_procs
    for task in tasks:
        if task['number_of_allocated_processors'] > n_procs:
            raise CloudSchedException("number of allocated processors is greater"
                                      " than number of current processors")
        # Since the processors is sorted in order of current run time,
        # we can allocate the task in the processor equivalent to the (number
        # of processors the task required) - 1. This would be the new task
        # start time.
        procs.sort()
        task_procs = int(task['number_of_allocated_processors'])
        start_task_time = procs[task_procs - 1]
        for p in range(task_procs):
            # TODO: needs to implement backfilling!
            procs[p] = start_task_time + task['run_time']
    # Makespan is the finish of the last allocated task
    return max(procs)


def largest_task_first(tasks, max_n_procs):
    minimum_makespan = float("inf")
    resulting_tasks = tasks
    for procs in range(1, max_n_procs + 1):
        no_processed_tasks = copy.deepcopy(tasks)
        pre_processed_tasks = pre_process_tasks(no_processed_tasks, procs)
        lft_sorted_tasks = sorted(pre_processed_tasks,
                                  key=lambda t:
                                  t['run_time'] *
                                  t['number_of_allocated_processors'],
                                  reverse=True)
        current_makespan = calculate_makespan(lft_sorted_tasks, procs)
        if current_makespan < minimum_makespan:
            logger.debug("New minimum makespan found => n_procs={}, t={}"
                         .format(procs, current_makespan))
            minimum_makespan = current_makespan
            resulting_tasks = lft_sorted_tasks
        else:
            logger.debug("New makespan is greater than minimum = > n_procs={}, t={}"
                         .format(procs, current_makespan))

    return resulting_tasks


if __name__ == "__main__":
    tasks = parse_swf_file("UniLu-Gaia-2014-2.swf")
    filtered_tasks = filter_tasks(tasks, 500, 300, 1)
    largest_task_first(filtered_tasks, 32)
