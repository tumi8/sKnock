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

import logging, socket, random, struct, datetime, time

logger = logging.getLogger(__name__)

class Connection:

    TCP = 'tcp'
    UDP = 'udp'
    MIN_PORT = 10000
    MAX_PORT = 60000

    def __init__(self, cryptoEngine, timeout, numberOfRetries):
        self.timeout = timeout
        self.numberOfRetries = numberOfRetries
        self.cryptoEngine = cryptoEngine

    def knockOnPort(self, targetHost, requestedPort):
        randomPort = random.randint(Connection.MIN_PORT, Connection.MAX_PORT)

        for i in range(0, self.numberOfRetries):
            self.sendKnockPacket(targetHost, requestedPort, randomPort)
            if self.verifyTargetPortIsOpen(targetHost,requestedPort):
                logger.info('Port-knocking successfull. Application Port %s is now open!', requestedPort)
                break
            logger.info('Port still not open - maybe packet got lost. Retrying...')
        logger.error('Port-knocking failed. Verify you are authorized to open the requested port and check your configuration!')


    def sendKnockPacket(self, targetHost, requestedPort, knockPort):

        logger.debug('Knock Target Port: %s, Requested Application Port: %s', knockPort, requestedPort)

        # TODO: implement protocol
        protocol = 1    # 1 = TCP, 0 = UDP
        timestamp = time.mktime(datetime.datetime.now().timetuple())
        request = struct.pack('!B?HL', 0, protocol, int(requestedPort), timestamp)
        encryptedRequest = self.cryptoEngine.signAndEncryptRequest(request)

        socketToServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socketToServer.sendto(encryptedRequest, (targetHost, knockPort))

        logger.info('Knock Packet sent to %s:%s', targetHost, knockPort)


    def verifyTargetPortIsOpen(self, targetHost ,requestedPort):
        try:
            s = socket.create_connection((targetHost, requestedPort), timeout=self.timeout)
            s.shutdown(socket.SHUT_RDWR)

            return True
        except:
            return False