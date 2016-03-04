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

from modules.Firewall import PortOpenThread

LOG = logging.getLogger(__name__)

class ProcessRequestThread(Thread):

    def __init__(self, knockProcessor, ipVersion, addr, request):
        self.knockProcessor = knockProcessor
        self.ipVersion = ipVersion
        self.request = request
        self.addr = addr
        Thread.__init__(self)


    def run(self):
        success, protocol, port, addr = self.knockProcessor.security.decryptAndVerifyRequest(self.request, self.ipVersion)

        if success:
            # Check if the source ip in the header was changed in the mean time
            success = addr == self.addr


        if success:
            LOG.info('Processing decoded request for %s Port: %s from host: %s', protocol, port, addr)
            if not hash(str(port) + str(self.ipVersion) + protocol + addr) in self.knockProcessor.runningPortOpenTasks:
                PortOpenThread.PortOpenThread(self.knockProcessor.runningPortOpenTasks, self.knockProcessor.firewallHandler, self.ipVersion, protocol, port, addr).start()
            else:
                LOG.info('There is already a Port-open process running for %s Port: %s for host: %s!',
                            protocol, port, addr)

        else:
            LOG.warn('Client IP of request does not match Source IP of IP Header! -> Possible Man-in-the-Middle attack for request for %s Port: %s for host: %s! Source IP from packet header: %s',
                            protocol, port, addr, self.addr)