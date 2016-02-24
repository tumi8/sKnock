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

import logging, os, random

from definitions.Constants import PROTOCOL
from CertUtil import CertUtil
from Connection import Connection, MIN_PORT, MAX_PORT

LOG = logging.getLogger(__name__)

class ClientInterface:

    def __init__(self, timeout=10, numRetries=3, verify=True,
                 serverCertFile=os.path.join(os.path.dirname(__file__), os.pardir, 'certificates', 'devserver.cer'),
                 clientPFXFile=os.path.join(os.path.dirname(__file__), os.pardir, 'certificates', 'devclient.pfx'),
                 PFXPasswd='portknocking'):
        """
        This function initializes the Port-Knocking client library \"knock\"

        Set context parameters and load required certificates

        timeout: Time in seconds to wait between retries. Default: 10
        numRetries: Number of Retries. Default: 3
        verify: Verify if the target Port was successfully opened. Only TCP is supported. Default: True
        serverCertFile: Path to the Server Certificate File encoded in DER. Default: certificates/devserver.cer
        clientPFXFile: Path to the Client Certificate with Private Key in PKCS#7 Format (.pfx). Default: certificates/devclient.pfx
        PFXPasswd: Password to decrypt @clientPFXFile
        """

        self.connectionHandler = Connection(CertUtil(serverCertFile, clientPFXFile, PFXPasswd).initializeCryptoEngine(),
                                            timeout, numRetries, verify)


    def knockOnPort(self, host, port, protocol=PROTOCOL.TCP, knockPort = random.randint(MIN_PORT, MAX_PORT), forceIPv4 = False):
        """
        Actual port-knocking function

        Generate port-knocking packet for opening the requested @port on @host. Can be used to create TCP or UDP connections;
        Defaults to TCP connection if @protocol is not given.
        After sending the port-knocking request verifies that the target @port is open, and if necessary retries the port-knocking

        host: Target @host, on which the application is running
        port: Port to open on target @host
        protocol: Requested Target Protocol. Default: TCP
        knockPort: (Optional) Port to use for port-knocking request. Default: Random Port between MIN_PORT and MAX_PORT
        forceIPv4: (Optional) Force port-knocking via IPv4, even when IPv6 is available. Default: false
        """

        LOG.debug('Knocking %s on port %s', host, port)
        self.connectionHandler.knockOnPort(host, port, protocol, knockPort, forceIPv4)


def init(timeout, numRetries, verify,
         serverCert, clientCert, passwd):
    return ClientInterface(timeout=timeout, numRetries=numRetries,
                           verify=verify,
                           serverCertFile=os.path.abspath(serverCert),
                           clientPFXFile=os.path.abspath(clientCert),
                           PFXPasswd=passwd)

def init_defaults(passwd):
    return ClientInterface(PFXPasswd=passwd)


# protocol_num: 0 for UDP; 1 for TCP
def knock(interface, host, port, protocol_num):
    protocol = PROTOCOL.getById (protocol_num)
    return interface.knockOnPort (host, port, protocol)
