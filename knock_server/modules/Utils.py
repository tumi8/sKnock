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
from knock_server.lib.X509Cert import X509

LOG = logging.getLogger(__name__)

# Authorization String Format: PROTOCOL.PORTNUMBER,PROTOCOL.PORTNUMBER,... eg: 1.2000,1.3000,0.5000
# Request has to be tuple of (PROTOCOL, PORTNUMBER) eg.: (1, 2000)
# TCP = 1, UDP = 0
def checkIfRequestIsAuthorized(request, rawCert):
    cert = X509(rawCert)

    if cert.SAN_auth == None:
        LOG.warning('Unsupported Authenticator in Certificate!')
        return False, None

    for authorizationString in cert.SAN_auth.split(','):
        try:
            authorization = [int(x) for x in authorizationString.split('.')]
        except ValueError:
            LOG.warning('Malformed Authorization string in Authenticator')
            return False, cert.getFingerprint().encode('hex')

        if request == authorization:
            return True, cert.getFingerprint().encode('hex')

    return False, cert.getFingerprint().encode('hex')