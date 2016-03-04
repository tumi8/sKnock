from unittest import TestCase
import os, logging
from client.modules.Security import Security as SecurityClient
from server.modules.Security.Security import Security as SecurityServer
from configurations import config_server_valid

class TestCryptoEngine_VALID(TestCase):

    @classmethod
    def setUpClass(cls):
        logging.basicConfig()

        cls.securityClient = SecurityClient(
            serverCertFile=os.path.join(os.path.dirname(__file__), 'data', 'devserver_valid.cer'),
            pfxFile=os.path.join(os.path.dirname(__file__), 'data', 'devclient_valid.pfx'),
            pfxPasswd='portknocking')

        cls.cryptoEngineServer = SecurityServer(
            config_server_valid).cryptoEngine

    def test_encryption(self):
        original_message = "Writing tests makes me want to jump out of the window..."
        encryptedMessage, ephPubKey = self.securityClient.cryptoEngine.encryptWithECIES(original_message, self.securityClient.serverPublicKey)
        encryptedMessage += ephPubKey

        evaluate_message = self.cryptoEngineServer.decryptWithECIES(encryptedMessage)
        self.assertEqual(original_message, evaluate_message)
