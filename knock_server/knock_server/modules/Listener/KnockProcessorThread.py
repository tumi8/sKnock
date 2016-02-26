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
from threading import Thread
from NewPacketThread import NewPacketThread

LOG = logging.getLogger(__name__)

ETH_P_ALL = 3


class KnockProcessorThread(Thread):
    def __init__(self, config, cryptoEngine, firewallHandler):
        self.shutdown = False
        self.config = config
        self.cryptoEngine = cryptoEngine
        self.firewallHandler = firewallHandler
        self.runningPortOpenTasks = list()
        self.socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ETH_P_ALL))
        Thread.__init__(self)

        LOG.debug("Sockets initialized")

    def run(self):
        import time
        while not self.shutdown:
            #packet = self.socket.recv(self.config.RECV_BUFFER)
            time.sleep(2)
            print 'hui' if self.shutdown else 'aww'
            #if len(packet) >= self.config.KNOCKPACKET_MIN_LENGTH:
             #   pass  # NewPacketThread(self, packet).start()

        print 'buhja'

    def stop(self):
        self.shutdown = True
