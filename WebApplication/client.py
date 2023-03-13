##
# client.py
# This code represents the client, that comuunicating with all of the servers in the project (the main code).
##

import socket # For communicating with the proxy server
from time import sleep # For pausing the client after getting a dhcp-offer
from scapy.all import * # For making dhcp and dns packets, and communicating
import random # For creating a source port for the client in the dns part
import struct # For creating packet in the rudp part
from PIL import Image # For making the picture show on the screen
import pyfiglet # For printing big fonts to the screen
from termcolor import colored # For printing colored strings to screen
from pyfiglet import Figlet # For printing big fonts to the screen

from scapy.layers.dhcp import DHCP, BOOTP
from scapy.layers.dns import DNSQR, DNS, DNSRR
from scapy.layers.inet import UDP, IP, TCP
from scapy.layers.l2 import Ether

SERVER_PORT = 30674 # Halel's id last 3 digits
CLIENT_PORT = 20069 # Ori's id last 3 digits
BUFFER_SIZE = 4096 # Packets' size that will be sendes and received between the client and the proxy
SEPARATOR = "<SEPARATOR>" # For splitting strings

PICTURES = "[1] - Sunset\n[2] - Cute Puppy\n[3] - Cyber Attack\n[4] - Ariel University\n[5] - Peace Sign\n[6] - Red Heart\n\nYour choice: " # Client msg
files = ["sunset.jpg", "cute puppy.jpg", "cyber attack.jpeg", "ariel university.jpg", "peace sign.png", "red heart.png"] # files list to send to server

def main():
    msg = pyfiglet.figlet_format("Welcome!")
    print(msg)
    f=input("This is Halel's & Ori's final project\n\nWe highly recommend to open this window in full size :)\n\nPress any key to start...")

    dhcp_part()

# ____  _   _  ____ ____
#|  _ \| | | |/ ___|  _ \
#| | | | |_| | |   | |_) |
#| |_| |  _  | |___|  __/
#|____/|_| |_|\____|_|

def dhcp_part():
    print("\nConnecting to a close network...")

    # Build DHCP Discover packet
    dhcp_discover = Ether(dst="ff:ff:ff:ff:ff:ff")/ \
                    IP(src="0.0.0.0",dst="255.255.255.255")/ \
                    UDP(sport=68,dport=67)/ \
                    BOOTP()/ \
                    DHCP(options=[("message-type","discover"),"end"])

    sendp(dhcp_discover, iface="enp0s1") # Sending Discover packet on layer 2 (link)
    sniff(filter="udp and (port 67 or 68)", prn=dhcp_request_func, iface="enp0s1", count=1) # Waiting for DHCP Offer from server

def dhcp_request_func(pkt):
    if pkt[DHCP].options[0][1] == 2: # Check if the packet is a DHCP Offer
        # Build DHCP Request packet
        dhcp_request = Ether(dst=pkt[Ether].src)/IP(src="0.0.0.0",dst=pkt[IP].src)/\
                       UDP(sport=68,dport=67)/\
                       BOOTP(chaddr=pkt[BOOTP].chaddr, xid=pkt[BOOTP].xid)/\
                       DHCP(options=[("message-type","request"),('requested_addr', pkt[BOOTP].yiaddr),"end"])

        sleep(1) # Waiting for server to start his sniff function
        sendp(dhcp_request) # Sending Request packet on layer 2 (link)

        sniff(filter="udp and (port 67 or 68)", prn=dhcp_ack, iface="enp0s1", count=1) # Waiting for DHCP Ack from server

def dhcp_ack(pkt):
    # Print to the screen the ip that the DHCP server sent.
    print("\n\n[-] Yout personal computer's ip address in the local network : " + pkt[IP].dst + "\n")

    dns_part(pkt[IP].dst, pkt[DHCP].options[4][1])

#  ____  _   _ ____
# |  _ \| \ | / ___|
# | | | |  \| \___ \
# | |_| | |\  |___) |
# |____/|_| \_|____/

