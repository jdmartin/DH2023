import sqlite3

import pandas as pd
import plotly.express as px
from util import get_pretty_hosts_count, get_working_dir

WORKINGDIR = get_working_dir()

# Connect to SQLite database
conn = sqlite3.connect(f'file:{WORKINGDIR}/dbs/private.db?mode=ro', uri=True)

# Query the data
query = """
SELECT port, category, definition, row_sum
FROM ports_by_year
ORDER BY row_sum DESC
"""
df = pd.read_sql_query(query, conn)

#Set some defaults
df['category'] = df['category'].fillna("Expected Private")
df['definition'] = df['definition'].fillna("misc")

# Calculate the total row_sum
total_count = df['row_sum'].sum()
pretty_count = format(total_count, ",")
pretty_hosts_count = get_pretty_hosts_count()

# Calculate the proportion of row_sum for each port
df['proportion'] = df['row_sum'] / total_count

# Create the treemap using Plotly
fig = px.treemap(df, 
                 path=['category', 'port'], 
                 values='proportion',
                 color='proportion',
                 color_continuous_scale='Agsunset',
                 hover_data={'port': True, 'proportion': ':.2%', 'definition': True, 'row_sum': True},
                 width=1600,
                 height=900
                 )

# Update the hover template
fig.update_traces(hovertemplate='<b>Port:</b> %{customdata[0]}<br><b>Proportion:</b> %{customdata[1]}<br><b>Definition:</b> %{customdata[2]}<br><b>Row Sum:</b> %{customdata[3]:,}')

# Update the font size of the labels
fig.update_layout(
    font=dict(size=14),
    title={
        'text': f"Open ports seen among {pretty_count} total in the set generated by {pretty_hosts_count} hosts",
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
fig.write_html(f"viz/output/{WORKINGDIR}-all_ports.html", auto_open=True)
