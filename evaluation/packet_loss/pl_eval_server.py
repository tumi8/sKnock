import logging, os, sys, getopt, signal, time

from server.ServerInterface import ServerThread
from evaluation.helper import test_server

from common.definitions.Constants import *


LOG = logging.getLogger(__name__)

shutdown = False
baconFile = None
knock_server = None
testServerThreads = []

def log_tcp(delay):
    global baconFile
    baconFile.write("%d,%s\n" % (1, round(delay, 2)))
    LOG.info("Processing Time for TCP request protected by port-knocking was %sms", delay)

def log_udp(delay):
    global baconFile
    baconFile.write("%d,%s\n" % (0, round(delay, 2)))
    LOG.info("Processing Time for UDP request protected by port-knocking was %sms", delay)


def test(packet_loss_percent = 0, delay_compensation = 0, csvOutput = '/tmp'):
    global baconFile
    baconFile = open(os.path.join(csvOutput, 'pl_eval_packetloss_server.csv'), 'w')

    global knock_server
    knock_server = ServerThread()
    knock_server.serverInterface.config.firewallPolicy = 'reject'
    knock_server.serverInterface.config.PORT_OPEN_DURATION_IN_SECONDS = 5
    knock_server.start()
    LOG.info("Knock Server started.")


    global testServerThreads
    test_server_tcp = test_server.TCPServerThread(delay_compensation, 2000, log_tcp)
    test_server_tcp.start()
    testServerThreads.append(test_server_tcp)
    LOG.info("Started test server for port-knocking protected TCP requests (port 2000)")


    test_server_udp = test_server.UDPServerThread(delay_compensation, 5000, log_udp)
    test_server_udp.start()
    testServerThreads.append(test_server_udp)
    LOG.info("Started test server for port-knocking protected UDP requests (port 5000)")

    global shutdown
    while not shutdown:
        time.sleep(3000)
    for t in testServerThreads:
        t.stop()
    for t in testServerThreads:
        t.join()
    knock_server.stop()
    baconFile.close()

def stop(sig, frame):
    global shutdown
    LOG.debug('Signal %s received', sig)
    LOG.info('Stopping server...')
    shutdown = True


def usage():
    print "Usage: pl_eval_server.py [-d <delay compensation in ms] <packet loss in percent>"
    sys.exit(2)

def parseArguments(argv):
    delay_compensation = 0
    packet_loss_percent = None

    try:
        opts, args = getopt.getopt(argv, "d:")
        for opt, arg in opts:
            if opt in ("-d"):
                delay_compensation = float(arg) / float(1000)
        if len(args) == 1:
            packet_loss_percent = int(args[0])
        else:
            usage()
    except getopt.GetoptError:
        usage()

    return packet_loss_percent, delay_compensation


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.WARNING,
        stream=sys.stdout)
    test_server.LOG.setLevel(logging.INFO)
    LOG.setLevel(logging.DEBUG)
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    test(*parseArguments(sys.argv[1:]))

