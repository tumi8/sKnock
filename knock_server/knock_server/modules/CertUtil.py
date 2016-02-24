# Copyright (C) 2015-2016 Daniel Sel
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
import logging
import struct
import sys
import os
import urllib2
import datetime
import time
import socket
import calendar

from CryptoEngine import CryptoEngine
from ..definitions.Exceptions import *
from ..decorators.synchronized import synchronized
from ..lib.OpenSSL import crypto

from Platform import PlatformUtils

CRL_UPDATE_INTERVAL = datetime.timedelta(minutes=30)

LOG = logging.getLogger(__name__)

class CertUtil:

    def __init__(self, config):
        self.config = config
        self.crlFile = config.crlFile
        self.pfxFile = config.serverPFXFile
        self.pfxPasswd = config.PFXPasswd
        self.platform = PlatformUtils.detectPlatform()

        self.lastCRLUpdate = None

    def initializeCryptoEngine(self):
        if(self.platform == PlatformUtils.LINUX):
            LOG.debug("Loading certificates...")
            try:
                pfx = crypto.load_pkcs12(file(self.pfxFile, 'rb').read(), self.pfxPasswd)

                self.loadCAFromPFX(pfx)
                self.updateCrl()
                self.importCrl()

                serverKey = pfx.get_privatekey()
                serializedServerPrivKey = crypto.dump_privatekey(crypto.FILETYPE_PEM, serverKey)

                return CryptoEngine(self.config, serializedServerPrivKey, certUtil=self)
            except:
                LOG.error("Failed to load certificates!")
                sys.exit("Failed to load certificates!")


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
            LOG.error("Invalid Certificate data!")
            return False

        return self.verifyCertificate(cert) and self.verifySignature(cert, payloadSignature, payload)


    def verifyCertificate(self, cert):
        if(self.platform == PlatformUtils.LINUX):
            CAContext = crypto.X509StoreContext(self.CA, cert)
            try:
                CAContext.verify_certificate()
                LOG.debug("Certificate OK!")
                self.updateCrl()
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
    def updateCrl(self):
        if self.lastCRLUpdate is not None and time.mktime((datetime.datetime.now() - CRL_UPDATE_INTERVAL).timetuple()) < self.lastCRLUpdate:
            return

        LOG.debug("Checking for new CRL on CA Server...")
        remoteCRL = None
        try:
            # TODO: get this from Certificate + CRL-specific cache
            remoteCRL = urllib2.urlopen(self.config.crlUrl, timeout=2)
        except (socket.timeout, urllib2.URLError, urllib2.HTTPError):
            LOG.warning("CA Server seems to be offline")

        if remoteCRL is not None:
            remoteCRLTimestamp = remoteCRL.info().getdate('last-modified')
            if remoteCRLTimestamp is None:
                remoteCRLTimestamp = remoteCRL.info().getdate('date')

            if remoteCRLTimestamp is None:
                LOG.error("Cannot obtain metadata of remote CRL file")
            else:
                remoteCRLTimestamp = calendar.timegm(remoteCRLTimestamp)

                if os.path.isfile(self.crlFile) and not os.path.getmtime(self.crlFile) < remoteCRLTimestamp:
                    # Our File is up to date -> no downloading
                    LOG.debug("CRL is up to date.")
                else:
                    if not os.path.isfile(self.crlFile):
                        # We don't have a CRL at all
                        LOG.debug("No CRL found in cache. Downloading...")
                    else:
                        # Our CRL is not up to date
                        LOG.debug("Found new CRL. Downloading...")

                    try:
                        with open(self.crlFile, 'w') as crlFileHandle:
                            crlFileHandle.write(remoteCRL.read())
                            LOG.debug("Successfully downloaded new CRL from Server")
                    except:
                        LOG.error("Error downloading CRL file!")


    @synchronized
    def importCrl(self):
        try:
            LOG.debug("Importing CRL from file...")
            crl = crypto.load_crl(crypto.FILETYPE_ASN1, file(self.crlFile, 'rb').read())

            # TODO: verify CRL signature

            if crl.get_revoked() is not None:
                self.revokedCertificateSerials = [x.get_serial() for x in crl.get_revoked()]
            else:
                self.revokedCertificateSerials = []
            self.lastCRLUpdate = time.mktime(datetime.datetime.now().timetuple())
            LOG.debug("CRL update complete!")
        except:
            LOG.error("Failed to load CRL!")






    def convertDERtoPEM(self, key):
        return crypto.dump_publickey(crypto.FILETYPE_PEM, crypto.load_publickey(crypto.FILETYPE_ASN1, key))


    def convertPEMtoDER(self, key):
        return crypto.dump_publickey(crypto.FILETYPE_ASN1, crypto.load_publickey(crypto.FILETYPE_PEM, key))
