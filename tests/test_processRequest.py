import time
from unittest import TestCase

from knock_server.definitions.Constants import *
from knock_server.modules.Listener.ProcessRequestThread import ProcessRequestThread


# Mocks / Stubs

class stub_Firewall:
    def __init__(self):
        self.counter = 0
    def openPortForClient(self, port, ipVersion, protocol, addr):
        self.counter+=1
    def closePortForClient(self, port, ipVersion, protocol, addr):
        self.counter-=1

class stub_CryptoEngine:
    def __init__(self):
        pass
    def decryptAndVerifyRequest(self, encryptedMessage):
        return True, PROTOCOL.TCP, 2000

Firewall = stub_Firewall
CryptoEngine = stub_CryptoEngine

# TEST CLASS
class TestProcessRequest(TestCase):

    def test_processAFewRequests(self):
        firewallHandler = Firewall()
        cryptoEngine = CryptoEngine()
        runningPortOpenTasks = list()

        for x in range(1, 10):
            ProcessRequestThread(cryptoEngine, firewallHandler, runningPortOpenTasks, IP_VERSION.V4, '5.5.5.5', 'I think I am a request?').start()

        for x in range(1, 10):
            ProcessRequestThread(cryptoEngine, firewallHandler, runningPortOpenTasks, IP_VERSION.V6, '5.5.5.5', 'I think I am a request?').start()

        if firewallHandler.counter != 2:
            self.fail()

        time.sleep(PORT_OPEN_DURATION_IN_SECONDS + 1)
        self.assertEqual(firewallHandler.counter, 0)





