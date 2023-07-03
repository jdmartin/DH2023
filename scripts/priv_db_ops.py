import sqlite3

from util import get_working_dir

#Create the disk database (for backups) and a cursor to handle transactions.
WORKINGDIR = get_working_dir()
disk_con = sqlite3.connect(f"./{WORKINGDIR}/dbs/private.db")
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

def setup_tables():
    remove_subtables()
    disk_cur.execute("DROP TABLE IF EXISTS ports_counts;")
    disk_cur.execute("DROP TABLE IF EXISTS results;")
    disk_cur.execute("DROP TABLE IF EXISTS services;")
    disk_cur.execute("CREATE TABLE IF NOT EXISTS results(`id` UNIQUE, `year`, `ip`, `host`, `isp`, `asn`, `num_hostnames`, `hostnames`, `ports_seen`, `count_seen`, `shodan_updated` DATETIME);")
    disk_cur.execute("CREATE TABLE IF NOT EXISTS ports_counts(`port` INTEGER PRIMARY KEY, `count` INTEGER, `service` TEXT);")
    disk_cur.execute("CREATE TABLE IF NOT EXISTS services(`port` INTEGER PRIMARY KEY, `category` TEXT, `definition` TEXT, FOREIGN KEY (port) REFERENCES ports_counts(port))")
    disk_cur.execute("DELETE FROM results;")
    disk_cur.execute("DELETE FROM ports_counts;")
    disk_cur.execute("DELETE FROM services;")
    disk_con.commit()
    disk_cur.execute("VACUUM;")

def setup_results_subtables():
    years = list_all_years()
    for year in years:
        # Define the name of the new table based on the year
        table_name = 'results_' + str(year)
        # Create the new table
        disk_cur.execute(f"CREATE TABLE {table_name} AS SELECT * FROM results WHERE year = ?", (year,))

def setup_ports_by_year():
    disk_cur.execute("DROP TABLE IF EXISTS ports_by_year;")
    disk_cur.execute("CREATE TABLE ports_by_year AS SELECT port FROM ports_counts;")
    disk_con.commit()

def update_ports_by_year():
    years = list_all_years()
    for year in years:
        temp_year = "y" + str(year)
        disk_cur.execute(f"ALTER TABLE ports_by_year ADD COLUMN `{temp_year}` INTEGER DEFAULT 0;")
    disk_cur.execute("ALTER TABLE ports_by_year ADD COLUMN row_sum INTEGER DEFAULT 0;")

def setup_asn_by_year():
    disk_cur.execute("CREATE TABLE asn_by_year AS SELECT DISTINCT asn, isp FROM results ORDER BY asn ASC;")
    disk_con.commit()

def update_asn_by_year():
    years = list_all_years()
    for year in years:
        temp_year = "y" + str(year)
        disk_cur.execute(f"ALTER TABLE asn_by_year ADD COLUMN `{temp_year}` INTEGER DEFAULT 0;")
    disk_cur.execute("ALTER TABLE asn_by_year ADD COLUMN row_sum INTEGER DEFAULT 0;")

def setup_domains_by_loc():
    disk_cur.execute("DROP TABLE IF EXISTS domains_by_loc;")
    disk_cur.execute("CREATE TABLE domains_by_loc AS SELECT ip FROM results ORDER BY ip ASC;")
    disk_cur.execute("ALTER TABLE domains_by_loc ADD COLUMN latitude REAL;")
    disk_cur.execute("ALTER TABLE domains_by_loc ADD COLUMN longitude REAL;")
    disk_cur.execute("ALTER TABLE domains_by_loc ADD COLUMN city TEXT;")
    disk_cur.execute("ALTER TABLE domains_by_loc ADD COLUMN region TEXT;")
    disk_cur.execute("ALTER TABLE domains_by_loc ADD COLUMN country TEXT;")
    disk_con.commit()

def setup_domains_by_year():
    disk_cur.execute("DROP TABLE IF EXISTS domains_by_year;")
    disk_cur.execute("CREATE TABLE domains_by_year AS SELECT DISTINCT host FROM results ORDER BY host ASC;")
    disk_con.commit()

