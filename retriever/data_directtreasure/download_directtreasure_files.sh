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

BONDS=()
read_array() {
	i=0
	while read -r line; do
		BONDS[i]=$line
		i=$((i + 1))
	done <"$1"
}
[ -e "./codes.txt" ] && read_array "./codes.txt"

#https://www.tesourodireto.com.br/titulos/historico-de-precos-e-taxas.htm
URL_BASE=https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/sistd

for BOND in "${BONDS[@]}"; do
	echo "Downloading ${BOND}_${YEAR}.xls..."
	wget -q --random-wait -O "${BOND}_${YEAR}.xls" "${URL_BASE}/${YEAR}/${BOND}_${YEAR}.xls"
done

CURRENT_YEAR=$(date +"%Y")
if [[ "${YEAR}" == "${CURRENT_YEAR}" ]]; then
	touch *"${CURRENT_YEAR}"*
fi
