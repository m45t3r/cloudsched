#!/usr/bin/env python

from __future__ import print_function, division

import csv
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
#console.setLevel(logging.DEBUG)
console.setLevel(logging.ERROR)
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

def reshape_task(task, max_n_procs=1):
    reshaped = False
    if task['number_of_allocated_processors'] > max_n_procs:
        reshaped = True
        task['run_time'] = \
            math.ceil(task['number_of_allocated_processors'] /
                      max_n_procs) * task['run_time']
        task['number_of_allocated_processors'] = max_n_procs
    return task, reshaped

def reshape_all_tasks(tasks, max_n_procs=1):
    processed_tasks = []
    count = 0
    for task in tasks:
        task, reshaped = reshape_task(task, max_n_procs)
        if reshaped:
            count += 1
        processed_tasks.append(task)
    logging.debug("Number of reshaped tasks: {}".format(count))

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


def round_robin(tasks, procs_per_vm, vms):
    tasks_per_vm = [[] for x in range(vms)]
    i = 0
    for task in tasks:
        try:
            tasks_per_vm[i]
        except IndexError:
            i = 0
        tasks_per_vm[i].append(task)
        i += 1

    return tasks_per_vm


def minimal_current_makespan(tasks, procs_per_vm, vms):
    tasks_per_vm = [[] for x in range(vms)]
    for task in tasks:
        minimal_makespan = float('inf')
        selected_vm = None
        for vm in tasks_per_vm:
            if not vm:
                selected_vm = vm
                break
            else:
                current_makespan = calculate_makespan(vm, procs_per_vm)
                if current_makespan < minimal_makespan:
                    minimal_makespan = current_makespan
                    selected_vm = vm
        selected_vm.append(task)

    return tasks_per_vm


def calculate_makespan_multiple_vms(tasks_per_vm, procs_per_vm, vms):
    time_per_vm = [0] * vms
    for i, vm_tasks in enumerate(tasks_per_vm):
        time_per_vm[i] = calculate_makespan(vm_tasks, procs_per_vm)
    return max(time_per_vm)


def first_in_first_out(tasks, max_n_procs):
    minimum_makespan = float("inf")
    resulting_tasks = tasks
    for procs in range(1, max_n_procs + 1):
        no_processed_tasks = copy.deepcopy(tasks)
        pre_processed_tasks = reshape_all_tasks(no_processed_tasks, procs)
        current_makespan = calculate_makespan(pre_processed_tasks, procs)
        if current_makespan < minimum_makespan:
            logger.debug("New minimum makespan found => n_procs={}, t={}"
                         .format(procs, current_makespan))
            minimum_makespan = current_makespan
            resulting_tasks = pre_processed_tasks
        else:
            logger.debug("New makespan is greater than minimum = > n_procs={}, t={}"
                         .format(procs, current_makespan))

    return resulting_tasks


def largest_task_first(tasks, max_n_procs):
    minimum_makespan = float("inf")
    resulting_tasks = tasks
    for procs in range(1, max_n_procs + 1):
        no_processed_tasks = copy.deepcopy(tasks)
        pre_processed_tasks = reshape_all_tasks(no_processed_tasks, procs)
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


def export_schedule(result_tasks, filename):
    with open(filename, 'w') as result_file:
        fieldnames = ['vm_number', 'job_order', 'orig_job_number', 'run_time', 'procs']
        csv_writer = csv.DictWriter(result_file, fieldnames)
        csv_writer.writeheader()
        for vm_number, vm_tasks in enumerate(result_tasks):
            for job_order, vm_task in enumerate(vm_tasks):
                csv_writer.writerow({'vm_number': vm_number,
                                     'job_order': job_order,
                                     'orig_job_number': vm_task['job_number'],
                                     'run_time': vm_task['run_time'],
                                     'procs': vm_task['number_of_allocated_processors']
                                     })


def generate_schedule(tasks, task_schedule_alg, vm_schedule_alg, procs_per_vm, number_of_vms):
    task_schedule = task_schedule_alg(tasks, procs_per_vm)
    vm_schedule = vm_schedule_alg(task_schedule, procs_per_vm, number_of_vms)
    calculated_makespan = calculate_makespan_multiple_vms(vm_schedule, procs_per_vm, number_of_vms)
    print("{}/{} calculated makespan={}"
          .format(task_schedule_alg.__name__, vm_schedule_alg.__name__,calculated_makespan))
    result_filename = "tasks_{}-{}-{}-cpus_{}-vms_{}.csv".format(len(tasks),
            task_schedule_alg.__name__, vm_schedule_alg.__name__, procs_per_vm, number_of_vms)
    export_schedule(vm_schedule, result_filename)


if __name__ == "__main__":
    tasks = parse_swf_file("UniLu-Gaia-2014-2.swf")
    filtered_tasks = filter_tasks(tasks, 500, 300, 1, None)
    generate_schedule(filtered_tasks, first_in_first_out, round_robin, 16, 2)
    generate_schedule(filtered_tasks, largest_task_first, round_robin, 16, 2)
    generate_schedule(filtered_tasks, first_in_first_out, minimal_current_makespan, 16, 2)
    generate_schedule(filtered_tasks, largest_task_first, minimal_current_makespan, 16, 2)
