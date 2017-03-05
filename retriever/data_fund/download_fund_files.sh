#!/usr/bin/env bash

set -e

# Check if argument ($1) is a valid year (4 digits starting with 19 or 20)
[[ $1 =~ ^(19|20)[0-9]{2}$ ]] && YEAR=$1
# If argument is not present or is invalid, use current year
[[ -z $YEAR ]] && YEAR=$(date +"%Y")

FUNDS=()
read_array() {
    i=0
    while read LINE
    do
        #FUNDS[i]=${LINE//[\.\/-]/}
        FUNDS[i]=${LINE}
        i=$((i + 1))
    done < "$1"
}
[ -e "./codes.txt" ] && read_array "./codes.txt"

source env/bin/activate

for CNPJ in "${FUNDS[@]}" ; do
    CNPJ_NUMBERS=${CNPJ//[\.\/-]/}

    echo "Downloading ${CNPJ_NUMBERS}_${YEAR}-MM.csv files..."
    ./cvm_retriever.py "${CNPJ}" "${YEAR}"

    YEAR_FILE="${CNPJ_NUMBERS}_${YEAR}.csv"
    echo "Assembling ${YEAR_FILE} file..."
    head -n 1 "${CNPJ_NUMBERS}_${YEAR}-01.csv" > "${YEAR_FILE}"

    for MONTH in $(seq -f "%02g" 1 12) ; do
        MONTH_FILE="${CNPJ_NUMBERS}_${YEAR}-${MONTH}.csv"
        [ -e "${MONTH_FILE}" ] && gtail -n +2 "${MONTH_FILE}" | while read LINE
        do
            [[ $LINE =~ ", , , , , , ," ]] && continue
            echo -n "${YEAR}-${MONTH}-" >> "${YEAR_FILE}"
            echo "${LINE}" >> "${YEAR_FILE}"
        done
    done
done
