import os
from task_parser import TaskParser

TASK_DIR = 'task_dir/'
SCRIPT_DIR = 'task/'


class FileModel:

    def get_all_task(self):
        taskparser = TaskParser(TASK_DIR)
        return taskparser.parse()

    def get_all_scripts(self):
        taskparser = TaskParser(TASK_DIR)
        return taskparser.parse_scripts(SCRIPT_DIR)

    def delete(self, id):
        path = os.path.join(TASK_DIR, id + '.yml')
        print 'deleting ' + path
        os.remove(path)

    def add(self, task):
        pass

    def update(self, task):
        pass
