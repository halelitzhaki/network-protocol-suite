##
# proxy.py
# This code represents the web server, that communicates with the client and the server that holds the files
##
import socket # For communicating with the client and the server
import pyfiglet # For printing big fonts to the screen
import struct # For creating packet in the rudp part

SERVER_PORT = 80 # HTTP server port
ADDRESS = "127.0.0.1"
PROXY_PORT = 30674 # Halel's id last 3 digits
BUFFER_SIZE = 4096 # Packets' size that will be sendes and received between the server and the proxy
SEPARATOR = "<SEPARATOR>" # For splitting strings

def tcp_communication():
    # Setting up the proxy server
    listening_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Open TCP socket
    listening_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listening_sock.bind((ADDRESS, PROXY_PORT)) # Determine that the socket's source port, will be the requested port from the instructions
    listening_sock.listen(1) # Waiting for the client to connect
    print(f'Waiting to client on port {str(PROXY_PORT)}')

    client_sock, client_addr = listening_sock.accept() # Client got connected to the proxy
    print(f'Client connected successfully. Address - {client_addr[0]}, Port - {str(client_addr[1])}')

    http_get = client_sock.recv(BUFFER_SIZE).decode() # Getting the HTTP Get message from proxy
    print('Got HTTP Get message from client')

    start, end = http_get.split("HTTP/1.1")
    http_get_to_server = start + f'HTTP/1.1\r\nHost: {ADDRESS}:{str(SERVER_PORT)}\r\n\r\n'

    # Setting TCP Connection with server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Open TCP socket
    sock.connect((ADDRESS, SERVER_PORT)) # Connecting to server
    sock.send(http_get_to_server.encode()) # Sending client's HTTP Get message to server
    print('Sending HTTP Get message to server')

    response = sock.recv(BUFFER_SIZE) # Getting server's HTTP response message
    client_sock.send(response) # Sending server's response to client

    # Transferring the file to the client
    while True:
        bytes_read = sock.recv(BUFFER_SIZE) # Getting the file data from server
        if not bytes_read:
            break
        client_sock.sendall(bytes_read) # Sending the file data to client
    print('File transferred successfully')

    sock.close() # Closing the connection with the server
    client_sock.close() # Closing the connection with the client
    listening_sock.close() # Closing the proxy socket (shutting down the proxy)



def rudp_communication():
    print("rudp")
    # Setting TCP Connection with server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ADDRESS, SERVER_PORT))

    # Setting Reliable UDP Connection with client
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    proxy_socket.bind((ADDRESS,PROXY_PORT))

    #proxy_socket.settimeout(5.0)
    sent_packets = {}
    seq_num = 0

    dgram, client_addr = proxy_socket.recv(BUFFER_SIZE)
    header = struct.unpack('!HHHH', dgram[:8])
    dgram_checksum = header[3]
    if dgram_checksum == calculate_checksum(dgram[8:]):
        sock.send(dgram[8:])
        server_response = sock.recv(BUFFER_SIZE)
        dgram_seq, dgram_timestamp = struct.unpack('!LL', dgram[:8])
        msg = f'Ack for {dgram[8:]}, seq={dgram_seq}>>>{server_response.decode()}'.encode()
        datagram = struct.pack('!HHLL', PROXY_PORT, client_addr[1], seq_num, int(time.time() * 1000)) + msg
        datagram_checksum = calculate_checksum(datagram)
        datagram_with_checksum = struct.pack('!HHHH', PROXY_PORT, client_addr[1], len(datagram), datagram_checksum) + datagram
        proxy_socket.sendto(datagram_with_checksum, client_addr)
        sent_packets[seq_num] = datagram_with_checksum
        seq_num+=1
        while True:
            try:
                bytes_read = sock.recv(BUFFER_SIZE) # file
                if not bytes_read:
                    break

                data, client_addr = proxy_socket.recv(BUFFER_SIZE)
                header = struct.unpack('!HHHH', data[:8])
                data_checksum = header[3]
                if data_checksum == calculate_checksum(data[8:]):
                    data_seq, data_timestamp = struct.unpack('!LL', data[:8])
                    ack_sent_seq = data[8:].decode().split("seq=")[1]
                    sent_packets.pop(int(ack_sent_seq))

                    msg = f'Ack for {data[8:]}, seq={data_seq}>>>{bytes_read.decode()}'.encode() # ACK + file
                    datagram = struct.pack('!HHLL', PROXY_PORT, client_addr[1], seq_num, int(time.time() * 1000)) + msg
                    datagram_checksum = calculate_checksum(datagram)
                    datagram_with_checksum = struct.pack('!HHHH', PROXY_PORT, client_addr[1], len(datagram), datagram_checksum) + datagram
                    proxy_socket.sendto(datagram_with_checksum, client_addr)

                    sent_packets[seq_num] = datagram_with_checksum
                    seq_num+=1
                else:
                    pass

            except socket.timeout:
                print('Timeout occurred')

                # retransmit lost packets
                for packet_number, packet_data in sent_packets.items():
                    proxy_socket.sendto(packet_data, client_addr)
                    print(f'Retransmitted packet {packet_number}')

    proxy_socket.close()

def calculate_checksum(data):
    checksum_calc = 0
    for i in range(0, len(data), 2):
        word = (data[i] << 8) + (data[i + 1])
        checksum_calc += word
        if checksum_calc > 0xFFFF:
            checksum_calc = (checksum_calc & 0xFFFF) + 1
    return ~checksum_calc & 0xFFFF

def main():
    # Printing to the screen 'PROXY'
    msg = pyfiglet.figlet_format("PROXY")
    print(msg)

    tcp_communication() # Communicating only in TCP with client, because rudp isn't running

main()
