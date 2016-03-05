import logging, os, sys, getopt, signal, time

from common.definitions.Constants import IP_VERSION, PROTOCOL
from server.ServerInterface import ServerThread
from helper import test_server

LOG = logging.getLogger(__name__)

baconFile = None
knock_server = None
testServerThreads = []

def log_knocked(delay):
    global baconFile
    baconFile.write("%d,%s\n" % (1, round(delay, 2)))
    LOG.warn("Processing Time for request protected by port-knocking was %sms", delay)

def log_open(delay):
    global baconFile
    baconFile.write("%d,%s\n" % (0, round(delay, 2)))
    LOG.warn("Processing Time for unportected request was %sms", delay)

def test(udp, delay_compensation, client_ip, csvOutput = '/tmp'):
    global baconFile
    baconFile = open(os.path.join(csvOutput, 'ko_eval_overhead.csv'), 'w')

    global knock_server
    knock_server = ServerThread()
    knock_server.start()

    time.sleep(2)
    knock_server.serverInterface.firewallHandler.openPortForClient(60001, IP_VERSION.V4, PROTOCOL.getById(not udp), client_ip)
    knock_server.proto = PROTOCOL.getById(not udp)
    knock_server.client_ip = client_ip

    global testServerThreads
    test_server_knocked = test_server.ServerThread(udp, delay_compensation, 60000, log_knocked)
    test_server_knocked.start()
    testServerThreads.append(test_server_knocked)

    test_server_open = test_server.ServerThread(udp, delay_compensation, 60001, log_open)
    test_server_open.start()
    testServerThreads.append(test_server_open)


def stop(sig, frame):
    global testServerThreads
    for t in testServerThreads:
        t.stop()

    for t in testServerThreads:
        t.join()

    global knock_server
    knock_server.serverInterface.firewallHandler.closePortForClient(60001, IP_VERSION.V4, knock_server.proto, knock_server.client_ip)




def usage():
    print "Usage: ko_eval_server.py [-d <delay compensation in ms] <tcp | udp> <client ip>"
    sys.exit(2)

def parseArguments(argv):
    client_ip = None
    delay_compensation = 0
    try:
        opts, args = getopt.getopt(argv, "d:")
        for opt, arg in opts:
            if opt in ("-d"):
                delay_compensation = float(arg) / float(1000)
        if len(args) == 2:
            proto = args[0]
            client_ip = args[1]
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
    return udp, delay_compensation, client_ip


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.WARNING,
        stream=sys.stdout)
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    test(*parseArguments(sys.argv[1:]))
