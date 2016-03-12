import logging, sys, getopt, signal, os, time, csv

from evaluation.helper import test_server
from common.definitions.Constants import *
from server.modules.Configuration import config, initialize
from server.modules.Firewall.Firewall import Firewall

LOG = logging.getLogger(__name__)

number_of_ports_to_open = 10000
port_open_interval = 1000
start_port = 1
packets_to_log_per_port = 10


number_of_open_ports = 0
number_of_open_ports_by_id = [0, 0, 0, 0]
loggedPackets = 0

nextPort = 0

currentCSVRow = [0]
baconCSV = None

firewallHandler = None
shutdown = False


def openNextPort():
    global nextPort
    global number_of_open_ports
    global number_of_open_ports_by_id
    if nextPort == 0:
        number_of_open_ports += 1
        number_of_open_ports_by_id[nextPort] += 1
        firewallHandler.openPortForClient(number_of_open_ports_by_id[nextPort], IP_VERSION.V4, PROTOCOL.TCP, '192.168.0.2')
        LOG.debug("Opened port (%s, %s, %s, %s)", number_of_open_ports_by_id[nextPort], PROTOCOL.TCP, '192.168.0.2', IP_VERSION.V4)
        nextPort = 1
    elif nextPort == 1:
        number_of_open_ports += 1
        number_of_open_ports_by_id[nextPort] += 1
        firewallHandler.openPortForClient(number_of_open_ports_by_id[nextPort], IP_VERSION.V4, PROTOCOL.UDP, '192.168.0.2')
        LOG.debug("Opened port (%s, %s, %s, %s)", number_of_open_ports_by_id[nextPort], PROTOCOL.UDP, '192.168.0.2', IP_VERSION.V4)
        nextPort = 2
    elif nextPort == 2:
        number_of_open_ports += 1
        number_of_open_ports_by_id[nextPort] += 1
        firewallHandler.openPortForClient(number_of_open_ports_by_id[nextPort], IP_VERSION.V4, PROTOCOL.TCP, '192.168.0.3')
        LOG.debug("Opened port (%s, %s, %s, %s)", number_of_open_ports_by_id[nextPort], PROTOCOL.TCP, '192.168.0.3', IP_VERSION.V4)
        nextPort = 3
    elif nextPort == 3:
        number_of_open_ports += 1
        number_of_open_ports_by_id[nextPort] += 1
        firewallHandler.openPortForClient(number_of_open_ports_by_id[nextPort], IP_VERSION.V4, PROTOCOL.UDP, '192.168.0.3')
        LOG.debug("Opened port (%s, %s, %s, %s)", number_of_open_ports_by_id[nextPort], PROTOCOL.UDP, '192.168.0.3', IP_VERSION.V4)
        nextPort = 0

def openAPortAndMeasureStuff():
    global loggedPackets
    global packets_to_log_per_port
    while loggedPackets < packets_to_log_per_port:
        time.sleep(0.1)

    global currentCSVRow
    baconCSV.writerow(currentCSVRow)
    currentCSVRow = []

    openNextPort()
    
    # Relax a little
    time.sleep(2)

    currentCSVRow.append(number_of_open_ports)
    loggedPackets = 0


def openSomePorts():
    global firewallHandler
    global shutdown
    global number_of_open_ports
    global number_of_ports_to_openu
    global port_open_interval

    while number_of_open_ports < number_of_ports_to_open:
        openAPortAndMeasureStuff()
        if shutdown:
            return

        while loggedPackets < packets_to_log_per_port:
            time.sleep(0.1)

        # Open the ports that we don't want to measure
        for x in xrange(port_open_interval -1):
            openNextPort()
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

def test(udp, delay_compensation, ego_mode, csvOutput = '/tmp'):
    initialize()
    config.firewallPolicy = 'none'

    global firewallHandler
    firewallHandler = Firewall(config)
    firewallHandler.startup()

    global baconCSV
    baconFile = open(os.path.join(csvOutput, 'ap_firewall_rulesetsize_vs_processing_delay.csv'), 'wb')
    baconCSV = csv.writer(baconFile)

    server = test_server.start_threaded(udp, delay_compensation=delay_compensation, port=60000, callback=logProcessingDelay, ego_mode=ego_mode)

    global start_port
    for i in xrange(start_port):
        openNextPort()

    openSomePorts()
    server.stop()
    baconFile.close()
    firewallHandler.shutdown()




def usage():
    print "Usage: fw_pp_eval_server.py [-e (\"ego-mode)\"] [-d delay compensation in ms] [-p precision] [-n number of ports] [-x distance between measurements] [-s start port] <tcp | udp>"
    sys.exit(2)

def parseArguments(argv):
    delay_compensation = 0
    ego_mode = False
    try:
        opts, args = getopt.getopt(argv, "d:p:n:x:s:e")
        for opt, arg in opts:
            if opt in ("-e"):
                ego_mode = True
            if opt in ("-d"):
                delay_compensation = float(arg) / float(1000)
            elif opt in ("-p"):
                global packets_to_log_per_port
                packets_to_log_per_port = int(arg)
            elif opt in ("-n"):
                global number_of_ports_to_open
                number_of_ports_to_open = int(arg)
            elif opt in ("-x"):
                global port_open_interval
                port_open_interval = int(arg)
            elif opt in ("-s"):
                global start_port
                start_port = int(arg)

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
    return udp, delay_compensation, ego_mode


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.WARNING,
        stream=sys.stdout)
    LOG.setLevel(logging.DEBUG)
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    test(*parseArguments(sys.argv[1:]))
