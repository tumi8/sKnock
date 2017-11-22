import logging
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key, load_pem_public_key)
from cryptography.exceptions import UnsupportedAlgorithm

SIGNATURE_SIZE = 73

LOG = logging.getLogger(__name__)

_TAG_KNOCK = b"knock"
_TAG_IV = b"iv0AES128CBC"
_BLOCKSIZE = 128
_CURVE = ec.SECP256R1()         # NIST P-256 Curve
_CIPHER = algorithms.AES
_CIPHER_MODE = modes.CBC


class EncryptionError(Exception):

    def __init__(self, message):
        super(EncryptionError, self).__init__(message)


class DecryptionError(Exception):

    def __init__(self, message):
        super(DecryptionError, self).__init__(message)


class CryptoEngine:

    def __init__(self, privKey):
        self.privKey = self.loadPrivKeyFromPEM(privKey)

    def encryptWithECIES(self, message, pubKey):
        """Return the message encrypted with the given public key and our
        ephemeral public key.

        The given message is padded and ECIES encrypted.  The public key is
        expected to be from the NIST P-256 Curve.  An ephemeral private key is
        generated from the same curve and its public point is encoded without
        compression according to SEC 1 v2.0.

        Args:
          message (bytes): the message to encyrpt
          pubkey (EllipticCurvePublicKey): the public key to which this message
            has to be encrypted

        Returns:
          bytes: the encrypted message
          bytes: the uncompressed point encoding of our ephemeral public key
                 (size: 65 bytes)

        Raises:
          EncryptionError: upon error during encryption
        """
        LOG.debug("Generating ECC ephemeral key...")
        ephemeral = ec.generate_private_key(_CURVE(),
                                            default_backend())
        LOG.debug("Deriving AES symmetric key...")
        ecdhSecret = ephemeral.exchange(ec.ECDH(), pubKey)
        aesKey = self._hkdf(_TAG_KNOCK, ecdhSecret)
        LOG.debug("Encrypting with AES...")
        iv = self._hkdf(_TAG_IV, ecdhSecret)
        padder = PKCS7(_BLOCKSIZE).padder()
        padded_message = padder.update(message) + padder.finalize()
        try:
            encryptor = Cipher(_CIPHER(aesKey), _CIPHER_MODE(iv),
                               default_backend()).encryptor()
            encryptedMessage = encryptor.update(padded_message)
            encryptedMessage += encryptor.finalize()
        except UnsupportedAlgorithm as e:
            raise EncryptionError(str(e))
        # ValueError can be ignored because we always pad the message
        # encode the public point using uncompressed encoding from SEC 1 v2.0
        point_encoding = ephemeral.public_key().public_numbers().encode_point()
        return encryptedMessage, point_encoding

    def decryptWithECIES(self, encryptedMessage):
        """Returns the decryption of the given ECIES encrypted message.

        The key required for decryption is derived from the last 65 bytes of the
        message, which encode the public point of the ephemeral ECDH key without
        compression according to SEC 1 v2.0.

        Args:
          encryptedMessage = the encrypted message to be decrypted

        Returns:
          bytes: the decrypted message

        Raises:
          DecryptionError: when decryption fails due to issufficient length of
            the message, failure while decoding the ECDH public point, or
            incorrect padding

        """
        LOG.debug("Calculating decryption key...")
        enc_len = 65
        if len(encryptedMessage) <= enc_len:
            msg = "Insufficient message size to hold payload and decryption key"
            raise DecryptionError(msg)
        eph_pubkey_bytes = encryptedMessage[-enc_len:]
        try:
            point = ec.EllipticCurvePublicNumbers.from_encoded_point(
                _CURVE(), eph_pubkey_bytes)
        except ValueError as e:
            raise DecryptionError("Invalid point encoding")
        ephPubKey = point.publickey(default_backend())
        encryptedMessage = encryptedMessage[0:-enc_len]
        ecdhSecret = self.privKey.exchange(ec.ECDH(), ephPubKey)
        aesKey = self._hkdf(_TAG_KNOCK, ecdhSecret)
        iv = self._hkdf(_TAG_IV, ecdhSecret)
        LOG.debug("Decrypting AES encrypted request...")
        try:
            decryptor = Cipher(_CIPHER(aesKey), _CIPHER_MODE(iv),
                               default_backend()).decryptor()
        except UnsupportedAlgorithm as e:
            raise DecryptionError(str(e))
        padded_payload = decryptor.update(encryptedMessage)
        try:
            padded_payload += decryptor.finalize()
        except ValueError as e:
            msg = "Encrypted message size not a block size multiple"
            raise DecryptionError(msg)
        if b"" == padded_payload:
            return padded_payload
        unpadder = PKCS7(_BLOCKSIZE).unpadder()
        message = unpadder.update(padded_payload)
        try:
            message += unpadder.finalize()
        except ValueError as e:
            raise DecryptionError("Invalid message padding")
        return message

    def _hkdf(self, tag, ecdhSecret):
        salt = (b"54686579206c6976696e272069742075702061742074686520486f74656c"
                b"2043616c69666f726e69610a576861742061206e69636520737572707269"
                b"73652028776861742061206e696365207375727072697365290a4272696e"
                b"6720796f757220616c69626973")
        hkdf = HKDF(algorithm=SHA256(),
                    length=_BLOCKSIZE/8,
                    salt=salt,
                    info=tag,
                    backend=default_backend())
        return hkdf.derive(ecdhSecret)

    @staticmethod
    def loadPrivKeyFromPEM(pem):
        return load_pem_private_key(pem, None, default_backend())

    @staticmethod
    def loadPubKeyFromPEM(pem):
        return load_pem_public_key(pem, default_backend())
