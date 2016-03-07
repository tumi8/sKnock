from evaluation.helper import test_client
import logging, sys, getopt, signal, socket, errno, time, os

from common.definitions.Constants import *

from client.ClientInterface import ClientInterface

LOG = logging.getLogger(__name__)
shutdown = False
baconFile = None

current_start_time = None
current_time_delta = None
current_attempts = None
current_success = False

numAttempts = 0
numFailedAttempts = 0

numRequests = 0
numFailedRequests = 0

def attemptConnection(knockClient, target, udp, waitTime, number_of_retries):
    if udp:
        port = 5000
    else:
        port = 2000

    global numAttempts
    numAttempts += 1
    global numRequests
    global numFailedRequests

    global current_success
    current_success = False
    global current_attempts
    current_attempts = 0
    global current_start_time
    current_start_time = time.time()

    for i in xrange(number_of_retries):
        LOG.debug("Attempt %s...", i+1)
        try:
            numRequests += 1
            test_client.send(target, udp, port=port, knockWaitTimeMS=waitTime,
                             knockClient= knockClient, callback=connectionSuccessCallback)
            break

        except socket.timeout:
            LOG.info("Request timed out.")
            current_attempts += 1
            numFailedRequests += 1
            continue

        except socket.error, e:
            if e.errno == errno.ECONNREFUSED:
                LOG.info("Connection refused.")
                current_attempts += 1
                numFailedRequests += 1
                continue
            else:
                numFailedRequests += 1
                raise e

def connectionSuccessCallback(delay, time_recv):
    global current_success
    global current_start_time
    global current_time_delta
    current_time_delta = time_recv - current_start_time
    current_success = True


def processResult(packet_loss_percent, udp):
    global current_success
    global current_attempts
    global current_time_delta

    global numFailedAttempts

    if current_success:
        LOG.info("%d%% Percent Packet-Loss: Successfully established %s
        connection after %s attempts taking (in total) %sms",
                 packet_loss_percent, PROTOCOL.getById(not udp), current_attempts,
                 current_time_delta)
    else:
        LOG.info("%d%% Percent Packet-Loss: %s Connection attempt still failed \
        after %s attempts",
                 packet_loss_percent, PROTOCOL.getById(not udp),
                 current_attempts)
        current_time_delta = -1
        numFailedAttempts += 1

    global baconFile
    baconFile.write('%d, %d, %d, %s' % (packet_loss_percent, not udp, current_attempts, round(current_time_delta, 2)))

def start(target, packet_loss_percent, waitTime = 12, repetitions = 10, attempts_per_repetition = 3, csvOutput = '/tmp'):
    knockClient =  ClientInterface(verify=False)

    global baconFile
    baconFile = open(os.path.join(csvOutput, 'pl_eval_packetloss_client_%d.csv' % packet_loss_percent), 'w')

    for i in xrange(repetitions):
        if shutdown:
            break

        LOG.info("Repetition %d...", i+1)
        attemptConnection(knockClient, target, False, waitTime, attempts_per_repetition)
        processResult(packet_loss_percent, False)


    for i in xrange(repetitions):
        if shutdown:
            break

        LOG.info("Repetition %d...", i+1)
        attemptConnection(knockClient, target, True, waitTime, attempts_per_repetition)
        processResult(packet_loss_percent, True)

    stop(None, None)



def stop(sig, frame):
    LOG.debug('Signal %s received', sig)
    LOG.info('Stopping client...')

    global shutdown
    shutdown = True

    global numAttempts
    LOG.info('Total number of attempts: %s', numAttempts)
    global numFailedAttempts
    LOG.info('Total number of failed attempts: %s', numFailedAttempts)

    global numRequests
    LOG.info('Total number of sent port-knocking requests: %s', numRequests)
    global numFailedRequests
    LOG.info('Total number of failed port-knocking requests: %s', numFailedRequests)




def usage():
    print "Usage: pl_eval_client.py [-w <wait-time>] [-n <number of \
    repetitions>] [-a <number of attempts per repetition>] \
    <target host> <packet loss in percent>"
    sys.exit(2)

def parseArguments(argv):
    wait_time = 12
    number_of_repetitions = 10
    attempts_per_repetition = 3
    try:
        opts, args = getopt.getopt(argv, "w:n:a:")
        for opt, arg in opts:
            if opt in ("-w"):
                wait_time = float(arg)
            elif opt in ("-n"):
                number_of_repetitions = int(arg)
            elif opt in ("-a"):
                attempts_per_repetition = int(arg)

        if len(args) == 2:
            host = args[0]
            packet_loss_percent = int(args[1])
        else:
            usage()

    except getopt.GetoptError:
        usage()


    return (host, packet_loss_percent, wait_time, number_of_repetitions, attempts_per_repetition)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.WARN, stream=sys.stdout)
    test_client.LOG.setLevel(logging.INFO)
    LOG.setLevel(logging.DEBUG)
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    start(*parseArguments(sys.argv[1:]))