def dns_part(pc_ip, dns_ip):
    user_choice = input("Please enter your choice, according to the following options:\n"
                          "[1] To connect to our web application\n[2] To get another website ip\nYour choice: ")

    if user_choice == '1':
        requested_web = "WebApplication.com"
        # Build DNS Query packet
        dns_request = IP(src=pc_ip, dst=dns_ip) / UDP(sport=random.randint(30000, 60000), dport=53) / DNS(id=1, rd=1, qd=DNSQR(qname=requested_web, qtype="A"))
        send(dns_request)  # Send DNS Query [acket on layer 3 (network)

        print("Conneting to WebApplication.com")
        # Printing to screen 'WebApplication.com'
        f = Figlet(font='standard', width=100)
        print(colored(f.renderText(requested_web), 'green'))
        
        sniff(filter="udp and (port 53) and (dst host " + pc_ip + ")", prn=web_part, iface="enp0s1", count=1)  # Waiting for DNS Response packet from server
    else:
        requested_web = input("\nEnter website's domain: \n")
        # Build DNS Query packet
        dns_request = IP(src=pc_ip, dst=dns_ip) / UDP(sport=random.randint(30000, 60000), dport=53) / DNS(id=1, rd=1, qd=DNSQR(qname=requested_web, qtype="A"))
        send(dns_request)  # Send DNS Query [acket on layer 3 (network)
        packet = sniff(filter="udp and (port 53) and (dst host " + pc_ip + ")", iface="enp0s1", count=1, timeout=3)  # Waiting for DNS Response packet from server
        if not packet:
            print("Couldn't get the ip address :(")
        else:
            print("The requested domain's ip is - " + packet[DNSRR].rdata)
        exit()


# __        __   _       _                _ _           _   _
# \ \      / /__| |__   / \   _ __  _ __ | (_) ___ __ _| |_(_) ___  _ __    ___ ___  _ __ ___
#  \ \ /\ / / _ \ '_ \ / _ \ | '_ \| '_ \| | |/ __/ _` | __| |/ _ \| '_ \  / __/ _ \| '_ ` _ \
#   \ V  V /  __/ |_) / ___ \| |_) | |_) | | | (_| (_| | |_| | (_) | | | || (_| (_) | | | | | |
#    \_/\_/ \___|_.__/_/   \_\ .__/| .__/|_|_|\___\__,_|\__|_|\___/|_| |_(_)___\___/|_| |_| |_|
#                            |_|   |_|


def web_part(pkt):
    web_ip = pkt[DNSRR].rdata
    client_ip = pkt[IP].dst
    tcp(client_ip, web_ip)

def tcp(client_ip, web_ip):
    choice = input("Choose picture to download.\nEnter your choice according to the following options:\n"+PICTURES)

    file_name = files[0]
    if choice == "1":
        file_name = files[0]
    elif choice == "2":
        file_name = files[1]
    elif choice == "3":
        file_name = files[2]
    elif choice == "4":
        file_name = files[3]
    elif choice == "5":
        file_name = files[4]
    elif choice == "6":
        file_name = files[5]
    else:
        print("Invalid input!!, choosing alternative picture - sunset")

    # Build HTTP Get
    http_request = "GET /" + file_name + " HTTP/1.1\r\nHost: " + str(web_ip) + ":" + str(SERVER_PORT) +"\r\n\r\n"

    # Connecting to Proxy server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Open TCP socket
    sock.bind(('localhost', CLIENT_PORT)) # Determine that the socket's source port, will be the requested port from the instructions
    sock.connect((web_ip, SERVER_PORT)) # Connecting socket to server
    sock.send(http_request.encode()) # Sending HTTP Get

    response = sock.recv(BUFFER_SIZE).decode() # Getting HTTP response from server, with the file's name
    start, end = response.split("Type: ") # Splitting the response
    file_name = end[:-2] # Getting file's name

    with open(file_name, "wb") as f: # Openning the file on the project's main directory, to store in it the received bytes
        while True:
            bytes_read = sock.recv(BUFFER_SIZE) # Getting the file's data (in bytes)
            if not bytes_read:
                break
            f.write(bytes_read) # Writing the file's data to the file on the project's main directory
        f.close() # Closing the file safely
        sock.close() # Closing the connection with the proxy

    user_choice = input("\nPicture was succefully downloaded to the project's main directory :)\n\n"
                        "Enter your choice according to the following options:\n[1] - Show the picture\n[2] - EXIT\n\nYour choice: ")
    if user_choice == '1':
        print("\nShowing Picture...\n")
        img = Image.open(file_name)
        img.show()

    msg = pyfiglet.figlet_format("Goodbye!")
    print(msg)


