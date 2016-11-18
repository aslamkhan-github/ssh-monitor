import os
from task_parser import TaskParser
import shutil

TASK_DIR = 'task_dir/'
SCRIPT_DIR = 'task/'


class FileModel:

    def get_fullpath(self, id):
        return os.path.join(TASK_DIR, id + '.yml')

    def get_all_task(self):
        taskparser = TaskParser(TASK_DIR)
        return taskparser.parse()

    def get_all_scripts(self):
        taskparser = TaskParser(TASK_DIR)
        return taskparser.parse_scripts(SCRIPT_DIR)

    def disable(self, id):
        path = self.get_fullpath(id)
        shutil.move(path, os.path.join(TASK_DIR, id))

    def delete(self, id):
        path = os.path.join(TASK_DIR, id)
        os.remove(path)

    def get_task(self, id):
        path = self.get_fullpath(id)
        with open(path, 'r') as f:
            return f.read()

    def get_inactive(self, id):
        path = os.path.join(TASK_DIR, id)
        with open(path, 'r') as f:
            return f.read()

    def activate(self, id):
        path = os.path.join(TASK_DIR, id)
        shutil.move(path, path + '.yml')

    def get_template(self):
        path = os.path.join(TASK_DIR, 'template')
        with open(path, 'r') as f:
            return f.read()

    def get_all_inactives(self):
        inactives = [f for f in os.listdir(TASK_DIR) if '.yml' not in f]
        return inactives

    def update(self, id, text):
        with open(self.get_fullpath(id), 'w') as f:
            f.write(text)
