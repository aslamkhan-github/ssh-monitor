import socket


class LinuxBasic:

    def __init__(self, host, port, session):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.session = session
        self.host = host
        self.port = port

    def on_output(self, task, line):
        print 'Received: {}'.format(line)

    def execute(self):
        self.session.execute('uptime', on_stdout=self.on_output)
