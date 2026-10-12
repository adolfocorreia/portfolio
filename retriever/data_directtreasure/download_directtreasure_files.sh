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


echo "Downloading and loading precotaxatesourodireto.csv..."

# https://www.tesourodireto.com.br/titulos/historico-de-precos-e-taxas.htm
# https://www.tesourotransparente.gov.br/ckan/dataset/taxas-dos-titulos-ofertados-pelo-tesouro-direto
CSV_URL=https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/precotaxatesourodireto.csv
wget --quiet --timestamping ${CSV_URL}

# If td.ddb does not exist or is older than precotaxatesourodireto.csv
if [[ ( ! -e td.ddb ) || ( td.ddb -ot precotaxatesourodireto.csv ) ]]; then
  duckdb td.ddb -f load_td_data.sql
fi


for BOND in "${BONDS[@]}"; do
	LOCAL_FILE="${BOND}_${YEAR}.parquet"

	duckdb td.ddb -c "
	  SET VARIABLE year = ${YEAR};
	  SET VARIABLE bond = '${BOND}';
    SET VARIABLE destination_path = '${LOCAL_FILE}';
	" -f create_td_files.sql
done

CURRENT_YEAR=$(date +"%Y")
if [[ "${YEAR}" == "${CURRENT_YEAR}" ]]; then
	touch ./*"${CURRENT_YEAR}"*
fi
