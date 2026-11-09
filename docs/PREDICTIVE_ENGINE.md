# JOKER PREDICTIVE ENGINE v0.1

## Scope

This release is a read-only Polymarket market-data collector plus a local paper-order simulator. It does not contain wallet credentials, CLOB authentication, order submission, cancellation, or redemption code.

## Data sources

- Gamma API: active market discovery and market metadata.
- Public CLOB API: individual outcome order-book snapshots.
- Public reads only; no API key is required for these endpoints.

## API

- `GET /api/predictive/health` — confirms paper-only mode.
- `GET /api/predictive/markets?limit=100&offset=0` — paginated market discovery.
- `POST /api/predictive/scan?pages=1&page_size=100&offset=0` — stores snapshots and returns consensus-momentum signals. Repeat with the returned `next_offset` to traverse the catalog in pages.
- `POST /api/predictive/paper/orders` — simulates a limit order against a fresh public book snapshot. It cannot submit a live order.

If `JOKER_API_TOKEN` is configured, all predictive routes require the existing Bearer authorization.

## Baseline model limitations

`consensus_momentum_baseline_v0.1` is a transparent heuristic: it compares the latest Gamma outcome price with the previous stored observation and projects half of that change forward. Its confidence field is an activity/liquidity heuristic, not a calibrated probability. The first observation has no prior momentum and is reported as flat.

This is not a trained ML model, reinforcement-learning policy, arbitrage guarantee, or investment recommendation. It requires historical data, walk-forward evaluation, calibration, fee/slippage modeling, and independent review before any strategy claims are made.

## Paper execution

The simulator walks the current public order-book levels and fills only at prices compatible with the requested limit. It reports filled, partial, or unfilled status. The paper ledger is stored in SQLite using WAL mode, FULL synchronous writes, and a SHA-256 chained record hash. This is tamper-evident within the local database, not a cryptographic guarantee against an administrator who can rewrite the entire database.

## Operational limits

- Scan is paginated and capped at 10 pages per request (up to 1,000 markets); continue using `next_offset` for larger catalogs.
- This version polls REST snapshots; WebSocket streaming is not yet implemented.
- Historical order-book depth is not reconstructed.
- Paper fills are estimates against one observed snapshot; they do not model queue priority, latency, cancellations, or market impact.
- No live trading path is present in this release.
