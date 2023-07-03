import ast
import sqlite3

from util import get_working_dir

#Create the disk database (for backups) and a cursor to handle transactions.
WORKINGDIR = get_working_dir()
disk_con = sqlite3.connect(f"./{WORKINGDIR}/dbs/sqlite3.db")
disk_con.row_factory = sqlite3.Row
disk_cur = disk_con.cursor()

#  __  __      __
#  \ \/ /___  / /___
#   \  / __ \/ / __ \
#   / / /_/ / / /_/ /
#  /_/\____/_/\____/
#

disk_cur.execute("PRAGMA synchronous = OFF;")
disk_cur.execute("PRAGMA cache_size = 100000;")
disk_cur.execute("PRAGMA journal_mode = MEMORY;")
disk_cur.execute("PRAGMA temp_store = MEMORY;")  

#Create the Database and Tables
def create_db_and_tables():
    #If we're touching this function, it's because we're re-processing the data set.
    disk_cur.execute("DROP TABLE IF EXISTS hosts;")
    disk_cur.execute("DROP TABLE IF EXISTS ports;")
    disk_cur.execute("CREATE TABLE IF NOT EXISTS hosts(`id`, `ip`, `host`, `isp`, `asn`, `num_hostnames`, `hostnames`, `count_seen`, `shodan_updated` DATETIME);")
    disk_cur.execute("CREATE TABLE IF NOT EXISTS ports(`id`, `ports_seen`);")
    disk_cur.execute("VACUUM;")

def create_candidates_table():
    disk_cur.execute("DROP TABLE IF EXISTS candidates;")
    disk_cur.execute("CREATE TABLE IF NOT EXISTS candidates(`domain`, `year`, `ip`);")
    disk_cur.execute("VACUUM;")

def create_indices():
    disk_cur.execute("CREATE INDEX IF NOT EXISTS hosts_idx ON hosts(id);")
    disk_cur.execute("CREATE INDEX IF NOT EXISTS ports_idx ON ports(id);")

#Insert results
def insert_host_result_to_db(data):
    statement = "INSERT INTO hosts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);"
    disk_cur.executemany(statement, data)
    disk_con.commit()

def insert_ports_result_to_db(data):
    statement = "INSERT INTO ports VALUES(?, ?);"
    disk_cur.executemany(statement, data)
    disk_con.commit()

def insert_candidate_urls_to_db(data):
    statement = "INSERT OR IGNORE INTO candidates VALUES(?, ?, ?);"
    disk_cur.executemany(statement, data)
    disk_con.commit()

#Select results
def read_candidates_from_db():
    statement = "SELECT DISTINCT domain, ip FROM candidates;"
    disk_cur.execute(statement)
    results = []
    for item in disk_cur:
        results.append([item['domain'], item['ip']])
    return results

def read_candidates_with_years_from_db():
    statement = "SELECT DISTINCT domain, year FROM candidates;"
    disk_cur.execute(statement)
    results = []
    for item in disk_cur:
        results.append([item['domain'], item['year']])
    return results

def read_ports_from_db():
    statement = "SELECT ports_seen FROM ports;"
    disk_cur.execute(statement)
    results = []
    for item in disk_cur:
        results.append(ast.literal_eval(item[0]))
    return results

def read_ips_from_processed():
    disk_cur.execute("SELECT DISTINCT ip FROM hosts;")
    results = []
    for item in disk_cur:
        results.append(item['ip'])
    return results

def read_all_domains_from_candidates():
    disk_cur.execute("SELECT domain FROM candidates;")
    results = disk_cur.fetchall()
    temp_list = []
    for result in results:
        temp_list.append(result['domain'])
    return temp_list

#Helper Functions
def do_ports_and_hosts_join():
    statement = """
        SELECT
        hosts.id, 
        year, 
        hosts.ip, 
        host, 
        isp, 
        asn, 
        num_hostnames, 
        hostnames, 
        ports_seen, 
        count_seen, 
        shodan_updated
        FROM hosts 
        JOIN ports ON hosts.id = ports.id
        JOIN candidates ON hosts.ip = candidates.ip;
    """
    disk_cur.execute(statement)
    results = []
    for item in disk_cur:
        results.append((item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9], item[10]))
    return results