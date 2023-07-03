import os

import netaddr
from db_ops import read_ips_from_processed
from tqdm import tqdm

found_threats = []
our_ips = read_ips_from_processed()

def load_list_data():
    network_blocks = []

    directory = 'common_data/threat_lists'
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r') as f:
                for line in f:
                    if line.strip() not in network_blocks:
                        network_blocks.append(line.strip())

    #Uncomment to pollute test for checking
    #our_ips.append("176.111.174.2")

    return network_blocks

def check_against_lists(network_blocks):
    total_ip_count = len(our_ips)
    total_networks = len(network_blocks)

    pbar = tqdm(desc=f'Checking IPs against threat lists with {total_networks} networks...', total=total_ip_count, colour="#33fff9", bar_format='{l_bar}{bar} {n_fmt}/{total_fmt} | Elapsed: [{elapsed}]')
    
    # Create a list of netaddr IPNetwork objects for all the network blocks
    network_blocks = [netaddr.IPNetwork(network) for network in network_blocks] #type: ignore
    
    for ip in our_ips:
        # Check if the IP address is within any of the network blocks
        if any(netaddr.IPAddress(ip) in network for network in network_blocks):
            found_threats.append(ip)
        pbar.update(1)
    pbar.close()

def main():
    print("\nLoading data...\n")
    network_blocks = load_list_data()
    check_against_lists(network_blocks)
    
    print("Threats Found\n")
    print(found_threats)

if __name__ == "__main__":
    main()