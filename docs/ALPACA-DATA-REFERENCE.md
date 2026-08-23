# Alpaca Data Reference — What We Have Access To
2026-08-23 · Free Basic plan · Verified working

## Confirmed Working Endpoints

### Stock Bars (OHLCV)
GET /v2/stocks/{symbol}/bars?timeframe=1Hour&start=2026-07-01&end=2026-08-23&limit=10000
Auth: APCA-API-KEY-ID + APCA-API-SECRET-KEY headers
Returns: {"bars": [{"t","o","h","l","c","v","n","vw"}], "next_page_token"}

Timeframes: 1Min | 1Hour | 1Day | 1Week | 1Month
Feed: iex (free) | sip (paid)
Adjustments: split, dividend, all

### Account
GET /v2/account -> {account_number, status: ACTIVE, cash: $100000, ...}

## Rate Limits
200 calls/min on Basic plan
Each call returns up to 10000 bars = 2M data points/min capacity

## Data Available
- US Stocks & ETFs since 2016
- Crypto (BTC, ETH etc)
- Options chains
- Trades (tick level)
- Quotes (bid/ask)

## For Cogym Worlds
Fetch daily or hourly bars for any symbol/date range.
Convert via csvio.py into Bar objects.
Feed into TradingWorld.
World is deterministic because historical data never changes.

Example verified:
AAPL hourly July-Aug 2026: ~500+ bars available
Price range confirmed from actual market data
