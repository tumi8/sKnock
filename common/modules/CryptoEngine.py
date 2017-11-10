import logging
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key,
    load_pem_public_key,
    load_der_public_key,
    Encoding,
    PublicFormat)

SIGNATURE_SIZE = 73

LOG = logging.getLogger(__name__)

_TAG_KNOCK = b"knock"
_TAG_IV = b"iv0AES128CBC"
_BLOCKSIZE = 128
class CryptoEngine:

    def __init__(self, privKey):
        self.privKey = self.loadPrivKeyFromPEM(privKey)

    def encryptWithECIES(self, message, pubKey):
        LOG.debug("Generating ECC ephermal key...")
        ephermal = ec.generate_private_key(ec.SECP256R1(), # NIST P-256 Curve
                                      default_backend())
        LOG.debug("Deriving AES symmetric key...")
        ecdhSecret = ephermal.exchange(ec.ECDH(), pubKey)
        aesKey = self._hkdf(_TAG_KNOCK, ecdhSecret)
        LOG.debug("Encrypting with AES...")
        iv = self._hkdf(_TAG_IV, ecdhSecret)
        padder = PKCS7(_BLOCKSIZE).padder()
        padded_message = padder.update(message) + padder.finalize()
        encryptor = Cipher(algorithms.AES(aesKey), modes.CBC(iv), default_backend()).encryptor()
        encryptedMessage = encryptor.update(padded_message) + encryptor.finalize()

        # Serialize the ephemeral pub key in DER format
        ephPubKey = ephermal.public_key().public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
        return encryptedMessage, ephPubKey

    def decryptWithECIES(self, encryptedMessage):
        LOG.debug("Calculating decryption key...")
        eph_pubkey_bytes = encryptedMessage[-91:]
        ephPubKey = load_der_public_key(eph_pubkey_bytes, default_backend())
        encryptedMessage = encryptedMessage[0:-91]
        ecdhSecret = self.privKey.exchange(ec.ECDH(), ephPubKey)
        aesKey = self._hkdf(_TAG_KNOCK, ecdhSecret)
        iv = self._hkdf(_TAG_IV, ecdhSecret)
        LOG.debug("Decrypting AES encrypted request...")
        decryptor = Cipher(algorithms.AES(aesKey), modes.CBC(iv), default_backend()).decryptor()
        decryptedMessage_padded = decryptor.update(encryptedMessage) + decryptor.finalize()
        unpadder = PKCS7(_BLOCKSIZE).unpadder()
        decryptedMessage = unpadder.update(decryptedMessage_padded) + unpadder.finalize()
        return decryptedMessage

    def _hkdf(self, tag, ecdhSecret):
        hkdf = HKDF(algorithm=hashes.SHA256(),
                    length=_BLOCKSIZE/8,
                    salt=b"54686579206c6976696e272069742075702061742074686520486f74656c2043616c69666f726e69610a576861742061206e6963652073757270726973652028776861742061206e696365207375727072697365290a4272696e6720796f757220616c69626973",
                    info=tag,
                    backend=default_backend())
        return hkdf.derive(ecdhSecret)


    @staticmethod
    def loadPrivKeyFromPEM(pem):
        return load_pem_private_key(pem, None, default_backend())

    @staticmethod
    def loadPubKeyFromPEM(pem):
        return load_pem_public_key(pem, default_backend())
