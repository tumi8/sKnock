from unittest import TestCase
import os
from knock_client.modules.CertUtil import CertUtil as CertUtilClient
from knock_server.modules.CertUtil import CertUtil as CertUtilServer
from configurations import config_server_valid

class TestCryptoEngine_VALID(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cryptoEngineClient = CertUtilClient(
            serverCertFile=os.path.join(os.path.dirname(__file__), 'data', 'devserver_valid.cer'),
            pfxFile=os.path.join(os.path.dirname(__file__), 'data', 'devclient_valid.pfx'),
            pfxPasswd='portknocking').initializeCryptoEngine()

        cls.cryptoEngineServer = CertUtilServer(
            config_server_valid).initializeCryptoEngine()

    def test_encryption(self):
        original_message = "Writing tests makes me want to jump out of the window..."
        encryptedMessage, ephPubKey = self.cryptoEngineClient.encryptWithECIES(original_message, self.cryptoEngineClient.serverPublicKey)
        encryptedMessage += ephPubKey

        evaluate_message = self.cryptoEngineServer.decryptWithECIES(encryptedMessage)
        self.assertEqual(original_message, evaluate_message)
