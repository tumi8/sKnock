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
import socket, errno
from NewPacketThread import NewPacketThread

LOG = logging.getLogger(__name__)

ETH_P_ALL = 3


class KnockProcessor:
    def __init__(self, config, cryptoEngine, firewallHandler):
        self.shutdown = False
        self.config = config
        self.cryptoEngine = cryptoEngine
        self.firewallHandler = firewallHandler
        self.runningPortOpenTasks = list()
        self.socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ETH_P_ALL))

        LOG.debug("Sockets initialized")

    def run(self):
        while not self.shutdown:
            try:
                packet = self.socket.recv(self.config.RECV_BUFFER)
            except socket.error, e:
                if e.errno != errno.EINTR:
                    raise e
                else:
                    return

            if len(packet) >= self.config.KNOCKPACKET_MIN_LENGTH:
                NewPacketThread(self, packet).start()

    def stop(self):
        self.shutdown = True
