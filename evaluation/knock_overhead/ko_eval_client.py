from helper import test_client
import logging, sys, getopt, signal, socket, errno

from client.ClientInterface import ClientInterface

LOG = logging.getLogger(__name__)
shutdown = False

def start(target, udp):
    knockClient =  ClientInterface(timeout=2, verify=False)

    global shutdown
    while not shutdown:
        try:
            test_client.send(target, udp, 60000)
            test_client.send(target, udp, 60001, knockClient)
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
    print "Usage: ko_eval_client.py <tcp | udp> <target host>"
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
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG, stream=sys.stdout)
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    start(*parseArguments(sys.argv[1:]))