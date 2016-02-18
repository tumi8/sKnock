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

from PacketListenerThread import PacketListenerThread

LOG = logging.getLogger(__name__)

class KnockListener:

    def __init__(self, cryptoEngine, firewallHandler):
        self.cryptoEngine = cryptoEngine
        self.firewallHandler = firewallHandler
        self.runningPortOpenTasks = list()
        udpsocket4 = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
        udpsocket6 = socket.socket(socket.AF_INET6, socket.SOCK_RAW, socket.IPPROTO_UDP)
        self.listener4 = PacketListenerThread(udpsocket4)
        self.listener6 = PacketListenerThread(udpsocket6)
        LOG.debug("Sockets initialized")

    def processPossibleKnockPackets(self):
        self.listener4.start()
        self.listener6.start()

        self.listener4.join()
        self.listener6.join()