## NOT WORKING!!
## NOT WORKING!!
## NOT WORKING!!
def rudp(client_ip, web_ip):
    choice = input("Choose picture to download.\nEnter your choice according to the following options:\n" + PICTURES)

    file_name = files[0]
    if choice == "1":
        file_name = files[0]
    elif choice == "2":
        file_name = files[1]
    elif choice == "3":
        file_name = files[2]
    elif choice == "4":
        file_name = files[3]
    elif choice == "5":
        file_name = files[4]
    elif choice == "6":
        file_name = files[5]
    else:
        print("Invalid input!!, choosing alternative picture - sunset")

    # Build HTTP3 Get
    http_request = f'GET / {file_name} HTTP/3\r\nHost: {web_ip}:{SERVER_PORT}\r\n\r\n'.encode()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Create UDP socket
    sock.bind((client_ip, CLIENT_PORT)) # Determine that the socket's source port, will be the requested port from the instructions

    seq_num = 0
    sent_packets = {}

    datagram = struct.pack('!HHLL', 0, SERVER_PORT, seq_num, int(time.time() * 1000)) + http_request
    datagram_checksum = calculate_checksum(datagram)
    datagram_with_checksum = struct.pack('!HHHH', 0, SERVER_PORT, len(datagram), datagram_checksum) + datagram
    sock.sendto(datagram_with_checksum, (SERVER_PORT, web_ip)) # Send http get

    sent_packets[seq_num] = datagram_with_checksum
    seq_num+=1

    with open(file_name, "wb") as f:
        while True:
            try:
                data = sock.recv(BUFFER_SIZE)
                header = struct.unpack('!HHHH', data[:8])
                data_checksum = header[3]
                if data_checksum == calculate_checksum(data[8:]):
                    data_seq, data_timestamp = struct.unpack('!LL', data[:8])
                    start, end = data[8:].decode().split("seq=")
                    seq, bytes_read = end.split(">>>")
                    if not bytes_read:
                        break
                    sent_packets.pop(int(seq))
                    f.write(bytes_read)

                    msg = f'Ack for {data[8:]}, seq={data_seq}'.encode()  # ACK
                    datagram = struct.pack('!HHLL', 0, SERVER_PORT, seq_num, int(time.time() * 1000)) + msg
                    datagram_checksum = calculate_checksum(datagram)
                    datagram_with_checksum = struct.pack('!HHHH', 0, SERVER_PORT, len(datagram), datagram_checksum) + datagram
                    sock.send(datagram_with_checksum)

                    sent_packets[seq_num] = datagram_with_checksum
                    seq_num += 1
                else:
                    pass

            except socket.timeout:
                print('Timeout occurred')

                # Retransmit lost packets
                for packet_number, packet_data in sent_packets.items():
                    sock.send(packet_data)
                    print(f'Retransmitted packet {packet_number}')
    sock.close()


def calculate_checksum(data):
    if len(data) % 2 == 1:
        data += b'\x00'
    words = struct.unpack('>' + str(len(data) // 2) + 'H', data)
    checksum = sum(words)
    while checksum >> 16:
        checksum = (checksum & 0xFFFF) + (checksum >> 16)
    return ~checksum & 0xFFFF

main()
