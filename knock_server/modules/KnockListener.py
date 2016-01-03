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

import socket
from struct import *
from PortOpenerThread import PortOpenerThread
from PlatformUtils import PlatformUtils
from Connection import Connection

class KnockListener:

    KNOCKPACKET_LENGTH = 4

    def __init__(self, cryptoEngine, firewallHandler):
        self.cryptoEngine = cryptoEngine
        self.firewallHandler = firewallHandler
        self.udpsocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
        print 'socket initialized'

    def capturePossibleKnockPackets(self):
        udpsocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
        print 'socket initialized'
        while True:
            source, packet = udpsocket.recvfrom(2048)

            ipVersionLengthByte = unpack('!B', packet[0])
            ipVersion = ipVersionLengthByte[0] >> 4
            udpHeaderLength = 8;

            if ipVersion == 4:
                ipHeaderLength = (ipVersionLengthByte[0] & 0xF) * 4
            elif ipVersion == 6:
                ipHeaderLength = 40

            udpHeader = packet[ipHeaderLength:ipHeaderLength + udpHeaderLength]

            lengthByte = unpack('!H', udpHeader[4:6])
            payloadLength = lengthByte[0] - udpHeaderLength

            if payloadLength == KnockListener.KNOCKPACKET_LENGTH:
                payload = packet[ipHeaderLength + udpHeaderLength : ipHeaderLength + udpHeaderLength + payloadLength]
                yield source, payload


    def processIncomingPackets(self):
        for source, request in KnockListener.capturePossibleKnockPackets():
            success, protocol, port = self.cryptoEngine.decryptAndVerifyRequest(request)

            if success:
                print 'Got request For ' + protocol + ' Port: ' + port + ' from host: ' + source

                PortOpenerThread(self.firewallHandler, protocol, port, source).start()