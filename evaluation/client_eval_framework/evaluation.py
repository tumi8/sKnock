import os, time, datetime, logging, random, socket, urllib2, schedule, ConfigParser, calendar, string, subprocess
from socket import gethostname
from config import config

from client.ClientInterface import ClientInterface
from lib import daemonize

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
    job.parameters = Job()

    job.parameters.ID = jobReader.get('General', 'id')
    job.processed = jobReader.getboolean('General', 'processed')

    job.startTime = jobReader.get('Parameters', 'starttime')
    job.repeatNum = jobReader.getint('Parameters', 'repetitions')
    job.repeatWait = jobReader.getint('Parameters', 'time_between_repetitions')
    job.type = jobReader.get('Parameters', 'job_type')

    job.parameters.targetServer = jobReader.get('Target', 'hostname')
    job.targetRetries = jobReader.getint('Target', 'retries')
    job.targetTimeout = jobReader.getint('Target', 'timeout')

    job.resultServer = jobReader.get('Result', 'collection_server')
    job.resultServerPath = jobReader.get('Result', 'path')
    job.resultServerUser = jobReader.get('Result', 'username')
    job.resultServerPass = jobReader.get('Result', 'password')

    # Optional
    if jobReader.has_option('Target', 'port'):
        job.parameters.targetPort = jobReader.getint('Target', 'port')
    else:
        job.parameters.targetPort = random.randint(1900, 20000)

    if jobReader.has_option('Target', 'port'):
        job.parameters.forceIPv4 = jobReader.getboolean('Target', 'force_ipv4')
    else:
        job.parameters.forceIPv4 = False

    return job



def executeJob(job):
    if job.processed:
        LOG.debug('JOB with ID %s has already been processed! Skipping execution...', job.parameters.ID)
        return

    LOG.debug('Processing JOB with ID %s', job.parameters.ID)

    try:
        jobExec = __import__("jobs.%s.job" % job.type, fromlist="jobs.%s").execute
    except ImportError:
        LOG.error("Error importing implementation for Job Type: %s", job.type)
        return False

    job.parameters.resultsDir = os.path.join(os.path.dirname(__file__), 'results', 'job-%s' % job.parameters.ID)
    if not os.path.exists(job.parameters.resultsDir):
        os.makedirs(job.parameters.resultsDir)

    reconfigureLogging(os.path.join('job-%s' % job.parameters.ID, 'trace.log'))

    startTime = datetime.datetime.strptime(job.startTime, '%Y-%m-%d %H:%M:%S')
    while datetime.datetime.now() < startTime:
        time.sleep(1)

    job.parameters.knockClient = ClientInterface(timeout=job.targetTimeout, numRetries=job.targetRetries)



    for i in xrange(job.repeatNum):
        LOG.info('Executing iteration %s', i)
        jobExec(job.parameters)
        LOG.info('Finished iteration %s', i)
        LOG.info('Waiting %d seconds before continuing...', job.repeatWait)
        time.sleep(job.repeatWait)

    reconfigureLogging('eval.log')

    # Mark JOB as processed
    job.processed = True
    jobWriter = ConfigParser.SafeConfigParser()
    jobWriter.read(config.jobCfgFile)
    jobWriter.set('General', 'processed', 'true')
    with open(config.jobCfgFile, mode='w') as jobCfgFile:
        jobWriter.write(jobCfgFile)

    LOG.debug('Done processing JOB with ID %s', job.parameters.ID)
    return True




def collectResults(job):
    if not job.processed:
        LOG.warning('Tried to collect Results for JOB with ID %s, but it has not been processed yet!', job.parameters.ID)
        return
    LOG.info('Collecting result data for JOB with ID %s', job.parameters.ID)
    host_sub_folder = gethostname()
    if host_sub_folder is None:
        host_sub_folder = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(8)])
    results_target_folder = os.path.join(job.resultServerPath, 'job-%s' % job.parameters.ID, host_sub_folder)

    rsync_command = 'sshpass -p \"%s\" rsync -arze \"ssh -o StrictHostKeyChecking=no\" --rsync-path=\"mkdir -p %s && rsync\" \"%s\" %s@%s:\"%s\"' % (job.resultServerPass, results_target_folder, job.parameters.resultsDir, job.resultServerUser, job.resultServer, results_target_folder)
    LOG.debug('Generated rsync command for result data transfer: %s', rsync_command)
    subprocess.call(rsync_command, shell=True)

def processNewJob():
    if updateJob():
        try:
            job = loadJob()
            if executeJob(job):
                collectResults(job)
        except ConfigParser.Error:
            LOG.error('Could not load JOB!')



def main():
    reconfigureLogging('eval.log')
    LOG.debug('Starting new evaluation session...')
    schedule.every(1).minutes.do(processNewJob)

    daemonize.createDaemon()

    while True:
        schedule.run_pending()
        time.sleep(1)



if __name__ == '__main__':
    main()