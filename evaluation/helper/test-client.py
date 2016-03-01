import logging, time, struct, sys, getopt, socket

LOG = logging.getLogger(__name__)


def send(target, udp, knockClient = None):

    if udp:
        proto = socket.SOCK_DGRAM, socket.IPPROTO_UDP
        proto_str = 'udp'
    else:
        proto = socket.SOCK_STREAM, socket.IPPROTO_TCP
        proto_str = 'tcp'

    target_socket = socket.socket(socket.AF_INET, *proto)
    target_socket.settimeout(10)
    time_send = time.time()

    if knockClient is not None:
        LOG.info('Port-knocking the server before starting...')
        knockClient.knockOnPort(target, 60000, protocol=proto_str, forceIPv4=True)

    #print 'sendTime: %s' % time_send
    #LOG.info('Sending packet to test server...')
    data = struct.pack('!d', time_send)
    if udp:
        target_socket.sendto(data, (target, 60000))
    else:
        target_socket.connect((target, 60000))
        target_socket.send(data)

    response = target_socket.recv(8)

    if len(response) != 8:
        LOG.error('BOOM, something went wrong...')
        return

    time_server = struct.unpack('!d', response)[0]
    LOG.info('Received packet from test server...')
    time_recv = time.time()

    #print 'packetTime: %s' % time_server
    #print 'recvTime: %s' % time_recv

    LOG.info('Processing Delay      (Client -> Server [can start working on Data]:   %sms', (time_server - time_send) * 1000)
    LOG.info('Round-Trip-Time [RTT] (Client -> Server -> Client):                    %sms', (time_recv - time_send) * 1000)




def usage():
    print "Usage: test-client.py -p <tcp | udp> <target host>"
    sys.exit(2)

def parseArguments(argv):
    proto = None
    try:
        opts, args = getopt.getopt(argv, "p:")

        for opt, arg in opts:
            if opt in ("-p"):
                proto = arg
            else:
                usage()

        if len(args) == 1:
            host = args[0]
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
    send(*parseArguments(sys.argv[1:]))