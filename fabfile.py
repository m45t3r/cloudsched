from fabric.api import run, put
from fabric.context_managers import cd

TEST_DIR="~/tests"
TASK_SIM_FILE="./mp_task_sim"

def set_up():
    run("mkdir -p {}".format(TEST_DIR))
    put("tests/*", TEST_DIR)
    with cd(TEST_DIR):
        run("make all")
        run("make tests")

def sim_task(time_limit=1, threads=1):
    with cd(TEST_DIR):
        run("{} {} {}".format(TASK_SIM_FILE, time_limit, threads))

def clean_up():
    run("rm -rf {}".format(TEST_DIR))
