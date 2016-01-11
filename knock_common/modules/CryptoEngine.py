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

import logging, os, binascii, hashlib, base64

from M2Crypto import *
from hkdf import hkdf_expand, hkdf_extract

from knock_common.definitions import KnockProtocolDefinitions

class CryptoEngine:

    def __init__(self, sk, pk, certUtil):
        self.pk = EC.load_pub_key_bio(BIO.MemoryBuffer(pk))
        self.sk = None if sk == None else EC.load_key_bio(BIO.MemoryBuffer(sk))
        self.certUtil = certUtil


    def decryptAndVerifyRequest(self, request):
        success = True
        protocol = KnockProtocolDefinitions.PROTOCOL.TCP
        port = request

        return success, protocol, port


    def signAndEncryptRequest(self, request):
        signedMessage = self.certUtil.sign(request)
        signedAndEncryptedMessage, ephPubKey = self.encryptWithECIES(signedMessage, self.pk)
        signedAndEncryptedMessage += ephPubKey
        return signedAndEncryptedMessage



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

        ephPubKey = ''.join(ephPubKeyBIO.read_all().split('\n')[1:-2]) # Remove BEGIN & END Lines
        ephPubKey = base64.b64decode(ephPubKey)

        return encryptedMessage, ephPubKey


    def hkdf(self, ecdhSecret):
        prk = hkdf_extract(salt=b"54686579206c6976696e272069742075702061742074686520486f74656c2043616c69666f726e69610a576861742061206e6963652073757270726973652028776861742061206e696365207375727072697365290a4272696e6720796f757220616c69626973",
                           hash=hashlib.sha256,
                           input_key_material=ecdhSecret)

        return hkdf_expand(pseudo_random_key=prk,
                           info=b"knock",
                           length=16)
