from evaluation.helper import test_client
import logging, sys, getopt, signal, socket, errno, time

LOG = logging.getLogger(__name__)
shutdown = False

def start(target, udp, ego_mode, rate_limit):
    global shutdown

    rate_limit_wait = None
    if rate_limit is not None:
        rate_limit_wait = 1.0 / rate_limit

    while not shutdown:
        try:
            test_client.send(target, udp, ego_mode=ego_mode)
            if rate_limit_wait is not None:
                time.sleep(rate_limit_wait)
        except socket.error, e:
                if e.errno != errno.ECONNREFUSED:
                    raise e
                else:
                    return


def stop(sig, frame):
    LOG.debug('Signal %s received', sig)
    LOG.info('Stopping server...')
    global shutdown
    shutdown = True




def usage():
    print "Usage: fw_pp_eval_client.py [-e (\"ego-mode)\"] [-l <limit pps>] <tcp | udp> <target host>"
    sys.exit(2)

def parseArguments(argv):
    proto = None
    ego_mode = False
    rate_limit = None
    try:
        opts, args = getopt.getopt(argv, "l:e")
        for opt, arg in opts:
            if opt in ("-e"):
                ego_mode = True
            elif opt in ("-l"):
                rate_limit = int(arg)

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

    return (host, udp, ego_mode, rate_limit)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG, stream=sys.stdout)
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    start(*parseArguments(sys.argv[1:]))