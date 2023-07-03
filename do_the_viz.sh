#!/usr/bin/env bash

set -euo pipefail

get_choice () {
    while true;
    do
        printf "Which project would you like to work on?\n\n\t1. DHQ\n\t2. ADHO\n"
        read -rp "> " project_choice

        if [[ $project_choice == "1" || $project_choice == "2" ]]; then
            break
        fi
    done

    case $project_choice in 
    1)
        cd DHQ;
        ;;
    2)
        cd adho;
        ;;
    esac
}

do_viz () {
    python viz/plot_top50_asn.py;
    python viz/plot_top50_cve.py;
    python viz/plot_top50_domains.py;
    python viz/plot_top50_ports.py;
    python viz/plot_top50_tld.py;

    python viz/plot_all_asn.py;
    python viz/plot_all_cve.py;
    python viz/plot_all_domains.py;
    python viz/plot_all_ports.py;
    python viz/plot_all_tld.py;

    python viz/graph_age_of_cves.py;
    python viz/geo_map_domains.py

    python viz/geo_map_cves.py;
    python viz/geo_map_top5000_cves.py
}

get_choice
do_viz
cd -
