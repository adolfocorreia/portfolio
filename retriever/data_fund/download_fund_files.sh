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

FUNDS=()
read_array() {
	i=0
	while read -r LINE; do
		FUNDS[i]=${LINE}
		i=$((i + 1))
	done <"$1"
}
[ -e "./codes.txt" ] && read_array "./codes.txt"

# Download zip files (see also http://cvmweb.cvm.gov.br/SWB/Sistemas/SCW/CPublica/CConsolFdo/FormBuscaParticFdo.aspx)
if [[ $YEAR -le 2020 ]]; then
	echo "Downloading ${YEAR}.zip fund file..."
	ZIP_FILE="inf_diario_fi_${YEAR}.zip"
	TIME_FLAG=""; [[ -e ${ZIP_FILE} ]] && TIME_FLAG="--time-cond ${ZIP_FILE}"
	curl --silent ${TIME_FLAG:+${TIME_FLAG}} --remote-time --remote-name "https://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/HIST/${ZIP_FILE}"
	unzip -q -o "${ZIP_FILE}"
else
	echo "Downloading ${YEAR}-MM.zip fund files..."
	LAST_MONTH=12; [[ $YEAR -eq $(date +"%Y") ]] && LAST_MONTH=$(date +"%m")
	for MONTH in $(seq -f "%02g" "${LAST_MONTH}"); do
		ZIP_FILE="inf_diario_fi_${YEAR}${MONTH}.zip"
		TIME_FLAG=""; [[ -e ${ZIP_FILE} ]] && TIME_FLAG="--time-cond ${ZIP_FILE}"
		curl --silent ${TIME_FLAG:+${TIME_FLAG}} --remote-time --remote-name --fail "https://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/${ZIP_FILE}" && unzip -q -o "${ZIP_FILE}"
	done
fi

# Normalize CSV headers
for CSV_FILE in inf_diario_fi_"${YEAR}"*.csv; do (
	sed --in-place '1s/CNPJ_FUNDO_CLASSE/CNPJ_FUNDO/' "${CSV_FILE}"
	csvcut --delimiter ';' --columns "CNPJ_FUNDO,DT_COMPTC,VL_TOTAL,VL_QUOTA,VL_PATRIM_LIQ,CAPTC_DIA,RESG_DIA,NR_COTST" "${CSV_FILE}" | sponge "${CSV_FILE}"
	csvclean --enable-all-checks "${CSV_FILE}" 2>&1 1>/dev/null
)& done
wait

# Assemble file for each fund
for CNPJ in "${FUNDS[@]}"; do (
	CNPJ_NUMBERS=${CNPJ//[\.\/-]/}
	YEAR_FILE="${CNPJ_NUMBERS}_${YEAR}.csv"
	echo "Assembling ${YEAR_FILE} file..."
	csvstack inf_diario_fi_"${YEAR}"*.csv | csvgrep --column "CNPJ_FUNDO" --match "${CNPJ}" | csvsort --column "DT_COMPTC" > "${YEAR_FILE}"
)& done
wait

# Remove temporary CSV files
rm inf_diario_fi_*.csv

# Return with success code if this line is reached
true