def update_domains_by_year():
    years = list_all_years()
    for year in years:
        temp_year = "y" + str(year)
        disk_cur.execute(f"ALTER TABLE domains_by_year ADD COLUMN `{temp_year}` INTEGER DEFAULT 0;")
    disk_cur.execute("ALTER TABLE domains_by_year ADD COLUMN row_sum INTEGER DEFAULT 0;")

def setup_tld_by_year():
    disk_cur.execute("DROP TABLE IF EXISTS tld_by_year;")
    disk_cur.execute("CREATE TABLE IF NOT EXISTS tld_by_year (`tld` UNIQUE, `country` TEXT);")
    disk_con.commit()

def update_tld_by_year():
    years = list_all_years()
    for year in years:
        temp_year = "y" + str(year)
        disk_cur.execute(f"ALTER TABLE tld_by_year ADD COLUMN `{temp_year}` INTEGER DEFAULT 0;")
    disk_cur.execute("ALTER TABLE tld_by_year ADD COLUMN row_sum INTEGER DEFAULT 0;")

def setup_vulns():
    disk_cur.execute("DROP TABLE IF EXISTS vulns;")
    disk_cur.execute("DROP TABLE IF EXISTS cve_counts;")
    disk_cur.execute("DROP TABLE IF EXISTS cve_defs;")
    disk_cur.execute("CREATE TABLE IF NOT EXISTS vulns(`id` INTEGER PRIMARY KEY AUTOINCREMENT, `ip`, `CVE`, `is_database`, `is_self_signed`, `is_starttls`, `is_cloud`, `is_vpn`, `is_eol_product`, `is_cdn`, `is_eol_os`);")
    disk_cur.execute("CREATE TABLE IF NOT EXISTS cve_defs(`CVE` TEXT UNIQUE, `cvss` REAL, `summary` TEXT, `refs`);")
    disk_cur.execute("CREATE TABLE IF NOT EXISTS cve_counts(`CVE` TEXT, `count` INTEGER DEFAULT 0);")
    disk_con.commit()

def remove_subtables():
    pattern = "results_%"
    ports_pattern = "ports_%"
    asn_pattern = "asn_%"
    disk_cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '{pattern}' OR name LIKE '{ports_pattern}' OR name LIKE '{asn_pattern}';")
    tables = disk_cur.fetchall()
    for table in tables:
        disk_cur.execute(f"DROP TABLE IF EXISTS {table[0]}")

def list_subtables():
    years = list_all_years()
    temp_list = []
    for year in years:
        # Define the name of the new table based on the year
        temp_list.append('results_' + str(year))
        temp_list.append('ports_' + str(year))
    
    return temp_list

def list_all_years():
    disk_cur.execute("SELECT DISTINCT year FROM results ORDER BY year;")
    years = disk_cur.fetchall()
    temp_list = []
    for year in years:
        temp_list.append(year[0])
    return temp_list

def list_all_ports():
    disk_cur.execute("SELECT port FROM ports_counts ORDER BY port ASC;")
    ports = disk_cur.fetchall()
    temp_list = []
    for port in ports:
        temp_list.append(port[0])
    return temp_list

def insert_ports_and_hosts_to_private_db(data):
    statement = "INSERT OR IGNORE INTO results VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
    disk_cur.executemany(statement, data)
    disk_con.commit()

def insert_ports_and_counts_to_private_db(data):
    statement = "INSERT OR IGNORE INTO ports_counts VALUES (?,?,?);"
    disk_cur.executemany(statement, data)
    disk_con.commit()

def insert_services(data):
    statement = "INSERT OR IGNORE INTO services VALUES (?,?,?);"
    disk_cur.executemany(statement, data)
    disk_con.commit()

def insert_port_years(column, port, count):
    disk_cur.execute(f"UPDATE ports_by_year SET {column} = ? WHERE port = ?;", [count, port])

def insert_vulns(data):
    statement = "INSERT OR IGNORE INTO vulns (ip, CVE, is_database, is_self_signed, is_starttls, is_cloud, is_vpn, is_eol_product, is_cdn, is_eol_os) VALUES (?,?,?,?,?,?,?,?,?,?);"
    disk_cur.executemany(statement, data)
    disk_con.commit()

def insert_cve_defs(data):
    statement = "INSERT OR IGNORE INTO cve_defs (CVE, cvss, summary, refs) VALUES (?,?,?,?)"
    disk_cur.executemany(statement, data)
    disk_con.commit()

