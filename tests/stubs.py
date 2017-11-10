from configurations import config_server_valid
from common.definitions.Constants import *
from server.modules.Security.Security import Security as Security_Server
# Mocks / Stubs

class stub_Firewall:

    def __init__(self):
        self.config = config_server_valid
        self.config.PORT_OPEN_DURATION_IN_SECONDS = 2
        self.counter = 0
    def openPortForClient(self, port, ipVersion, protocol, addr):
        self.counter+=1
    def closePortForClient(self, port, ipVersion, protocol, addr):
        self.counter-=1

class stub_CryptoEngine_Server:
    def __init__(self, dummy_ipv4_address, dummy_ipv6_address):
        self.dummy_ipv4_address = dummy_ipv4_address
        self.dummy_ipv6_address = dummy_ipv6_address
    def decryptAndVerifyRequest(self, encryptedMessage, ipVersion):
        if ipVersion == IP_VERSION.V4:
            return True, PROTOCOL.TCP, 2000, self.dummy_ipv4_address
        elif ipVersion == IP_VERSION.V6:
            return True, PROTOCOL.TCP, 2000, self.dummy_ipv6_address
        else:
            return None

class stub_KnockProcessor:
    def __init__(self, firewallHandler, security):
        self.config = config_server_valid
        self.runningPortOpenTasks = set()
        self.firewallHandler = firewallHandler
        self.security = security

def fake_Security_updateCrl(fake_self):
    pass
stub_Security_Server = Security_Server
stub_Security_Server.updateCrl = fake_Security_updateCrl
