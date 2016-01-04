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

import os, subprocess
from  knock_common.modules.PlatformUtils import PlatformUtils

class Firewall:

    def __init__(self):
        self.platform = PlatformUtils.detectPlatform()
        self.backupFirewallState()
        self.setupDefaultFirewallState()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.restoreFirewallState()

    def setupEmergencyAccessFirewallRules(self):
        if(self.platform == PlatformUtils.LINUX):
            subprocess.call('iptables -D INPUT -p tcp --dport 22 -j ACCEPT', shell=True, stderr=open(os.devnull,'w'))
            subprocess.call('iptables -I INPUT -p tcp --dport 22 -j ACCEPT', shell=True)

    def setupDefaultFirewallState(self):
        if(self.platform == PlatformUtils.LINUX):
            subprocess.call('iptables -D INPUT -j knockknock', shell=True, stderr=open(os.devnull,'w'))
            subprocess.call('iptables -F knockknock', shell=True, stderr=open(os.devnull,'w'))
            subprocess.call('iptables -X knockknock', shell=True, stderr=open(os.devnull,'w'))
            subprocess.call('iptables -N knockknock', shell=True)
            subprocess.call('iptables -P INPUT ACCEPT', shell=True)
            subprocess.call('iptables -I INPUT -j knockknock', shell=True)

        self.setupEmergencyAccessFirewallRules()


    def backupFirewallState(self):
        subprocess.call('iptables-save > /tmp/iptables.bak', shell=True)


    def restoreFirewallState(self):
        subprocess.call('iptables-restore < /tmp/iptables.bak', shell=True)

    def openPortForClient(self, port, protocol, addr):
        self.closePortForClient(port, protocol, addr)

        if(self.platform == PlatformUtils.LINUX):
            subprocess.call('iptables -A knockknock -s ' + addr + ' -p' + protocol + ' --dport ' + port + ' -j RETURN', shell=True)


    def closePortForClient(self, port, protocol, addr):
        if(self.platform == PlatformUtils.LINUX):
            subprocess.call('iptables -D knockknock -s ' + addr + ' -p' + protocol + ' --dport ' + port + ' -j RETURN', shell=True, stderr=open(os.devnull,'w'))


    def __del__(self):
        print 'suicide'