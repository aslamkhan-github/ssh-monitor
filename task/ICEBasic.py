import logging
from datetime import datetime, timedelta
import LinuxCpuAverage
import ICEMemoryUsage
import LinuxDiskUsage
import LinuxProcessMonitoring
import LinuxThreadMonitoring
from SShUtil import CreateSshSession

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)


class ICEBasic:

    def __init__(self, task):
        task.path = task.path + '.os.linux'
        self.task = task
        self.cpu = LinuxCpuAverage.LinuxCpuAverage(task)
        self.mem = ICEMemoryUsage.ICEMemoryUsage(task)
        self.disk = LinuxDiskUsage.LinuxDiskUsage(task)
        self.process = LinuxProcessMonitoring.LinuxProcessMonitoring(task)
        self.thread = LinuxThreadMonitoring.LinuxThreadMonitoring(task)
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
        try:
            self.cpu.execute(self.session)
            self.mem.execute(self.session)
            self.disk.execute(self.session)
            self.process.execute(self.session)
            self.thread.execute(self.session)
        except:
            logger.exception("ICEBasic raised exception on %s:", self.task.id)
            self.session = None
