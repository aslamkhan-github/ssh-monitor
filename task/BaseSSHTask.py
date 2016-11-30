import logging
from datetime import datetime, timedelta
from SShUtil import CreateSshSession

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)


class BaseSSHTask(object):

    def __init__(self, task):
        ''' Basic constructor for every SSH Task
            DO NOT OVERLOAD to keep all the functionnalities '''
        # Used in every tasks
        self.task = task
        self.valid = self.validateTask()

        # SSH specific
        self.session = None
        self.last_connection = None
        # Reconnection timeout
        self.timeout = timedelta(hours=1)

    def _updateValuePath(self):
        ''' Child class must implement this function so the path
            in graphite is updated with correct hiearchy '''
        raise NotImplementedError

    def _validateTask(self):
        ''' Child class must implement this method to validate their input
            This function must log their own error based on the validation
            Return value: True, valid input
                          False, invalid input execute will be skipped
        '''
        raise NotImplementedError

    def _execute(self, session):
        ''' Child class must implement this method, this is the specific
            processing of the function
            session will be a valid ssh session, no need to validate it '''
        raise NotImplementedError

    def _connect(self):
        ''' Handle the ssh connection and timeout '''
        # Check if already connected
        if self.session:
            # Expire session
            if datetime.now() - self.last_connection > self.timeout:
                self.session.close()
            else:
                # Keep session alive
                return True

        self.session = CreateSshSession(self.task)
        self.last_connection = datetime.now()
        return (self.session is not None)

    def validateTask(self):
        ''' Validate minimal ssh requirements then call
            implementation specific validation
            Right now task import validate non optional arguments'''
        valid = self._validateTask()
        return valid

    def execute(self, session=None):
        ''' Base template method for all tasks, it handle the redundancy of
            checking for exception and the reconnection
            Child should not override this method '''

        # Invalid arguments where passed, do not execute
        if not self.valid:
            return

        try:
            # Session was provided by higher task, simply execute
            if session:
                self._execute(session)
            # Create our own session and handle reconnection
            else:
                if not self.connect():
                    return
                self._execute(self.session)
        except:
            # Traceback will be logged here
            logger.exception('Execute raised exception on: %s', self.task.id)
            # Assume there was a ssh problem, reconnect next time
            self.session = None
