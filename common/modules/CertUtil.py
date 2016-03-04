import logging, sys, struct, datetime
from common.lib.OpenSSL import crypto
from common.decorators.synchronized import synchronized
from common.definitions.Exceptions import *
from Platform import PlatformUtils


LOG = logging.getLogger(__name__)

class CertUtil:
    def __init__(self, pfxFile, pfxPasswd):
        self.platform = PlatformUtils.detectPlatform()
        self.revokedCertificateSerials = None

        if(self.platform == PlatformUtils.LINUX):
            LOG.debug("Loading certificates...")
            try:
                LOG.debug ("Loading certficate:" + pfxFile);
                pfx = crypto.load_pkcs12(file(pfxFile, 'rb').read(), pfxPasswd)

                self.loadCAFromPFX(pfx)
                self.certificate = pfx.get_certificate()
                self.privKey = pfx.get_privatekey()

            except:
                LOG.error("Failed to load certificates!")
                sys.exit("Failed to load certificates!")

    def getPrivKeyPEM(self):
        return crypto.dump_privatekey(crypto.FILETYPE_PEM, self.privKey)


    def signIncludingCertificate(self, message):
        messageWithCert = message + crypto.dump_certificate(crypto.FILETYPE_ASN1, self.certificate)
        signature = crypto.sign(self.privKey, messageWithCert, self.hashAlgorithm)

        padding = ''.join(['x' for diff in xrange(72 - len(signature))])

        signedMessageWithCert = messageWithCert + struct.pack('!B' + padding, len(signature)) + signature

        return signedMessageWithCert


    def verifyCertificateAndSignature(self, rawCert, payloadSignature, payload):
        try:
            cert = crypto.load_certificate(crypto.FILETYPE_ASN1, rawCert)
        except:
            LOG.error("Invalid Certificate data!")
            return False

        return self.verifyCertificate(cert) and self.verifySignature(cert, payloadSignature, payload)


    def verifyCertificate(self, cert):
        if(self.platform == PlatformUtils.LINUX):
            CAContext = crypto.X509StoreContext(self.CA, cert)
            try:
                CAContext.verify_certificate()
                LOG.debug("Certificate OK!")
                if not (self.revokedCertificateSerials is None or format(cert.get_serial_number(), 'x').upper() in self.revokedCertificateSerials):
                    LOG.debug("Certificate Revocation Status OK")
                    return True
                else:
                    LOG.warning("Certificate with Serial Number: %s is revoked!", cert.get_serial_number())
                    return False

            except:
                LOG.debug("Certificate check failed!")
                return False


    def verifySignature(self, cert, signature, message):
        if(self.platform == PlatformUtils.LINUX):
            try:
                crypto.verify(cert, signature, message, self.hashAlgorithm)
                LOG.debug("Signature OK!")
                return True
            except:
                LOG.debug("Invalid Signature!")
                return False


    def loadCAFromPFX(self, pfx):
        CAcerts = pfx.get_ca_certificates()
        if len(CAcerts) != 1:
            LOG.error("Incompatible Root CA structure!")
            raise IncompatibleRootCAException

        if (CAcerts[0].get_signature_algorithm() != 'ecdsa-with-SHA256'):
            LOG.error("Incompatible Signature Algorithm!")
            raise IncompatibleRootCAException

        self.hashAlgorithm = 'sha256'

        self.CA = crypto.X509Store()
        self.CA.add_cert(CAcerts[0])


    @synchronized
    def importCrl(self, crlFile):
        try:
            LOG.debug("Importing CRL from file...")
            crl = crypto.load_crl(crypto.FILETYPE_ASN1, file(crlFile, 'rb').read())

            # TODO: verify CRL signature

            if crl.get_revoked() is not None:
                self.revokedCertificateSerials = [x.get_serial() for x in crl.get_revoked()]
            else:
                self.revokedCertificateSerials = []
            self.lastCRLUpdate = datetime.datetime.utcnow()
            LOG.debug("CRL update complete!")
        except:
            LOG.error("Failed to load CRL!")


    @staticmethod
    def loadPubKeyPEMFromCert(certFile):
         cert = crypto.load_certificate(crypto.FILETYPE_ASN1, file(certFile, 'rb').read())
         pubKey = cert.get_pubkey()

         return crypto.dump_publickey(crypto.FILETYPE_PEM, pubKey)