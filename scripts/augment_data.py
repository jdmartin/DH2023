import ast

from db_ops import do_ports_and_hosts_join
from priv_db_ops import (combine_port_count_and_service,
                         combine_port_count_by_year_and_service,
                         insert_port_years,
                         insert_ports_and_counts_to_private_db,
                         insert_ports_and_hosts_to_private_db, insert_services,
                         list_all_years, setup_asn_by_year,
                         setup_domains_by_year, setup_ports_by_year,
                         setup_tables, update_asn_by_year, update_asn_sums,
                         update_asn_years, update_domain_sums,
                         update_domain_years, update_domains_by_year,
                         update_port_sums, update_ports_by_year)
from rich import print
from rich.console import Console

console = Console()

joined = do_ports_and_hosts_join()


def process_port_counts(joined):
    temp_transactions = {}
    port_and_count_transactions = []

    for item in joined:
        for port in ast.literal_eval(item[8]):
            try:
                temp_transactions[port] += 1
            except KeyError:
                temp_transactions[port] = 1
                
    for key, value in temp_transactions.items():
        port_and_count_transactions.append((int(key), int(value), ""))

    insert_ports_and_counts_to_private_db(port_and_count_transactions)

def process_ports_by_year(joined):
    ports_sums = {}
    temp_port_year = {}
    
    #ensure outer keys in temp_port_year
    years = list_all_years()
    for year in years:
        temp_port_year[year] = {}

    for item in joined:
        for port in ast.literal_eval(item[8]):
            try:
                temp_port_year[item[1]][port] += 1
            except KeyError:
                temp_port_year[item[1]][port] = 1
            
            try:
                ports_sums[port] += 1
            except KeyError:
                ports_sums[port] = 1

    for key, value in temp_port_year.items():
        temp_key = "y" + str(key)
        for port, count in value.items():
            insert_port_years(temp_key, port, int(count))
    
    for key, value in set(ports_sums.items()):
        update_port_sums(key, value)

def process_asn_by_year(joined):
    asn_sums = {}
    temp_asn_year = {}
    
    #ensure outer keys in temp_asn_year
    years = list_all_years()
    for year in years:
        temp_asn_year[year] = {}

    for item in joined:
        try:
            temp_asn_year[item[1]][item[5]] += 1
        except KeyError:
            temp_asn_year[item[1]][item[5]] = 1
        
        try:
            asn_sums[item[5]] += 1
        except KeyError:
            asn_sums[item[5]] = 1

    for key, value in temp_asn_year.items():
        temp_key = "y" + str(key)
        for asn, count in value.items():
            update_asn_years(temp_key, asn, int(count))
    
    for key, value in set(asn_sums.items()):
        update_asn_sums(key, value)

def process_domain_by_year(joined):
    domains_sums = {}
    temp_domains_year = {}
    
    #ensure outer keys in temp_asn_year
    years = list_all_years()
    for year in years:
        temp_domains_year[year] = {}

    for item in joined:
        try:
            temp_domains_year[item[1]][item[3]] += 1
        except KeyError:
            temp_domains_year[item[1]][item[3]] = 1
        
        try:
            domains_sums[item[3]] += 1
        except KeyError:
            domains_sums[item[3]] = 1

    for key, value in temp_domains_year.items():
        temp_key = "y" + str(key)
        for host, count in value.items():
            update_domain_years(temp_key, host, int(count))
    
    for key, value in set(domains_sums.items()):
        update_domain_sums(key, value)

def process_services():
    temp_services = []
    with open('common_data/services', 'r') as f:
        for line in f:
            port = int(line.split(';')[0].strip())
            category = line.split(';')[1].strip()
            definition = line.split(';')[2].strip()
            temp_services.append((port, category, definition))
    
    insert_services(temp_services)

def main():
    setup_tables() #Creates tables
    insert_ports_and_hosts_to_private_db(joined)    #populates results
    process_port_counts(joined)                     #populates ports_counts
    setup_ports_by_year()                           #creates table to hold port counts by year
    update_ports_by_year()                          #add year columns
    process_ports_by_year(joined)                   #now, break things down by year    
    process_services()                              #populates services
    combine_port_count_and_service()                #updates ports_counts with service defs
    setup_asn_by_year()                             #Let's keep track of the ASN info by year, too.
    update_asn_by_year()                            #add year columns
    process_asn_by_year(joined)                     #populates asn_by_year
    setup_domains_by_year()                         #Count domain usage (well, 'host') by year.
    update_domains_by_year()                        #add year columns
    process_domain_by_year(joined)                  #populates domains_by_year
    combine_port_count_by_year_and_service()        #add service definitions to ports_by_year.

    print("\nAll done!\n")


if __name__ == "__main__":
    main()