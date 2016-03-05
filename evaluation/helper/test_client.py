import logging, time, struct, sys, getopt, socket

LOG = logging.getLogger(__name__)

KNOCK_WAIT_TIME = 0


def send(target, udp, port = 60000, knockClient = None, callback = None):

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
        #LOG.debug('Port-knocking the server before starting...')
        knockClient.knockOnPort(target, port, protocol=proto_str, forceIPv4=True)
        time.sleep(KNOCK_WAIT_TIME)

    #print 'sendTime: %s' % time_send
    #LOG.debug('Sending packet to test server...')
    data = struct.pack('!d', time_send)
    if udp:
        target_socket.sendto(data, (target, port))
    else:
        target_socket.connect((target, port))
        target_socket.send(data)

    response = target_socket.recv(8)

    if len(response) != 8:
        LOG.error('BOOM, something went wrong...')
        return

    time_server = struct.unpack('!d', response)[0]
    LOG.debug('Received packet from test server...')
    time_recv = time.time()

    if callback is not None:
        callback((time_server - time_send) * 1000)

    #print 'packetTime: %s' % time_server
    #print 'recvTime: %s' % time_recv

    LOG.debug('Processing Delay      (Client -> Server [can start working on Data]:   %sms', (time_server - time_send) * 1000)
    LOG.debug('Round-Trip-Time [RTT] (Client -> Server -> Client):                    %sms', (time_recv - time_send) * 1000)

    target_socket.close()




def usage():
    print "Usage: test_client.py <tcp | udp> <target host>"
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
    send(*parseArguments(sys.argv[1:]))