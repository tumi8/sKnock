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
import socket
import struct
import time
from common.definitions.Constants import (
    KNOCK_ID, KNOCK_VERSION, PROTOCOL)
from common.modules.CryptoEngine import EncryptionError

PROTOCOL_INFORMATION = struct.pack('!cBBB', KNOCK_ID, *KNOCK_VERSION)
MIN_PORT = 10000
MAX_PORT = 60000
LOG = logging.getLogger(__name__)


class Connection:

    def __init__(self, security, timeout, numberOfRetries, verify):
        self.timeout = timeout
        self.numberOfRetries = numberOfRetries
        self.security = security
        self.verify = verify

    def knockOnPort(self, targetHost, requestedPort, requestedProtocol,
                    knockPort, forceIPv4, clientIP):
        for i in range(0, self.numberOfRetries):
            self.sendKnockPacket(targetHost, requestedPort, requestedProtocol,
                                 knockPort, forceIPv4, clientIP)
            if not self.verify:
                LOG.info("Port-knocking finished."
                         " Verification of target port is disabled.")
                return True
            elif PROTOCOL.UDP == requestedProtocol:
                LOG.info("Port-knocking finished."
                         " Verification of UDP Ports is not supported.")
                return True
            time.sleep(1)
            if self.verifyTargetTCPPortIsOpen(targetHost, requestedPort):
                LOG.info("Port-knocking successful."
                         " Application Port %s is now open!", requestedPort)
                return True
            LOG.info('Port still not open - maybe packet got lost. Retrying...')
        LOG.error("Port-knocking failed. Verify you are authorized to open the"
                  "requested port and check your configuration!")
        return False

    def sendKnockPacket(self, targetHost, requestedPort, requestedProtocol,
                        knockPort, forceIPv4, clientIP):
        LOG.debug('Knock Target Protocol: %s, Requested Application Port: %s',
                  requestedProtocol, requestedPort)
        targetInfo = socket.getaddrinfo(targetHost, knockPort)
        for i in xrange(len(targetInfo)):
            if targetInfo[i][:3] == (socket.AF_INET6,
                                     socket.SOCK_DGRAM,
                                     socket.AF_PACKET) and not forceIPv4:
                socketToServer = socket.socket(socket.AF_INET6,
                                               socket.SOCK_DGRAM)
                if clientIP is None:
                    try:
                        socketToServer.connect((targetInfo[i][4][0],
                                                knockPort))
                    except socket.error:
                        LOG.error("Could not determine IP of network interface."
                                  " Please check network configuration and"
                                  " internet connectivity!")
                        return
                    clientIP = socketToServer.getsockname()[0]
                    LOG.debug("Determined client ip: %s", clientIP)
                    # 16 bytes IPv6 address
                    clientIP_binary = socket.inet_pton(socket.AF_INET6,
                                                       clientIP)
                    break
            elif targetInfo[i][:3] == (socket.AF_INET,
                                       socket.SOCK_DGRAM,
                                       socket.AF_PACKET):
                socketToServer = socket.socket(socket.AF_INET,
                                               socket.SOCK_DGRAM)
                if clientIP is None:
                    try:
                        socketToServer.connect((targetInfo[i][4][0],
                                                knockPort))
                    except socket.error:
                        LOG.error("Could not determine IP of network interface."
                                  " Please check network configuration and"
                                  " internet connectivity!")
                        return
                    clientIP = socketToServer.getsockname()[0]
                    LOG.debug("Determined client ip: %s", clientIP)
                    # 4 bytes IPv4 address + padding
                    clientIP_binary = ''.join((socket.inet_pton(socket.AF_INET,
                                                                clientIP),
                                               struct.pack('xxxxxxxxxxxx')))
        try:
            encryptedRequest = (
                self.security.
                signAndEncryptRequest(
                    PROTOCOL.getId(requestedProtocol),
                    requestedPort,
                    clientIP_binary)
            )
        except EncryptionError as e:
            LOG.error("Encrypting message failed: %s", str(e))
            return
        socketToServer.sendto(PROTOCOL_INFORMATION + encryptedRequest,
                              (targetHost, knockPort))
        LOG.info('Knock Packet sent to %s:%s', targetHost, knockPort)

    def verifyTargetTCPPortIsOpen(self, targetHost, requestedPort):
        try:
            s = socket.create_connection((targetHost, requestedPort),
                                         timeout=self.timeout)
            s.shutdown(socket.SHUT_RDWR)
            s.close()
            return True
        except Exception:
            return False
