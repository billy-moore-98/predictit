TRUNCATE TABLE markets.stg_dim_contracts;

INSERT INTO markets.stg_dim_contracts (id, market_id, name, short_name, status, date_end)
SELECT
    contract.value:id::INT,
    market.value:id::INT,
    contract.value:name::STRING,
    contract.value:shortName::STRING,
    contract.value:status::STRING,
    CASE
        WHEN contract.value:dateEnd::STRING = 'NA' THEN NULL
        ELSE TO_TIMESTAMP_NTZ(contract.value:dateEnd::STRING)
    END
FROM markets.stage_raw
    , LATERAL FLATTEN (input => raw_data:markets) AS market
    , LATERAL FLATTEN (input => market.value:contracts) AS contract;