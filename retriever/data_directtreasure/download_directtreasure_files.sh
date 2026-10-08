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

# https://www.tesourotransparente.gov.br/ckan/dataset/taxas-dos-titulos-ofertados-pelo-tesouro-direto
CSV_URL=https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/precotaxatesourodireto.csv
wget --quiet --timestamping ${CSV_URL}

duckdb td.ddb -c "
  CREATE OR REPLACE TABLE td AS
  SELECT
      data_base,
      CASE tipo_titulo
        WHEN 'Tesouro Selic'                           THEN 'LFT'
        WHEN 'Tesouro Prefixado'                       THEN 'LTN'
        WHEN 'Tesouro IPCA+'                           THEN 'NTN-B'
        WHEN 'Tesouro IPCA+ com Juros Semestrais'      THEN 'NTN-Bp'
        WHEN 'Tesouro Renda+ Aposentadoria Extra'      THEN 'NTN-Br'
        WHEN 'Tesouro Educa+'                          THEN 'NTN-Be'
        WHEN 'Tesouro IGPM+ com Juros Semestrais'      THEN 'NTN-C'
        WHEN 'Tesouro Prefixado com Juros Semestrais'  THEN 'NTN-F'
        ELSE NULL
      END AS tipo_titulo,
      data_vencimento,
      taxa_compra_manha,
      taxa_venda_manha,
      pu_compra_manha,
      pu_venda_manha,
      pu_base_manha
  FROM read_csv(
    'precotaxatesourodireto.csv',
    header=true,
    delim=';',
    decimal_separator=',',
    thousands='.',
    dateformat='%d/%m/%Y',
    columns={
      'tipo_titulo': varchar,
      'data_vencimento': date,
      'data_base': date,
      'taxa_compra_manha': double,
      'taxa_venda_manha': double,
      'pu_compra_manha': double,
      'pu_venda_manha': double,
      'pu_base_manha': double
    }
  );
"


# https://www.tesourodireto.com.br/titulos/historico-de-precos-e-taxas.htm
URL_BASE=https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/sistd

for BOND in "${BONDS[@]}"; do
	LOCAL_FILE="${BOND}_${YEAR}.xls"

	if [[ "${BOND}" == "NTN-B1" ]]; then
		REMOTE_FILE="Tesouro_Renda+_Aposentadoria_Extra_${YEAR}.xls"
	else
		REMOTE_FILE="${LOCAL_FILE}"
	fi

	if [[ "${YEAR}" -lt 2023 && "${BOND}" =~ NTN-B1 ]]; then
		# Create empty Excel file (with 'Sheet' worksheet)
		uv run python -c "import xlwt; wb = xlwt.Workbook(); wb.add_sheet('Sheet'); wb.save('${LOCAL_FILE}')"
	else
		echo "Downloading ${LOCAL_FILE}..."
		wget --quiet --random-wait -O "${LOCAL_FILE}" "${URL_BASE}/${YEAR}/${REMOTE_FILE}"
	fi

	LOCAL_FILE="${BOND}_${YEAR}.csv"
	duckdb td.ddb -c "
	  COPY (
	    SELECT *
	    FROM td
	    WHERE year(data_base)=${YEAR} AND tipo_titulo='${BOND}'
	    ORDER BY data_base, data_vencimento
	  ) TO '${LOCAL_FILE}' (HEADER);"
done

CURRENT_YEAR=$(date +"%Y")
if [[ "${YEAR}" == "${CURRENT_YEAR}" ]]; then
	touch ./*"${CURRENT_YEAR}"*
fi
