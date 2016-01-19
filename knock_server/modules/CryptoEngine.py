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

import datetime
import hashlib
import logging
import struct

from M2Crypto import *
from hkdf import hkdf_expand, hkdf_extract

from knock_server.definitions.Constants import *

import Utils

SIGNATURE_SIZE = 73

LOG = logging.getLogger(__name__)

class CryptoEngine:

    def __init__(self, privateKey, certUtil):
        self.privateKey = EC.load_key_bio(BIO.MemoryBuffer(privateKey))
        self.certUtil = certUtil


    def decryptAndVerifyRequest(self, encryptedMessage):
        protocol = None
        port = None

        signedRequestWithSignature = self.decryptWithECIES(encryptedMessage)
        LOG.debug("Checking Integrity of decrypted Message...")
        zeroBits = struct.unpack('!B',signedRequestWithSignature[0])[0]
        success = zeroBits == 0

        if success:
            LOG.debug("Decrypted Message OK!")
            LOG.debug("Verifying certificate & signature...")
            signatureLength = struct.unpack('!B',signedRequestWithSignature[-73:-72])[0]
            signedRequest = signedRequestWithSignature[0:-73]
            signature = signedRequestWithSignature[-signatureLength:]
            certificate = signedRequestWithSignature[8:-73]
            success = self.certUtil.verifyCertificateAndSignature(certificate, signature, signedRequest)
        else:
            LOG.error("Unable to decrypt Request. Invalid Format?")
            return success, None, None

        if success:
            LOG.debug("Certificate & signature OK!")
            LOG.debug("Checking Timestamp of Request...")
            timestamp = struct.unpack('!L', signedRequest[4:8])[0]
            packetTime = datetime.datetime.fromtimestamp(timestamp)
            success = packetTime <= datetime.datetime.now() + datetime.timedelta(0, TIMESTAMP_THRESHOLD_IN_SECONDS)
        else:
            LOG.error("Invalid Certificate or Signature!")
            return success, None, None

        if success:
            LOG.debug("Timestamp OK!")
            LOG.debug("Processing request...")
            request = signedRequest[1:4]
            protocol, port = struct.unpack('!?H', request)
            protocol = PROTOCOL.getById(protocol)      # Convert to Enum
            LOG.debug("Checking if user is authorized to open requested port...")
            success, certFingerprint = Utils.checkIfRequestIsAuthorized([PROTOCOL.getId(protocol), port], certificate)
        else:
            LOG.error("Timestamp verification failed (Timestamp: %s). Check System time & Threshold - otherwise: possible REPLAY ATTACK", packetTime)
            return success, protocol, port

        if success:
            LOG.debug("Authorization OK!")
        else:
            LOG.warning("Unauthorized Request for %s Port: %s from User with Certificate Fingerprint: %s", protocol, port, certFingerprint)
            return success, protocol, port

        return success, protocol, port


    def decryptWithECIES(self, encryptedMessage):
        LOG.debug("Calculating decryption key...")
        ephPubKey = encryptedMessage[-91:]
        encryptedMessage = encryptedMessage[0:-91]
        ecdhSecret = self.privateKey.compute_dh_key(EC.load_pub_key_bio(BIO.MemoryBuffer(self.certUtil.convertDERtoPEM(ephPubKey))))
        aesKey = self.hkdf(ecdhSecret)

        LOG.debug("Decrypting AES encrypted request...")
        decrypt = EVP.Cipher(alg='aes_128_cbc', key=aesKey, iv = '\0' * 16, padding=1, op=0)
        decryptedMessage = decrypt.update(encryptedMessage)
        decryptedMessage += decrypt.final()

        return decryptedMessage



    def hkdf(self, ecdhSecret):
        prk = hkdf_extract(salt=b"54686579206c6976696e272069742075702061742074686520486f74656c2043616c69666f726e69610a576861742061206e6963652073757270726973652028776861742061206e696365207375727072697365290a4272696e6720796f757220616c69626973",
                           hash=hashlib.sha256,
                           input_key_material=ecdhSecret)

        return hkdf_expand(pseudo_random_key=prk,
                           info=b"knock",
                           length=16)
