import BaseSSHTask
import logging
import time
import pickle
import struct

from SShUtil import SendGraphitePayload

logger = logging.getLogger(__name__)


class LinuxProcessMonitoring(BaseSSHTask):

    def _validateTask(self):
        if len(self.task.process) < 1:
            logger.warning("No process name provided, task will not execute")
            return False

        return True

    def _updateValuePath(self):
        self.task.path = self.task.path + '.process'

    def _execute(self, session):
        for p in self.task.process:
            session.execute(
                'top -n 1 -p $(pgrep {}) | grep {}'.format(p, p),
                on_stdout=self.on_output)

    def on_output(self, task, line):
        # pid  user                                       CPU  MEM
        # 1566 root      20   0  719932  20128   7784 S   0.0  1.0  9:02.08  {p}
        if not line:
            return

        if 'unknown option' in line:
            logger.error('Invalid process name, more than one value returned')
            return

        now = int(time.time())
        out = line.split()

        process = out[-1].replace('/', '_')
        path = self.task.path + process
        mem = (path + '.memory_percent', (now, out[-3]))
        cpu = (path + '.cpu_percent', (now, out[-4]))

        payload = pickle.dumps([mem, cpu], protocol=2)
        header = struct.pack("!L", len(payload))

        if SendGraphitePayload(self.destination, header, payload):
            logger.debug('Sent:\n%s', [mem, cpu])
