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

from threading import Thread


class PortOpenerThread(Thread):

    def __init__(self, firewallHandler, protocol, port, addr):
        self.firewallHandler = firewallHandler
        self.protocol = protocol
        self.port = port
        self.addr = addr
        Thread.__init__()


    def run(self):
        self.firewallHandler.openPortForClient(self.port, self.protocol, self.addr)