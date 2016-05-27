import unittest
import logging
import yaml
import sys

from os import listdir, path
from os.path import join, basename

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ssh-monitor')


class Task:

    def __init__(self, key):
        self.id = key
        self.host = ''
        self.user = ''
        self.task = ''
        self.port = 22
        self.passwd = ''
        self.interval = 0
        self.disks = []
        self.db_host = ''
        self.db_port = 0
        self.path = ''

    def __repr__(self):
        return 'Task(id: {}, host: {}, user: {}, pass: {}, interval: {} \
 disks: {}, path: {}, db_host: {}, db_port: {})'.format(
                          self.id, self.host, self.user, self.passwd,
                          self.interval, self.disks, self.path,
                          self.db_host, self.db_port)
        '''
        msg = 'Task:\n'
        for attr, value in Task.__dict__.iteritems():
            msg += '{}: {}\n'.format(str(attr) or '', str(value) or '')
        return msg
        '''


class TaskParser:

    def __init__(self, dir):
        self.dir = path.abspath(dir)
        self.task_list = []

    def parse_scripts(self, dir):
        ignore = ['__init__.py', 'SShUtil.py']
        file_list = [f.replace('.py', '') for f in listdir(dir)
                     if f.endswith('.py') and f not in ignore]
        return file_list

    def parse(self):
        self.task_list = []
        file_list = [join(self.dir, f)
                     for f in listdir(self.dir) if f.endswith('.yml')]
        for f in file_list:
            with open(f, 'r') as stream:
                v = yaml.load(stream)
                self.task_list.append(self.createTask(f, v))
        return self.task_list

    def createTask(self, id, v):
        t = Task(basename(id).replace('.yml', ''))
        try:
            t.host = v['host']
            t.user = v['user']
            t.task = v['task']
            t.passwd = v['pass']
            t.interval = v['interval']
            t.disks = list(v['disks'])
            t.db_host = v['db_host']
            t.db_port = v['db_port']
            t.path = v['path']
            if 'port' in v:
                t.port = int(v['port'])
        except:
            logger.exception('Invalid file format in %s', id)
            sys.exit(1)

        return t


class TaskParserTests(unittest.TestCase):

    @unittest.skip("")
    def test_parse(self):
        t = TaskParser('/home/elwiss/dev/collectd_task')
        t.parse()
        print t.task_dict

    def test_repr(self):
        t = Task('id')
        print t

    @unittest.skip("")
    def test_set(self):
        a = ['a', 'c', 'd']
        b = ['a', 'b', 'd', 'e']
        result = set(a) ^ set(b)
        print result

if __name__ == '__main__':
    unittest.main()
