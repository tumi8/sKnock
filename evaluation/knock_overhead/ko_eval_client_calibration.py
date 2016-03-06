from evaluation.helper import test_client
import logging, sys, getopt, signal, socket, errno, time

from client.ClientInterface import ClientInterface

LOG = logging.getLogger(__name__)
shutdown = False

def start(target, udp, startWaitTime = 20, failureRateLimit = 0.05, precision = 0.01):
    knockClient =  ClientInterface(timeout=2, verify=False)
    waitTime = calibration(target, udp, knockClient, startWaitTime, failureRateLimit, precision)
    LOG.info("Optimal wait time for %s failure Rate at a precision of %s: %sms", failureRateLimit, precision, waitTime)



def stop(sig, frame):
    LOG.debug('Signal %s received', sig)
    LOG.info('Stopping client...')
    global shutdown
    shutdown = True



def calibration(target, udp, knockClient, startWaitTime = 20, failureRateLimit = 0.05, precision = 0.01):
    LOG.info("Calibrating wait time...")
    waitTime = -1
    newWaitTime = startWaitTime
    numFailures = 0
    numRuns = int(1 / float(precision))

    if udp:
        port = 5000
    else:
        port = 2000

    iteration = 0
    global shutdown

    while waitTime != newWaitTime:
        iteration += 1
        waitTime = newWaitTime
        for i in xrange(numRuns):
            if shutdown: return
            try:
                LOG.debug("Iteration %s, Run %s", iteration, i+1)
                test_client.send(target, udp, port, knockClient=knockClient, knockWaitTimeMS=waitTime)
                time.sleep(1.2)
            except socket.timeout:
                numFailures +=1
                LOG.info("Request timed out.")
                continue
            except socket.error, e:
                if e.errno == errno.ECONNREFUSED:
                    LOG.info("Connection refused.")
                    numFailures +=1
                    continue
                else:
                    raise e

        LOG.debug("Calibration - number of failures: %s", numFailures)
        newWaitTime = adjustKnockWaitTime(waitTime, numFailures / float(numRuns), failureRateLimit, precision)
        LOG.debug("Calibration - adjusted wait time. New wait time: %sms.", newWaitTime)
        numFailures = 0

    LOG.info("Wait time calibrated to: %s", newWaitTime)
    return newWaitTime


def adjustKnockWaitTime(waitTime, failureRate, failureRateLimit, precision):
    # If we are close to the limit, but smaller we are where we want to be :)
    if failureRate <= failureRateLimit and abs(failureRateLimit - failureRate) <= precision:
        LOG.debug("Calibration - SMALLER & < %s", precision)
        return waitTime

    if failureRate < failureRateLimit and abs(failureRateLimit - failureRate) <= precision * 10:
        LOG.debug("Calibration - SMALLER & < %s", precision * 10)
        return waitTime - 2

    if failureRate < failureRateLimit and abs(failureRateLimit - failureRate) > precision * 10:
        LOG.debug("Calibration - SMALLER & > %s", precision * 10)
        return waitTime - 10

    if failureRate > failureRateLimit and abs(failureRateLimit - failureRate) <= precision * 10:
        LOG.debug("Calibration - BIGGER & < %s", precision * 10)
        return waitTime + 2

    if failureRate > failureRateLimit and abs(failureRateLimit - failureRate) > precision * 10:
        LOG.debug("Calibration - BIGGER & > %s", precision * 10)
        return waitTime + 10

    else:
        LOG.debug("Failure Rate: %s", failureRate)
        LOG.debug("Wait Time: %s", waitTime)
        LOG.debug("abs: %s", abs(failureRateLimit - failureRate))




def usage():
    print "Usage: ko_eval_client_calibration.py -w <starting wait-time> -l <failure rate limit> -p <precision> <tcp | udp> <target host>"
    sys.exit(2)

def parseArguments(argv):
    proto = None
    wait_time = 20
    limit = 0.05
    precision = 0.01

    try:
        opts, args = getopt.getopt(argv, "w:l:p:")
        for opt, arg in opts:
            if opt in ("-w"):
                wait_time = float(arg)

            if opt in ("-l"):
                limit = float(arg)

            if opt in ("-p"):
                precision = float(arg)

        if len(args) == 2:
            proto = args[0]
            host = args[1]
        else:
            usage()

    except getopt.GetoptError:
        usage()

    udp = None
    if proto == 'tcp':
        udp = False
    elif proto == 'udp':
        udp = True
    else:
        usage()

    return (host, udp, wait_time, limit, precision)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.WARNING, stream=sys.stdout)
    LOG.setLevel(logging.DEBUG)
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    start(*parseArguments(sys.argv[1:]))