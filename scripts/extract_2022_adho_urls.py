import os
from datetime import datetime

from lxml import etree

# Set the directory to search
dir_path = 'adho/data/abstracts/2022'

# Set the output file name
out_file = 'adho/data/xml.all.urls/2022.xml'

# Get the current timestamp
timestamp = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

# Create the root element with the timestamp attribute
root = etree.Element('metadata', timestamp=timestamp)

# Define the namespace
ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

# Iterate over the files in the directory
for filename in os.listdir(dir_path):
    if filename.endswith('.xml'):
        # Parse the XML file
        tree = etree.parse(os.path.join(dir_path, filename))

        # Get the body element
        body = tree.xpath('//tei:body', namespaces=ns)

        # Get the bibl elements
        bibls = tree.xpath('//tei:bibl', namespaces=ns)

        # Create a list to store the refs
        refs = []

        # Get the refs in the body
        if body:
            refs += body[0].xpath('.//tei:ref[@target]', namespaces=ns)

        # Get the refs in the bibls
        for bibl in bibls:
            refs += bibl.xpath('.//tei:ref[@target]', namespaces=ns)

        # Filter the refs by target starting with "http://" or "https://"
        targets = [ref.get('target') for ref in refs if ref.get('target', '').startswith(('http://', 'https://'))]

        # Create url elements for each target and add to the root element
        for target in targets:
            url_elem = etree.Element('url', href=target)
            root.append(url_elem)

# Create the output directory if it doesn't exist
os.makedirs(os.path.dirname(out_file), exist_ok=True)

# Write the XML file
etree.ElementTree(root).write(out_file, pretty_print=True, xml_declaration=True, encoding='UTF-8')
