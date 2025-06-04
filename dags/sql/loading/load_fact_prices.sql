INSERT INTO markets.fact_prices
SELECT
    market.value:id::INT AS market_id,
    contract.value:id::INT AS contract_id,
    CURRENT_TIMESTAMP AS trade_timestamp,
    contract.value:lastTradePrice::FLOAT AS last_trade_price,
    contract.value:bestBuyYesCost::FLOAT AS best_buy_yes_cost,
    contract.value:bestBuyNoCost::FLOAT AS best_buy_no_cost,
    contract.value:bestSellYesCost::FLOAT AS best_sell_yes_cost,
    contract.value:bestSellNoCost::FLOAT AS best_sell_no_cost,
    contract.value:lastClosePrice::FLOAT AS last_close_price
FROM markets.stage_raw
    , LATERAL FLATTEN(input => raw_data:markets) AS market
    , LATERAL FLATTEN(input => market.value:contracts) AS contract;