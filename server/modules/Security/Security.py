import datetime
import logging
import socket
import struct
from common.definitions.Constants import PROTOCOL, IP_VERSION
from common.modules.CertUtil import CertUtil
from common.modules.CryptoEngine import CryptoEngine
from server.modules import Utils
from UpdateCRLThread import UpdateCRLThread

LOG = logging.getLogger(__name__)


class Security:

    def __init__(self, config):
        """
        Initializes the security module.

        Raises OSError if the file for downloading CRL cannot be accessed or its
        permissions cannot be set to nobody
        """
        self.config = config
        self.certUtil = CertUtil(pfxFile=config.serverPFXFile,
                                 pfxPasswd=config.PFXPasswd)
        self.cryptoEngine = CryptoEngine(self.certUtil.getPrivKeyPEM())
        self.startContinuousCRLUpdate()

    # Note: Returns a Thread that has to be stopped before program can exit
    def startContinuousCRLUpdate(self):
        self.updateCRLThread = UpdateCRLThread(
            self.config.crlFile,
            self.config.crlUrl,
            self.config.crlInterval,
            importFunc=self.certUtil.importCrl)
        self.updateCRLThread.importFunc(self.updateCRLThread.crlFile)
        self.updateCRLThread.start()

    def decryptAndVerifyRequest(self, encryptedMessage, ipVersion):
        protocol = None
        port = None
        addr = None
        # payload is the decrypted message
        payload = self.cryptoEngine.decryptWithECIES(encryptedMessage)
        LOG.debug("Checking Integrity of decrypted Message...")
        zeroBits = struct.unpack('!B', payload[0])[0]
        success = zeroBits == 0

        if success:
            LOG.debug("Decrypted Message OK!")
            LOG.debug("Verifying certificate & signature...")
            signatureLength = (
                struct.unpack('!B',
                              payload[-(self.config.SIGNATURE_SIZE+1)])[0])
            signedRequest = payload[0:-(self.config.SIGNATURE_SIZE+1)]
            signature = payload[-signatureLength:]
            certificate = payload[24:-(self.config.SIGNATURE_SIZE+1)]
            success = self.certUtil.verifyCertificateAndSignature(certificate,
                                                                  signature,
                                                                  signedRequest)
        else:
            LOG.error("Unable to decrypt Request. Invalid Format?")
            return success, None, None, None

        if success:
            LOG.debug("Certificate & signature OK!")
            LOG.debug("Checking Timestamp of Request...")
            timestamp = struct.unpack('!L', signedRequest[20:24])[0]
            packetTime = datetime.datetime.utcfromtimestamp(timestamp)
            threshold = self.config.TIMESTAMP_THRESHOLD_IN_SECONDS
            delta = datetime.timedelta(0, threshold)
            present = datetime.datetime.utcnow()
            success = (
                (present - delta) <= packetTime
                and
                packetTime <= (present + delta)
            )
        else:
            LOG.error("Invalid Certificate or Signature!")
            return success, None, None, None

        if success:
            LOG.debug("Timestamp OK!")
            LOG.debug("Processing request...")
            request = signedRequest[1:20]
            protocol, port = struct.unpack('!?H', request[0:3])
            protocol = PROTOCOL.getById(protocol)      # Convert to Enum

            if ipVersion == IP_VERSION.V4:
                addr = socket.inet_ntop(socket.AF_INET, request[3:7])
            elif ipVersion == IP_VERSION.V6:
                addr = socket.inet_ntop(socket.AF_INET6, request[3:19])

            LOG.debug("Checking if user is authorized to open requested port...")
            success, certFingerprint = (
                Utils.checkIfRequestIsAuthorized([PROTOCOL.getId(protocol),
                                                  port],
                                                 certificate)
                )
        else:
            LOG.error("Timestamp verification failed (Timestamp: %s)."
                      " Check System time & Threshold."
                      " If OK this could be a REPLAY ATTACK", packetTime)
            return success, protocol, port, addr

        if success:
            LOG.debug("Authorization OK!")
        else:
            LOG.warning("Unauthorized Request for %s Port: %s from"
                        " User with Certificate Fingerprint: %s",
                        protocol, port, certFingerprint)
            return success, protocol, port, addr

        return success, protocol, port, addr
