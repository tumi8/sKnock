import logging
import os
import time

from definitions.Constants import *
from modules.Configuration import config, initialize
from modules.Firewall.Firewall import Firewall


LOG = logging.getLogger(__name__)

def benchmark(ipv4 = True, ipv6 = False, tcp = True, udp = False, csvOutput = '/tmp'):
    initialize()
    config.PORT_OPEN_DURATION_IN_SECONDS = 100
    config.firewallPolicy = 'none'

    firewallHandler = Firewall(config)
    firewallHandler.startup()

    # Begin Benchmark
    # WARNING: total time is only approximation by summing up the single operation times and subtracting the estimated time wasted on the timing of the functions

    # Calibration
    timingCost = 0
    for i in xrange(5):
        prev_time = time.time()
        for i in xrange(10000000):
            currTime = time.time()

        newTimingCost = (currTime - prev_time) * 1000
        timingCost = min(timingCost, newTimingCost) if timingCost != 0 else newTimingCost

    perTimingError = timingCost / 10000000
    LOG.info('Calculated accumulated timing cost: %s ms per 10m Operations', round(timingCost, 4))

    v4_rulesetSize = 0
    v6_rulesetSize = 0


    if ipv4 and tcp:
        baconFile = open(os.path.join(csvOutput, 'ap_firewall_rulesetsize_vs_operationtime_ipv4_tcp_open.csv'), 'w')
        baconFile.write("Number of Rules in Chain, Time for a single IPv4/TCP port-open operation [ms]\n")
        approxTotalTime = 0
        for i in xrange(0, 65536):
            prev_time = time.time()
            firewallHandler.openPortForClient(i, IP_VERSION.V4, PROTOCOL.TCP, '1.1.1.1')
            currTime = time.time()
            computationTime = (currTime-prev_time) * 1000 - perTimingError
            approxTotalTime += computationTime
            LOG.info('Computation Time for Operation: %f', computationTime)
            baconFile.write("%d,%s\n" % (v4_rulesetSize + i, round(computationTime, 2)))
        v4_rulesetSize += 65536
        LOG.info('Approximate total time for opening 65536 IPv4 TCP ports: %s', round(approxTotalTime, 2))
        baconFile.close()


    if ipv4 and udp:
        baconFile = open(os.path.join(csvOutput, 'ap_firewall_rulesetsize_vs_operationtime_ipv4_udp_open.csv'), 'w')
        baconFile.write("Number of Rules in Chain, Time for a single IPv4/UDP port-open operation [ms]\n")
        approxTotalTime = 0
        for i in xrange(0, 65536):
            prev_time = time.time()
            firewallHandler.openPortForClient(i, IP_VERSION.V4, PROTOCOL.UDP, '1.1.1.1')
            currTime = time.time()
            computationTime = (currTime-prev_time) * 1000 - perTimingError
            approxTotalTime += computationTime
            LOG.info('Computation Time for Operation: %f', computationTime)
            baconFile.write("%d,%s\n" % (v4_rulesetSize + i, round(computationTime, 2)))
        v4_rulesetSize += 65536
        LOG.info('Approximate total time for opening 65536 IPv4 UDP ports: %s', round(approxTotalTime, 2))
        baconFile.close()

    if ipv6 and tcp:
        baconFile = open(os.path.join(csvOutput, 'ap_firewall_rulesetsize_vs_operationtime_ipv6_tcp_open.csv'), 'w')
        baconFile.write("Number of Rules in Chain, Time for a single IPv6/TCP port-open operation [ms]\n")
        approxTotalTime = 0
        for i in xrange(0, 65536):
            prev_time = time.time()
            firewallHandler.openPortForClient(i, IP_VERSION.V6, PROTOCOL.TCP, '1111::1')
            currTime = time.time()
            computationTime = (currTime-prev_time) * 1000 - perTimingError
            approxTotalTime += computationTime
            LOG.info('Computation Time for Operation: %f', computationTime)
            baconFile.write("%d,%s\n" % (v6_rulesetSize + i, round(computationTime, 2)))
        v6_rulesetSize += 65536
        LOG.info('Approximate total time for opening 65536 IPv6 TCP ports: %s', round(approxTotalTime, 2))
        baconFile.close()

    if ipv6 and udp:
        baconFile = open(os.path.join(csvOutput, 'ap_firewall_rulesetsize_vs_operationtime_ipv6_udp_open.csv'), 'w')
        baconFile.write("Number of Rules in Chain, Time for a single IPv6/UDP port-open operation [ms]\n")
        approxTotalTime = 0
        for i in xrange(0, 65536):
            prev_time = time.time()
            firewallHandler.openPortForClient(i, IP_VERSION.V6, PROTOCOL.UDP, '1111::1')
            currTime = time.time()
            computationTime = (currTime-prev_time) * 1000 - perTimingError
            approxTotalTime += computationTime
            LOG.info('Computation Time for Operation: %f', computationTime)
            baconFile.write("%d,%s\n" % (v6_rulesetSize + i, round(computationTime, 2)))
        v6_rulesetSize += 65536
        LOG.info('Approximate total time for opening 65536 IPv6 UDP ports: %s', round(approxTotalTime, 2))
        baconFile.close()


    if ipv4 and tcp:
        baconFile = open(os.path.join(csvOutput, 'ap_firewall_rulesetsize_vs_operationtime_ipv4_tcp_close.csv'), 'w')
        baconFile.write("Number of Rules in Chain, Time for a single IPv4/TCP port-close operation [ms]\n")
        approxTotalTime = 0
        for i in xrange(0, 65536):
            prev_time = time.time()
            firewallHandler.closePortForClient(i, IP_VERSION.V4, PROTOCOL.TCP, '1.1.1.1')
            currTime = time.time()
            computationTime = (currTime-prev_time) * 1000 - perTimingError
            approxTotalTime += computationTime
            LOG.info('Computation Time for Operation: %f', computationTime)
            baconFile.write("%d,%s\n" % (v4_rulesetSize - i, round(computationTime, 2)))
        v4_rulesetSize -= 65536
        LOG.info('Approximate total time for closing 65536 IPv4 TCP ports: %s', round(approxTotalTime, 2))
        baconFile.close()

    if ipv4 and udp:
        baconFile = open(os.path.join(csvOutput, 'ap_firewall_rulesetsize_vs_operationtime_ipv4_udp_close.csv'), 'w')
        baconFile.write("Number of Rules in Chain, Time for a single IPv4/UDP port-close operation [ms]\n")
        approxTotalTime = 0
        for i in xrange(0, 65536):
            prev_time = time.time()
            firewallHandler.closePortForClient(i, IP_VERSION.V4, PROTOCOL.UDP, '1.1.1.1')
            currTime = time.time()
            computationTime = (currTime-prev_time) * 1000 - perTimingError
            approxTotalTime += computationTime
            LOG.info('Computation Time for Operation: %f', computationTime)
            baconFile.write("%d,%s\n" % (v4_rulesetSize - i, round(computationTime, 2)))
        v4_rulesetSize -= 65536
        LOG.info('Approximate total time for closing 65536 IPv4 UDP ports: %s', round(approxTotalTime, 2))
        baconFile.close()

    if ipv6 and tcp:
        baconFile = open(os.path.join(csvOutput, 'ap_firewall_rulesetsize_vs_operationtime_ipv6_tcp_close.csv'), 'w')
        baconFile.write("Number of Rules in Chain, Time for a single IPv6/TCP port-close operation [ms]\n")
        approxTotalTime = 0
        for i in xrange(0, 65536):
            prev_time = time.time()
            firewallHandler.closePortForClient(i, IP_VERSION.V6, PROTOCOL.TCP, '1111::1')
            currTime = time.time()
            computationTime = (currTime-prev_time) * 1000 - perTimingError
            approxTotalTime += computationTime
            LOG.info('Computation Time for Operation: %f', computationTime)
            baconFile.write("%d,%s\n" % (v6_rulesetSize - i, round(computationTime, 2)))
        v6_rulesetSize -= 65536
        LOG.info('Approximate total time for closing 65536 IPv6 TCP ports: %s', round(approxTotalTime, 2))
        baconFile.close()

    if ipv6 and udp:
        baconFile = open(os.path.join(csvOutput, 'ap_firewall_rulesetsize_vs_operationtime_ipv6_udp_close.csv'), 'w')
        baconFile.write("Number of Rules in Chain, Time for a single IPv6/UDP port-close operation [ms]\n")
        approxTotalTime = 0
        for i in xrange(0, 65536):
            prev_time = time.time()
            firewallHandler.closePortForClient(i, IP_VERSION.V6, PROTOCOL.UDP, '1111::1')
            currTime = time.time()
            computationTime = (currTime-prev_time) * 1000 - perTimingError
            approxTotalTime += computationTime
            LOG.info('Computation Time for Operation: %f', computationTime)
            baconFile.write("%d,%s\n" % (v6_rulesetSize - i, round(computationTime, 2)))
        v6_rulesetSize -= 65536
        LOG.info('Approximate total time for closing 65536 IPv6 UDP ports: %s', round(approxTotalTime, 2))
        baconFile.close()
        # End Benchmark


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, filename='/tmp/ap_firewall.log')
    benchmark(1,1,1,1)