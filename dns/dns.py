##
# dns.py
# This code represents the domain name server, that sending to the clients domains' ip addresses
##

from scapy.all import * # For making dns packets, and communicating
import pyfiglet # For printing big fonts to the screen


from scapy.layers.dns import DNS, DNSRR, DNSQR
from scapy.layers.inet import IP, UDP


web_app_domain = "WebApplication.com" # Our Website's domain
web_app_ip = "127.0.0.1"
google_dns = "8.8.8.8"

# Printing to the screen 'DNS'
msg = pyfiglet.figlet_format("DNS")
print(msg)


def dns_server(pkt):
    print("Captured DNS Query from: " + pkt[IP].src)
    requested_web = pkt[DNS].qd.qname # Extract the requested website's domain fom DNS query in the packet
    if str(requested_web).find(web_app_domain) == -1:
        domain = str(requested_web)[2:-1]
        dns_request = IP(src=pkt[IP].dst, dst=google_dns) / UDP(sport=1024, dport=53) / DNS(id=1, rd=1, qd=DNSQR(qname=domain,qtype="A"))
        packet = sr(dns_request)[0][1] # not working
        print(packet)

    else:
        response = IP(src=pkt[IP].dst, dst=pkt[IP].src) / \
                   UDP(sport=53, dport=pkt[UDP].sport) / \
                   DNS(id=pkt[DNS].id, qd=pkt[DNS].qd, aa=1, rd=0, qr=1, qdcount=1, ancount=1, nscount=0, arcount=0) / \
                   DNSRR(type='A', rrname=requested_web, ttl=60, rdlen=4, rdata=web_app_ip)
        print("Sent DNS Response to: " + pkt[IP].src + ", with the requested ip address: " + web_app_ip)

        send(response)

# Listening to clients in the local network, that want to get domains' ip addresses
sniff(filter="udp and (port 53) and (dst host 192.168.0.2)", prn=dns_server, iface="enp0s1", count=1)
