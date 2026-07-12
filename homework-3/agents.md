# agents.md — AI Agent Guidelines for the Fraud Detection Scoring Service

> These rules configure any AI coding partner (Claude Code in particular) working in this repository. They make the agent behave consistently and safely for a **regulated FinTech** codebase. Read this together with [`specification.md`](specification.md). Where they overlap, the specification is the source of truth for *what* to build; this file governs *how* the agent works.

---

## 1. Project context the agent must assume

- **Domain:** real-time, inline **fraud detection scoring** at card authorization time.
- **What the service does:** produces a normalized **risk score (0–1000) + reason codes** for a single authorization, synchronously, within a strict latency budget.
- **What the service does NOT do (do not build these):** it does **not** decide approve/challenge/deny, does **not** apply fraud actions, does **not** own case management, and does **not** train or host the ML model. Those are external systems. If asked to add them, flag the scope boundary and stop.
- **Read-only w.r.t. money:** the service must never write to ledgers, accounts, cards, or move funds. Reject any task that would introduce a money/account side effect.

---

## 2. Tech stack assumptions

- **Language:** Python 3.12+.
- **Service framework:** FastAPI; **validation:** Pydantic v2.
- **Concurrency:** `asyncio`; feature and model calls run concurrently under a shared deadline.
- **Money:** `decimal.Decimal` only — never `float` for monetary amounts.
- **Testing:** `pytest` (+ `pytest-asyncio`); fixtures under `tests/fixtures/`.
- **Formatting/lint:** `ruff` + `black`; type-checked with `mypy` (strict on new modules).
- **Config:** versioned config artifacts (YAML) for thresholds, weights, reason-code taxonomy — never hardcode risk logic in source.

> This is a spec/documentation exercise; no runnable code is required. When generating illustrative code, keep it consistent with these conventions.

---

## 3. Banking / domain rules (non-negotiable)

- **Never persist or log** PAN, CVV, expiry, or full track data. Card references are **tokens**; display uses masked form only (`************1234`).
- **Determinism:** identical inputs (same idempotency key + feature snapshot + model/config version) must yield an identical score. No wall-clock or RNG inside scoring logic; time-based features derive from the request's event timestamp.
- **Idempotency:** writes and scoring are idempotent on `idempotency_key`. Retries never recompute or double-write audit records.
- **Fail-open (confirmed policy):** on model/feature/config timeout or error, return a **degraded** score (`degraded=true`, `SCORE_UNAVAILABLE`/`DEGRADED` reason) within budget and emit an alert. Never block the auth path for a dependency failure. Never return 5xx to the auth path for a dependency problem. (Fail-closed is the documented rejected alternative — do not implement it as the default.)
- **Version everything that affects a score:** every response and audit record carries `model_version` and `config_version`.
- **Immutable audit:** every score → one append-only, tamper-evident audit record. No update/delete path on audit data. Every human read of scores/snapshots is itself audited.
- **Governed config:** threshold/taxonomy/weight changes require dual-control (proposer ≠ approver) and produce a new versioned artifact + audit record.

---

## 4. Code style & conventions

- Small, single-responsibility modules matching the layout in `specification.md` (`app/api`, `app/services`, `app/clients`, `app/models`).
- Explicit, typed function signatures; Pydantic models at the boundary; no untyped dicts crossing module lines.
- Errors are typed and meaningful: distinguish **client errors** (invalid input → 4xx, audited as rejected) from **degradation** (dependency failure → 200 degraded). Do not conflate them.
- No secrets, tokens, or PII in code, comments, logs, test fixtures, or commit messages.
- Prefer pure functions for scoring/normalization so they are trivially testable and deterministic.
- Currency-aware money handling; amounts always paired with an ISO-4217 currency.

---

## 5. Testing & verification expectations

- Every new behavior ships with tests. Cover **happy path + the edge cases** in the `specification.md` edge-case table (E1–E15).
- Required categories: **unit** (normalization, reason codes, validators, redaction, idempotency), **integration** (endpoint + stubbed dependencies + audit), **degradation/fault-injection** (model/feature/config/deadline), **reconciliation** (score↔audit 1:1, no orphans/duplicates, version fields non-null).
- Fault-injection tests must prove fail-open: each simulated dependency failure yields a degraded 200 + one alert + one audit record, and never blocks.
- A test that could leak a PAN into logs/fixtures is a bug — add a redaction assertion instead.
- Latency-sensitive logic (Tasks 2, 4) includes tests asserting the deadline path.

---

## 6. Security & compliance constraints

- Least-privilege service identity; TLS in transit; encryption at rest for score store and audit log.
- RBAC on all reads of scores/snapshots; deny-by-default; log allowed **and** denied reads.
- PII minimization; retention per policy (~400 days), then purge; data-subject requests resolvable via token linkage.
- No new external egress or dependency without explicitly noting it — supply-chain and data-boundary changes must be surfaced, not silently added.

---

## 7. How the agent should handle edge cases & ambiguity

- When a task touches a scoring input, **always** consider: stale/missing feature, model timeout, duplicate key, invalid amount, PAN present, cold-start, config outage, clock skew. Map each to the expected behavior in the edge-case table.
- Prefer **idempotent writes** and **fail-safe defaults** whenever behavior under failure is unspecified.
- If a request would violate a rule in this file (log a PAN, add a money side effect, implement fail-closed as default, skip audit, hot-edit risk logic), **stop and flag it** rather than complying.
- If scope is unclear or the request drifts toward decisioning/case-management/model-training, **ask** rather than guessing — those are out of scope.
- Cite the relevant `specification.md` section (MO/NFR/Task/Edge id) in PR descriptions so reviewers can trace changes to requirements.

---

## 8. Definition of done for any change

- [ ] Ties to a Mid-Level Objective / Task / NFR in `specification.md` (referenced by id).
- [ ] Tests cover happy path + relevant edge cases; fault-injection where applicable.
- [ ] No PAN/CVV/PII in code, logs, fixtures, or commits.
- [ ] `model_version` + `config_version` recorded where a score is produced.
- [ ] Audit record written (append-only) for any score or config change.
- [ ] Fail-open preserved; no 5xx to the auth path for dependency failures.
- [ ] Latency budget respected for inline paths.
