#!/bin/python

import logging
import time
import os
import argparse
from importlib import import_module

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from apscheduler.schedulers.background import BackgroundScheduler
from task_parser import TaskParser

HOST = '10.102.22.29'
PORT = 8125

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ssh-manager')
# Set main logging level
logging.getLogger().setLevel(logging.INFO)


def createClass(task):
    MyClass = getattr(import_module('task.' + task.task), task.task)
    return MyClass(task)


def parse_arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument('-f', required=True, help='Task folder to be watched')
    return vars(ap.parse_args())


def addJob(task, scheduler):
    t = createClass(task)
    scheduler.add_job(t.execute, 'interval', seconds=task.interval, id=task.id)
    logger.info("Added task: %s", id)


class YmlFileEventHandler(PatternMatchingEventHandler):

    def set_scheduler(self, scheduler):
        self.scheduler = scheduler

    def set_parser(self, parser):
        self.parser = parser

    def on_modified(self, event):
        id = os.path.basename(event.src_path).replace('.yml', '')
        logger.info("on_modified: %s", id)
        try:
            self.scheduler.remove_job(id)
        except:
            pass # We don't care if we don't find the task

        self.parser.parse()
        task = filter(lambda x: x.id == id, self.parser.task_list)
        if len(task) == 0:
            logging.error("Could not find task with ID: %s", id)
        addJob(task[0], self.scheduler)

    def on_deleted(self, event):
        id = os.path.basename(event.src_path).replace('.yml', '')
        logger.info("on_deleted: %s", id)
        self.scheduler.remove_job(id)

    def on_created(self, event):
        self.parser.parse()
        id = os.path.basename(event.src_path).replace('.yml', '')
        logger.info("on_created: %s", id)
        task = filter(lambda x: x.id == id, self.parser.task_list)
        if len(task) == 0:
            logging.error("Could not find task with ID: %s", id)
        addJob(task[0], self.scheduler)


def main(args):
    # import pdb; pdb.set_trace()
    scheduler = BackgroundScheduler()
    taskparser = TaskParser(args['f'])
    taskparser.parse()

    yml_handler = YmlFileEventHandler(patterns=["*.yml"])
    yml_handler.set_scheduler(scheduler)
    yml_handler.set_parser(taskparser)
    file_observer = Observer()
    file_observer.schedule(yml_handler, path=args['f'], recursive=False)
    file_observer.start()

    # Initial parsing of the task folder
    for t in taskparser.task_list:
        addJob(t, scheduler)
    scheduler.start()

    # Update jobs while running
    while True:
        try:
            time.sleep(15)
            # Rest of the task changes are handled by YmlFileEventHandler
            '''
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
            '''

        except KeyboardInterrupt:
            break

    scheduler.shutdown()

if __name__ == '__main__':
    main(parse_arguments())
