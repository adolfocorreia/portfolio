CREATE OR REPLACE TABLE td AS
SELECT
    data_base,
    CASE tipo_titulo
        WHEN 'Tesouro Selic' THEN 'LFT'
        WHEN 'Tesouro Prefixado' THEN 'LTN'
        WHEN 'Tesouro IPCA+ com Juros Semestrais' THEN 'NTN-B'
        WHEN 'Tesouro IPCA+' THEN 'NTN-Bp'
        WHEN 'Tesouro Renda+ Aposentadoria Extra' THEN 'NTN-Br'
        WHEN 'Tesouro Educa+' THEN 'NTN-Be'
        WHEN 'Tesouro IGPM+ com Juros Semestrais' THEN 'NTN-C'
        WHEN 'Tesouro Prefixado com Juros Semestrais' THEN 'NTN-F'
    END AS tipo_titulo,
    data_vencimento,
    taxa_compra_manha,
    taxa_venda_manha,
    pu_compra_manha,
    pu_venda_manha,
    pu_base_manha
FROM read_csv(
    'precotaxatesourodireto.csv',
    header = true,
    delim = ';',
    decimal_separator = ',',
    thousands = '.',
    dateformat = '%d/%m/%Y',
    columns = {
        'tipo_titulo': varchar,
        'data_vencimento': date,
        'data_base': date,
        'taxa_compra_manha': float,
        'taxa_venda_manha': float,
        'pu_compra_manha': float,
        'pu_venda_manha': float,
        'pu_base_manha': float
    }
);
