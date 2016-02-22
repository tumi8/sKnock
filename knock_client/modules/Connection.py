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

import logging, random, socket, struct, sys

from knock_client.definitions.Constants import *

PROTOCOL_INFORMATION = struct.pack('!cBBB', KNOCK_ID, *KNOCK_VERSION)
MIN_PORT = 10000
MAX_PORT = 60000

LOG = logging.getLogger(__name__)

class Connection:



    def __init__(self, cryptoEngine, timeout, numberOfRetries, verify):
        self.timeout = timeout
        self.numberOfRetries = numberOfRetries
        self.cryptoEngine = cryptoEngine
        self.verify = verify

    def knockOnPort(self, targetHost, requestedPort, requestedProtocol):
        randomPort = random.randint(MIN_PORT, MAX_PORT)

        for i in range(0, self.numberOfRetries):
            self.sendKnockPacket(targetHost, requestedPort, requestedProtocol, randomPort)
            if not self.verify:
                LOG.info("Port-knocking finished. Verification of target port is disabled.")
                return True
            elif PROTOCOL.UDP == requestedProtocol:
                LOG.info("Port-knocking finished. Verification of UDP Ports is not supported.")
                return True
            elif self.verifyTargetTCPPortIsOpen(targetHost, requestedPort):
                LOG.info('Port-knocking successful. Application Port %s is now open!', requestedPort)
                return True
            LOG.info('Port still not open - maybe packet got lost. Retrying...')
        LOG.error('Port-knocking failed. Verify you are authorized to open the requested port and check your configuration!')
        return False


    def sendKnockPacket(self, targetHost, requestedPort, requestedProtocol, knockPort):

        LOG.debug('Knock Target Port: %s, Requested Application Port: %s', requestedProtocol, requestedPort)

        targetInfo = socket.getaddrinfo(targetHost, knockPort)

        socketToServer = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

        try:
            socketToServer.connect((targetHost,knockPort))
        except socket.error: pass
        localIPString = socketToServer.getsockname()[0]

        if localIPString == '::':
            LOG.warn('IPV6 not supported in current environment, using IPv4...')
            socketToServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            try:
                socketToServer.connect((targetHost,knockPort))
            except socket.error: pass
            localIPString = socketToServer.getsockname()[0]

            if localIPString == '0.0.0.0':
                LOG.error('Could not determine IP of network interface. Please check network configuration and internet connectivity!')
                sys.exit(2)

            else:
                LOG.debug("Determined client ip: %s", localIPString)
                localIP = ''.join((socket.inet_pton(socket.AF_INET, localIPString), struct.pack('xxxxxxxxxxxx'))) # 4 bytes IPv4 address + padding

        else:
            LOG.debug("Determined client ip: %s", localIPString)
            localIP = socket.inet_pton(socket.AF_INET6, localIPString) # 16 bytes IPv6 address



        encryptedRequest = self.cryptoEngine.signAndEncryptRequest(PROTOCOL.getId(requestedProtocol), requestedPort, localIP)
        socketToServer.sendto(PROTOCOL_INFORMATION + encryptedRequest, (targetHost, knockPort))

        LOG.info('Knock Packet sent to %s:%s', targetHost, knockPort)


    def verifyTargetTCPPortIsOpen(self, targetHost, requestedPort):
        try:
            s = socket.create_connection((targetHost, requestedPort), timeout=self.timeout)
            s.shutdown(socket.SHUT_RDWR)
            return True
        except:
            return False