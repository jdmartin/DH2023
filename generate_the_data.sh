#!/usr/bin/env bash

set -euo pipefail

PROJECTROOT=$(pwd)

compress_adho_abstracts () {
    if [[ ! -f data/abstracts.tar.gz ]]; then
        cd data;
        printf "Compressing abstracts... one moment!\n"
        tar -czf ./abstracts.tar.gz ./abstracts;
        rm -rf ./abstracts;
        cd -
    fi
}

compress_dhq_abstracts () {
    if [[ ! -f data/articles.tar.gz ]]; then
        cd data;
        printf "Compressing articles... one moment!\n"
        tar -czf ./articles.tar.gz ./dhq-xml;
        rm -rf ./dhq-xml;
        cd -
    fi
}

decompress_adho_abstracts () {
    if [[ -f data/abstracts.tar.gz ]]; then
        cd data;
        printf "Preparing abstracts... one moment!\n"
        tar -xzf ./abstracts.tar.gz;
        rm ./abstracts.tar.gz;
        cd -
    fi
}

decompress_dhq_abstracts () {
    if [[ -f data/articles.tar.gz ]]; then
        cd data;
        printf "Preparing articles... one moment!\n"
        tar -xzf ./articles.tar.gz;
        rm ./articles.tar.gz;
        cd -
    fi
}

do_everything () {
    read -rp "Do you want to start fresh and wipe all existing data? (y/n) " proceed_choice

    local lower_choice
    lower_choice=$(echo "$proceed_choice" | awk '{print tolower($0)}')

    if [ "$lower_choice" == "y" ]; then
        read -rp "Are you really sure? This is the nuclear option. (y/n) " really_really

        local lower_confirm
        lower_confirm=$(echo "$really_really" | awk '{print tolower($0)}')

        if [ "$lower_confirm" == "y" ]; then

            if [ -e ./dbs/sqlite3.db ]; then
                tar -czf ./dbs/sqlite3.db.bak.tar.gz ./dbs/sqlite3.db;
                rm ./dbs/sqlite3.db;
            fi
            
            if [ -e ./dbs/private.db ]; then
                tar -czf ./dbs/private.db.bak.tar.gz ./dbs/private.db;
                rm ./dbs/private.db;
            fi

            clear;
            #Initialize the db
            python scripts/init_db.py;
            #Get all URLs, even dupes, and store them in the candidates table
            python scripts/import_urls.py;
            #Get Distinct Candidate domains and ips from db, and query Shodan
            python scripts/get_shodan.py;
            #Create a csv in common_data/port_counts with the port and count from Shodan
            python scripts/gen_port_stats.py;
            #Combine lots of data in the private.db, count all the things.
            python scripts/augment_data.py;
            #Create stats about the type and frequency of top-level domains in the set.
            python scripts/tld-stats.py;
            #Get info about known vulnerabilities in candidates, from saved Shodan files, and store it.
            python scripts/get_vulns_from_shodan_data.py;
            #Extract info about location of host ips for mapping, and store it.
            python scripts/get_domain_locs.py
        else
            exit 0
        fi
    else
        exit 0
    fi
}

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
        rm ./data/shodan/*;
        decompress_dhq_abstracts;
        cd "$PROJECTROOT";
        perl -pi -e 's/^WORKINGDIR=.*/WORKINGDIR=DHQ/' .env;
        do_everything;
        cd DHQ;
        compress_dhq_abstracts;
        cd "$PROJECTROOT";
        ;;
    2)
        cd adho;
        rm ./data/shodan/*;
        decompress_adho_abstracts;
        cd "$PROJECTROOT";
        perl -pi -e 's/^WORKINGDIR=.*/WORKINGDIR=adho/' .env
        do_everything;
        cd adho;
        compress_adho_abstracts;
        cd "$PROJECTROOT";
        ;;
    esac
}

get_choice
