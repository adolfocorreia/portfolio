#/bin/bash

# Check if argument ($1) is a valid year (4 digits starting with 19 or 20)
[[ $1 =~ ^(19|20)[0-9]{2}$ ]] && YEAR=$1
# If argument is not present or is invalid, use current year
[[ -z $YEAR ]] && YEAR=$(date +"%Y")

FUNDS=()
read_array() {
    i=0
    while read LINE
    do
        FUNDS[i]=${LINE//[\.\/-]/}
        i=$((i + 1))
    done < "$1"
}
[ -e "./codes.txt" ] && read_array "./codes.txt"

SEARCH_URL="http://fundosdeinvestimentos.valor.com.br/vo2/Safi/Home/Pesquisa"
SEARCH_DATA="TipoBusca=cnpj&Buscar=Buscar&AdminList=&txtBuscaPorFundo="
SHEET_URL="http://fundosdeinvestimentos.valor.com.br/vo2/Safi/Home/ExcelEx"
SHEET_DATA="per=3&dtIni=01/01/${YEAR}&dtFim=31/12/${YEAR}&anbid="

for CNPJ in "${FUNDS[@]}" ; do
    echo "Downloading ${CNPJ}_${YEAR}.xlsx..."
    FUND_ID=$(wget -q --random-wait -O- --post-data "${SEARCH_DATA}${CNPJ}" "${SEARCH_URL}" | grep FundoResult | sed -e 's/^.*anbid=//' | sed -e "s/'.*$//")
    wget -q --random-wait -O "${CNPJ}_${YEAR}.xlsx" --post-data "${SHEET_DATA}${FUND_ID}" "${SHEET_URL}"
done
