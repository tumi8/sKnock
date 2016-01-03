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

import subprocess
from  PlatformUtils import PlatformUtils

class Firewall:

    def __init__(self):
        self.platform = PlatformUtils.detectPlatform()
        self.setupDefaultFirewallState()

    def setupEmergencyAccessFirewallRules(self):
        if(self.platform == PlatformUtils.LINUX):
            subprocess.call('iptables -I INPUT -p tcp --dport 22 -j ACCEPT', shell=True)

    def setupDefaultFirewallState(self):
        if(self.platform == PlatformUtils.LINUX):
            subprocess.call('iptables -D INPUT -j knockknock', shell=True)
            subprocess.call('iptables -P INPUT DROP', shell=True)
            subprocess.call('iptables -I INPUT -j knockknock', shell=True)
            subprocess.call('iptables -F knockknock', shell=True)
            subprocess.call('iptables -X knockknock', shell=True)
            subprocess.call('iptables -N knockknock', shell=True)

        self.setupEmergencyAccessFirewallRules()

    def openPortForClient(self, port, protocol, addr):
        if(self.platform == PlatformUtils.LINUX):
            subprocess.call('iptables -A knockknock -s ' + addr + ' -p' + protocol + ' --dport ' + port, shell=True)
