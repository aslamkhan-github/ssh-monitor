import logging

import LinuxCpuAverage
import LinuxMemoryUsage
import LinuxDiskUsage

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)


class LinuxBasic:

    def __init__(self, task):
        task.path = task.path + '.os.linux'
        self.cpu = LinuxCpuAverage.LinuxCpuAverage(task)
        self.mem = LinuxMemoryUsage.LinuxMemoryUsage(task)
        self.disk = LinuxDiskUsage.LinuxDiskUsage(task)

    def execute(self):
        self.cpu.execute()
        self.mem.execute()
        self.disk.execute()
