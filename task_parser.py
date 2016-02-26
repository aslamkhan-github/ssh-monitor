import unittest
import yaml
from os import listdir, path
from os.path import isfile, join


class Task:

    def __init__(self, id):
        self.id = id
        self.host = ''
        self.user = ''
        self.task = ''
        self.passwd = ''


class TaskParser:

    def __init__(self, dir):
        self.dir = path.abspath(dir)
        self.task_list = []

    def parse(self):
        self.task_list = []
        file_list = [join(self.dir, f)
                     for f in listdir(self.dir) if isfile(join(self.dir, f))]
        for f in file_list:
            with open(f, 'r') as stream:
                v = yaml.load(stream)
                self.task_list.append(self.createTask(f, v))

    def createTask(self, id, v):
        t = Task(id)
        t.host = v['host']
        t.user = v['user']
        t.task = v['task']
        t.passwd = v['pass']
        t.interval= v['interval']
        return t


class TaskParserTests(unittest.TestCase):

    def test_parse(self):
        t = TaskParser('/home/elwiss/dev/collectd_task')
        t.parse()
        print t.task_dict

    def test_set(self):
        a = ['a', 'c', 'd']
        b = ['a', 'b', 'd', 'e']
        result = set(a) ^ set(b)
        print result

if __name__ == '__main__':
    unittest.main()
