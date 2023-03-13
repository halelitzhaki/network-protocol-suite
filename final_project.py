##
# Final_project.py
# This code represents the program's runner, that runs all the programs in once
##

import subprocess
import getpass

# Project's programs paths
programs = [
    'dns/dns.py',
    'dhcp/dhcp_server.py',
    'WebApplication/servers/server.py',
    'WebApplication/servers/proxy.py',
    'WebApplication/client.py',
]

# Getting user's super-user password, for the programs that need to be run as super-user
superuser_password = getpass.getpass(prompt='Enter your super-user password: ')

# Running all the programs
for program in programs:
    print(f'running {program}') # Printing the program's name that is running now
    sudo_command = ['sudo', '-S', 'gnome-terminal', '--', 'bash', '-c', f'python3 {program}; exec bash'] # Building "sudo command"
    subprocess.Popen(sudo_command, stdin=subprocess.PIPE).communicate(input=f'{superuser_password}\n'.encode()) # Running program in separate window
    # with super-user password, that is filled in automatically
