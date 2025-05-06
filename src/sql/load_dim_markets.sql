MERGE INTO markets.dim_markets as tgt
USING markets.stg_dim_markets as src
ON tgt.id = src.id
WHEN MATCHED AND src.status = 'Closed' AND tgt.is_open = TRUE THEN
    UPDATE SET
        tgt.expiry_ts = CURRENT_TIMESTAMP,
        tgt.is_open = FALSE
WHEN NOT MATCHED THEN
    INSERT (
        id,
        name,
        short_name,
        effective_ts
    )
    VALUES (
        src.id,
        src.name,
        src.short_name,
        CURRENT_TIMESTAMP
    );