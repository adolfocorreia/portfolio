#!/usr/bin/env bash

set -eET
echo_error_line() {
	local lineno=$1
	local line=$2
	echo "Error at line ${lineno}: ${line}"
}
trap 'echo_error_line ${LINENO} "${BASH_COMMAND}"' ERR


# Check if argument ($1) is a valid year (4 digits starting with 19 or 20)
[[ $1 =~ ^(19|20)[0-9]{2}$ ]] && YEAR=$1
# If argument is not present or is invalid, use current year
[[ -z $YEAR ]] && YEAR=$(date +"%Y")


# http://www.bmfbovespa.com.br/pt-br/cotacoes-historicas/FormSeriesHistoricasArq.asp
BASENAME="COTAHIST_A${YEAR}"
ZIP_PATH="zip://${BASENAME}.zip/${BASENAME}.TXT"
URL="https://bvmf.bmfbovespa.com.br/InstDados/SerHist/${BASENAME}.ZIP"

echo "Downloading ${BASENAME}.zip and assembling ${BASENAME}.parquet..."
ZIP_FILE="${BASENAME}.zip"
wget --quiet --no-check-certificate --random-wait --timestamping -O "${ZIP_FILE}" "${URL}"
[[ -s ${ZIP_FILE} ]] || false

duckdb -c "
  SET VARIABLE cotahist_path = '${ZIP_PATH}';
  SET VARIABLE destination_path = '${BASENAME}.parquet';
" -f extract_data_from_cotahist.sql
