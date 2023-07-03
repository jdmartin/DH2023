import sqlite3

import pandas as pd
import plotly.express as px
from util import get_working_dir

WORKINGDIR = get_working_dir()

# Connect to SQLite database
conn = sqlite3.connect(f'file:{WORKINGDIR}/dbs/private.db?mode=ro', uri=True)

# Read data from SQLite database into a pandas dataframe
twisty_join_statement = """
    SELECT cve_defs.CVE,
    cve_defs.cvss,
    cve_defs.summary,
    cve_counts.count,
    vulns.ip,
    domains_by_loc.city,
    domains_by_loc.region,
    domains_by_loc.country,
    domains_by_loc.latitude,
    domains_by_loc.longitude
    FROM cve_defs
    JOIN cve_counts ON cve_defs.CVE = cve_counts.CVE
    JOIN vulns ON cve_counts.CVE = vulns.CVE
    JOIN domains_by_loc ON vulns.ip = domains_by_loc.ip
    WHERE cve_defs.cvss >= 4.0 
    ORDER BY cve_defs.cvss DESC
"""
df = pd.read_sql_query(twisty_join_statement, conn)
df = df.sort_values('count', ascending=False)

# Create a Plotly scatter_geo plot
fig = px.scatter_geo(
    df, 
    lat='latitude', 
    lon='longitude', 
    color='cvss', 
    scope='world', 
    color_continuous_scale='Agsunset', 
    hover_data=['CVE', 'cvss', 'city', 'region', 'country', 'summary'], 
    hover_name='country', 
    category_orders={'color': df['country'].tolist()}, 
    geojson='countries',
    fitbounds='geojson',
    width=1600,
    height=900,
    template="plotly_white"
)

# Update the color scale of the plot
fig.update_traces(marker=dict(colorscale='Agsunset', reversescale=True))

# Add a title to the figure
fig.update_layout(
    title={
        'text': "Danger Zone(s) - All Observed CVE with a CVSS >= 4.0",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    geo=dict(
        showcountries=True,
        countrywidth=0.5,
        projection_scale=125,
        center=dict(lat=0, lon=0),
        showland=True,
        landcolor='rgb(217, 217, 217)',
        subunitwidth=0.5,
        showlakes=False,
        showocean=False,
        oceancolor='rgb(222, 222, 222)',
        lakecolor='rgb(255, 255, 255)'
    ),
    legend=dict(
        orientation="v",
        yanchor="top",
        y=1,
        xanchor="right",
        x=1.15,
        traceorder="normal",
        bordercolor="#FFFFFF",
        borderwidth=2,
        bgcolor="#E2E2E2",
        title_font=dict(size=1),
        font=dict(size=12)
    )
)

# Save and show the plot
fig.write_html(f"viz/output/{WORKINGDIR}-locations_of_CVEs.html", auto_open=True)
