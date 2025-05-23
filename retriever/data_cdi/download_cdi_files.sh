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

#http://www.cetip.com.br/astec/series_v05/paginas/taxadi_i1.htm
URL=ftp://ftp.cetip.com.br/MediaCDI

CSV_FILE=CDI_${YEAR}.csv

OFFSET=86400 # 24*60*60
INITIAL_TS=$(date --date="${YEAR}-01-01 00:00:00" "+%s")
FINAL_TS=$(date --date="${YEAR}-12-31 00:00:00" "+%s")
TODAY=$(date "+%Y-%m-%d")
TODAY_TS=$(date --date="${TODAY} 00:00:00" "+%s")

if [[ ${FINAL_TS} -lt ${TODAY_TS} ]]; then
	MINIMAL_TS=${FINAL_TS}
else
	MINIMAL_TS=${TODAY_TS}
fi

END_TS=$((MINIMAL_TS + OFFSET))

echo "Date,CDI" >"${CSV_FILE}"

CURRENT_TS=$INITIAL_TS
while [[ "${CURRENT_TS}" -le "${END_TS}" ]]; do
	CURRENT_DATE=$(date --date="@${CURRENT_TS}" "+%Y%m%d")
	FILENAME=${CURRENT_DATE}.txt

	# Download file only if it does not exist and if day is not Saturday (6) nor Sunday (7)
	if [[ ! -e ${FILENAME} && $(date --date="@${CURRENT_TS}" "+%u") -lt 6 ]]; then
		wget -q --random-wait "${URL}/${FILENAME}" || true
	fi

	if [[ -e ${FILENAME} ]]; then
		echo -n "${CURRENT_DATE}," >>"${CSV_FILE}"
		cat "${FILENAME}" >>"${CSV_FILE}"
	fi

	CURRENT_TS=$((CURRENT_TS + OFFSET))
done
