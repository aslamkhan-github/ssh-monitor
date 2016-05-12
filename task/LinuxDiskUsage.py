import logging
import socket

from SShUtil import CreateSshSession

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class LinuxDiskUsage:

    def __init__(self, task):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.destination = (task.db_host, task.db_port)
        self.session = CreateSshSession(task)
        self.path = task.path
        if len(task.disks) == 0:
            logging.error("LinuxDiskUsage: No disk name list provided")
        self.disks = task.disks

    def on_output(self, task, line):
        if 'Permission denied' in line:
            return
        out = line.split()
        disk_name = out[0].split('/')[2]
        path = self.path + '.disk.' + disk_name
        msg = '{}:{}|c\n'.format(path + '.size', out[1].replace('M', ''))
        msg += '{}:{}|c\n'.format(path + '.used', out[2].replace('M', ''))
        msg += '{}:{}|c\n'.format(path + '.available', out[3].replace('M', ''))
        msg += '{}:{}|c'.format(path + '.used_percent',
                                out[4].replace('M', '').replace('%', ''))
        self.sock.sendto(msg, self.destination)
        logger.info('Sent:\n%s', msg)

    def execute(self):
        for disk in self.disks:
            self.session.execute('df -BM | grep {}'.format(disk),
                                 on_stdout=self.on_output)
