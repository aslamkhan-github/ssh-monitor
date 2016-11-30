import logging
import time
import pickle
import struct
from datetime import datetime, timedelta

from SShUtil import CreateSshSession, SendGraphitePayload

logger = logging.getLogger(__name__)


class LinuxProcessMonitoring:

    def __init__(self, task):
        self.destination = (task.db_host, task.db_port)
        self.session = None
        self.last_connection = None
        self.task = task
        self.pid = 0
        self.path = self.task.path + '.process'
        self.current = ''

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

    def execute(self, session):
        if session:
            # Use external session
            self._execute(session)
        else:
            if not self.connect():
                return

            self._execute(self.session)

    def _execute(self, session):
        for p in self.task.process:
            try:
                self.current = p
                # First get the pid
                cmd = 'ps aux | grep {} | grep -v grep'.format(p)
                pid = session.execute(cmd, on_stdout=self.on_pid_output,
                                      output_timeout=3)

                # Wait until we have the pid
                pid.wait(raise_if_error=False)
                if pid.error():
                    logger.error("[%s] Error ProcessMonitoring: %s (%s) : %s", self.task.id, p, self.pid,
                                 pid.error())

                # Get top information
                pid = session.execute(
                    'top -b -n 1 -p {} | grep {}'.format(self.pid, self.pid),
                    on_stdout=self.on_output, output_timeout=3)

                pid.wait(raise_if_error=False)
                if pid.error():
                    logger.error("[%s] Error ProcessMonitoring: %s (%s) : %s", self.task.id, p, self.pid,
                                 pid.error())

            except:
                logger.exception("[%s] Exception ProcessMonitoring: %s (%s)", self.task.id, p, self.pid)

    def on_pid_output(self, task, line):
        if not line:
            return

        out = line.split()
        if len(out) < 2:
            return
        # Verify that pid is a number
        try:
            pid = int(out[1])
        except:
            logger.error("[%s] Invalid PID: %s", self.task.id, out[1])
            logger.error(line)
            return

        self.pid = out[1]

    def on_output(self, task, line):
        # pid  user                                       CPU  MEM
        # 1566 root      20   0  719932  20128   7784 S   0.0  1.0  9:02.08  {p}
        if not line:
            return

        if 'unknown option' in line or 'TERM' in line:
            logger.error(line)
            return

        now = int(time.time())
        out = line.split()

        path = self.path + "." + self.current.replace('/', '_').replace('.', '_')
        mem = (path + '.memory_percent', (now, out[-3]))
        cpu = (path + '.cpu_percent', (now, out[-4]))

        payload = pickle.dumps([mem, cpu], protocol=2)
        header = struct.pack("!L", len(payload))

        if SendGraphitePayload(self.destination, header, payload):
            logger.debug('Sent:\n%s', [mem, cpu])
