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

import logging, os, binascii, hashlib, base64, struct, datetime, time

from M2Crypto import *
from hkdf import hkdf_expand, hkdf_extract

from knock_common.definitions import KnockProtocolDefinitions

class CryptoEngine:

    def __init__(self, sk, pk, certUtil):
        self.pk = None if pk == None else EC.load_pub_key_bio(BIO.MemoryBuffer(pk))
        self.sk = None if sk == None else EC.load_key_bio(BIO.MemoryBuffer(sk))
        self.certUtil = certUtil


    def signAndEncryptRequest(self, protocol, port):

        timestamp = time.mktime(datetime.datetime.now().timetuple())
        request = struct.pack('!B?HL', 0, protocol, int(port), timestamp)

        signedMessage = self.certUtil.signIncludingCertificate(request)
        signedAndEncryptedMessage, ephPubKey = self.encryptWithECIES(signedMessage, self.pk)
        signedAndEncryptedMessage += ephPubKey
        return signedAndEncryptedMessage



    def decryptAndVerifyRequest(self, payload):
        signedRequestWithSignature = self.decryptWithECIES(payload)

        zeroBits = struct.unpack('!B',signedRequestWithSignature[0])[0]
        success = zeroBits == 0

        if success:
            signatureLength = struct.unpack('!B',signedRequestWithSignature[-1:])[0]
            signedRequest = signedRequestWithSignature[0:-(signatureLength+1)]
            signature = signedRequestWithSignature[-(signatureLength+1):-1]
            certificate = signedRequestWithSignature[8:-(signatureLength+1)]
            success = self.certUtil.verifyCertificateAndSignature(certificate, signature, signedRequest)

        if success:
            timestamp = struct.unpack('!L', signedRequest[4:8])[0]
            packetTime = datetime.datetime.fromtimestamp(timestamp)
            success = packetTime <= datetime.datetime.now() + datetime.timedelta(0, KnockProtocolDefinitions.TIMESTAMP_THRESHOLD_IN_SECONDS)

        if success:
            request = signedRequest[1:4]
            protocol, port = struct.unpack('!?H', request)
            protocol = KnockProtocolDefinitions.PROTOCOL.getById(protocol)      # Convert to Enum



        return success, protocol, port

    def encryptWithECIES(self, message, pk):
        ephermal = EC.gen_params(EC.NID_X9_62_prime256v1)
        ephermal.gen_key()
        ecdhSecret = ephermal.compute_dh_key(pk)
        aesKey = self.hkdf(ecdhSecret)

        encrypt = EVP.Cipher(alg='aes_128_cbc', key=aesKey, iv = '\0' * 16, padding=1, op=1)
        encryptedMessage = encrypt.update(message)
        encryptedMessage += encrypt.final()

        ephPubKeyBIO = BIO.MemoryBuffer()
        ephermal.save_pub_key_bio(ephPubKeyBIO)
        ephPubKey = self.certUtil.convertPEMtoDER(ephPubKeyBIO.read_all())

        return encryptedMessage, ephPubKey


    def decryptWithECIES(self, encryptedMessage):
        ephPubKey = encryptedMessage[-91:]
        encryptedMessage = encryptedMessage[0:-91]
        ecdhSecret = self.sk.compute_dh_key(EC.load_pub_key_bio(BIO.MemoryBuffer(self.certUtil.convertDERtoPEM(ephPubKey))))
        aesKey = self.hkdf(ecdhSecret)

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
