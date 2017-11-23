import logging
import os
import socket
import urllib2
import calendar
import atexit
from threading import Lock, Thread, Timer

LOG = logging.getLogger(__name__)


class UpdateCRLThread(Thread):

    def __init__(self, crlFile, crlUrl, crlInterval, importFunc=None):
        self.crlFile = crlFile
        self.crlUrl = crlUrl
        self.crlInterval = crlInterval * 60  # to seconds
        self.importFunc = importFunc
        self.shutdown = False
        Thread.__init__(self)
        self.daemon = True
        self.updateJob = None
        self.lock = Lock()

    def updateCRL(self):
        LOG.debug("Checking for new CRL on CA Server...")
        remoteCRL = None
        try:
            # TODO: get this from Certificate + CRL-specific cache
            remoteCRL = urllib2.urlopen(self.crlUrl, timeout=2)
        except (socket.timeout,
                socket.sslerror,
                urllib2.URLError,
                urllib2.HTTPError):
            LOG.warning("CA Server seems to be offline")
        if remoteCRL is None:
            return

        crl_timestamp = remoteCRL.info().getdate('last-modified')
        if crl_timestamp is None:
            crl_timestamp = remoteCRL.info().getdate('date')
        if crl_timestamp is None:
            LOG.error("Cannot obtain metadata of remote CRL file")
            return
        crl_timestamp = calendar.timegm(crl_timestamp)

        if (os.path.isfile(self.crlFile)
            and crl_timestamp <= os.path.getmtime(self.crlFile)):
            # Our File is up to date -> no downloading
            LOG.debug("CRL is up to date.")
            return
        if not os.path.isfile(self.crlFile):
            # We don't have a CRL at all
            LOG.debug("No CRL found in cache. Downloading...")
        else:
            # Our CRL is not up to date
            LOG.debug("Found new CRL. Downloading...")
        try:
            with open(self.crlFile, 'w') as crlFileHandle:
                crlFileHandle.write(remoteCRL.read())
                LOG.debug("Successfully downloaded new CRL from Server")
                self.importFunc(self.crlFile)
        except Exception as e:
            LOG.error("Error downloading CRL file: %s", str(e))



    def schedule(self):
        self.lock.acquire()
        self.updateJob = None
        if self.shutdown:
            self.lock.release()
            return
        try:
            self.updateCRL()
        except Exception:
            pass
        self.updateJob = Timer(self.crlInterval, self.schedule)
        self.updateJob.start()
        self.lock.release()

    def run(self):
        atexit.register(self.stop)
        self.schedule()

    def stop(self):
        self.lock.acquire()
        self.shutdown = True
        try:
            if self.updateJob is not None:
                self.updateJob.cancel()
        finally:
            self.lock.release()
