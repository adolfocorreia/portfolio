#!/bin/bash

# Check if argument ($1) is a valid year (4 digits starting with 19 or 20)
[[ $1 =~ ^(19|20)[0-9]{2}$ ]] && YEAR=$1
# If argument is not present or is invalid, use current year
[[ -z $YEAR ]] && YEAR=$(date +"%Y")


DEBS=()
read_array() {
    i=0
    while read line
    do
        DEBS[i]=$line
        i=$((i + 1))
    done < "$1"
}
[ -e "./codes.txt" ] && read_array "./codes.txt"


# PU: curva teórica
#http://www.debentures.com.br/exploreosnd/consultaadados/emissoesdedebentures/puhistorico_f.asp
URL_PU="http://www.debentures.com.br/exploreosnd/consultaadados/emissoesdedebentures/puhistorico_e.asp?op_exc=False&dt_ini=01%2F01%2F${YEAR}&dt_fim=31%2F12%2F${YEAR}&ativo="
URL_PU_SUFIX="++++"

# NEG: negociação em mercado secundário
#http://www.debentures.com.br/exploreosnd/consultaadados/mercadosecundario/precosdenegociacao_f.asp
URL_NEG="http://www.debentures.com.br/exploreosnd/consultaadados/mercadosecundario/precosdenegociacao_e.asp?op_exc=False&dt_ini=${YEAR}0101&dt_fim=${YEAR}1231&ativo="


for DEB in "${DEBS[@]}" ; do
    TSV_PU_FILE_NAME=${DEB}_PU_${YEAR}.tsv
    CSV_PU_FILE_NAME=${DEB}_PU_${YEAR}.csv
    echo "Downloading ${CSV_PU_FILE_NAME}..."
    wget -q --random-wait -O- "${URL_PU}${DEB}${URL_PU_SUFIX}" | iconv --from-code=ISO-8859-1 --to-code=UTF-8 | dos2unix -q > ${TSV_PU_FILE_NAME}
    [ -e ${TSV_PU_FILE_NAME} ] && gtail -n +3 ${TSV_PU_FILE_NAME} | ghead --lines=-4 | sed 's/\.//g' | sed 's/,/./g' | tr '\t' ',' | sed 's/,$//' > ${CSV_PU_FILE_NAME}

    TSV_NEG_FILE_NAME=${DEB}_NEG_${YEAR}.tsv
    CSV_NEG_FILE_NAME=${DEB}_NEG_${YEAR}.csv
    echo "Downloading ${CSV_NEG_FILE_NAME}..."
    wget -q --random-wait -O- "${URL_NEG}${DEB}" | iconv --from-code=ISO-8859-1 --to-code=UTF-8 | dos2unix -q > ${TSV_NEG_FILE_NAME}
    [ -e ${TSV_NEG_FILE_NAME} ] && gtail -n +3 ${TSV_NEG_FILE_NAME} | sed 's/\.//g' | sed 's/,/./g' | tr '\t' ',' > ${CSV_NEG_FILE_NAME}
done
