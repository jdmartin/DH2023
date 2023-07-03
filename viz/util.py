import sqlite3

import pandas as pd
from dotenv import dotenv_values

config = dotenv_values(".env")

def get_shodan_key():
    SHODAN_API_KEY = config["SHODAN_API_KEY"]
    return SHODAN_API_KEY

def get_working_dir():
    WORKINGDIR = config["WORKINGDIR"]
    return WORKINGDIR

def get_pretty_hosts_count():
    dir = get_working_dir()
    # Connect to SQLite database
    conn = sqlite3.connect(f'file:{dir}/dbs/private.db?mode=ro', uri=True)

    num_hosts_query = """
        SELECT COUNT(*) AS num_hosts 
        FROM results;
    """
    df_hosts = pd.read_sql_query(num_hosts_query, conn)
    pretty_hosts_count = format(df_hosts['num_hosts'][0], ",")

    conn.close()
    return pretty_hosts_count

def get_pretty_links_count():
    dir = get_working_dir()
    # Connect to SQLite database
    conn = sqlite3.connect(f'file:{dir}/dbs/private.db?mode=ro', uri=True)

    num_links_query = """
        SELECT SUM(row_sum) AS num_links 
        FROM domains_by_year;
    """
    df_hosts = pd.read_sql_query(num_links_query, conn)
    pretty_links_count = format(df_hosts['num_links'][0], ",")

    conn.close()
    return pretty_links_count

def get_all_cve_years_and_counts():
    dir = get_working_dir()
    # Connect to SQLite database
    conn = sqlite3.connect(f'file:{dir}/dbs/private.db?mode=ro', uri=True)

    cve_age_query = """
        SELECT CVE, count 
        FROM cve_counts;
    """
    cve_ages = pd.read_sql_query(cve_age_query, conn)
    # Split the first column on the "-" character
    cve_ages[['col1', 'year', 'col3']] = cve_ages['CVE'].str.split('-', expand=True)
    result = cve_ages.groupby('year')['count'].sum().to_dict()

    #NOTE: Just learn to do this in one op, and stop being silly.
    df = pd.DataFrame.from_dict(result, orient='index', columns=['count'])
    df.index.name = 'year'
    df.reset_index(inplace=True)
    
    conn.close()
    return df