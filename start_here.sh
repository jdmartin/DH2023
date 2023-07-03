#!/usr/bin/env bash

set -euo pipefail
WORKINGDIR=""

get_project_choice () {
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
        WORKINGDIR="DHQ"
        perl -pi -e 's/^WORKINGDIR=.*/WORKINGDIR=DHQ/' .env
        ;;
    2)
        WORKINGDIR="adho"
        perl -pi -e 's/^WORKINGDIR=.*/WORKINGDIR=adho/' .env
        ;;
    esac
}

check_threat_lists () {
    while true;
    do
        printf "Would you like to check observed hosts against threat lists?\n"
        read -rp "> " check_threats

        if [[ $check_threats == "y" || $check_threats == "n" ]]; then
            break
        fi
    done

    case $check_threats in 
        "y")
            python scripts/check_threat_lists.py;
            ;;
        "n")
            printf "Ok, skipping threat checking...\n\n"
            ;;
    esac
}

do_the_viz () {
    while true;
    do
        printf "Would you like to generate the visualizations?\n"
        read -rp "> " do_viz

        if [[ $do_viz == "y" || $do_viz == "n" ]]; then
            break
        fi
    done

    case $do_viz in 
        "y")
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
            python viz/geo_map_domains.py;

            python viz/geo_map_cves.py;
            python viz/geo_map_top5000_cves.py
            ;;
        "n")
            printf "Ok, skipping visualizations...\n\n"
            ;;
    esac
}

check_that_pieces_exist () {
    if [ ! -e ./$WORKINGDIR/dbs/sqlite3.db ] || [ ! -e ./$WORKINGDIR/dbs/private.db ]; then
        printf "\nLooks like one or both of the databases is missing.\nMake sure they're there, or use generate_the_data.sh\n"
    else
        check_threat_lists;
        do_the_viz
    fi
}

get_project_choice
check_that_pieces_exist