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
from threading import Thread

from PortOpenerThread import PortOpenerThread


LOG = logging.getLogger(__name__)

class ProcessRequestThread(Thread):

    def __init__(self, cryptoEngine, firewallHandler, runningPortOpenTasks, ipVersion, addr, request):
        self.cryptoEngine = cryptoEngine
        self.firewallHandler = firewallHandler
        self.runningPortOpenTasks = runningPortOpenTasks
        self.ipVersion = ipVersion
        self.request = request
        self.addr = addr
        Thread.__init__(self)


    def run(self):
        success, protocol, port = self.cryptoEngine.decryptAndVerifyRequest(self.request)

        if success:
            LOG.info('Got request for %s Port: %s from host: %s', protocol, port, self.addr)
            if not hash(str(port) + str(self.ipVersion) + protocol + self.addr) in self.runningPortOpenTasks:
                PortOpenerThread(self.runningPortOpenTasks, self.firewallHandler, self.ipVersion, protocol, port, self.addr).start()
            else:
                LOG.info('There is already a Port-open process running for %s Port: %s for host: %s!',
                            protocol, port, self.addr)