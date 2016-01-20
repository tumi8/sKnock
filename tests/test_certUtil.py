from unittest import TestCase
import os, base64, struct
from knock_client.modules.CertUtil import CertUtil as CertUtilClient
from knock_server.modules.CertUtil import CertUtil as CertUtilServer


class TestCertUtil_VALID(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certUtilClient = CertUtilClient(serverCertFile=os.path.join(os.path.dirname(__file__), 'data', 'devserver_valid.cer'),
                                pfxFile=os.path.join(os.path.dirname(__file__), 'data', 'devclient_valid.pfx'),
                                pfxPasswd='portknocking')
        cls.certUtilClient.initializeCryptoEngine()

        cls.certUtilServer = CertUtilServer(crlFile=os.path.join(os.path.dirname(__file__), 'data', 'devca_valid.crl'),
                                pfxFile=os.path.join(os.path.dirname(__file__), 'data', 'devserver_valid.pfx'),
                                pfxPasswd='portknocking')
        cls.certUtilServer.initializeCryptoEngine()

    def test_signature(self):
        message = "Baby don't hurt me, no more"
        try:
            evaluate_signedMessageWithCert = self.certUtilClient.signIncludingCertificate(message)

            signatureLength = struct.unpack('!B',evaluate_signedMessageWithCert[-73:-72])[0]
            signedRequest = evaluate_signedMessageWithCert[0:-73]
            signature = evaluate_signedMessageWithCert[-signatureLength:]
            certificate = evaluate_signedMessageWithCert[len(message):-73]

            self.assertTrue(self.certUtilServer.verifyCertificateAndSignature(certificate, signature, signedRequest))
        except:
            self.fail()