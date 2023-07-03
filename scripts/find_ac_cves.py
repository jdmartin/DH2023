import ast
import sqlite3

import pandas as pd
from util import get_working_dir

WORKINGDIR = get_working_dir()

conn = sqlite3.connect(f'file:{WORKINGDIR}/dbs/private.db?mode=ro', uri=True)

get_top_cve_query = """
    SELECT 
    cve_counts.CVE, 
    cve_defs.summary
    FROM cve_counts
    JOIN cve_defs ON cve_counts.CVE = cve_defs.CVE
    WHERE cve_defs.cvss >= 8.0
    ORDER BY cve_counts.count DESC
    LIMIT 10;
"""

query = """
    SELECT * FROM vulns 
    JOIN results ON vulns.ip = results.ip 
    WHERE vulns.CVE = '{}' 
    AND vulns.is_cdn = 0
    AND (results.host LIKE '%.edu'
    OR results.host LIKE '%.ac.%'
    OR results.host LIKE '%.uni-%');
"""

found_cves_by_uni = {}
found_unis_count = {}

cve_counts_df = pd.read_sql_query(get_top_cve_query, conn)
for item in cve_counts_df['CVE']:
    found_hostnames = []
    query = query.format(item)
    df = pd.read_sql_query(query, conn)

    for index, row in df.iterrows():
        hosts = ast.literal_eval(row['hostnames'])

        for host in hosts:
            if '.edu' in host:
                if host.split('.')[-2] + '.edu' not in found_cves_by_uni:
                    found_cves_by_uni[host.split('.')[-2] + '.edu'] = {}
            if '.ac.' in host:
                ac_parts = host.split('.ac.')
                if len(ac_parts) > 1:
                    if ac_parts[0].split('.')[-1] + '.ac.' + ac_parts[1] not in found_cves_by_uni:
                        found_cves_by_uni[ac_parts[0].split('.')[-1] + '.ac.' + ac_parts[1]] = {}
            if '.uni-' in host:
                if 'uni-' + host.split('.uni-')[1] not in found_cves_by_uni:
                    found_cves_by_uni['uni-' + host.split('.uni-')[1]] = {}
        
        for host in hosts:
            found_hostnames.append(host)
            if '.edu' in host:
                try:
                    found_unis_count[host.split('.')[-2] + '.edu'] += 1
                except KeyError:
                    found_unis_count[host.split('.')[-2] + '.edu'] = 1
                
                if item in found_cves_by_uni[host.split('.')[-2] + '.edu']:
                    found_cves_by_uni[host.split('.')[-2] + '.edu'][item] += 1
                else:
                    found_cves_by_uni[host.split('.')[-2] + '.edu'][item] = 1

            if '.ac.' in host:
                ac_parts = host.split('.ac.')
                if len(ac_parts) > 1:
                    try:
                        found_unis_count[ac_parts[0].split('.')[-1] + '.ac.' + ac_parts[1]] += 1
                    except KeyError:
                        found_unis_count[ac_parts[0].split('.')[-1] + '.ac.' + ac_parts[1]] = 1
                    
                    if item in found_cves_by_uni[ac_parts[0].split('.')[-1] + '.ac.' + ac_parts[1]]:
                        found_cves_by_uni[ac_parts[0].split('.')[-1] + '.ac.' + ac_parts[1]][item] += 1
                    else:
                        found_cves_by_uni[ac_parts[0].split('.')[-1] + '.ac.' + ac_parts[1]] = {item: 1}

            if '.uni-' in host:
                try:
                    found_unis_count['uni-' + host.split('.uni-')[1]] += 1
                except KeyError or TypeError:
                    found_unis_count['uni-' + host.split('.uni-')[1]] = 1
                
                if item in found_cves_by_uni['uni-' + host.split('.uni-')[1]]:
                    found_cves_by_uni['uni-' + host.split('.uni-')[1]][item] += 1
                else:
                    found_cves_by_uni['uni-' + host.split('.uni-')[1]] = {item: 1}

df = pd.DataFrame(found_cves_by_uni).T.fillna(0).astype(int)
df['row_sum'] = df.sum(axis=1)
df_sorted = df.sort_values(by='row_sum', ascending=False)
df.index.name = 'domain'

new_conn = sqlite3.connect(f'file:{WORKINGDIR}/dbs/dc.db', uri=True)
df.to_sql('ac_cves', new_conn)
print(df_sorted)