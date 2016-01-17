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

import datetime
import logging

import LinuxHelpers
from knock_server.definitions.Exceptions import *
from knock_server.modules.PlatformUtils import PlatformUtils
from knock_server.decorators.synchronized import synchronized
from knock_server.definitions import Constants

logger = logging.getLogger(__name__)

class Firewall:

    def __init__(self):
        self.platform = PlatformUtils.detectPlatform()

        if(self.platform == PlatformUtils.LINUX):
            LinuxHelpers.backupIPTablesState()

        self.setupDefaultFirewallState()
        self.openPortsList = list()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if(self.platform == PlatformUtils.LINUX):
            LinuxHelpers.restoreIPTablesState()

    def setupEmergencyAccessFirewallRules(self):
        if(self.platform == PlatformUtils.LINUX):
            LinuxHelpers.insertEmergencySSHAccessRule()

    def setupDefaultFirewallState(self):
        if(self.platform == PlatformUtils.LINUX):
            LinuxHelpers.setupIPTabkesPortKnockingChainAndRedirectTraffic()

        self.setupEmergencyAccessFirewallRules()


    @synchronized
    def openPortForClient(self, port, ipVersion, protocol, addr):

        openPort = hash(str(port) + str(ipVersion) + protocol + addr)
        if openPort in self.openPortsList:
            logger.info('%s Port: %s for host: %s is already open!', protocol, port, addr)
            raise PortAlreadyOpenException

        if(self.platform == PlatformUtils.LINUX):
            chain = LinuxHelpers.getIPTablesChainForVersion(ipVersion, LinuxHelpers.IPTABLES_CHAIN_KNOCK)
            rule = LinuxHelpers.getIPTablesRuleForClient(port, ipVersion, protocol, addr)

            LinuxHelpers.deleteIPTablesRuleIgnoringError(rule, chain)
            chain.append_rule(rule)

        self.openPortsList.append(openPort)
        logger.info('%s Port: %s opened for host: %s from: %s until: %s',
                    protocol, port, addr,
                    datetime.datetime.now(),
                    datetime.datetime.now() +
                    datetime.timedelta(0, Constants.PORT_OPEN_DURATION_IN_SECONDS))



    @synchronized
    def closePortForClient(self, port, ipVersion, protocol, addr):
        if(self.platform == PlatformUtils.LINUX):
            chain = LinuxHelpers.getIPTablesChainForVersion(ipVersion, LinuxHelpers.IPTABLES_CHAIN_KNOCK)
            rule = LinuxHelpers.getIPTablesRuleForClient(port, ipVersion, protocol, addr)

            chain.delete_rule(rule)

        self.openPortsList.remove(hash(str(port) + str(ipVersion) + protocol + addr))
        logger.info('%s Port: %s closed for host: %s at: %s', protocol, port, addr, datetime.datetime.now())