import logging

import LinuxCpuAverage
import ICEMemoryUsage
import LinuxDiskUsage

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)


class ICEBasic:

    def __init__(self, task):
        task.path = task.path + '.os.linux'
        self.cpu = LinuxCpuAverage.LinuxCpuAverage(task)
        self.mem = ICEMemoryUsage.ICEMemoryUsage(task)
        self.disk = LinuxDiskUsage.LinuxDiskUsage(task)

    def execute(self):
        self.cpu.execute()
        self.mem.execute()
        self.disk.execute()
