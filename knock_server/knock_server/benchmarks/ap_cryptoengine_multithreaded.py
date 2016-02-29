import logging, os, timeit, time, sys
from ..definitions.Constants import *
from ..modules.Configuration import config, initialize

from ..modules.CertUtil import CertUtil
from ..modules.Firewall import PortOpenThread
from ..modules.Listener.ProcessRequestThread import ProcessRequestThread

LOG = logging.getLogger(__name__)

class KnockProcessor: pass
class PortOpenThread_stub:
    def __init__(self, arg1, arg2, arg3, arg4, arg5, arg6):
        pass
    def start(self):
        pass

PortOpenThread.PortOpenThread = PortOpenThread_stub

def benchmark():
    LOG.warn('Initializing...')
    initialize()
    with open(os.path.join(os.path.dirname(__file__), 'data', 'v4packet.enc'), 'rb') as baconFile:
        v4packet = baconFile.read()
        LOG.debug('Loaded IPv4 dummy request!')
    with open(os.path.join(os.path.dirname(__file__), 'data', 'v6packet.enc'), 'rb') as baconFile:
        v6packet = baconFile.read()
        LOG.debug('Loaded IPv6 dummy request!')

    knockProcessor = KnockProcessor()
    knockProcessor.firewallHandler = None
    knockProcessor.runningPortOpenTasks = []
    knockProcessor.cryptoEngine = CertUtil(config).initializeCryptoEngine()
    LOG.debug('Initialized Crypto Engine!')

    threadList = []

    def eval_func():
        t1 = ProcessRequestThread(knockProcessor, IP_VERSION.V4, '192.168.204.101', v4packet)
        t2 = ProcessRequestThread(knockProcessor, IP_VERSION.V6, 'fd4a:d78b:ec7a:425a::101', v6packet)
        threadList.append(t1)
        threadList.append(t2)
        t1.start()
        t2.start()

    number_packets = 300000
    LOG.warn('Computing CryptoEngine performance based on data set of %s packets', number_packets)

    compute_time_result = timeit.timeit(eval_func, number=number_packets/2)

    # We still need to wait for all threads to finish and calculate the time
    prev_time = time.time()
    for t in threadList:
        t.join()
    thread_wait_time = time.time() - prev_time

    time_result = compute_time_result + thread_wait_time

    LOG.debug("Compute Time: %f", compute_time_result)
    LOG.debug("Thread wait time: %f", thread_wait_time)

    pps = number_packets / time_result

    LOG.warn('Benchmark finished!')
    LOG.warn('Result: %fs overall compuation time, %fms time per packet, approx. %d pps (packets per second)', time_result, time_result/number_packets*1000, pps)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.WARNING, stream=sys.stdout)
    benchmark()