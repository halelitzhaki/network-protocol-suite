##
# server.py
# This code represents the server, that holds the requested files and communicates with the proxy server
##

import socket # For communicating with the proxy server
import pyfiglet # For printing big fonts to the screen
import os # For getting the file's size
import tqdm as tqdm # For showing the file's sending process on the screen

PORT = 80 # HTTP server port
ADDRESS = "127.0.0.1"
BUFFER_SIZE = 4096 # Packets' size that will be sendes and received between the server and the proxy
SEPARATOR = "<SEPARATOR>" # For splitting strings
file_direct = 'pictures/' # For openning the files from their directory

# Printing to the screen 'SERVER'
msg = pyfiglet.figlet_format("SERVER")
print(msg)

# Setting up the server
listening_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Open TCP socket
listening_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listening_sock.bind((ADDRESS, PORT)) # Determine that the socket's source port, will be http port (80)
listening_sock.listen(1) # Waiting for the proxy to connect
print(f'Waiting to proxy on port {str(PORT)}')

proxy_sock, proxy_addr = listening_sock.accept() # Proxy got connected to the server
print(f'Proxy connected successfully. Address - {proxy_addr[0]}, Port - {str(proxy_addr[1])}')

file_to_send = proxy_sock.recv(BUFFER_SIZE) # Getting the HTTP Get message from proxy
print('Got HTTP Get message from proxy')

start, end = file_to_send.decode().split(" HTTP/1.1") # Splitting the message
start, file_name = start.split("/") # Getting the file's name from the splitted message

response = f'HTTP/ 200 OK\r\nContent-Type: {file_name}\r\n' # Creating HTTP Response to the client
proxy_sock.send(response.encode()) # Sending the response to proxy
print('Sent HTTP response to proxy')

file_size = os.path.getsize(file_direct+file_name) # Getting file's size
progress = tqdm.tqdm(range(file_size), f"Sending {file_name}", unit="B", unit_scale=True, unit_divisor=1024) # Printing to the screen the progress

# Sending the file
with open(file_direct+file_name, "rb") as f: # Open the client's requested file
    while True:
        bytes_read = f.read(BUFFER_SIZE) # Reading the BUFFER_SIZE's (4096) bytes from the file
        if not bytes_read:
            break
        proxy_sock.sendall(bytes_read) # Sending the read bytes to proxy
        progress.update(len(bytes_read)) # Updating the progress bar on the screen
    f.close() # Closing the file safely

proxy_sock.close() # Closing the connection with the proxy
listening_sock.close() # Closing the server's socket (shutting down the server)
