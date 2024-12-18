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

#http://www.bmfbovespa.com.br/pt-br/cotacoes-historicas/FormSeriesHistoricasArq.asp
BASENAME=COTAHIST_A${YEAR}
FILENAMEZIP=${BASENAME}.ZIP
FILENAMETXT=${BASENAME}.TXT
URL=https://bvmf.bmfbovespa.com.br/InstDados/SerHist/${FILENAMEZIP}

echo "Downloading ${FILENAMEZIP}..."
wget -q --no-check-certificate --random-wait -O "${FILENAMEZIP}" "${URL}"
[[ -s ${FILENAMEZIP} ]] || false
unzip -q -o "${FILENAMEZIP}"

touch "${FILENAMEZIP}"
touch "${FILENAMETXT}"
