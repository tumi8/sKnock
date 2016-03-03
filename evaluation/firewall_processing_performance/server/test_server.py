import logging, time, struct, sys, getopt, signal, socket, errno, threading

LOG = logging.getLogger(__name__)
requestLOG = logging.getLogger('requests')
[requestLOG.removeHandler(handler) for handler in requestLOG.handlers[:]]
requestLOG.addHandler(logging.FileHandler('requests.log'))

shutdown = False

class ConnectionThread(threading.Thread):
    def __init__(self, conn, delay_compensation, callback, addr = None):
        self.conn = conn
        self.client_addr = addr
        self.delay_compensation = delay_compensation
        self.callback = callback
        self.shutdown = False
        threading.Thread.__init__(self)

    def run(self):
        while not shutdown:
            try:
                packet, client_addr = self.conn.recvfrom(8)
            except socket.timeout:
                continue
            except socket.error, e:
                    if e.errno != errno.EINTR:
                        raise e
                    else:
                        return

            time_now = time.time()

            if len(packet) == 0:
                break;

            if len(packet) != 8:
                continue

            if client_addr is None:
                client_addr = self.client_addr

            packetTimestamp  = struct.unpack('!d', packet)[0]
            #print 'packetTime: %s' % packetTimestamp
            #print 'serverTime: %s' % time_now
            time_server = time_now - self.delay_compensation
            delay = time_server - packetTimestamp
            requestLOG.debug("Delay for client %s was %sms", client_addr, delay * 1000)

            if self.callback is not None:
                self.callback(delay * 1000)

            self.conn.sendto(struct.pack('!d', time_server), client_addr)
        self.conn.close()

    def stop(self):
        shutdown = True

def startTCPServer(delay_compensation, callback):
    LOG.info('Starting TCP server...')
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    server_socket.settimeout(5)
    server_socket.bind(('0.0.0.0', 60000))
    server_socket.listen(1)

    threadList = []
    global shutdown
    while not shutdown:
        try:
            conn, addr = server_socket.accept()
        except socket.timeout:
            continue
        except socket.error, e:
                    if e.errno != errno.EINTR:
                        raise e
                    else:
                        return
        LOG.debug('Connection from %s', addr)

        t = ConnectionThread(conn, delay_compensation, callback, addr)
        threadList.append(t)
        t.start()

    for t in threadList:
        t.stop()
        t.join(7)

def startUDPServer(delay_compensation, callback):
    LOG.info('Starting UDP server...')
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server_socket.settimeout(5)
    server_socket.bind(('0.0.0.0', 60000))
    t = ConnectionThread(server_socket, delay_compensation, callback)
    t.start()

    global shutdown
    while not shutdown:
        time.sleep(5)

    t.stop()
    t.join(7)



def start(udp, delay_compensation = 0, callback = None):
    global shutdown

    if udp:
        startUDPServer(delay_compensation, callback)
    else:
        startTCPServer(delay_compensation, callback)

def stop(sig, frame):
    LOG.debug('Signal %s received', sig)
    LOG.info('Stopping server...')
    global shutdown
    shutdown = True






def usage():
    print "Usage: test_server.py [-d <delay compensation in ms] <tcp | udp>"
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
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG, stream=sys.stdout)
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    start(*parseArguments(sys.argv[1:]))