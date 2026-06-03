{{ config(materialized='view') }}

WITH silver_data AS (
    SELECT * FROM {{ ref('silver_macro_fred') }}
)

SELECT 
    record_date,
    interest_rate,
    interest_rate - LAG(interest_rate, 1) OVER (ORDER BY record_date) AS mom_change_bps,
    ROUND(AVG(interest_rate) OVER (
        ORDER BY record_date 
        ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
    ), 2) AS rolling_12m_avg
FROM silver_data
