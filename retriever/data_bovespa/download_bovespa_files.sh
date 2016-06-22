#!/usr/bin/env bash

set -e

# Check if argument ($1) is a valid year (4 digits starting with 19 or 20)
[[ $1 =~ ^(19|20)[0-9]{2}$ ]] && YEAR=$1
# If argument is not present or is invalid, use current year
[[ -z $YEAR ]] && YEAR=$(date +"%Y")

#http://www.bmfbovespa.com.br/pt-br/cotacoes-historicas/FormSeriesHistoricasArq.asp
FILENAME=COTAHIST_A${YEAR}.ZIP
URL=http://bvmf.bmfbovespa.com.br/InstDados/SerHist/${FILENAME}

echo "Downloading ${FILENAME}..."
wget -q --random-wait -O "${FILENAME}" "${URL}"
unzip -q -o "${FILENAME}"
