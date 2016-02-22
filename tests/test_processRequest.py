import time
from unittest import TestCase

from knock_server.definitions.Constants import *
from knock_server.modules.Listener.ProcessRequestThread import ProcessRequestThread

from configurations import config_server_valid


# Mocks / Stubs

class stub_Firewall:

    def __init__(self):
        self.config = config_server_valid
        self.config.PORT_OPEN_DURATION_IN_SECONDS = 15
        self.counter = 0
    def openPortForClient(self, port, ipVersion, protocol, addr):
        self.counter+=1
    def closePortForClient(self, port, ipVersion, protocol, addr):
        self.counter-=1

class stub_CryptoEngine:
    def __init__(self):
        pass
    def decryptAndVerifyRequest(self, encryptedMessage, ipVersion):
        if ipVersion == IP_VERSION.V4:
            return True, PROTOCOL.TCP, 2000, '5.5.5.5'
        elif ipVersion == IP_VERSION.V6:
            return True, PROTOCOL.TCP, 2000, '5555:5555:5555:5555::5555'
        else:
            return None

class stub_KnockProcessor:
    def __init__(self, firewallHandler, cryptoEngine):
        self.config = config_server_valid
        self.runningPortOpenTasks = list()
        self.firewallHandler = firewallHandler
        self.cryptoEngine = cryptoEngine

Firewall = stub_Firewall
CryptoEngine = stub_CryptoEngine
KnockProcessor = stub_KnockProcessor

# TEST CLASS
class TestProcessRequest(TestCase):

    def test_processAFewRequests(self):
        firewallHandler = Firewall()
        cryptoEngine = CryptoEngine()
        knockProcessor = KnockProcessor(firewallHandler, cryptoEngine)
        runningPortOpenTasks = list()

        for x in range(1, 10):
            ProcessRequestThread(knockProcessor, IP_VERSION.V4, '5.5.5.5', 'I think I am a request?').start()

        for x in range(1, 10):
            ProcessRequestThread(knockProcessor, IP_VERSION.V6, '5555:5555:5555:5555::5555', 'I think I am a request?').start()

        if firewallHandler.counter != 2:
            self.fail()

        time.sleep(firewallHandler.config.PORT_OPEN_DURATION_IN_SECONDS + 1)
        self.assertEqual(firewallHandler.counter, 0)





