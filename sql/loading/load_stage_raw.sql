TRUNCATE TABLE stage_raw;

COPY INTO stage_raw
FROM (
    SELECT
        $1,
        METADATA$FILENAME
    FROM @predictit_s3_stage/raw_data/market_data_{{ params.execution_timestamp }}.json
    (FILE_FORMAT => predictit_json)
);