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
import os

from CertUtil import CertUtil
from Firewall.Firewall import Firewall
from knock_server.modules.Listener.KnockProcessor import KnockProcessor
from knock_server.modules.Platform.LinuxUtils import dropPrivileges

LOG = logging.getLogger(__name__)

class ServerInterface:

    def __init__(self,
                 crlFile=os.path.join(os.path.dirname(__file__), os.pardir, 'certificates', 'devca.crl'),
                 serverPFXFile=os.path.join(os.path.dirname(__file__), os.pardir, 'certificates', 'devserver.pfx'),
                 PFXPasswd='portknocking'):

        self.cryptoEngine = CertUtil(crlFile, serverPFXFile, PFXPasswd).initializeCryptoEngine()

    def runKnockDaemon(self):
        with Firewall() as firewallHandler:
            knockListener = KnockProcessor(self.cryptoEngine, firewallHandler)
            # knock_server.lib.daemonize.createDaemon()
            dropPrivileges()
            knockListener.processPossibleKnockPackets()
