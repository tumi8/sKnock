import time, logging
from unittest import TestCase

from knock_server.knock_server.definitions.Constants import *
from knock_server.knock_server.modules.Listener.ProcessRequestThread import ProcessRequestThread

from stubs import *

Firewall = stub_Firewall
CryptoEngine = stub_CryptoEngine_Server
KnockProcessor = stub_KnockProcessor

# TEST CLASS
class TestProcessRequest(TestCase):

    def test_processAFewRequests(self):
        logging.basicConfig()

        firewallHandler = Firewall()
        cryptoEngine = CryptoEngine('5.5.5.5', '5555:5555:5555:5555::5555')
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





