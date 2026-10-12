COPY (
    SELECT
        data_base,
        tipo_titulo,
        data_vencimento,
        taxa_compra_manha,
        taxa_venda_manha,
        pu_compra_manha,
        pu_venda_manha,
        pu_base_manha,
        tipo_titulo || '_' || strftime(data_vencimento, '%d%m%y') AS codigo
    FROM td
    WHERE
        year(data_base) = getvariable('year')
        AND tipo_titulo = getvariable('bond')
    ORDER BY data_base, data_vencimento
)
TO (getvariable('destination_path'));
