#!/usr/bin/env python

import random
import math
from pprint import pprint

import numpy
from matplotlib import pyplot

from swf_parser import parse_swf_file


def filter_tasks(tasks, task_limit=500, time_limit=300, status_code=None, shuffle=None):
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


def pre_process_tasks_alg(tasks, max_n_procs=1):
    processed_tasks = []
    for task in tasks:
        if task['number_of_allocated_processors'] > max_n_procs:
            task['run_time'] = math.ceil(task['number_of_allocated_processors']
                    // max_n_procs) * task['run_time']
            task['number_of_allocated_processors'] = max_n_procs
        processed_tasks.append(task)
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


if __name__ == "__main__":
    tasks = parse_swf_file("UniLu-Gaia-2014-2.swf")
    for i in range(3):
        filtered_tasks = filter_tasks(tasks, 500, 300, 1, i)
        processed_tasks = pre_process_tasks_alg(filtered_tasks, 2)
        pprint(tasks_statistics(processed_tasks, 'run_time'))
        tasks_histogram(processed_tasks, 'run_time', 50)
