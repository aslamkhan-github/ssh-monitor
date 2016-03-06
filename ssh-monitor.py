#!/bin/python

import logging
import time
import argparse
from importlib import import_module

from apscheduler.schedulers.background import BackgroundScheduler
from task_parser import TaskParser
from rcontrol.ssh import SshSession, ssh_client

HOST = '10.102.22.29'
PORT = 8125

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ssh-manager')
# Set main logging level
logging.getLogger().setLevel(logging.INFO)


def createClass(task, session):
    MyClass = getattr(import_module('task.' + task.task), task.task)
    return MyClass(task, session)


def parse_arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument('-f', required=True, help='Task folder to be watched')
    return vars(ap.parse_args())


def addJob(task, scheduler):
    try:
        conn = ssh_client(task.host, task.user, task.passwd)
    except:
        logger.warning('Could not connect to: %s', task.host)
        return

    session = SshSession(conn, auto_close=False)
    t = createClass(task, session)
    scheduler.add_job(t.execute, 'interval', seconds=task.interval, id=task.id)
    logger.info("Added task: %s", id)


def main(args):
    scheduler = BackgroundScheduler()
    taskparser = TaskParser(args['f'])
    taskparser.parse()

    # Initial parsing of the task folder
    for t in taskparser.task_list:
        addJob(t, scheduler)

    scheduler.start()
    # Update jobs while running
    while True:
        try:
            time.sleep(15)

            # Check the folder to see if job list changed
            taskparser.parse()
            tasks_list = set([t.id for t in taskparser.task_list])

            # Get scheduler current job list
            jobs_list = set([job.id for job in scheduler.get_jobs()])

            # Find the difference between two
            difference = jobs_list ^ tasks_list

            # Add or remove accordingly
            for id in difference:
                # We got a new task
                if id not in jobs_list:
                    task = filter(lambda x: x.id == id, taskparser.task_list)
                    assert(len(task) == 1)
                    addJob(task[0], scheduler)

                # Task has been removed
                if id not in tasks_list:
                    scheduler.remove_job(id)
                    logger.info("Removed task: %s", id)

        except KeyboardInterrupt:
            break

    scheduler.shutdown()

if __name__ == '__main__':
    main(parse_arguments())
