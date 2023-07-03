from db_ops import read_candidates_with_years_from_db
from priv_db_ops import (list_all_years, populate_tld, setup_tld_by_year,
                         update_tld_by_year, update_tld_countries,
                         update_tld_sums, update_tld_years)

list_of_domains = read_candidates_with_years_from_db()
dict_of_countries = {}
seen_domains_dict = {}

def add_country_data():
    with open('common_data/tld.csv', 'r') as f:
        for line in f:
            tld = line.split(',')[0]
            country = line.split(',')[1]
            update_tld_countries(tld,country)

#Util to get the TLD and filter as needed
def get_the_tld(domain):
    tld = domain.split('.')[-1]

    return tld

#Generate the dictionary of seen domains with counts
def generate_dictionary():
    for domain in list_of_domains:
        tld = get_the_tld(domain[0])
        try:
            seen_domains_dict[tld] += 1
        except KeyError:
            seen_domains_dict[tld] = 1
        populate_tld(tld)

#Check domains in dict against country list and count

def process_tld_by_year():
    tld_overall = {}
    temp_tld_year = {}
    
    #ensure outer keys in temp_asn_year
    years = list_all_years()
    for year in years:
        temp_tld_year[year] = {}

    for item in list_of_domains:
        tld = get_the_tld(item[0])
        try:
            temp_tld_year[item[1]][tld] += 1
        except KeyError:
            temp_tld_year[item[1]][tld] = 1
        
        try:
            tld_overall[tld] += 1
        except KeyError:
            tld_overall[tld] = 1

    for key, value in temp_tld_year.items():
        temp_key = "y" + str(key)
        for tld, count in value.items():
            update_tld_years(temp_key, tld, int(count))

    for key, value in set(tld_overall.items()):
        update_tld_sums(key, value)

if __name__ == "__main__":
    setup_tld_by_year()
    update_tld_by_year()
    generate_dictionary()
    process_tld_by_year()
    add_country_data()