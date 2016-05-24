import logging
import time
import pickle
import struct
import traceback
from datetime import datetime, timedelta
from SShUtil import CreateSshSession, SendGraphitePayload

# logging.basicConfig(level=logging.INFO)
# logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class LinuxDiskUsage:

    def __init__(self, task):
        self.destination = (task.db_host, task.db_port)
        self.task = task
        if len(task.disks) == 0:
            logging.error("LinuxDiskUsage: No disk name list provided")
        self.session = None
        self.last_connection = None

    def connect(self):
        # Check if already connected
        if self.session:
            # Expire session
            if datetime.now() - self.last_connection > timedelta(hours=1):
                self.session.close()
            else:
                # Keep session alive
                return True

        self.session = CreateSshSession(self.task)
        self.last_connection = datetime.now()
        return (self.session is not None)

    def on_output(self, task, line):
        if 'Permission denied' in line:
            logger.error("Permission denied")
            return
        now = int(time.time())
        out = line.split()

        try:
            disk_name = out[5].replace('/', '_')
            path = self.task.path + '.disk.' + disk_name
            free = (path + '.free', (now, out[1].replace('M', '')))
            used = (path + '.used', (now, out[2].replace('M', '')))
            total = (path + '.available', (now, out[3].replace('M', '')))
            percent = (path + '.used_percent',
                       (now, out[4].replace('M', '').replace('%', '')))

            payload = pickle.dumps([free, used, total, percent], protocol=2)
            header = struct.pack("!L", len(payload))

            if SendGraphitePayload(self.destination, header, payload):
                logger.debug('Sent:\n%s', [free, used, total, percent])
        except:
            logger.error(traceback.format_exc)

    def execute(self, session=None):
        if session:
            # use external session
            for disk in self.task.disks:
                session.execute('df -BM | grep {}'.format(disk),
                                     on_stdout=self.on_output)
        else:
            # Use our own session
            if not self.connect():
                return
            for disk in self.task.disks:
                self.session.execute('df -BM | grep {}'.format(disk),
                                     on_stdout=self.on_output)
