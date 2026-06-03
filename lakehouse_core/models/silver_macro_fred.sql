{{ config(materialized='view') }}

WITH source_data AS (
    SELECT * FROM {{ source('oracle_adw', 'bronze_macro_fred') }}
)

SELECT 
    TO_DATE(jt.observation_date, 'YYYY-MM-DD') AS record_date,
    CAST(jt.fed_funds_rate AS NUMBER) AS interest_rate
FROM source_data b,
JSON_TABLE(
    b.json_document,
    '$.observations[*]'
    COLUMNS (
        observation_date VARCHAR2(10) PATH '$.date',
        fed_funds_rate   VARCHAR2(20) PATH '$.value'
    )
) jt
