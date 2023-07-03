import csv

from db_ops import read_ports_from_db
from util import get_working_dir

WORKINGDIR = get_working_dir()
ports_list_from_db = read_ports_from_db()
ports_dict = {}

def generate_stats():
    for item in ports_list_from_db:
        for port in item:
            try:
                ports_dict[port] += 1
            except KeyError:
                ports_dict[port] = 1

def generate_csv():
    sorted_ports = sorted(ports_dict.items(), key=lambda x: x[1], reverse=True)

    with open(f'common_data/port_counts/{WORKINGDIR}-ports.csv', 'w+', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Port', 'Count'])  # Write header row
        for port, count in sorted_ports:
            writer.writerow([port, count])

if __name__ == "__main__":
    generate_stats()
    generate_csv()