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

INDICES=()
read_array() {
	i=0
	while read -r line; do
		INDICES[i]=$line
		i=$((i + 1))
	done <"$1"
}
[ -e "./codes.txt" ] && read_array "./codes.txt"

#https://data.anbima.com.br/indices/consulta/ima/resultados-diarios
URL_BASE=https://adata-precos-prod.s3.amazonaws.com/arquivos/indices-historico

for INDEX in "${INDICES[@]}"; do
	echo "Downloading ${INDEX}.xls..."
	wget -q --random-wait -O "${INDEX}.xls" "${URL_BASE}/${INDEX}-HISTORICO.xls"
done
