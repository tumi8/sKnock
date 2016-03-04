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
import logging
import struct
import time

from common.modules.CertUtil import CertUtil
from common.modules.CryptoEngine import CryptoEngine

LOG = logging.getLogger(__name__)

class Security:

    def __init__(self, pfxFile, pfxPasswd, serverCertFile):
        self.certUtil = CertUtil(pfxFile, pfxPasswd)
        self.security = CryptoEngine(self.certUtil.getPrivKeyPEM())
        self.serverPublicKey = CryptoEngine.loadPubKeyFromPEM(CertUtil.loadPubKeyPEMFromCert(serverCertFile))


    def signAndEncryptRequest(self, protocol, port, clientIP):
        LOG.debug("Signing and encrypting request...")
        packetTime = datetime.datetime.utcnow()
        timestamp = time.mktime(packetTime.timetuple())
        request = ''.join((struct.pack('!B?H', 0, protocol, int(port)), clientIP, struct.pack('!L', timestamp)))
        LOG.debug("Added timestamp: %s", packetTime)

        signedMessage = self.certUtil.signIncludingCertificate(request)
        signedAndEncryptedMessage, ephPubKey = self.security.encryptWithECIES(signedMessage, self.serverPublicKey)
        signedAndEncryptedMessage += ephPubKey
        return signedAndEncryptedMessage