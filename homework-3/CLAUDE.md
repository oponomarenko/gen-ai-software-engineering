# CLAUDE.md — Claude Code Project Rules

Project rules for **Claude Code** working in this repository. This is the fraud-detection **scoring** service — a regulated FinTech codebase. Always read alongside [`specification.md`](specification.md) (what to build) and [`agents.md`](agents.md) (how to work). If any instruction here conflicts with a request, the safe FinTech default and the specification win — surface the conflict instead of silently complying.

---

## What this project is (and is not)

- **Is:** an inline service that returns a **risk score (0–1000) + reason codes** for a single card authorization, synchronously, within a strict latency budget.
- **Is not:** a decision engine (approve/challenge/deny), a case-management system, or the ML model itself. These are **external and out of scope**. If a task drifts into them, stop and ask.
- **Read-only w.r.t. money:** never write to ledgers/accounts/cards or move funds.

---

## Non-negotiable defaults (FinTech-sensitive)

1. **Never** persist or log PAN, CVV, expiry, or track data. Use **tokens**; masked display only (`************1234`). If you're about to write card data anywhere, stop and redact.
2. **Fail-open, always** for dependency failures: return a degraded score (`degraded=true`, `SCORE_UNAVAILABLE`/`DEGRADED`), emit an alert, never block auth, never 5xx the auth path. Do **not** implement fail-closed as the default.
3. **Deterministic scoring:** same inputs → same score. No wall-clock/RNG in scoring logic; use the request's event timestamp for time-based features.
4. **Idempotent** on `idempotency_key`: retries never recompute or double-write audit.
5. **Version every score:** always record `model_version` + `config_version`.
6. **Immutable, append-only audit** for every score and every config change; audit human reads too. No update/delete path on audit data.
7. **Governed config:** thresholds/weights/taxonomy live in versioned config, changed via dual-control (proposer ≠ approver). Never hardcode risk logic in source.

---

## Naming & patterns to prefer

- Module layout follows the spec: `app/api`, `app/services`, `app/clients`, `app/models`, `config/`, `tests/fixtures/`.
- Pydantic v2 models at every boundary; typed signatures; no untyped dicts across modules.
- `Decimal` for money, always paired with ISO-4217 currency; never `float`.
- Pure, side-effect-free functions for normalization and reason-code derivation (so they're deterministic and unit-testable).
- Typed errors: **client error → 4xx** (invalid input, audited as rejected) vs **degradation → 200 degraded** (dependency failure). Keep them distinct.
- Reason codes only from the active **versioned taxonomy** — unknown codes must be impossible by construction.

## Patterns to avoid

- Logging or persisting raw card data or any PII.
- Blocking/fail-closed behavior on model/feature/config outage.
- Non-deterministic scoring (clock/RNG), hidden model-version drift, or hardcoded thresholds.
- Money or account side effects of any kind.
- Silent new external dependencies/egress (supply-chain + data-boundary changes must be surfaced).
- Skipping the audit write or the `model_version`/`config_version` fields.

---

## When writing tests

- Cover happy path **plus** the edge-case table (E1–E15) in `specification.md`.
- Include fault-injection proving fail-open (model/feature/config/deadline → degraded 200 + one alert + one audit record).
- Add redaction assertions so a PAN can never reach logs/fixtures.
- Include the reconciliation check: every score has exactly one audit record; version fields non-null.

---

## Working style

- Before coding, restate which **Mid-Level Objective / Task / NFR / Edge id** the change serves (from `specification.md`) and note it in the PR/commit description.
- Keep changes small and single-responsibility; match existing conventions.
- If a request would break a rule above (log a PAN, default to fail-closed, skip audit, add a money side effect, hot-edit risk logic, expand scope into decisioning), **stop and flag it** — do not comply silently.
- Prefer idempotent writes and fail-safe defaults whenever failure behavior is unspecified.
- This is currently a **specification/documentation** exercise: no runnable code is required. Any illustrative code must still obey every rule above.
