
# Network Protocol Suite

This project simulates a network protocol suite in Python, providing a hands-on experience with fundamental protocols like DHCP, DNS, and HTTP. The application demonstrates communication between clients and servers using these protocols, incorporating error handling and latency optimization techniques.

## Components

The system includes the following:

1. **DHCP Server**: Assigns IP addresses to clients attempting to connect to the WiFi network.
2. **DNS Server**: Resolves domain names to IP addresses for clients within the network.
3. **Proxy Server**: Acts as an intermediary between the client and the application server, retrieving files requested by the client.
4. **Application Server**: Handles HTTP requests and delivers the requested images or files.
5. **Client**: Communicates with all servers to simulate a real-world user interaction.

## Features

### DHCP
- Clients broadcast `Discover` messages to locate available networks.
- The server assigns IP addresses via `Offer` messages.
- Final acknowledgment (`Ack`) establishes the connection.

### DNS
- Resolves domain names to IP addresses.
- Directs traffic to the correct server based on client requests.

### Application Layer
- Clients send HTTP `GET` requests to the Proxy Server for specific files.
- Proxy Server fetches files from the Application Server and relays them to clients.

## Enhancements
- Uses TCP for reliable data transmission, with acknowledgment and retransmission mechanisms.
- Dynamic congestion control to manage packet loss and latency.

## Running the Project

### Prerequisites
- Python 3.x installed
- Dependencies listed in `requirements.txt`

### Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/halelitzhaki/network-protocol-suite.git
   ```
2. Navigate to the project directory:
   ```bash
   cd network-protocol-suite
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the main script:
   ```bash
   python Final_project.py
   ```

### Notes
- The project requires super-user privileges at the start to handle network-level operations.
- All components are executed as subprocesses for seamless integration.

## Code Structure

1. **`Final_project.py`**: Automates the execution of all components.
2. **`Dhcp_server.py`**: Simulates the DHCP server functionality.
3. **`Dns.py`**: Implements DNS server capabilities.
4. **`Proxy.py`**: Acts as the intermediary server.
5. **`Server.py`**: Hosts files and processes client requests.
6. **`Client.py`**: Interacts with the servers and displays the received content.

## Bibliography
- Project resources and implementation references are listed in the document.

---

