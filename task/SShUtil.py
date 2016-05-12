import logging

from rcontrol.ssh import SshSession, ssh_client

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)


def CreateSshSession(task):
    try:
        conn = ssh_client(task.host, task.user, task.passwd)
    except:
        logger.warning('Could not connect to: %s', task.host)
        return

    try:
        session = SshSession(conn, auto_close=False)
    except:
        logger.warning('SshSession error: %s', task.host)

    return session
