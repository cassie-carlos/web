# Usage: python3 nmapParser.py <NmapResultsFile>

import re 
import sys

def parse_nmap_results(filename): 
    ip_ports = {} 
    current_ip = None

    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
	    # Match IP addresses
            ip_match = re.match(r'Nmap scan report for (\d+\.\d+\.\d+\.\d+)', line)
            if ip_match:
                current_ip = ip_match.group(1)
                ip_ports[current_ip] = []
                continue
		
		# Match open ports
            port_match = re.match(r'(\d+)/udp\s+open', line)
            if port_match and current_ip:
                ip_ports[current_ip].append(port_match.group(1))

    output_filename = f"{filename}_OpenPorts.txt"
    with open(output_filename, 'w', encoding='utf-8') as output_file:
        for ip, ports in ip_ports.items():
    	    if ports:
                output_file.write(f"{ip}: \n{', '.join(ports)}\n\n")
            

    print(f"Results saved to {output_filename}")

if __name__ == "__main__":
    parse_nmap_results(sys.argv[1])
