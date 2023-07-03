import json

import shodan
from db_ops import (create_indices, insert_host_result_to_db,
                    insert_ports_result_to_db, read_candidates_from_db,
                    read_ips_from_processed)
from rich import print
from rich.console import Console
from tqdm import tqdm
from util import get_shodan_key, get_working_dir

console = Console()

#API Reference: https://developer.shodan.io/api
SHODAN_API_KEY = get_shodan_key()
api = shodan.Shodan(SHODAN_API_KEY)

WORKINGDIR = get_working_dir()
targets = {} #site: ip
host_metadata = [] # id, ip, host, isp, hostnames, count
ports_metadata = [] # id, ports
host_counts = {} #site: int
seen_ip_addrs = [] #Because we are using site names, this helps to make sure we don't lookup same IP twice.

def load_the_data():
    #Populate seen_ip_addrs with already processed ips
    temp_seen = read_ips_from_processed()
    for item in temp_seen:
        seen_ip_addrs.append(item)

    #Get Candidate data from abstracts
    temp_candidates = read_candidates_from_db()
    for item in temp_candidates:
        targets[item[0]] = item[1]

def fetch_the_data():
    number_of_steps = len(set(targets.items()))
    i = 1
    id_counter = 1
    info_dict = {}

    while i <= number_of_steps:
        pbar = tqdm(desc='Fetching from Shodan API', total=number_of_steps, colour="#00FF00", bar_format='{l_bar}{bar} {n_fmt}/{total_fmt} | Elapsed: [{elapsed}]')

        #Do the lookups and generate the db
        for host, item in sorted(set(targets.items())):
            if item not in info_dict:
                #Let's make sure there's a count to insert
                try:
                    host_counts[host] += 1
                except KeyError:
                    host_counts[host] = 1

                #Now, let's try the API:
                try:
                    info = api.host(item)
                    host_metadata.append((id_counter, info['ip_str'], host, info['isp'], info['asn'], str(len(info['hostnames'])), str(info['hostnames']), host_counts[host], info['last_update']))
                    ports_metadata.append((id_counter, str(sorted(info['ports']))))
                    id_counter += 1
                    info_dict[item] = info
                except Exception:
                    pass

            seen_ip_addrs.append(item)
            i+=1
            pbar.update(1)
        pbar.close()
    
    for host, info in info_dict.items():
        json_object = json.dumps(info, indent=4)
        with open(f"{WORKINGDIR}/data/shodan/{host}.json", "w+") as f:
            f.write(json_object)

def store_the_data():
    insert_host_result_to_db(host_metadata)
    insert_ports_result_to_db(ports_metadata)

def main():
    console.clear()
    load_the_data() #Get data from file in data/ (currently hard-coded)
    fetch_the_data() #Get data from Shodan API
    store_the_data() #Insert data to db.
    create_indices() #Creating indices after load is faster.

if __name__ == "__main__":
    main()