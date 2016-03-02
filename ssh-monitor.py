#!/bin/python

import time
import argparse
from importlib import import_module

from apscheduler.schedulers.background import BackgroundScheduler
from task_parser import TaskParser
from rcontrol.ssh import SshSession, ssh_client

HOST = '10.102.22.29'
PORT = 8125


def importTask(class_name, session):
    global HOST, PORT
    MyClass = getattr(import_module('task.' + class_name), class_name)
    return MyClass(HOST, PORT, session)


def parse_arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument('-f', required=True, help='Task folder to be watched')
    return vars(ap.parse_args())


def addJob(task, scheduler):
    conn = ssh_client(task.host, task.user, task.passwd)
    session = SshSession(conn, auto_close=False)
    t = importTask(task.task, session)
    scheduler.add_job(t.execute, 'interval', seconds=task.interval, id=task.id)


def main(args):

    import pdb
    pdb.set_trace()
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
            jobs = scheduler.get_jobs()
            jobs_list = set([job.id for job in jobs])

            # Find the difference between two
            difference = jobs_list ^ tasks_list

            # Add or remove accordingly
            for id in difference:
                # We got a new task
                if id not in jobs_list:
                    print 'Added ', id
                    task = filter(lambda x: x.id == id, taskparser.task_list)
                    addJob(task, scheduler)

                # Task has been removed
                if id not in tasks_list:
                    print 'Removed ', id
                    scheduler.remove_job(id)

        except KeyboardInterrupt:
            break

    scheduler.shutdown()

if __name__ == '__main__':
    main(parse_arguments())
