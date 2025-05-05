INSERT INTO markets.stg_dim_markets (id, name, short_name, status)
SELECT
    market.value:id::STRING,
    market.value:name::STRING,
    market.value:shortName::STRING,
    market.value:status::STRING
FROM markets.stage_raw
    , LATERAL FLATTEN(input => raw_data:markets) AS market;