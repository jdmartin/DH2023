import json
import os
import socket

from priv_db_ops import (insert_cve_defs, insert_vulns, setup_vulns,
                         update_cve_sums)
from tqdm import tqdm
from util import get_working_dir

WORKINGDIR = get_working_dir()

def get_list_of_json_files():
    json_dir = f"{WORKINGDIR}/data/shodan/"
    list_of_files = []
    for filename in os.listdir(json_dir):
        if filename.endswith(".json"):
            list_of_files.append(filename)
    
    return list_of_files

#This function exists because plotly.express chose violence when displaying data in hovertemplate.
def wrap_text(text, wrap_length):
    words = text.split(' ')
    new_text = ''
    line_length = 0
    for word in words:
        if len(word) > wrap_length:
            new_text += word[:wrap_length] + '<br>' + wrap_text(word[wrap_length:], wrap_length)
            line_length = len(word[wrap_length:])
        elif line_length + len(word) + 1 <= wrap_length:
            if new_text:
                new_text += ' '
            new_text += word
            line_length += len(word) + 1
        else:
            new_text += '<br>' + word
            line_length = len(word)
    return new_text

def load_all_vulns():
    processed_ips = []
    transactions = []
    cve_def_transactions = []
    processed_vulns_by_ip = {}
    cve_counts = {}
    list_of_files = get_list_of_json_files()

    pbar = tqdm(desc='Loading Vulnerability Data for our Hosts...', total=len(list_of_files), colour="#FF0000", bar_format='{l_bar}{bar} {n_fmt}/{total_fmt} | Elapsed: [{elapsed}]')
    
    # Loop over the JSON files in the directory
    for filename in list_of_files:
        is_database = 0
        is_self_signed = 0
        is_starttls = 0
        is_cloud = 0
        is_vpn = 0
        is_eol_product = 0
        is_cdn = 0
        is_eol_os = 0
        with open(f"{WORKINGDIR}/data/shodan/{filename}", "r") as f:
            data = json.load(f)

            # Convert the integer to a packed binary format in bytes
            ip_binary = int.to_bytes(data["ip"], 4, byteorder='big')
            # Convert the binary format to a string representation of the IP address
            ip_address = socket.inet_ntoa(ip_binary)
            
            # Check if the ip_address key is in processed_vulns_by_ip, and add it if it's not
            if ip_address not in processed_vulns_by_ip:
                processed_vulns_by_ip[ip_address] = []

            try:    
                # Access the "summary", "cvss", and "references" values for each item in the "vulns" list
                for vuln in data["vulns"]:
                    for vuln in data["data"]:
                        if "vulns" in vuln:
                            for sub_key in vuln["vulns"]:
                                summary = vuln["vulns"][sub_key]["summary"]
                                cvss = vuln["vulns"][sub_key]["cvss"]
                                references = vuln["vulns"][sub_key]["references"]
                                tags = data["tags"]

                                #Make sure there's something in references
                                if references is None:
                                    references = ""

                                #Make sure there's some number, even if it's 0.0
                                if cvss is None:
                                    cvss = 0.0
                                
                                #Make sure the summary isn't too long, so it can be read on the plot:
                                new_summary = wrap_text(summary, 120)

                                #Make sure refs aren't too long:
                                new_references = "<br>"
                                for ref in references[:5]:
                                    new_references += ref + "<br>"

                                #Populate tags list
                                for tag in tags:
                                    match tag:
                                        case 'database':
                                            is_database = 1
                                        case 'self-signed':
                                            is_self_signed = 1
                                        case 'starttls':
                                            is_starttls = 1
                                        case 'cloud':
                                            is_cloud = 1 
                                        case 'vpn':
                                            is_vpn = 1
                                        case 'eol-product':
                                            is_eol_product = 1
                                        case 'cdn':
                                            is_cdn = 1
                                        case 'eol-os':
                                            is_eol_os = 1

                                if sub_key not in processed_vulns_by_ip[ip_address]:
                                    processed_vulns_by_ip[ip_address].append(sub_key)
                                    transactions.append((ip_address, sub_key, is_database, is_self_signed, is_starttls, is_cloud, is_vpn, is_eol_product, is_cdn, is_eol_os))
                                    cve_def_transactions.append((sub_key, cvss, new_summary, new_references))

                                    try:
                                        cve_counts[sub_key] += 1
                                    except KeyError:
                                        cve_counts[sub_key] = 1
                                
                                processed_ips.append(ip_address)
            except KeyError:
                pass

        pbar.update(1)
    pbar.close()
    print("\nInserting Data... sit tight!")
    insert_vulns(transactions)
    insert_cve_defs(cve_def_transactions)
    for key, value in cve_counts.items():
        update_cve_sums(key, value)
    

if __name__ == "__main__":
    setup_vulns()
    load_all_vulns()