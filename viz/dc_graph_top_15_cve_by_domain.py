import sqlite3

import pandas as pd
import plotly.graph_objs as go
from util import get_working_dir

WORKINGDIR = get_working_dir()

# Connect to SQLite database
conn = sqlite3.connect(f'file:{WORKINGDIR}/dbs/dc.db?mode=ro', uri=True)

query = """
    SELECT * FROM ac_cves;
"""
df = pd.read_sql_query(query, conn)

# sort dataframe by row_sum and select top 25 rows
df_top = df.sort_values('row_sum', ascending=False)[:15]
top_fifteen_sum = df_top.head(15)['row_sum'].sum()
print(df_top)
# create pie chart trace
trace = go.Pie(
    labels=df_top['domain'],
    values=df_top['row_sum'],
    text = df_top.apply(
        lambda x: f"{x['domain']}<br>{x['row_sum']} ({x['row_sum']/top_fifteen_sum:.0%})".replace(" %)", ")"),
        axis=1
    ),
    hoverinfo='text+value',
    textinfo='text'
)

# Sort the CVEs by their sum and create a list of the CVE names
cve_sums = df.sum()[1:-1]

# Add the box to the layout
layout = go.Layout(
    title=f'Top 15 Academic Domains from the {WORKINGDIR} set in Observed Count of {top_fifteen_sum} CVEs with a CVSS >= 8',
)

# create figure and plot
fig = go.Figure(data=[trace], layout=layout)
cve_text = '<b>Top CVEs:</b><br>' + '<br>'.join([f'{cve}: {count}' for cve, count in cve_sums.items()])
fig.update_layout(
    annotations=[
        dict(
            text=cve_text,
            align='left',
            showarrow=False,
            xanchor='left',
            yanchor='bottom',
            x=1.0,
            y=0.3,
            xref='paper',
            yref='paper',
            bordercolor='#333',
            borderwidth=1,
            borderpad=5,
            bgcolor='#FFF',
            opacity=0.9
        )
    ]
)
fig.write_html(f"viz/output/{WORKINGDIR}-top15_cve_having_ac_domains.html", auto_open=True)
