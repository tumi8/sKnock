KNOCKPACKET_LENGTH = 827
PORT_OPEN_DURATION_IN_SECONDS = 15
TIMESTAMP_THRESHOLD_IN_SECONDS = 7


class IP_VERSION:
    V4=4
    V6=6

class PROTOCOL:
    TCP = 'tcp'
    UDP = 'udp'

    @staticmethod
    def getById(id):
        return PROTOCOL.TCP if id else PROTOCOL.UDP
