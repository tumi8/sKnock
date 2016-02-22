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
import struct
from threading import Thread

from ProcessRequestThread import ProcessRequestThread
from knock_server.definitions.Constants import *

LOG = logging.getLogger(__name__)

class PacketListenerThread(Thread):

    def __init__(self, knockProcessor, socket, ipVersion):
        self.knockProcessor = knockProcessor
        self.socket = socket
        self.ipVersion = ipVersion
        Thread.__init__(self)


    def run(self):
        while True:
            packet, source = self.socket.recvfrom(2048)
            source_ip = source[0]

            udpHeaderLength = 8;

            if self.ipVersion == IP_VERSION.V6:
                udpHeader = packet[0:udpHeaderLength]

            elif self.ipVersion == IP_VERSION.V4:
                ipVersionLengthByte = struct.unpack('!B', packet[0])
                ipHeaderLength = (ipVersionLengthByte[0] & 0xF) * 4
                udpHeader = packet[ipHeaderLength:ipHeaderLength + udpHeaderLength]

            lengthByte = struct.unpack('!H', udpHeader[4:6])
            payloadLength = lengthByte[0] - udpHeaderLength

            isPossibleKnockPacket = payloadLength >= self.knockProcessor.config.KNOCKPACKET_MIN_LENGTH

            if isPossibleKnockPacket:
                if self.ipVersion == IP_VERSION.V6:
                    payload = packet[udpHeaderLength : udpHeaderLength + payloadLength]

                elif self.ipVersion == IP_VERSION.V4:
                    payload = packet[ipHeaderLength + udpHeaderLength : ipHeaderLength + udpHeaderLength + payloadLength]

                knockId = struct.unpack('!c', payload[0])[0]
                isPossibleKnockPacket = knockId == KNOCK_ID

            if isPossibleKnockPacket:
                knockVersion = struct.unpack('!BBB', payload[1:4])
                isPossibleKnockPacket = knockVersion <= KNOCK_VERSION

            if isPossibleKnockPacket:
                ProcessRequestThread(self.knockProcessor, self.ipVersion, source_ip, payload[4:]).start()