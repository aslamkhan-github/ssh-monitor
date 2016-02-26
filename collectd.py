#!/bin/python

import time
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from task_parser import TaskParser


def job_function():
    global n
    print 'schedule delta:', datetime.datetime.now()


def main():

    scheduler = BackgroundScheduler()
    taskparser = TaskParser('/home/elwiss/dev/collectd_task')
    taskparser.parse()

    # Initial parsing of the task folder
    for id, value in taskparser.task_dict.iteritems():
        scheduler.add_job(job_function, 'interval',
                          seconds=value['interval'], id=id)

    scheduler.start()
    # Update jobs while running
    while True:
        try:
            time.sleep(15)

            # Check the folder to see if job list changed
            taskparser.parse()
            tasks_list = set([id for id in taskparser.task_dict])

            # Get scheduler current job list
            jobs = scheduler.get_jobs()
            jobs_list = set([job.id for job in jobs])

            # Find the difference between two
            difference = jobs_list ^ tasks_list

            # Add or remove accordingly
            for task in difference:
                # We got a new task
                if task not in jobs_list:
                    print 'Adding ', task
                    scheduler.add_job(
                        job_function, 'interval',
                        seconds=taskparser.task_dict[task]['interval'],
                        id=task)

                # Task has been removed
                if task not in tasks_list:
                    print 'Removing ', task
                    scheduler.remove_job(task)

        except KeyboardInterrupt:
            break

    scheduler.shutdown()

if __name__ == '__main__':
    main()
