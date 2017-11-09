import hashlib
import logging

from M2Crypto import *
#from hkdf import hkdf_expand, hkdf_extract
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from Utils import *

SIGNATURE_SIZE = 73

LOG = logging.getLogger(__name__)

class CryptoEngine:

    def __init__(self, privKey):
        self.privKey = self.loadPrivKeyFromPEM(privKey)

    def encryptWithECIES(self, message, pubKey):
        LOG.debug("Generating ECC ephermal key...")
        ephermal = EC.gen_params(EC.NID_X9_62_prime256v1)
        ephermal.gen_key()

        LOG.debug("Deriving AES symmetric key...")
        ecdhSecret = ephermal.compute_dh_key(pubKey)
        aesKey = self._hkdf(ecdhSecret)

        LOG.debug("Encrypting with AES...")
        encrypt = EVP.Cipher(alg='aes_128_cbc', key=aesKey, iv = '\0' * 16, padding=1, op=1)
        encryptedMessage = encrypt.update(message)
        encryptedMessage += encrypt.final()

        ephPubKeyBIO = BIO.MemoryBuffer()
        ephermal.save_pub_key_bio(ephPubKeyBIO)
        ephPubKey = convertPEMtoDER(ephPubKeyBIO.read_all())

        return encryptedMessage, ephPubKey

    def decryptWithECIES(self, encryptedMessage):
        LOG.debug("Calculating decryption key...")
        ephPubKey = encryptedMessage[-91:]
        encryptedMessage = encryptedMessage[0:-91]
        ecdhSecret = self.privKey.compute_dh_key(EC.load_pub_key_bio(BIO.MemoryBuffer(convertDERtoPEM(ephPubKey))))
        aesKey = self._hkdf(ecdhSecret)

        LOG.debug("Decrypting AES encrypted request...")
        decrypt = EVP.Cipher(alg='aes_128_cbc', key=aesKey, iv = '\0' * 16, padding=1, op=0)
        decryptedMessage = decrypt.update(encryptedMessage)
        decryptedMessage += decrypt.final()

        return decryptedMessage

    def _hkdf(self, ecdhSecret):
        hkdf = HKDF(algorithm=hashes.SHA256(),
                    length=16,
                    salt=b"54686579206c6976696e272069742075702061742074686520486f74656c2043616c69666f726e69610a576861742061206e6963652073757270726973652028776861742061206e696365207375727072697365290a4272696e6720796f757220616c69626973",
                    info=b"knock",
                    backend=default_backend())
        return hkdf.derive(ecdhSecret)


    @staticmethod
    def loadPrivKeyFromPEM(pem):
        return EC.load_key_bio(BIO.MemoryBuffer(pem))

    @staticmethod
    def loadPubKeyFromPEM(pem):
        return EC.load_pub_key_bio(BIO.MemoryBuffer(pem))
