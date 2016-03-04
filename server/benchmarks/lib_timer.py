import logging, time

LOG = logging.getLogger(__name__)

class Timer(object):
    def __init__(self, verbose = False):
        self.verbose = verbose

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time.time()
        self.secs = self.end - self.start
        self.msecs = self.secs * 1000
        self.micsecs = self.msecs * 1000
        if self.verbose:
            LOG.info('Elapsed time: %f ms', self.msecs)