#!/usr/bin/env python

import random
import math
from pprint import pprint

import numpy
from matplotlib import pyplot

from swf_parser import parse_swf_file


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


def print_tasks(tasks, limit=None):
    count = 0
    for task in tasks:
        if limit and count >= limit:
            break
        pprint(task)
        count += 1


def tasks_histogram(tasks, field, bins=10):
    data = []
    for task in tasks:
        data.append(task[field])

    pyplot.hist(data, bins)
    pyplot.title("{} histogram".format(field))
    pyplot.xlabel("Value")
    pyplot.ylabel("Frequency")
    pyplot.show()


def largest_task_first(tasks, max_n_procs):
    for procs in range(1, max_n_procs + 1):
        pre_processed_tasks = pre_process_tasks_alg(tasks, procs)
        processed_tasks = sorted(pre_processed_tasks, key=lambda t:
                                 t['run_time'] *
                                 t['number_of_allocated_processors'],
                                 reverse=True)
        #pprint(processed_tasks)
        #for task in processed_tasks:
            #print("Task {} total run time: {}"
                  #.format(task['job_number'],
                          #task['run_time'] *
                          #task['number_of_allocated_processors']))
        return tasks


if __name__ == "__main__":
    tasks = parse_swf_file("UniLu-Gaia-2014-2.swf")
    filtered_tasks = filter_tasks(tasks, 500, 300, 1)
    #processed_tasks = pre_process_tasks_alg(filtered_tasks, 2)
    #print_tasks(processed_tasks, 10)
    #stats = tasks_statistics(processed_tasks, 'run_time')
    #pprint(stats)
    #tasks_histogram(processed_tasks, 'run_time', 50)
    largest_task_first(filtered_tasks, 1)
