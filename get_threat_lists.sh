#!/usr/bin/env bash

set -euo pipefail

do_dshield () {
    curl -o ./dshield.txt 'https://feeds.dshield.org/block.txt';
    awk '$1 ~ /^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$/ {print $1 "/" $3}' ./dshield.txt | sed 's/ //g' > ./dshield_processed;
    mv ./dshield_processed ./dshield.txt
}

do_spamdrop () {
    curl -o ./spamdrop.txt 'https://www.spamhaus.org/drop/drop.txt';
    curl -o ./spamedrop.txt 'https://www.spamhaus.org/drop/edrop.txt';

    awk '$1 ~ /^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\/[0-9]+$/ {print $1}' ./spamdrop.txt > ./spamdrop.txt_temp
    mv ./spamdrop.txt_temp ./spamdrop.txt

    awk '$1 ~ /^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\/[0-9]+$/ {print $1}' ./spamedrop.txt > ./spamedrop.txt_temp
    mv ./spamedrop.txt_temp ./spamedrop.txt
}

do_emergingthreats () {
    curl -o ./et_ips.txt 'https://rules.emergingthreats.net/blockrules/compromised-ips.txt'
    curl -o ./emerging.txt 'https://rules.emergingthreats.net/blockrules/emerging-botcc.excluded'

    awk '$1 ~ /^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$/ {print $1 "/32"}' ./et_ips.txt | sed 's/ //g' > ./et_ips_temp;
    mv ./et_ips_temp ./et_ips.txt

    awk '$1 ~ /^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$/ {print $1 "/32"}' ./emerging.txt | sed 's/ //g' > ./emerging_temp;
    mv ./emerging_temp ./emerging.txt
}

do_cinsscore () {
    curl -o ./ci_bad.txt 'https://cinsscore.com/list/ci-badguys.txt'

    awk '$1 ~ /^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$/ {print $1 "/32"}' ./ci_bad.txt | sed 's/ //g' > ./ci_bad_temp;
    mv ./ci_bad_temp ./ci_bad.txt

}

do_blocklist () {
    curl -o ./blocklist.txt 'https://lists.blocklist.de/lists/all.txt'

    awk '$1 ~ /^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$/ {print $1 "/32"}' ./blocklist.txt | sed 's/ //g' > ./blocklist_temp;
    mv ./blocklist_temp ./blocklist.txt
}

do_bindef () {
    curl -o ./bindef.txt 'https://www.binarydefense.com/banlist.txt'

    awk '$1 ~ /^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$/ {print $1 "/32"}' ./bindef.txt | sed 's/ //g' > ./bindef_temp;
    mv ./bindef_temp ./bindef.txt
}

do_abuse () {
    curl -o ./abuse_ips.txt 'https://feodotracker.abuse.ch/downloads/ipblocklist.txt'
    curl -o ./abuse_rec.txt 'https://feodotracker.abuse.ch/downloads/ipblocklist_recommended.txt'
    curl -o ./abuse_bot.txt 'https://sslbl.abuse.ch/blacklist/sslipblacklist.txt'

    awk '$1 ~ /^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$/ {print $1 "/32"}' ./abuse_ips.txt | sed 's/ //g' > ./abuse_ips_temp;
    mv ./abuse_ips_temp ./abuse_ips.txt

    awk '$1 ~ /^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$/ {print $1 "/32"}' ./abuse_rec.txt | sed 's/ //g' > ./abuse_rec_temp;
    mv ./abuse_rec_temp ./abuse_rec.txt

    awk '$1 ~ /^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$/ {print $1 "/32"}' ./abuse_bot.txt | sed 's/ //g' > ./abuse_bot_temp;
    mv ./abuse_bot_temp ./abuse_bot.txt
}

do_myip () {
    curl -o ./myip.txt 'https://myip.ms/files/blacklist/general/latest_blacklist.txt'

    awk '$1 ~ /^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$/ {print $1 "/32"}' ./myip.txt | sed 's/ //g' > ./myip_temp;
    mv ./myip_temp ./myip.txt

}

process_lists () {
    mkdir -p common_data/threat_lists;
    cd common_data/threat_lists;
    do_dshield;
    do_spamdrop;
    do_emergingthreats;
    do_cinsscore;
    do_blocklist;
    do_bindef;
    do_abuse;
    do_myip;
    cd -
}

get_choice () {
    while true;
    do
        printf "Which project would you like to search for threats?\n\n\t1. DHQ\n\t2. ADHO\n\tq. Quit\n"
        read -rp "> " project_choice

        if [[ $project_choice == "1" || $project_choice == "2" || $project_choice == "q" ]]; then
            break
        fi
    done

    case $project_choice in 
    1)
        perl -pi -e 's/^WORKINGDIR=.*/WORKINGDIR=DHQ/' .env;
        python scripts/check_threat_lists.py;
        ;;
    2)
        perl -pi -e 's/^WORKINGDIR=.*/WORKINGDIR=adho/' .env;
        python scripts/check_threat_lists.py
        ;;
    q)
        exit 0;
        ;;
    esac
}

process_lists
get_choice