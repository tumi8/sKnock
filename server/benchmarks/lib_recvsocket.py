import socket

ETH_P_ALL = 3

def get_me_a_packet():

    recvsocket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ETH_P_ALL))

    while True:
        packet = recvsocket.recv(2048)
        if(len(packet) > 800):
            with open("v4packet.eth", 'wb') as baconFile:
                baconFile.write(packet)

            break

if __name__ == '__main__':
    get_me_a_packet()
