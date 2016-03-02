import logging, getopt, sys, test_client

LOG = logging.getLogger(__name__)

def calibrate(target, udp):
    delays_list = []

    def add_delay(delay):
        delays_list.append(delay)

    for i in xrange(10000):
        test_client.send(target, udp, callback=add_delay)

    avg_delay = sum(delays_list) / float(len(delays_list))
    LOG.info('Delay compensation value for calibration: %s', avg_delay)


def usage():
    print "Usage: test_client_calibration.py <tcp | udp> <target host>"
    sys.exit(2)

def parseArguments(argv):
    proto = None
    try:
        opts, args = getopt.getopt(argv, "")

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

    return (host, udp)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, stream=sys.stdout)
    calibrate(*parseArguments(sys.argv[1:]))