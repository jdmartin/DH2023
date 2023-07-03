import plotly.express as px
from util import (get_all_cve_years_and_counts, get_pretty_hosts_count,
                  get_working_dir)

WORKINGDIR = get_working_dir()

df = get_all_cve_years_and_counts()
# Calculate the proportion of total rows for each CVE
total_count = df['count'].sum()
pretty_count = format(total_count, ",")
pretty_hosts_count = get_pretty_hosts_count()

fig = px.pie(df, values='count', names=df.year, title=f'{pretty_count} observed CVEs, arranged by Age, from {pretty_hosts_count} hosts')

# Save the plot
fig.write_html(f"viz/output/{WORKINGDIR}-age_of_cves.html", auto_open=True)
