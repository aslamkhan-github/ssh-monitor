import logging
import socket

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class LinuxDiskUsage:

    def __init__(self, host, port, session, path, disks):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.destination = (host, port)
        self.session = session
        self.path = path
        self.disks = disks

    def on_output(self, task, line):
        out = line.split()
        disk_name = out[0].split('/')[2]
        path = self.path + 'disk.' + disk_name
        msg = '{}:{}|g\n'.format(path + '.size', out[1].replace('M', ''))
        msg += '{}:{}|g\n'.format(path + '.used', out[2].replace('M', ''))
        msg += '{}:{}|g\n'.format(path + '.available', out[3].replace('M', ''))
        msg += '{}:{}|g'.format(path + '.used_percent',
                                out[4].replace('M', '').replace('%',''))
        # self.sock.sendto(msg, self.destination)
        logger.info('Sent:\n%s', msg)

    def execute(self):
        for disk in self.disks:
            self.session.execute('df -BM | grep {}'.format(disk),
                                 on_stdout=self.on_output)
