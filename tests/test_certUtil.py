from unittest import TestCase
import os, struct, logging
from client.modules.Security import Security as SecurityClient

from configurations import config_server_valid

from stubs import *

SecurityServer = stub_Security_Server

class TestCertUtil_VALID(TestCase):
    @classmethod
    def setUpClass(cls):

        logging.basicConfig()

        cls.securityClient = SecurityClient(serverCertFile=os.path.join(os.path.dirname(__file__), 'data', 'devserver_valid.cer'),
                                            pfxFile=os.path.join(os.path.dirname(__file__), 'data', 'devclient_valid.pfx'),
                                            pfxPasswd='portknocking')

        cls.securityServer = SecurityServer(config_server_valid)

    def test_signature(self):
        message = "Baby don't hurt me, no more"
        try:
            evaluate_signedMessageWithCert = self.securityClient.certUtil.signIncludingCertificate(message)

            signatureLength = struct.unpack('!B',evaluate_signedMessageWithCert[-73:-72])[0]
            signedRequest = evaluate_signedMessageWithCert[0:-73]
            signature = evaluate_signedMessageWithCert[-signatureLength:]
            certificate = evaluate_signedMessageWithCert[len(message):-73]

            self.assertTrue(self.securityServer.certUtil.verifyCertificateAndSignature(certificate, signature, signedRequest))
        except:
            self.fail()