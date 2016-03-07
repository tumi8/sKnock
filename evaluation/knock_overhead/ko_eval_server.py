import logging, os, sys, getopt, signal, time

from common.definitions.Constants import IP_VERSION, PROTOCOL
from server.ServerInterface import ServerThread
from evaluation.helper import test_server

LOG = logging.getLogger(__name__)

baconFile = None
knock_server = None
testServerThreads = []

# Hack?
par_clientIP = None
par_proto = None

def log_knocked(delay):
    global baconFile
    baconFile.write("%d,%s\n" % (1, round(delay, 2)))
    LOG.info("Processing Time for request protected by port-knocking was %sms", delay)

def log_open(delay):
    global baconFile
    baconFile.write("%d,%s\n" % (0, round(delay, 2)))
    LOG.info("Processing Time for unprotected request was %sms", delay)

def test(udp, delay_compensation, client_ip, csvOutput = '/tmp'):
    global baconFile
    baconFile = open(os.path.join(csvOutput, 'ko_eval_overhead.csv'), 'w')

    global knock_server
    knock_server = ServerThread()
    knock_server.serverInterface.config.firewallPolicy = 'reject'
    knock_server.serverInterface.config.PORT_OPEN_DURATION_IN_SECONDS = 1
    knock_server.start()
    LOG.info("Knock Server started.")

    time.sleep(2)
    knock_server.serverInterface.firewallHandler.openPortForClient(60001, IP_VERSION.V4, PROTOCOL.getById(not udp), client_ip)
    global par_proto
    par_proto = PROTOCOL.getById(not udp)
    global par_clientIP
    par_clientIP = client_ip
    LOG.info("Added firewall exception for reference client (port 60001)")

    if udp:
        port = 5000
    else:
        port = 2000

    server_factory = test_server.UDPServerThread if udp else test_server.TCPServerThread
    global testServerThreads
    test_server_knocked = server_factory(delay_compensation, port, log_knocked)
    test_server_knocked.start()
    testServerThreads.append(test_server_knocked)
    LOG.info("Started test server for port-knocking protected requests (port %s)", port)

    test_server_open = server_factory(delay_compensation, 60001, log_open)
    test_server_open.start()
    testServerThreads.append(test_server_open)
    LOG.info("Started test server for (reference) un-protected requests (port 60001)")

    global shutdown
    while not shutdown:
        time.sleep(3000)
    baconFile.close()
    for t in testServerThreads:
        t.stop()
    for t in testServerThreads:
        t.join()
    knock_server.serverInterface.firewallHandler.closePortForClient(60001, IP_VERSION.V4, par_proto, par_clientIP)
    knock_server.stop()


def stop(sig, frame):
    global shutdown
    LOG.debug('Signal %s received', sig)
    LOG.info('Stopping server...')
    shutdown = True

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
    LOG.setLevel(logging.DEBUG)
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    test(*parseArguments(sys.argv[1:]))
