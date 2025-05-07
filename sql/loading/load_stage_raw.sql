TRUNCATE TABLE stage_raw;

COPY INTO stage_raw
FROM (
    SELECT
        $1,
        METADATA$FILENAME
    FROM @predictit_s3_stage/raw_data/market_data_{{ ts_nodash_with_t }}.json
    (FILE_FORMAT => predictit_json)
);