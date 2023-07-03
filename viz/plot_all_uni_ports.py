import ast
import sqlite3
from collections import Counter

port_count = Counter()
import pandas as pd
import plotly.express as px
from util import get_working_dir

WORKINGDIR = get_working_dir()
observed_ports = []
count_of_hosts = 0
unique_ports = set()

# Connect to SQLite database
conn = sqlite3.connect(f'file:{WORKINGDIR}/dbs/private.db?mode=ro', uri=True)

# Query the data
query = """
SELECT DISTINCT host, ports_seen
FROM results
WHERE host LIKE '%.edu' 
OR host LIKE '%.ac.%'
ORDER BY host ASC
"""

results = conn.execute(query).fetchall()
# Iterate over the results and extract the unique ports

for row in results:
    count_of_hosts += 1
    ports = ast.literal_eval(row[1])
    port_count.update(ports)
    unique_ports.update(set(ports))

df = pd.DataFrame({'port': list(port_count.keys()), 'count': list(port_count.values())})
df['port_str'] = df['port'].astype(str)
df = df.sort_values(by='count', ascending=False)

fig = px.pie(df, 
             names='port_str', 
             values='count',
             title=f"Open ports seen among {count_of_hosts} total hosts",
             width=1600, 
             height=900,
             color_discrete_sequence=px.colors.qualitative.Pastel)
             
fig.update_traces(textposition='inside', textinfo='percent+label')

# Update the hover template
#fig.update_traces(hovertemplate='<b>Port:</b> %{customdata[0]}<br><b>Count:</b> %{customdata[1]}<br><b>Row Sum:</b> %{customdata[2]:,}')

# Update the font size of the labels
fig.update_layout(
    font=dict(size=14),
    title={
        'text': f"Open ports seen among {count_of_hosts} total academic hosts",
        'font': {
            'size': 28,
            'color': 'black'
        },
        'x': 0.5,
        'y': 0.98,
        'xanchor': 'center',
        'yanchor': 'top'
    }
)

# Save the plot
fig.write_html(f"viz/output/{WORKINGDIR}-all_uni_ports.html", auto_open=True)
