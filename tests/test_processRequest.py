import time, logging
from unittest import TestCase

from common.definitions.Constants import IP_VERSION
from server.modules.Listener.ProcessRequestThread import ProcessRequestThread

from stubs import *

Firewall = stub_Firewall
CryptoEngine = stub_CryptoEngine_Server
KnockProcessor = stub_KnockProcessor

# TEST CLASS
class TestProcessRequest(TestCase):

    def test_processAFewRequests(self):
        logging.basicConfig()

        firewallHandler = Firewall()
        security = CryptoEngine('5.5.5.5', '5555:5555:5555:5555::5555')
        knockProcessor = KnockProcessor(firewallHandler, security)
        threads = []

        for x in range(1, 10):
            thread = ProcessRequestThread(knockProcessor, IP_VERSION.V4, '5.5.5.5', 'I think I am a request?')
            threads.append(thread)
            thread.start()

        for x in range(1, 10):
            thread = ProcessRequestThread(knockProcessor, IP_VERSION.V6, '5555:5555:5555:5555::5555', 'I think I am a request?')
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(firewallHandler.counter, 2)

        time.sleep(firewallHandler.config.PORT_OPEN_DURATION_IN_SECONDS + 1)
        self.assertEqual(firewallHandler.counter, 0)





