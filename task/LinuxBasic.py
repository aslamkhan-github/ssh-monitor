import logging
from datetime import datetime, timedelta
import LinuxCpuAverage
import LinuxMemoryUsage
import LinuxDiskUsage
from SShUtil import CreateSshSession

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)


class LinuxBasic:

    def __init__(self, task):
        task.path = task.path + '.os.linux'
        self.task = task
        self.cpu = LinuxCpuAverage.LinuxCpuAverage(task)
        self.mem = LinuxMemoryUsage.LinuxMemoryUsage(task)
        self.disk = LinuxDiskUsage.LinuxDiskUsage(task)
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

    def execute(self):
        if not self.connect():
            return
        self.cpu.execute(self.session)
        self.mem.execute(self.session)
        self.disk.execute(self.session)
