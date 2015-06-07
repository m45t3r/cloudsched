#!/usr/bin/env python

from __future__ import print_function, division

import csv
import copy
import logging
import math
import random
import time
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


# Tasks schedule algorithms
# To implement a new algorithm, maintain this same prototype:
#
# def task_schedule_algorithm(tasks, max_n_procs)
#
# Where tasks is a list of tasks and max_n_procs is the maximum number of
# processors
# TODO: implement backfilling where it makes sense
def first_in_first_out(tasks, max_n_procs):
    resulting_tasks = reshape_all_tasks(tasks, max_n_procs)

    return resulting_tasks


def largest_task_first(tasks, max_n_procs):
    minimum_makespan = float("inf")
    resulting_tasks = tasks
    for procs in range(1, max_n_procs + 1):
        pre_processed_tasks = reshape_all_tasks(tasks, procs)
        # We could use get_largest_task here but this should be faster
        lft_sorted_tasks = sorted(pre_processed_tasks,
                                  key=get_task_run_time,
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


def reduce_idle_time_conservative(tasks, max_n_procs):
    resulting_tasks = []
    pre_processed_tasks = reshape_all_tasks(tasks, max_n_procs)
    # The initial idle time is 0, since there is no tasks allocated yet
    idle_time = 0
    n_procs_idle = 0

    while True:
        if not pre_processed_tasks:
            break
        elif idle_time > 0 or n_procs_idle > 0:
            sorted_tasks = sorted(pre_processed_tasks, key=get_task_run_time, reverse=True)
            for task in sorted_tasks:
                if idle_time == 0 or n_procs_idle == 0:
                    break
                task_run_time = get_task_run_time(task)
                if task_run_time <= idle_time:
                    reshaped_task = reshape_task(task, n_procs_idle)[0]
                    for i in range(1, int(n_procs_idle))[::-1]:
                        current_reshaped_task, reshaped = reshape_task(task, n_procs_idle)
                        if not reshaped or current_reshaped_task['run_time'] > reshaped_task['run_time']:
                            break
                        else:
                            reshaped_task = current_reshaped_task
                    n_procs_idle -= reshaped_task['number_of_allocated_processors']
                    idle_time -= task_run_time
                    # This task should be skipped when calculating the makespan, because
                    # it's allocated between tasks.
                    reshaped_task['fill_up'] = True
                    resulting_tasks.append(reshaped_task)
                    pre_processed_tasks.remove(task)
            idle_time = 0
            n_procs_idle = 0
        else:
            largest_task = get_largest_task(pre_processed_tasks)
            resulting_tasks.append(largest_task)
            pre_processed_tasks.remove(largest_task)
            n_procs_idle = max_n_procs - largest_task['number_of_allocated_processors']
            idle_time = n_procs_idle * largest_task['run_time']

    return resulting_tasks


# VM tasks schedule algorithms
# To implement a new algorithm, maintain this same prototype:
#
# def task_schedule_algorithm(tasks, procs_per_vm, vms)
#
# Where tasks is a list of tasks, procs_per_vm is the number of processors
# per vm, and vms is the number of vms
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
    calculated_makespans = [0] * vms
    for task in tasks:
        minimal_makespan = float('inf')
        selected_vm = None
        for current_vm in enumerate(tasks_per_vm):
            if not current_vm:
                selected_vm = current_vm
                break
            else:
                if calculated_makespans[current_vm[0]] < minimal_makespan:
                    minimal_makespan = calculated_makespans[current_vm[0]]
                    selected_vm = current_vm
        vm_number, vm = selected_vm
        vm.append(task)
        calculated_makespans[vm_number] = \
                calculate_makespan(vm, procs_per_vm)

    return tasks_per_vm


# Auxiliary algorithms
# Used by the algorithms above
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


def calculate_makespan(tasks, n_procs):
    procs = [0] * n_procs
    for task in tasks:
        if task['number_of_allocated_processors'] > n_procs:
            raise CloudSchedException("number of allocated processors is greater"
                                      " than number of current processors")
        # Tasks marked with fill_up keyword should be skipped, since they're
        # allocated between tasks.
        if 'fill_up' in task:
            continue
        # Since the processors is sorted in order of current run time,
        # we can allocate the task in the processor equivalent to the (number
        # of processors the task required) - 1. This would be the new task
        # start time.
        procs.sort()
        task_procs = int(task['number_of_allocated_processors'])
        start_task_time = procs[task_procs - 1]
        gap = 0.0
        for p in range(task_procs):
            # TODO: implement backfilling to reduce this gaps
            gap += start_task_time - procs[p]
            procs[p] = start_task_time + task['run_time']
        if gap > 0.0:
            logger.debug("Gap of {} found before allocation of task {}"
                         .format(gap, task['job_number']))
    # Makespan is the finish of the last allocated task
    return max(procs)


def calculate_makespan_vms(tasks_per_vm, procs_per_vm, vms):
    time_per_vm = [0] * vms
    for i, vm_tasks in enumerate(tasks_per_vm):
        time_per_vm[i] = calculate_makespan(vm_tasks, procs_per_vm)
    return max(time_per_vm)


def get_largest_task(tasks):
    return max(tasks, key=get_task_run_time)


def get_task_run_time(task):
    return task['run_time'] * task['number_of_allocated_processors']


# Misc functions
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
    tasks_to_schedule = copy.deepcopy(tasks)
    tasks_scheduled = task_schedule_alg(tasks_to_schedule, procs_per_vm)
    tasks_scheduled_to_vms = vm_schedule_alg(tasks_scheduled, procs_per_vm, number_of_vms)
    calculated_makespan = calculate_makespan_vms(tasks_scheduled_to_vms, procs_per_vm, number_of_vms)
    result_filename = "tasks_{}-{}-{}-cpus_{}-vms_{}.csv".format(len(tasks),
            task_schedule_alg.__name__, vm_schedule_alg.__name__, procs_per_vm, number_of_vms)
    export_schedule(tasks_scheduled_to_vms, result_filename)

    return calculated_makespan


if __name__ == "__main__":
    tasks = parse_swf_file("UniLu-Gaia-2014-2.swf")
    filtered_tasks = filter_tasks(tasks, 500, 300, 1, None)

    for task_schedule_alg in [first_in_first_out, largest_task_first, reduce_idle_time_conservative]:
        for vm_schedule_alg in [round_robin, minimal_current_makespan]:
            start = time.clock()
            calculated_makespan = generate_schedule(filtered_tasks, task_schedule_alg, vm_schedule_alg, 32, 1)
            end = time.clock()
            print("{}/{} calculated makespan={}".format(task_schedule_alg.__name__,
                                                        vm_schedule_alg.__name__,
                                                        calculated_makespan))
            print("elapsed time={}".format(end - start))
