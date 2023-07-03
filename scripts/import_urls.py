import os
import xml.etree.ElementTree as ET

import dns.resolver
from db_ops import create_candidates_table, insert_candidate_urls_to_db
from tqdm import tqdm
from util import get_working_dir

WORKINGDIR = get_working_dir()

# Create a new instance of the Resolver class
resolver = dns.resolver.Resolver()
# Define the DNS server to use
resolver.nameservers = ['1.1.1.1', '9.9.9.9']
# Create a cache for the resolver
cache = {}

# Define the directory containing the XML files
xml_dir = f'{WORKINGDIR}/data/xml.all.urls/'

#No duplicate domain lookups
seen_domains = {}
temp_transactions = []

def resolve_dns(domain):
    if domain in cache:
        return cache[domain]

    answers = resolver.resolve(domain)
    ip = str(answers[0])

    cache[domain] = ip
    return ip

def process_file(xml_file):
    #Extract year
    current_year = xml_file.replace(".xml", "")

    with tqdm(desc=f'Fetching IPs for {xml_file}', total=None, colour="#FF0000", bar_format='{l_bar}{bar} {n_fmt}/{total_fmt} | Elapsed: [{elapsed}]') as pbar:
        
        # Open the XML file for reading
        with open(os.path.join(xml_dir, xml_file), 'r') as file:
            # Parse the XML file and get the root element
            tree = ET.parse(file)
            root = tree.getroot()
            # Loop through each line in the file
            for url_elem in root.findall('.//url'):
                url = url_elem.get('href')
                #Don't re-run a domain you've already run:
                url = url.replace('http://', '') #type: ignore
                url = url.replace('https://', '') #type: ignore
                url = url.split('/')[0]
                try:
                    # Perform a DNS lookup to resolve the domain to an IP address
                    ip_address = resolve_dns(url) #type: ignore
                    temp_transactions.append((url, current_year, ip_address))
                except:
                    pass

                pbar.update(1)
    pbar.close()

def main():
    create_candidates_table()
    print("\n")
    for f in os.listdir(xml_dir): 
            if f.endswith('.xml'):
                process_file(f)

    insert_candidate_urls_to_db(temp_transactions)

if __name__ == "__main__":
    
    main()
