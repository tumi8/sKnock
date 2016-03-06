import logging, sys, getopt, signal, os, time, csv

from evaluation.helper import test_server
from common.definitions.Constants import *
from server.modules.Configuration import config, initialize
from server.modules.Firewall.Firewall import Firewall

LOG = logging.getLogger(__name__)

number_of_ports_to_open = 10000
number_of_open_ports = 0
loggedPackets = 0
packets_to_log_per_port = 10

currentCSVRow = [0]
baconCSV = None

firewallHandler = None
shutdown = False


def openAPortAndMeasureStuff(port, ipVersion, protocol, addr):
    global loggedPackets
    global packets_to_log_per_port
    while loggedPackets < packets_to_log_per_port:
        time.sleep(0.1)

    global currentCSVRow
    baconCSV.writerow(currentCSVRow)
    currentCSVRow = []

    firewallHandler.openPortForClient(port, ipVersion, protocol, addr)
    LOG.debug("Opened port (%s, %s, %s, %s)", port, protocol, addr, ipVersion)
    global number_of_open_ports
    number_of_open_ports += 1
    currentCSVRow.append(number_of_open_ports)
    loggedPackets = 0

def closeAPortAndMeasureStuff(port, ipVersion, protocol, addr):
    global loggedPackets
    while loggedPackets < packets_to_log_per_port:
        time.sleep(0.1)

    global currentCSVRow
    baconCSV.writerow(currentCSVRow)
    currentCSVRow = []

    firewallHandler.closePortForClient(port, ipVersion, protocol, addr)
    LOG.debug("Closed port (%s, %s, %s, %s)", port, protocol, addr, ipVersion)
    global number_of_open_ports
    number_of_open_ports -= 1
    currentCSVRow.append(number_of_open_ports)
    loggedPackets = 0

def openSomePorts():
    global firewallHandler, number_of_open_ports, shutdown
    for i in xrange(number_of_ports_to_open/4):
        openAPortAndMeasureStuff(i, IP_VERSION.V4, PROTOCOL.TCP, '192.168.0.2')
        openAPortAndMeasureStuff(i, IP_VERSION.V4, PROTOCOL.UDP, '192.168.0.2')
        openAPortAndMeasureStuff(i, IP_VERSION.V4, PROTOCOL.TCP, '192.168.0.3')
        openAPortAndMeasureStuff(i, IP_VERSION.V4, PROTOCOL.UDP, '192.168.0.3')
        if shutdown:
            return
    closeSomePorts()

def closeSomePorts():
    global firewallHandler, number_of_open_ports, shutdown
    for i in xrange(number_of_ports_to_open/4):
        closeAPortAndMeasureStuff(i, IP_VERSION.V4, PROTOCOL.TCP, '192.168.0.2')
        closeAPortAndMeasureStuff(i, IP_VERSION.V4, PROTOCOL.UDP, '192.168.0.2')
        closeAPortAndMeasureStuff(i, IP_VERSION.V4, PROTOCOL.TCP, '192.168.0.3')
        closeAPortAndMeasureStuff(i, IP_VERSION.V4, PROTOCOL.UDP, '192.168.0.3')
        if shutdown:
            return

def stop(sig, frame):
    global shutdown
    shutdown = True

def logProcessingDelay(delay):
    global loggedPackets
    global packets_to_log_per_port

    if loggedPackets < packets_to_log_per_port:
        global currentCSVRow
        currentCSVRow.append(round(delay, 2))
        LOG.info("IPTables Processing Time for chain-size of %s rules was %sms", number_of_open_ports, delay)
        loggedPackets += 1

def test(udp, delay_compensation, csvOutput = '/tmp'):
    initialize()
    config.firewallPolicy = 'none'

    global firewallHandler
    firewallHandler = Firewall(config)
    firewallHandler.startup()

    global baconCSV
    baconFile = open(os.path.join(csvOutput, 'ap_firewall_rulesetsize_vs_processing_delay.csv'), 'w')
    baconCSV = csv.writer(baconFile)

    test_server.start_threaded(udp, delay_compensation, 60000, logProcessingDelay)
    openSomePorts()
    test_server.stop_threaded()
    baconFile.close()
    firewallHandler.shutdown()




def usage():
    print "Usage: fw_pp_eval_server.py [-d delay compensation in ms] [-p precision] [-n number of ports] <tcp | udp>"
    sys.exit(2)

def parseArguments(argv):
    delay_compensation = 0
    try:
        opts, args = getopt.getopt(argv, "d:p:n:")
        for opt, arg in opts:
            if opt in ("-d"):
                delay_compensation = float(arg) / float(1000)
            elif opt in ("-p"):
                global packets_to_log_per_port
                packets_to_log_per_port = int(arg)
            elif opt in ("-n"):
                global number_of_ports_to_open
                number_of_ports_to_open = int(arg)

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
    LOG.setLevel(logging.DEBUG)
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    test(*parseArguments(sys.argv[1:]))
