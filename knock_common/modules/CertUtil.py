# Copyright (c) 2015 Daniel Sel
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA
#
import logging, os, struct
from knock_common.lib.OpenSSL import crypto
from knock_common.definitions.Exceptions import *
from PlatformUtils import PlatformUtils
from CryptoEngine import CryptoEngine


logger = logging.getLogger(__name__)

class CertUtil:

    PROBABLE_INDEX_FOR_SUBJECTALTNAME = 4



    def __init__(self, config):
        self.config = config
        self.platform = PlatformUtils.detectPlatform()

    def initializeCryptoEngineForClient(self):
        if(self.platform == PlatformUtils.LINUX):
            logger.debug("Loading certificates...")
            try:
                pfx = crypto.load_pkcs12(file(os.path.join(self.config.certdir, 'devclient1.pfx'), 'rb').read(), self.config.pfxPasswd)

                self.loadCAFromPFX(pfx)
                self.clientCert = pfx.get_certificate()
                self.clientKey = pfx.get_privatekey()

                serverCert = crypto.load_certificate(crypto.FILETYPE_ASN1, file(os.path.join(self.config.certdir, 'devserver.cer'), 'rb').read())
                serverPubKey = serverCert.get_pubkey()

                serializedClientPrivKey = crypto.dump_privatekey(crypto.FILETYPE_PEM, self.clientKey)
                serializedServerPubKey = crypto.dump_publickey(crypto.FILETYPE_PEM, serverPubKey)

                return CryptoEngine(serializedClientPrivKey, serializedServerPubKey, certUtil=self)
            except:
                logger.error("Failed to load certificates!")


    def initializeCryptoEngineForServer(self):
        if(self.platform == PlatformUtils.LINUX):
            logger.debug("Loading certificates...")
            try:
                pfx = crypto.load_pkcs12(file(os.path.join(self.config.certdir, 'devserver.pfx'), 'rb').read(), self.config.pfxPasswd)

                self.loadCAFromPFX(pfx)
                serverKey = pfx.get_privatekey()

                serializedServerPrivKey = crypto.dump_privatekey(crypto.FILETYPE_PEM, serverKey)

                return CryptoEngine(serializedServerPrivKey, None, certUtil=self)
            except:
                logger.error("Failed to load certificates!")


    def signIncludingCertificate(self, message):
        messageWithCert = message + crypto.dump_certificate(crypto.FILETYPE_ASN1, self.clientCert)
        signature = crypto.sign(self.clientKey, messageWithCert, self.hashAlgorithm)

        padding = ''.join(['x' for diff in xrange(72 - len(signature))])

        signedMessageWithCert = messageWithCert + struct.pack('!B' + padding, len(signature)) + signature

        return signedMessageWithCert


    def verifyCertificateAndSignature(self, rawCert, payloadSignature, payload):
        try:
            cert = crypto.load_certificate(crypto.FILETYPE_ASN1, rawCert)
        except:
            logger.error("Invalid Certificate data!")
            return False

        return self.verifyCertificate(cert) and self.verifySignature(cert, payloadSignature, payload)


    def verifyCertificate(self, cert):
        if(self.platform == PlatformUtils.LINUX):
            CAContext = crypto.X509StoreContext(self.CA, cert)
            try:
                CAContext.verify_certificate()
                logger.debug("Certificate OK!")
                #TODO: Revocation check
                return True
            except:
                logger.debug("Certificate check failed!")
                return False


    def verifySignature(self, cert, signature, message):
        if(self.platform == PlatformUtils.LINUX):
            try:
                crypto.verify(cert, signature, message, self.hashAlgorithm)
                logger.debug("Signature OK!")
                return True
            except:
                logger.debug("Invalid Signature!")
                return False



    def extractEncryptedAuthorizationStringFromCertificate(self, cert):

        try:
            extension = cert.get_extension(CertUtil.PROBABLE_INDEX_FOR_SUBJECTALTNAME)
            if extension.get_short_name() != 'subjectAltName':
                raise Exception
        except:
            for i in range (0, cert.get_extension_count()):
                extension = cert.get_extension(i)
                if extension.get_short_name() == 'subjectAltName':
                    break

        return None if extension == None else extension.get_data()


    def loadCAFromPFX(self, pfx):
        CAcerts = pfx.get_ca_certificates()
        if len(CAcerts) != 1:
            logger.error("Incompatible Root CA structure!")
            raise IncompatibleRootCAException

        if (CAcerts[0].get_signature_algorithm() != 'ecdsa-with-SHA256'):
            logger.error("Incompatible Signature Algorithm!")
            raise IncompatibleRootCAException

        self.hashAlgorithm = 'sha256'

        self.CA = crypto.X509Store()
        self.CA.add_cert(CAcerts[0])


    def convertDERtoPEM(self, key):
        return crypto.dump_publickey(crypto.FILETYPE_PEM, crypto.load_publickey(crypto.FILETYPE_ASN1, key))


    def convertPEMtoDER(self, key):
        return crypto.dump_publickey(crypto.FILETYPE_ASN1, crypto.load_publickey(crypto.FILETYPE_PEM, key))
