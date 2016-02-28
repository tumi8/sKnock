import logging, os, timeit, time, sys
from ..definitions.Constants import *
from ..modules.Listener import ProcessRequestThread
from ..modules.Listener.NewPacketThread import NewPacketThread


LOG = logging.getLogger(__name__)


class ProcessRequestThread_stub:
    def __init__(self, arg1, arg2, arg3, arg4):
        pass
    def start(self):
        pass

ProcessRequestThread.ProcessRequestThread = ProcessRequestThread_stub

def benchmark():
    LOG.info('Initializing...')
    with open(os.path.join(os.path.dirname(__file__), 'data', 'v4packet.eth'), 'rb') as baconFile:
        v4packet = baconFile.read()
        LOG.debug('Loaded IPv4 dummy packet!')
    with open(os.path.join(os.path.dirname(__file__), 'data', 'v6packet.eth'), 'rb') as baconFile:
        v6packet = baconFile.read()
        LOG.debug('Loaded IPv6 dummy packet!')

    threadList = []

    def eval_func():
        t1 = NewPacketThread(None, v4packet)
        t2 = NewPacketThread(None, v6packet)
        threadList.append(t1)
        threadList.append(t2)
        t1.start()
        t2.start()


    number_packets = 10000000
    LOG.info('Computing PacketProcessor performance based on data set of %s packets', number_packets)

    compute_time_result = timeit.timeit(eval_func, number=number_packets/2)

    # We still need to wait for all threads to finish and calculate the time
    prev_time = time.time()
    for t in threadList:
        t.join()
    thread_wait_time = time.time() - prev_time

    time_result = compute_time_result + thread_wait_time

    #print "Compute Time: %f" % compute_time_result
    #print "Thread wait time: %f" % thread_wait_time


    pps = number_packets / time_result

    LOG.info('Benchmark finished!')
    LOG.info('Result: %fs overall compuation time, %fms time per packet, approx. %d pps (packets per second)', time_result, time_result/number_packets*1000, pps)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, stream=sys.stdout)
    benchmark()