import logging
import socket

from rcontrol.ssh import SshSession, ssh_client

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)


def CreateSshSession(task):
    try:
        conn = ssh_client(task.host, task.user, task.passwd, port=task.port)
    except:
        logger.warning('Could not connect to: %s', task.host)
        return

    try:
        session = SshSession(conn, auto_close=True)
    except:
        logger.warning('SshSession error: %s', task.host)

    return session


def SendGraphitePayload(destination, header, payload):
    sock = socket.socket()
    try:
        sock.connect(destination)
        sock.sendall(header)
        sock.sendall(payload)
    except:
        logging.error("Could not reach graphite database at: %s",
                      destination)
        return False

    return True
