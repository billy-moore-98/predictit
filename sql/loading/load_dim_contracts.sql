MERGE INTO markets.dim_contracts AS tgt
USING markets.stg_dim_contracts AS src
ON src.id = tgt.id
WHEN MATCHED AND src.date_end IS NOT NULL AND tgt.expiry_ts IS NULL THEN
    UPDATE SET
        tgt.expiry_ts = src.date_end,
        tgt.is_open = FALSE
WHEN NOT MATCHED THEN
    INSERT (
        id,
        market_id,
        name,
        short_name,
        effective_ts
    )
    VALUES (
        src.id,
        src.market_id,
        src.name,
        src.short_name,
        CURRENT_TIMESTAMP
    );