import sqlite3

import pandas as pd
import plotly.express as px
from util import get_working_dir

WORKINGDIR = get_working_dir()

# Connect to SQLite database
conn = sqlite3.connect(f'file:{WORKINGDIR}/dbs/private.db?mode=ro', uri=True)

# Read data from SQLite database into a pandas dataframe
df = pd.read_sql_query("SELECT latitude, longitude, city, region, country , city_count, country_count FROM domains_by_loc", conn)
df = df.sort_values('country_count', ascending=False)

# Create a Plotly scatter_geo plot
fig = px.scatter_geo(
    df, 
    lat='latitude', 
    lon='longitude', 
    color='country', 
    scope='world', 
    size='city_count',
    size_max=10, 
    color_continuous_scale='Agsunset', 
    hover_data=['city', 'region', 'country', 'city_count', 'country_count'], 
    hover_name='country', 
    projection='natural earth',
    category_orders={'color': df['country'].tolist()}, 
    geojson='countries',
    fitbounds='geojson'
)

# Update the color scale of the plot
fig.update_traces(marker=dict(colorscale='Agsunset', reversescale=True, sizemode='diameter', sizemin=10, opacity=0.5))

# Add a title to the figure
fig.update_layout(
    title={
        'text': "Where the Links Go...",
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
fig.write_html(f"viz/output/{WORKINGDIR}-locations_of_linked_hosts.html", auto_open=True)
