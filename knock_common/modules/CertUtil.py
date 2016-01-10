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
import logging, os, OpenSSL
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
            pfx = OpenSSL.crypto.load_pkcs12(file(os.path.join(self.config.certdir, 'devclient1.pfx'), 'rb').read(), self.config.pfxPasswd)

            self.loadCAFromPFX(pfx)
            self.clientCert = pfx.get_certificate()
            self.clientKey = pfx.get_privatekey()

            serverCert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, file(os.path.join(self.config.certdir, 'devserver.cer'), 'rb').read())
            serverPubKey = serverCert.get_pubkey()

            return CryptoEngine(self.clientKey, serverPubKey)


    def initializeCryptoEngineForServer(self):
        if(self.platform == PlatformUtils.LINUX):
            pfx = OpenSSL.crypto.load_pkcs12(file(os.path.join(self.config.certdir, 'devserver.pfx'), 'rb').read(), self.config.pfxPasswd)

            self.loadCAFromPFX(pfx)
            serverKey = pfx.get_privatekey()

            return CryptoEngine(serverKey, None)


    def sign(self, message):
        messageWithCert = message + OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_ASN1, self.clientCert)
        signedMessageWithCert = messageWithCert + OpenSSL.crypto.sign(self.clientKey, messageWithCert, self.hashAlgorithm)
        return signedMessageWithCert




    def verifyCertificate(self, cert):
        if(self.platform == PlatformUtils.LINUX):
            CAContext = OpenSSL.crypto.X509StoreContext(self.CA, cert)
            if(CAContext.verify_certificate()):
                # TODO revocation check
                return True
            else:
                return False





    def verifySignature(self, cert, payloadSignature, payload):
        if(self.platform == PlatformUtils.LINUX):
            OpenSSL.crypto.verify(cert, payloadSignature, payload, self.hashAlgorithm)



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
        CAstore = pfx.get_ca_certificates()
        if len(CAstore) != 1:
            logger.error("Incompatible Root CA structure!")
            raise IncompatibleRootCAException

        self.CA = CAstore[0]

        if (self.CA.get_signature_algorithm() != 'ecdsa-with-SHA256'):
            logger.error("Incompatible Signature Algorithm!")
            raise IncompatibleRootCAException

        self.hashAlgorithm = 'sha256'