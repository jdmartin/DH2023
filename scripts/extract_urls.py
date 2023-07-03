import datetime
import glob
import os
import re
import xml.etree.ElementTree as ET

from util import get_working_dir

WORKINGDIR = get_working_dir()
# Replace the directory path with your own directory
directory = f'{WORKINGDIR}/data/dhq-xml/'
subdirs = [f.path for f in os.scandir(directory) if f.is_dir()]

for subdir in subdirs:
    year = subdir.split('/')[2]
    # Use glob to find all the XML files in the directory
    xml_files = glob.glob(f'{subdir}/*.xml')

    # Create the root element for the XML document
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H:%M:%S")
    root = ET.Element('metadata', timestamp=timestamp)

    # Loop over each file and extract the links from the body of the HTML document
    for xmlfile in xml_files:
        with open(xmlfile, 'r') as file:
            # Loop through each line in the file
            for line in file:
                # Search for the URL pattern using regex
                match = re.search(r'https?://([\w\.]+)/', line)
                if match:
                    # Extract the text between the `//` and `/`
                    url = match.group(1)
                    # Strip any ending `"` characters
                    url = url.strip('"')
                    url = ET.SubElement(root, 'url', href=url)

    # Create the XML document and write it to a file
    xml_data = ET.tostring(root, encoding='unicode')
    with open(f'{WORKINGDIR}/data/xml.all.urls/{year}.xml', 'w', encoding='utf-8') as f:
        f.write(xml_data)
