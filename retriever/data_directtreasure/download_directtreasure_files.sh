#!/usr/bin/env bash

set -e

# Check if argument ($1) is a valid year (4 digits starting with 19 or 20)
[[ $1 =~ ^(19|20)[0-9]{2}$ ]] && YEAR=$1
# If argument is not present or is invalid, use current year
[[ -z $YEAR ]] && YEAR=$(date +"%Y")

BONDS=()
read_array() {
    i=0
    while read line
    do
        BONDS[i]=$line
        i=$((i + 1))
    done < "$1"
}
[ -e "./codes.txt" ] && read_array "./codes.txt"


#http://www.tesouro.fazenda.gov.br/balanco-e-estatisticas

URL_BASE=http://sisweb.tesouro.gov.br/apex
source ./URLs.txt

for BOND in "${BONDS[@]}" ; do
    echo "Downloading ${BOND}_${YEAR}.xls..."
    wget -q --random-wait -O ${BOND}_${YEAR}.xls ${URL_BASE}/${URLS[${BOND}_${YEAR}]}
done

# Old URL
#URL=http://www.tesouro.fazenda.gov.br/documents/10180/137713
#for BOND in "${BONDS[@]}" ; do
#    echo "Downloading ${BOND}_${YEAR}.xls..."
#    wget -q --random-wait -O ${BOND}_${YEAR}.xls "${URL}/${BOND}_${YEAR}.xls"
#done
