from evaluation.helper import test_client
import logging, sys, getopt, signal, socket, errno, time

from client.ClientInterface import ClientInterface

import ko_eval_client_calibration as kecc

LOG = logging.getLogger(__name__)
shutdown = False

numRequests = 0
numFailedRequests = 0

def start(target, udp, waitTime):
    knockClient =  ClientInterface(timeout=2, verify=False)
    if udp:
        port = 5000
    else:
        port = 2000

    if waitTime is None:
        waitTime = kecc.calibration(target, udp, knockClient=knockClient, precision=0.1)

    global numRequests
    global numFailedRequests
    global shutdown
    while not shutdown:
        try:
            numRequests += 1
            test_client.send(target, udp, port=60001)
            time.sleep(1)
            test_client.send(target, udp, port=port, knockClient=knockClient, knockWaitTimeMS=waitTime)
            time.sleep(2)

        except socket.timeout:
            LOG.info("Request timed out.")
            numFailedRequests += 1
            continue

        except socket.error, e:
            if e.errno == errno.ECONNREFUSED:
                LOG.info("Connection refused.")
                numFailedRequests += 1
                continue
            else:
                raise e

def stop(sig, frame):
    LOG.debug('Signal %s received', sig)
    LOG.info('Stopping client...')

    global shutdown
    shutdown = True

    global numRequests
    LOG.info('Total number of sent port-knocking requests: %s', numRequests)
    global numFailedRequests
    LOG.info('Total number of failed port-knocking requests: %s', numFailedRequests)




def usage():
    print "Usage: ko_eval_client.py -w <wait-time> <tcp | udp> <target host>"
    sys.exit(2)

def parseArguments(argv):
    proto = None
    wait_time = None
    try:
        opts, args = getopt.getopt(argv, "w:")
        for opt, arg in opts:
            if opt in ("-w"):
                wait_time = float(arg)

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

    return (host, udp, wait_time)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.WARN, stream=sys.stdout)
    kecc.LOG.setLevel(logging.INFO)
    LOG.setLevel(logging.DEBUG)
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    start(*parseArguments(sys.argv[1:]))