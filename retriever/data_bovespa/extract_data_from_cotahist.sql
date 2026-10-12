LOAD zipfs;

COPY (
    WITH

    raw_lines AS (
        SELECT line
        FROM
            read_csv(
                getvariable('cotahist_path'),
                auto_detect = false,
                columns = { 'line': varchar },
                delim = '\n',
                encoding = 'CP1252',
                header = false
            )
        WHERE line.starts_with('01')  -- Drop first and last lines
    ),

    records AS (
        SELECT
            cast(strptime(substr(line, 3, 8), '%Y%m%d') AS DATE) AS data,
            substr(line, 13, 12).trim() AS codneg,
            substr(line, 25, 3) AS tpmerc,
            cast(substr(line, 109, 13) AS FLOAT) / 100.0 AS preult
        FROM raw_lines
    )

    SELECT
        data,
        codneg,
        preult
    FROM records
    WHERE tpmerc = '010'  -- Mercado à vista
    ORDER BY data, codneg
)

TO (getvariable('destination_path'));
