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

import logging, os

from knock_client.definitions.Constants import PROTOCOL
from CertUtil import CertUtil
from Connection import Connection

LOG = logging.getLogger(__name__)

class ClientInterface:

    def __init__(self, timeout=10, numRetries=3,
                 serverCertFile=os.path.join(os.path.dirname(__file__), os.pardir, 'devserver.cer'),
                 clientPFXFile=os.path.join(os.path.dirname(__file__), os.pardir, 'devclient.pfx'),
                 PFXPasswd='portknocking'):

        self.connectionHandler = Connection(CertUtil(serverCertFile, clientPFXFile, PFXPasswd).initializeCryptoEngine(),
                                            timeout, numRetries)


    def knockOnPort(self, host, port, protocol=PROTOCOL.TCP):
        LOG.debug('Knocking %s on port %s', host, port)
        self.connectionHandler.knockOnPort(host, port, protocol)
