##
# dhcp_server.py
# This code represents the dhcp server, that connecting clients to the local network
#
# DHCP Flow:
# 1. Getting DHCP Discover from client
# 2. Sending DHCP Offer to client
# 3. Getting DHCP Request from client
# 4. Sending DHCP Ack to client
##

from time import sleep # For pausing the server after getting a dhcp-request
from scapy.all import * # For making dhcp packets, and communicating
import random # For setting client's ip
import pyfiglet # For printing big fonts to the screen

from scapy.layers.dhcp import DHCP, BOOTP
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether

server_mac = "12:34:56:78:90:12" # Server's mac
server_ip = "192.168.0.1" # Server's and Router's ip
dns_ip = "192.168.0.2" # Domain Name Server's ip
offered_ip = "192.168.0." + str(random.randint(3, 10)) # Client's ip
broadcast_mac = "ff:ff:ff:ff:ff:ff"
broadcast_ip = "255.255.255.255"

# Printing to the screen 'DHCP'
msg = pyfiglet.figlet_format("DHCP")
print(msg)

def dhcp_offer(pkt):
    print("Captured DHCP Discover packet from: " + pkt[Ether].src + " - " + pkt[IP].src)
    print("Sent DHCP Offer packet to: " + broadcast_mac)

    # Build DHCP offer packet
    dhcp_offer = Ether(src=server_mac, dst=pkt[Ether].src) / \
                 IP(src=server_ip, dst=broadcast_ip) / \
                 UDP(sport=67, dport=68) / \
                 BOOTP(op=2, siaddr=server_ip, yiaddr=offered_ip, ciaddr=pkt[IP].src) / \
                 DHCP(options=[("message-type", "offer"),
                               ("server_id", server_ip),
                               ("subnet_mask", "255.255.255.0"),
                               ("router", server_ip),
                               ("name_server", dns_ip),
                               ("lease_time", 3600),
                               "end"])

    sleep(1) # Letting client to start his sniff function

    sendp(dhcp_offer, iface="enp0s1") # Send the DHCP offer packet on layer 2 (link)

    sniff(filter="udp and (port 67 or 68)", prn=dhcp_ack, iface="enp0s1", count=1) # Waiting for DHCP Request from client

def dhcp_ack(pkt):
    if pkt[DHCP].options[0][1] == 3:
        print("Captured DHCP Request packet from: " + pkt[Ether].src + " - " + pkt[IP].src)
        dhcp_ack = Ether(src=server_mac, dst=pkt[Ether].src) / \
                   IP(src=server_ip, dst=offered_ip) / \
                   UDP(sport=67, dport=68) / \
                   BOOTP(op=2, yiaddr=pkt[IP].src, siaddr=server_ip) / \
                   DHCP(options=[("message-type", "ack"),
                                       ("server_id", server_ip),
                                       ("subnet_mask", "255.255.255.0"),
                                       ("router", server_ip),
                                       ("name_server", dns_ip),
                                       ("lease_time", 3600),
                                       "end"])
        
        sleep(1) # Letting client to start his sniff function

        print("Sent DHCP Ack packet to: " + dhcp_ack[Ether].src + " - " + dhcp_ack[IP].src)
        sendp(dhcp_ack) # Send the DHCP ACK packet on layer 2 (link)
        
# Listening to clients that want to connect
sniff(filter="udp and (port 67 or 68)", prn=dhcp_offer, iface="enp0s1", count=1)
