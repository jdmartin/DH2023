import json
import os

from priv_db_ops import (setup_domains_by_loc, update_domain_locs,
                         update_domain_locs_totals)
from util import get_working_dir

WORKINGDIR = get_working_dir()
directory_path = f"{WORKINGDIR}/data/shodan"
transactions = []

def process_domain_by_loc():
    for filename in os.listdir(directory_path):
        candidate_ip = os.path.splitext(filename)[0]
        with open(f"{WORKINGDIR}/data/shodan/{filename}", "r") as f:
            data = json.load(f)
            transactions.append((data["latitude"], data["longitude"], data["city"], data["region_code"], data["country_name"], candidate_ip))

def main():
    setup_domains_by_loc()
    process_domain_by_loc()
    update_domain_locs(transactions)
    update_domain_locs_totals()


if __name__ == "__main__":
    main()