def update_port_sums(port, count):
    disk_cur.execute(f"UPDATE ports_by_year SET row_sum = ? WHERE port = ?;", [count, port])
    disk_con.commit()

def update_asn_years(column, asn, count):
    disk_cur.execute(f"UPDATE asn_by_year SET {column} = ? WHERE asn = ?;", [count, asn])
    disk_con.commit()

def update_asn_sums(port, count):
    disk_cur.execute(f"UPDATE asn_by_year SET row_sum = ? WHERE asn = ?;", [count, port])
    disk_con.commit()

def update_domain_locs(data):
    statement = """
        UPDATE domains_by_loc 
        SET latitude = ?, 
        longitude = ?, 
        city = ?, 
        region = ?,
        country = ? 
        WHERE ip = ?
    """
    disk_cur.executemany(statement, data)
    disk_con.commit()

def update_domain_locs_totals():
    # Add the 'country_count' and 'city_count' columns to the 'domains_by_loc' table
    disk_cur.execute("ALTER TABLE domains_by_loc ADD COLUMN country_count INTEGER DEFAULT 0")
    disk_cur.execute("ALTER TABLE domains_by_loc ADD COLUMN city_count INTEGER DEFAULT 0")
    disk_con.commit()

    # Update the 'country_count' column with the number of times each country appears in the 'domains_by_loc' table
    disk_cur.execute("""
        UPDATE domains_by_loc
        SET country_count = (
            SELECT COUNT(*) FROM domains_by_loc AS subquery
            WHERE subquery.country = domains_by_loc.country
        ),
        city_count = (
            SELECT COUNT(*) FROM domains_by_loc AS subquery
            WHERE subquery.city = domains_by_loc.city
            AND subquery.region = domains_by_loc.region
        )
    """)

    disk_con.commit()

def update_domain_years(column, host, count):
    disk_cur.execute(f"UPDATE domains_by_year SET {column} = ? WHERE host = ?;", [count, host])
    disk_con.commit()

def update_domain_sums(tld, count):
    disk_cur.execute(f"UPDATE domains_by_year SET row_sum = ? WHERE host = ?;", [count, tld])
    disk_con.commit()

def update_cve_sums(CVE, count):
    disk_cur.execute(f"INSERT INTO cve_counts VALUES (?,?);", [CVE, count])
    disk_con.commit()

def populate_tld(tld):
    disk_cur.execute("INSERT OR IGNORE INTO tld_by_year(`tld`) VALUES (?);", (tld,))
    disk_con.commit()

def update_tld_years(column, tld, count):
    disk_cur.execute(f"UPDATE tld_by_year SET {column} = ? WHERE tld = ?;", [count, tld])
    disk_con.commit()

def update_tld_sums(tld, count):
    disk_cur.execute(f"UPDATE tld_by_year SET row_sum = ? WHERE tld = ?;", [count, tld])
    disk_con.commit()

def update_tld_countries(tld, country):
    disk_cur.execute(f"UPDATE tld_by_year SET country = ? WHERE tld = ?;", [country, tld])
    disk_con.commit()

def combine_port_count_and_service():
    statement = """
        CREATE TABLE new_ports_counts AS SELECT 
        ports_counts.port, 
        ports_counts.count, 
        services.definition 
        FROM ports_counts 
        LEFT JOIN services ON ports_counts.port = services.port 
    """
    disk_cur.execute(statement)
    disk_cur.execute("DROP TABLE ports_counts;")
    disk_cur.execute("ALTER TABLE new_ports_counts RENAME TO ports_counts;")
    disk_cur.execute("VACUUM;")

def combine_port_count_by_year_and_service():
    statement = """
        CREATE TABLE new_ports_counts AS SELECT 
        ports_by_year.*, 
        services.category, 
        services.definition 
        FROM ports_by_year 
        LEFT JOIN services ON ports_by_year.port = services.port 
    """
    disk_cur.execute(statement)
    disk_cur.execute("DROP TABLE ports_by_year;")
    disk_cur.execute("ALTER TABLE new_ports_counts RENAME TO ports_by_year;")
    disk_cur.execute("VACUUM;")
