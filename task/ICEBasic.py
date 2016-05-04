import logging

import LinuxCpuAverage
import ICEMemoryUsage
import LinuxDiskUsage

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)


class ICEBasic:

    def __init__(self, task, session):
        path = task.path + '.os.linux'
        self.cpu = LinuxCpuAverage.LinuxCpuAverage(task.db_host, task.db_port,
                                                   session, path)
        self.mem = ICEMemoryUsage.ICEMemoryUsage(task.db_host, task.db_port,
                                                 session, path)
        self.disk = LinuxDiskUsage.LinuxDiskUsage(task.db_host, task.db_port,
                                                  session, path, task.disks)

    def execute(self):
        self.cpu.execute()
        self.mem.execute()
        self.disk.execute()
