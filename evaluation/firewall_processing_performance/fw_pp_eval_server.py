import threading, logging, sys, getopt, signal, os

from helper import test_server
from common.definitions.Constants import *
from server.modules.Configuration import config, initialize
from server.modules.Firewall.Firewall import Firewall

LOG = logging.getLogger(__name__)

number_of_open_ports = 0
firewallHandler = None
baconFile = None
shutdown = False

def openSomePorts():
    global firewallHandler, number_of_open_ports, shutdown
    for i in xrange(55000):
        firewallHandler.openPortForClient(i, IP_VERSION.V4, PROTOCOL.TCP, '192.168.0.2')
        number_of_open_ports += 1
        firewallHandler.openPortForClient(i, IP_VERSION.V4, PROTOCOL.UDP, '192.168.0.2')
        number_of_open_ports += 1
        firewallHandler.openPortForClient(i, IP_VERSION.V4, PROTOCOL.TCP, '192.168.0.3')
        number_of_open_ports += 1
        firewallHandler.openPortForClient(i, IP_VERSION.V4, PROTOCOL.UDP, '192.168.0.3')
        number_of_open_ports += 1
        if shutdown:
            return
    closeSomePorts()

def closeSomePorts():
    global firewallHandler, number_of_open_ports, shutdown
    for i in xrange(55000):
        firewallHandler.closePortForClient(i, IP_VERSION.V4, PROTOCOL.TCP, '192.168.0.2')
        number_of_open_ports -= 1
        firewallHandler.closePortForClient(i, IP_VERSION.V4, PROTOCOL.UDP, '192.168.0.2')
        number_of_open_ports -= 1
        firewallHandler.closePortForClient(i, IP_VERSION.V4, PROTOCOL.TCP, '192.168.0.3')
        number_of_open_ports -= 1
        firewallHandler.closePortForClient(i, IP_VERSION.V4, PROTOCOL.UDP, '192.168.0.3')
        number_of_open_ports -= 1
        if shutdown:
            return

def stop(sig, frame):
    global shutdown
    shutdown = True

def logProcessingDelay(delay):
    global baconFile
    baconFile.write("%d,%s\n" % (number_of_open_ports, round(delay, 2)))
    LOG.warn("IPTables Processing Time for chain-size of %s rules was %sms", number_of_open_ports, delay)

def test(udp, delay_compensation, csvOutput = '/tmp'):
    initialize()
    config.firewallPolicy = 'none'

    global firewallHandler
    firewallHandler = Firewall(config)
    firewallHandler.startup()

    global baconFile
    baconFile = open(os.path.join(csvOutput, 'ap_firewall_rulesetsize_vs_processing_delay.csv'), 'w')

    test_server.start_threaded((udp, delay_compensation, 60000, logProcessingDelay))
    openSomePorts()
    test_server.stop_threaded()
    baconFile.close()
    firewallHandler.shutdown()




def usage():
    print "Usage: fw_pp_eval_server.py [-d <delay compensation in ms] <tcp | udp>"
    sys.exit(2)

def parseArguments(argv):
    delay_compensation = 0
    try:
        opts, args = getopt.getopt(argv, "d:")
        for opt, arg in opts:
            if opt in ("-d"):
                delay_compensation = float(arg) / float(1000)
        if len(args) == 1:
            proto = args[0]
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
    return udp, delay_compensation


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.WARNING,
        stream=sys.stdout)
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    test(*parseArguments(sys.argv[1:]))
