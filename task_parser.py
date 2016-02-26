import unittest
import yaml
from os import listdir, path
from os.path import isfile, join


class TaskParser:

    def __init__(self, dir):
        self.dir = path.abspath(dir)
        self.task_dict = {}

    def parse(self):
        self.task_dict = {}
        file_list = [join(self.dir, f)
                     for f in listdir(self.dir) if isfile(join(self.dir, f))]
        for f in file_list:
            with open(f, 'r') as stream:
                self.task_dict[f] = yaml.load(stream)


class TaskParserTests(unittest.TestCase):

    def test_parse(self):
        t = TaskParser('/home/elwiss/dev/collectd_task')
        t.parse()
        print t.task_dict

    def test_set(self):
        a = ['a', 'c', 'd']
        b = ['a','b','d','e']
        result = set(a) ^ set(b)
        print result

if __name__ == '__main__':
    unittest.main()
