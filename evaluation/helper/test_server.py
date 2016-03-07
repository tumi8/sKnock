import logging, time, struct, sys, getopt, signal, socket, errno, threading

LOG = logging.getLogger(__name__)
requestLOG = logging.getLogger('requests')
[requestLOG.removeHandler(handler) for handler in requestLOG.handlers[:]]
requestLOG.addHandler(logging.FileHandler('requests.log'))

thread = None
shutdown = False

class _ServerThread(threading.Thread):
    def __init__(self,
                 delay_compensation = 0,
                 port = 60000,
                 callback = None,
                 ego_mode = False):
        threading.Thread.__init__(self)
        self.delay_compensation = delay_compensation
        self.port = port
        self.callback = callback
        self.ego_mode = ego_mode
        self.threadList = []
        self.shutdown = threading.Event()

    def run(self):
        LOG.info('Starting server')
        LOG.debug('Delay compensation: %s', self.delay_compensation)
        LOG.debug('Callback: %s', self.callback)
        self.serve()

    def stop(self):
        LOG.info('Stopping server')
        self.shutdown.set()

class UDPServerThread(_ServerThread):
    def __init__(self, *args):
        _ServerThread.__init__(self, *args)

    def serve(self):
        LOG.info('Starting UDP server on port %s', self.port)
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        server_socket.settimeout(5)
        server_socket.bind(('0.0.0.0', self.port))
        t = ConnectionThread(server_socket, self.delay_compensation, self.callback, self.ego_mode)
        t.start()
        self.shutdown.wait()
        t.stop()
        t.join()

class TCPServerThread(_ServerThread):
    def __init__(self, *args):
        _ServerThread.__init__(self, *args)

    def serve(self):
        LOG.info('Starting TCP server on port %s', self.port)
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        server_socket.settimeout(5)
        server_socket.bind(('0.0.0.0', self.port))
        server_socket.listen(1)
        threadList = []
        while not self.shutdown.is_set():
            try:
                conn, addr = server_socket.accept()
            except socket.timeout:
                continue
            except socket.error, e:
                if e.errno != errno.EINTR:
                    raise e
                else:
                    continue
            LOG.debug('Connection from %s', addr)
            t = ConnectionThread(conn,
                                 self.delay_compensation,
                                 self.callback,
                                 self.ego_mode,
                                 addr=addr)
            threadList.append(t)
            t.start()
        for t in threadList:
            t.stop()
            t.join()


class ConnectionThread(threading.Thread):
    def __init__(self, conn, delay_compensation, callback, ego_mode, addr = None):
        self.conn = conn
        self.client_addr = addr
        self.delay_compensation = delay_compensation
        self.callback = callback
        self.ego_mode = ego_mode
        self.shutdown = threading.Event()
        threading.Thread.__init__(self)

    def run(self):
        while not self.shutdown.is_set():
            try:
                packet, client_addr = self.conn.recvfrom(8)
            except socket.timeout:
                continue
            except socket.error, e:
                if e.errno != errno.EINTR:
                    raise e
                else:
                    continue

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

            if not self.ego_mode:
                self.conn.sendto(struct.pack('!d', time_server), client_addr)
        self.conn.close()

    def stop(self):
        self.shutdown.set()

def start_threaded(udp, delay_compensation = 0, port = 60000, callback = None, ego_mode = False):
    global thread
    factory = UDPServerThread if udp else TCPServerThread
    thread = factory(delay_compensation, port, callback, ego_mode)
    thread.start()
    return thread

def stop_threaded():
    global thread
    thread.stop()

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
