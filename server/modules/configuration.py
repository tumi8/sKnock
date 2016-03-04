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

# Initialize
class Settings: pass
config = Settings()

def initialize(configFilePath = os.path.join(os.path.dirname(__file__), os.pardir, 'config.ini')):

    global config
    configReader = ConfigParser.SafeConfigParser(
        {
            'KNOCKPACKET_MIN_LENGTH': '800',
            'PORT_OPEN_DURATION_IN_SECONDS': '15',
            'TIMESTAMP_THRESHOLD_IN_SECONDS': '7',
            'SIGNATURE_SIZE': '73',
            'RECV_BUFFER' : '1600',
            'crlFile': os.path.join('certificates', 'devca.crl'),
            'crlUrl' : 'https://home.in.tum.de/~sel/BA/CA/devca.crl',
            'serverPFXFile': os.path.join('certificates', 'devserver.pfx'),
            'PFXPasswd': 'portknocking',
            'firewallPolicy' : 'reject'
        }
    )
    configReader.read(configFilePath)

    config.KNOCKPACKET_MIN_LENGTH = configReader.getint('DEFAULT', 'KNOCKPACKET_MIN_LENGTH')
    config.PORT_OPEN_DURATION_IN_SECONDS = configReader.getint('DEFAULT', 'PORT_OPEN_DURATION_IN_SECONDS')
    config.TIMESTAMP_THRESHOLD_IN_SECONDS = configReader.getint('DEFAULT', 'TIMESTAMP_THRESHOLD_IN_SECONDS')
    config.SIGNATURE_SIZE = configReader.getint('DEFAULT', 'SIGNATURE_SIZE')
    config.RECV_BUFFER = configReader.getint('DEFAULT', 'RECV_BUFFER')

    config.crlFile = os.path.join(os.path.dirname(__file__), os.pardir, configReader.get('DEFAULT', 'crlFile'))
    config.crlUrl = configReader.get('DEFAULT', 'crlUrl')
    config.serverPFXFile = os.path.join(os.path.dirname(__file__), os.pardir, configReader.get('DEFAULT', 'serverPFXFile'))
    config.PFXPasswd = configReader.get('DEFAULT', 'PFXPasswd')

    config.firewallPolicy = configReader.get('DEFAULT', 'firewallPolicy')
