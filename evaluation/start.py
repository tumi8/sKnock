import os, time, datetime, logging, random, socket, urllib2, schedule, ConfigParser, calendar

from config import config

from knock_client.modules.ClientInterface import ClientInterface

class Job: pass

LOG = logging.getLogger('Evaluation')


def reconfigureLogging(logfile):
    [logging.root.removeHandler(handler) for handler in logging.root.handlers[:]]
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG, filename=os.path.join(os.path.dirname(__file__), 'results', logfile))

def updateJob():
    LOG.debug("Checking for new JOB on Control Server...")

    try:
        remoteJobCfg = urllib2.urlopen(config.jobCfgUrl, timeout=10)
    except (socket.timeout, socket.sslerror, urllib2.URLError, urllib2.HTTPError):
        LOG.warning("Control Server seems to be offline")
        return False


    if remoteJobCfg is not None:
        remoteJobCfgTimestamp = remoteJobCfg.info().getdate('last-modified')
        if remoteJobCfgTimestamp is None:
            remoteJobCfgTimestamp = remoteJobCfg.info().getdate('date')

        if remoteJobCfgTimestamp is None:
            LOG.error("Cannot obtain metadata of remote JOB file")
            return False
        else:
            remoteJobCfgTimestamp = calendar.timegm(remoteJobCfgTimestamp)
            #datetime.datetime.fromtimestamp(os.path.getmtime(config.jobCfgFile), tz=time.tzname[time.daylight]).utctimetuple()
            if os.path.isfile(config.jobCfgFile) and not os.path.getmtime(config.jobCfgFile) < remoteJobCfgTimestamp:
                # Our File is up to date -> no downloading
                LOG.debug("JOB is up to date.")
                return True
            else:
                if not os.path.isfile(config.jobCfgFile):
                    # We don't have a JOB at all
                    LOG.debug("No JOB found in cache. Downloading...")
                else:
                    # Our JOB is not up to date
                    LOG.debug("Found new JOB. Downloading...")

                try:
                    with open(config.jobCfgFile, 'w') as crlFileHandle:
                        crlFileHandle.write(remoteJobCfg.read())
                        LOG.debug("Successfully downloaded new JOB from Server")
                        return True
                except:
                    LOG.error("Error downloading JOB file!")
                    return False


def loadJob():
    jobReader = ConfigParser.SafeConfigParser()
    jobReader.read(config.jobCfgFile)

    job = Job()

    job.ID = jobReader.get('General', 'id')
    job.processed = jobReader.getboolean('General', 'processed')

    job.startTime = jobReader.get('Parameters', 'starttime')
    job.repeatNum = jobReader.getint('Parameters', 'repetitions')
    job.repeatWait = jobReader.getint('Parameters', 'time_between_repetitions')

    job.targetServer = jobReader.get('Target', 'hostname')
    job.targetRetries = jobReader.getint('Target', 'retries')
    job.targetTimeout = jobReader.getint('Target', 'timeout')
    if jobReader.has_option('Target', 'port'):
        job.targetPort = jobReader.getint('Target', 'port')
    else:
        job.targetPort = random.randint(1900, 20000)

    return job



def executeJob(job):
    if job.processed == True:
        LOG.debug('JOB with ID %s has already been processed! Skipping execution...', job.ID)
        return

    LOG.debug('Processing JOB with ID %s', job.ID)
    reconfigureLogging('job-%s.log' % job.ID)

    startTime = datetime.datetime.strptime(job.startTime, '%Y-%m-%d %H:%M:%S')
    while datetime.datetime.now() < startTime:
        time.sleep(1)

    knockClient = ClientInterface(timeout=job.targetTimeout, numRetries=job.targetRetries)

    for i in xrange(job.repeatNum):
        knockClient.knockOnPort(job.targetServer, job.targetPort)
        time.sleep(job.repeatWait)

    reconfigureLogging('eval.log')

    # Mark JOB as processed
    job.processed = True
    jobWriter = ConfigParser.SafeConfigParser()
    jobWriter.read(config.jobCfgFile)
    jobWriter.set('General', 'processed', 'true')
    with open(config.jobCfgFile, mode='w') as jobCfgFile:
        jobWriter.write(jobCfgFile)

    LOG.debug('Done processing JOB with ID %s', job.ID)




def processAndSendResults(): pass

def processNewJob():
    if updateJob():
        job = loadJob()
        executeJob(job)



def main():
    reconfigureLogging('eval.log')
    LOG.debug('Starting new evaluation session...')
    schedule.every(1).minutes.do(processNewJob)

    while True:
        schedule.run_pending()
        time.sleep(1)



if __name__ == '__main__':
    main()