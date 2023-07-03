import datetime
import glob
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

# Replace the directory path with your own directory
directory = 'adho/data/abstracts/2019'

# Use glob to find all the HTML files in the directory
html_files = glob.glob(f'{directory}/*.html')

# Create the root element for the XML document
now = datetime.datetime.now()
timestamp = now.strftime("%Y-%m-%d_%H:%M:%S")
root = ET.Element('metadata', timestamp=timestamp)

# Loop over each file and extract the links from the body of the HTML document
for html_file in html_files:
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
        soup = BeautifulSoup(html, 'html.parser')
        body = soup.find('body')
        links = body.find_all('a') #type: ignore
        for link in links:
            href = link.get('href')
            if href is not None and (href.startswith('http://') or href.startswith('https://')):
                url = ET.SubElement(root, 'url', href=href)

# Create the XML document and write it to a file
xml_data = ET.tostring(root, encoding='unicode')
with open('adho/data/xml.all.urls/2019.xml', 'w', encoding='utf-8') as f:
    f.write(xml_data)