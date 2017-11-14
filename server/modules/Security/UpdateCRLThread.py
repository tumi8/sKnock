import logging, os, socket, urllib2, calendar, schedule, time, atexit
from threading import Thread

LOG = logging.getLogger(__name__)

class UpdateCRLThread(Thread):
    def __init__(self, crlFile, crlUrl, crlInterval, importFunc = None):
        self.crlFile = crlFile
        self.crlUrl = crlUrl
        self.crlInterval = crlInterval
        self.importFunc = importFunc
        self.shutdown = False
        Thread.__init__(self)
        self.daemon = True
        self.updateJob = None

    def updateCRL(self):
        LOG.debug("Checking for new CRL on CA Server...")
        remoteCRL = None
        try:
            # TODO: get this from Certificate + CRL-specific cache
            remoteCRL = urllib2.urlopen(self.crlUrl, timeout=2)
        except (socket.timeout, socket.sslerror, urllib2.URLError, urllib2.HTTPError):
            LOG.warning("CA Server seems to be offline")

        if remoteCRL is not None:
            remoteCRLTimestamp = remoteCRL.info().getdate('last-modified')
            if remoteCRLTimestamp is None:
                remoteCRLTimestamp = remoteCRL.info().getdate('date')

            if remoteCRLTimestamp is None:
                LOG.error("Cannot obtain metadata of remote CRL file")
            else:
                remoteCRLTimestamp = calendar.timegm(remoteCRLTimestamp)

                if os.path.isfile(self.crlFile) and not os.path.getmtime(self.crlFile) < remoteCRLTimestamp:
                    # Our File is up to date -> no downloading
                    LOG.debug("CRL is up to date.")
                else:
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
                    except:
                        LOG.error("Error downloading CRL file!")

    def run(self):
        atexit.register(self.stop)

        self.updateCRL()
        self.updateJob = schedule.every(self.crlInterval).minutes.do(self.updateCRL)

        while not self.shutdown:
            schedule.run_pending()
            time.sleep(5)


    def stop(self):
        if self.updateJob is not None:
            schedule.cancel_job(self.updateJob)
        self.shutdown = True
