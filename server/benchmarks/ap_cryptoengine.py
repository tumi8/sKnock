import logging
import os
import sys
import timeit

from common.definitions.Constants import *
from modules.Security import Security
from modules.Configuration import config, initialize

LOG = logging.getLogger(__name__)

def benchmark():
    LOG.info('Initializing...')
    initialize()
    with open(os.path.join(os.path.dirname(__file__), 'data', 'v4packet.enc'), 'rb') as baconFile:
        v4packet = baconFile.read()
        LOG.debug('Loaded IPv4 dummy request!')
    with open(os.path.join(os.path.dirname(__file__), 'data', 'v6packet.enc'), 'rb') as baconFile:
        v6packet = baconFile.read()
        LOG.debug('Loaded IPv6 dummy request!')

    security = Security(config)
    LOG.debug('Initialized Crypto Engine!')

    def eval_func():
        security.decryptAndVerifyRequest(v4packet, IP_VERSION.V4)
        security.decryptAndVerifyRequest(v6packet, IP_VERSION.V6)

    number_packets = 300000
    LOG.info('Computing CryptoEngine performance based on data set of %s packets', number_packets)

    time_result = timeit.timeit(eval_func, number=number_packets/2)

    pps = number_packets / time_result

    LOG.info('Benchmark finished!')
    LOG.info('Result: %fs overall compuation time, %fms time per packet, approx. %d pps (packets per second)', time_result, time_result/number_packets*1000, pps)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, stream=sys.stdout)
    benchmark()