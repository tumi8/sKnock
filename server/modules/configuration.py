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

import logging, os, ConfigParser

LOG = logging.getLogger(__name__)

class Configuration:
    STR_PACKET_MIN_LENGTH = 'KNOCKPACKET_MIN_LENGTH'
    STR_PORT_OPEN_DURATION_IN_SECONDS = 'PORT_OPEN_DURATION_IN_SECONDS'
    STR_TIMESTAMP_THRESHOLD_IN_SECONDS = 'TIMESTAMP_THRESHOLD_IN_SECONDS'
    STR_SIGNATURE_SIZE = 'SIGNATURE_SIZE'
    STR_RECV_BUFFER = 'RECV_BUFFER'
    STR_CRL_FILE = 'CRL_FILE'
    STR_CRL_URL = 'CRL_URL'
    STR_PFX_FILE = 'PFX_FILE'
    STR_PFX_PASSWD = 'PFX_PASSWD'
    STR_FIREWALL_POLICY = 'FIREWALL_POLICY'

    def __init__(self):
        pass

    def load_from_file(self,
                       configFilePath = os.path.join(os.path.dirname(__file__), os.pardir, 'config.ini')):
        """
        Load configuration from the given file substituting default values
        whenever applicable.
        """

        parser = ConfigParser.SafeConfigParser(
            {
                STR_PACKET_MIN_LENGTH: '800',
                STR_PORT_OPEN_DURATION_IN_SECONDS: '15',
                STR_TIMESTAMP_THRESHOLD_IN_SECONDS: '7',
                STR_SIGNATURE_SIZE: '73'
                STR_RECV_BUFFER : '1600',
                STR_CRL_FILE: os.path.join('certificates', 'devca.crl'),
                STR_CRL_URL : 'https://home.in.tum.de/~sel/BA/CA/devca.crl',
                STR_PFX_FILE: os.path.join('certificates', 'devserver.pfx'),  #PKCS12 file containing the private key
                STR_PFX_PASSWD: 'portknocking',
                STR_FIREWALL_POLICY : 'reject'
            }
        )
        parser.read(configFilePath)
        section = 'DEFAULT'
        self.PACKET_MIN_LENGTH = parser.getint(section, STR_PACKET_MIN_LENGTH)
        self.PORT_OPEN_DURATION_IN_SECONDS = parser.getint(section, STR_PORT_OPEN_DURATION_IN_SECONDS)
        self.TIMESTAMP_THRESHOLD_IN_SECONDS = parser.getint(section, STR_TIMESTAMP_THRESHOLD_IN_SECONDS)
        self.SIGNATURE_SIZE = parser.getint(section, STR_SIGNATURE_SIZE)
        self.RECV_BUFFER = parser.getint(section, STR_RECV_BUFFER)
        self.CRL_FILE = os.path.join(os.path.dirname(__file__), os.pardir, parser.get(section, STR_CRL_FILE))
        self.CRL_URL = parser.get(section, STR_CRL_URL)
        self.PFX_FILE = os.path.join(os.path.dirname(__file__), os.pardir, parser.get(section, STR_PFX_FILE))
        self.PFX_PASSWD = parser.get(section, STR_PFX_PASSWD)
        self.FIREWALL_POLICY = parser.get(section, STR_FIREWALL_POLICY)
