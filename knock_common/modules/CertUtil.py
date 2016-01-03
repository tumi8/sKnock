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
import OpenSSL
from PlatformUtils import PlatformUtils


class CertUtil:

    HASH_ALGORITHM = 'sha256'

    def __init__(self, certificatePath, trustAnchorCAPath):
        self.certificatePath = certificatePath
        self.trustAnchorCAPath = OpenSSL.crypto.X509Store()
        self.trustAnchorCAPath.add_cert(trustAnchorCAPath)
        self.platform = PlatformUtils.detectPlatform()

    def verifyCertificate(self, rawCertData):
        if(self.platform == PlatformUtils.LINUX):
            certVerificationContext = OpenSSL.crypto.X509StoreContext(self.trustAnchorCAPath, rawCertData)
            if(certVerificationContext.verify_certificate()):
                # do revocation check
                return True
            else:
                return False


        elif(self.platform == PlatformUtils.WINDOWS):
            pass # TODO: implement for Windows





    def verifySignature(self, certificateData, payloadSignature, payload):
        if(self.platform == PlatformUtils.LINUX):
            OpenSSL.crypto.verify(certificateData, payloadSignature, payload, CertUtil.HASH_ALGORITHM)


        elif(self.platform == PlatformUtils.WINDOWS):
            pass # TODO: implement for Windows