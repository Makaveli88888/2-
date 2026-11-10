# JOKER Guardian Angel — Core v1

## Security boundary

Guardian Angel is the independent, fail-closed policy gate for proposed paper actions. A request is eligible for a paper reservation only when every mandatory rule passes. PAPER is a simulation mode, not a control bypass. The live order executor is intentionally a permanent stub that raises RuntimeError for every operation.

## Implemented controls

- Explicit PAPER-only mode; all other modes are denied.
- Market allow-list; an empty allow-list denies every market.
- Calibrated-confidence threshold.
- Order-book depth is mandatory; missing or insufficient depth denies the request.
- Per-market and total exposure reservations are made atomically within one process.
- Daily and weekly PnL drawdown checks with UTC period rollover.
- Per-process rolling one-minute decision rate limit.
- Emergency kill switch; restoration requires an explicit authorized operator call.
- Paper trades retain exposure reservations until closed; closing records realized PnL and releases the reservation.
- Polymarket CLOB market-data wrapper exposes GET only, with bounded retry and local rate limiting.
- Event extraction treats source text as untrusted data and validates structured output plus source hash.

## Important deployment limitations

The current exposure, PnL, rate-limit, and kill-switch state is in process memory. It is suitable for the initial single-process test harness only. It is NOT a multi-worker or production-grade financial control. Before multi-worker deployment, move reservations, PnL ledger, idempotency, kill-switch state, and rate limiting into shared transactional storage (preferably PostgreSQL with atomic transactions/row locks or a carefully designed Redis primitive). Persist policy versions, approvals, decisions, and audit events. Add signed, expiring approvals bound to canonical action hashes before any future side-effecting executor is considered.

The public market-data client is read-only and does not submit, sign, amend, or cancel orders. Event extraction is an untrusted candidate generator, not a probability model, recommendation, risk approval, or execution permission. Prompt instructions reduce but cannot eliminate prompt injection; output validation and downstream policy checks remain mandatory.

## Running tests

    python -m compileall -q app tests
    python -m unittest discover -s tests -v

No live trading capability is implemented or enabled.
