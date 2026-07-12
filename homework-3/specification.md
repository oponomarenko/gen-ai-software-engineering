# Real-Time Fraud Detection Scoring Service — Specification

> Ingest the information from this file, implement the Low-Level Tasks, and generate the code that will satisfy the High- and Mid-Level Objectives. This is a **specification-only** artifact: it defines *what* to build and *how well/how safely*, not a finished implementation.

---

## High-Level Objective

- Build a **real-time, inline fraud detection scoring service** that, during card transaction authorization, returns a normalized **risk score (0–1000)** with **human-readable reason codes** fast enough to sit inside the authorization path.
- **Scope boundary (single sentence):** the service *produces and explains a risk score for a single authorization request*; it does **not** decide approve/challenge/deny, does **not** apply any fraud action, and does **not** own a case-management workflow — those consuming systems and the ML model itself are **external dependencies**, out of scope for this specification.

---

## Stakeholders

| Stakeholder | Relationship to this service | Primary interests |
|-------------|------------------------------|-------------------|
| **End-user (cardholder)** | Indirect — the score is computed on their auth | Low latency (no perceptible checkout delay), high availability, low false-positive impact on legitimate spend |
| **Consuming decision system** | Caller — receives the score, makes the block/challenge/deny decision | Stable score contract, predictable latency, clear degradation signaling |
| **Internal Ops / Compliance** | Auditors and operators of the scoring service | Immutable audit trail of every score, reason-code explainability, model/config version traceability, governed thresholds, PII-safe logs |
| **Fraud/Risk analyst** | Reads scores + reason codes for investigations | Reproducibility of a past score, feature snapshot per score |

---

## Mid-Level Objectives

Each objective is **observable** — it states what changes in the world when the service works.

- **MO-1 — Score inline within budget.** Every authorization request receives a score + reason codes synchronously, within the latency budget (see NFR-1), before the caller's auth decision window closes.
- **MO-2 — Deterministic & idempotent scoring.** The same request (same idempotency key + same feature snapshot + same model/config version) always yields the same score; retries never double-write audit records or produce divergent scores.
- **MO-3 — Full audit & explainability.** Every score produced is written to an immutable audit log with its reason codes, feature snapshot reference, and inputs sufficient to reconstruct *why* the score was assigned.
- **MO-4 — Version traceability.** Every score records the exact **model version** and **scoring-config/threshold version** used, so any historical score is reproducible and attributable.
- **MO-5 — Graceful degradation (fail-open).** When a dependency (model endpoint, feature store) is slow or down, the service returns within budget with a **degraded** score marked `SCORE_UNAVAILABLE`/`DEGRADED`, never blocking the auth path, and emits an alert.
- **MO-6 — Data protection & access control.** No PAN/CVV/track data is ever persisted or logged; card references are tokenized. Read access to scores and feature snapshots is role-restricted and itself audited.
- **MO-7 — Governed configuration.** Scoring thresholds, reason-code taxonomy, and feature weights are versioned, change-controlled (dual-control approval), and every change is audited — no hot-editing of risk logic without a trail.

---

## Non-Functional & Policy Requirements

Numbers marked **(assumed target)** are hypothetical but justified for FinTech inline-auth UX; they are budgets/ranges, not aspirations.

- **NFR-1 — Latency.** End-to-end service time **p50 ≤ 80 ms, p95 ≤ 180 ms, p99 ≤ 250 ms** (assumed target). Rationale: card networks expect an auth decision within a low-hundreds-of-ms envelope; the scorer is one hop inside that, so it must leave headroom for the caller. A hard internal **deadline of 300 ms** triggers the fail-open path.
- **NFR-2 — Throughput.** Sustain **1,500 scores/sec** steady with burst to **4,000/sec** (assumed target), horizontally scalable, no single-instance bottleneck.
- **NFR-3 — Availability.** **99.95%** monthly for the scoring endpoint (assumed target). Degraded (fail-open) responses count as *available* — the endpoint answered in time.
- **NFR-4 — Feature-lookup budget.** Feature assembly (store reads + derivations) **≤ 60 ms p95** (assumed target); anything slower is skipped with a `FEATURE_STALE`/`FEATURE_MISSING` reason code rather than blowing the deadline.
- **NFR-5 — Security.** No PAN, CVV, expiry, or full track data persisted or logged anywhere; only a network/vault **card token** and a truncated masked form (`************1234`) are permitted. TLS in transit; encryption at rest for score store and audit log. Least-privilege service identity.
- **NFR-6 — Privacy & retention.** Feature snapshots and scores retained per policy (**assumed 400 days** to cover dispute/chargeback windows + regulatory audit), then purged; PII minimized to what scoring needs. GDPR/CCPA data-subject requests resolvable via token linkage.
- **NFR-7 — Audit/logging.** Every score → one **append-only, tamper-evident** audit record. Audit log is write-once; no update/delete API. Every *read* of scores/snapshots by a human is itself logged.
- **NFR-8 — Reliability & consistency.** Scoring is **read-only** with respect to customer money — it never moves funds. Config/threshold changes are **read-your-writes within ≤ 5 s** across all scoring instances (assumed target); until propagated, the prior config version is used and recorded.
- **NFR-9 — Observability.** Golden signals per instance (latency histogram, error rate, degraded-rate, deadline-exceeded count, model-call latency, feature-lookup latency) exported for SLO alerting.

---

## Implementation Notes (guardrails an agent must not violate)

- **Language/stack:** Python 3.12+, FastAPI for the service surface, Pydantic v2 for request/response models, `asyncio` for concurrent feature + model calls. (Conventions only — no code is delivered here.)
- **Money:** all monetary amounts handled as `Decimal`, never `float`. Amounts carry an explicit ISO-4217 currency; no cross-currency math without an explicit rate reference.
- **Identifiers:** card references are **tokens**, never PAN. Masked display form only in any human-facing field. All IDs are opaque strings; do not encode PII in IDs.
- **Idempotency:** the caller supplies an `idempotency_key` (e.g. auth attempt id). Re-submitting the same key returns the *original* score without recomputation or a second audit write. Keys retained ≥ 24 h.
- **Score normalization:** internal model output mapped to an integer **0–1000** band via the active scoring config; higher = riskier. Reason codes are a **closed, versioned taxonomy** (e.g. `VELOCITY_HIGH`, `GEO_MISMATCH`, `AMOUNT_ANOMALY`, `NEW_DEVICE`, `MERCHANT_RISK`), max N codes per score, ordered by contribution.
- **Model contract:** the external model is called over a versioned interface; the service pins a `model_version` and never silently follows a model change. Model I/O is validated; malformed model output → degraded path, not a crash.
- **Error semantics:** distinguish **client errors** (invalid request → 4xx, no score, audited as rejected) from **degradation** (dependency failure → 200 with degraded score + reason code). The service never returns a 5xx to the auth path for a *dependency* problem — that is the fail-open contract.
- **Determinism:** no wall-clock or RNG inside scoring logic that would make the same inputs score differently; any time-based feature is derived from the request's event timestamp and the pinned feature snapshot.
- **Fail-open policy (confirmed):** on model/feature timeout or error, return a degraded score (documented default value + `DEGRADED`/`SCORE_UNAVAILABLE` reason) so the caller can proceed; emit a high-priority alert; record the degradation in the audit log. Fail-closed is documented as the rejected alternative (see Edge Cases).
- **Config governance:** thresholds/taxonomy/weights live in a versioned config artifact; changes require dual-control approval and produce an audit record; the running score always records which config version it used.
- **No side effects on money or accounts.** The service must not write to ledgers, cards, or customer records.

---

## Context

### Beginning context (exists before work starts — hypothetical but specific)

- **Authorization gateway** that calls this service synchronously with an auth request (token, amount, currency, merchant, device/geo signals, timestamp, `idempotency_key`).
- **Feature store** (low-latency read API) keyed by card token / customer token, returning behavioral + velocity features with freshness timestamps.
- **External fraud model endpoint** (versioned) that maps a feature vector to a raw risk output.
- **Scoring config store** holding versioned thresholds, reason-code taxonomy, and weights.
- **Immutable audit log sink** (append-only).
- **Secrets/identity provider** for service auth and least-privilege access.
- **Empty repository** for this service (no code yet).

### Ending context (exists after the tasks are complete)

- A documented FastAPI scoring service with a stable `/score` contract (spec + API schema; **as documentation**, not required to run).
- Pydantic request/response models and the reason-code taxonomy definition.
- Feature-assembly, model-call, normalization, and degradation modules (specified with acceptance criteria).
- An immutable audit-record schema and access-control model.
- A verification package: unit/integration/e2e test *categories*, fixtures, and reconciliation checks (documented).
- Config-governance and versioning documentation.
- Observability/SLO definition doc.

---

## Low-Level Tasks

Each task ties back to a Mid-Level Objective and ends with **Acceptance Criteria (DoD)**. Tasks are intentionally small and numerous to show real decomposition.

### 1. Define the scoring request/response contract  *(MO-1, MO-3)*
- **Prompt:** "Create the Pydantic v2 models for the fraud scoring request and response, including idempotency key, tokenized card reference, Decimal amount + ISO-4217 currency, merchant/device/geo signals, event timestamp; and a response with integer score 0–1000, ordered reason codes, model_version, config_version, and a `degraded` flag."
- **File:** `app/models/scoring.py`
- **Function/class:** `ScoreRequest`, `ScoreResponse`, `ReasonCode`
- **Details:** amounts as `Decimal`; card ref must be a token pattern, PAN rejected by validation; reason codes constrained to the versioned enum; response always carries `model_version`, `config_version`, `degraded`.
- **Acceptance Criteria:** submitting a PAN-shaped card field is rejected with 4xx; a valid request round-trips; response schema always includes version fields and `degraded`.

### 2. Implement the `/score` endpoint skeleton with deadline enforcement  *(MO-1, MO-5)*
- **Prompt:** "Create the FastAPI POST `/score` endpoint that enforces a 300 ms internal deadline, orchestrates feature assembly and model call concurrently, and guarantees a response within budget."
- **File:** `app/api/score.py`
- **Function/class:** `post_score`
- **Details:** use `asyncio.wait_for`/deadline propagation; on deadline breach, take the fail-open path (Task 8); never raise a 5xx for dependency slowness.
- **Acceptance Criteria:** a simulated slow dependency (>300 ms) still returns 200 within budget with `degraded=true`; a fast path returns a normal score.

### 3. Implement idempotency handling  *(MO-2)*
- **Prompt:** "Add idempotency so the same `idempotency_key` returns the original score without recomputation or a second audit write."
- **File:** `app/services/idempotency.py`
- **Function/class:** `get_or_reserve`, `store_result`
- **Details:** short-TTL (≥24 h) idempotency store; concurrent duplicates resolve to a single computation.
- **Acceptance Criteria:** two concurrent identical requests produce one audit record and one identical score; a repeat after completion returns the stored score.

### 4. Implement feature assembly with freshness + budget  *(MO-1, MO-2, NFR-4)*
- **Prompt:** "Assemble the feature vector from the feature store within a 60 ms p95 budget, attaching freshness timestamps and marking stale/missing features."
- **File:** `app/services/features.py`
- **Function/class:** `assemble_features`
- **Details:** parallel reads; if a feature exceeds staleness threshold → mark `FEATURE_STALE`; if missing → `FEATURE_MISSING`; snapshot the exact feature set used for reproducibility.
- **Acceptance Criteria:** a stale feature yields the correct reason code and does not blow the deadline; the returned snapshot is persisted/reference-able for later reconstruction.

### 5. Implement the external model client with version pinning  *(MO-4, MO-5)*
- **Prompt:** "Create a client that calls the external fraud model at a pinned `model_version`, validates output, and fails safe on error/timeout."
- **File:** `app/clients/model.py`
- **Function/class:** `ModelClient.score`
- **Details:** validate model output shape; malformed/timeout → raise a typed degradation error caught by the endpoint; record the `model_version` actually used.
- **Acceptance Criteria:** malformed model output triggers the degraded path (no crash); the pinned version is recorded on every response.

### 6. Implement score normalization + reason-code derivation  *(MO-3, MO-7)*
- **Prompt:** "Map raw model output to a 0–1000 integer using the active scoring config, and derive ordered reason codes from feature contributions."
- **File:** `app/services/normalize.py`
- **Function/class:** `normalize_score`, `derive_reason_codes`
- **Details:** normalization + taxonomy come from the versioned config; reason codes ordered by contribution, capped at N; deterministic for identical inputs.
- **Acceptance Criteria:** identical inputs → identical score + identical ordered reason codes; the applied `config_version` is recorded.

### 7. Implement the versioned scoring-config loader  *(MO-4, MO-7, NFR-8)*
- **Prompt:** "Load thresholds/taxonomy/weights from the versioned config store with read-your-writes propagation ≤5 s, falling back to the last-known-good version."
- **File:** `app/services/config.py`
- **Function/class:** `ConfigProvider.current`
- **Details:** cache with bounded staleness; record which `config_version` each score used; never fail scoring because config refresh failed — use last-known-good and flag it.
- **Acceptance Criteria:** a config update is observed within 5 s; a config-store outage falls back to last-known-good and records the version used.

### 8. Implement the fail-open degradation path  *(MO-5)*
- **Prompt:** "Implement fail-open: on any dependency timeout/error, return a documented degraded score with `DEGRADED`/`SCORE_UNAVAILABLE` reason, `degraded=true`, and emit a high-priority alert."
- **File:** `app/services/degrade.py`
- **Function/class:** `degraded_response`, `emit_degradation_alert`
- **Details:** degraded default score value defined in config; degradation still writes an audit record; alert carries which dependency failed.
- **Acceptance Criteria:** each simulated dependency failure produces a degraded 200 response, an audit record, and exactly one alert; the auth path is never blocked.

### 9. Implement the immutable audit writer  *(MO-3, NFR-7)*
- **Prompt:** "Write one append-only, tamper-evident audit record per score, capturing tokenized inputs, feature-snapshot reference, score, reason codes, model_version, config_version, degraded flag, and timing — with no PAN/CVV."
- **File:** `app/services/audit.py`
- **Function/class:** `write_score_audit`
- **Details:** append-only, no update/delete path; tamper-evidence (e.g. hash chaining); PII redaction enforced before write.
- **Acceptance Criteria:** an attempt to log a PAN is blocked; audit records are append-only; a stored record contains everything needed to reconstruct the score decision.

### 10. Implement RBAC + read-auditing for score/snapshot access  *(MO-6, NFR-7)*
- **Prompt:** "Restrict reads of scores and feature snapshots to authorized roles and log every human read."
- **File:** `app/services/access.py`
- **Function/class:** `authorize_read`, `log_read_access`
- **Details:** least-privilege roles (analyst/ops/compliance); every read produces an access-audit entry.
- **Acceptance Criteria:** an unauthorized role is denied; every authorized read produces an access-audit record.

### 11. Define the reason-code taxonomy as versioned config  *(MO-7)*
- **Prompt:** "Define the closed reason-code taxonomy and its version as governed config, with descriptions for ops/compliance."
- **File:** `config/reason_codes.yaml` (documentation)
- **Function/class:** taxonomy schema
- **Details:** each code has id, human description, and severity; taxonomy carries a version; adding/removing codes is change-controlled.
- **Acceptance Criteria:** scoring only emits codes present in the active taxonomy version; unknown codes are impossible by construction.

### 12. Implement config-change dual-control governance  *(MO-7, NFR-7)*
- **Prompt:** "Require dual-control approval for threshold/taxonomy/weight changes and audit each change with before/after and approvers."
- **File:** `app/services/config_governance.py`
- **Function/class:** `propose_change`, `approve_change`
- **Details:** proposer ≠ approver; change produces a new immutable config version + audit record.
- **Acceptance Criteria:** a self-approved change is rejected; an approved change yields a new version and an audit entry with both identities.

### 13. Define observability & SLO signals  *(NFR-1, NFR-3, NFR-9)*
- **Prompt:** "Emit golden-signal metrics (latency histogram, error rate, degraded rate, deadline-exceeded, model/feature latency) and define SLO alerts."
- **File:** `app/observability/metrics.py` + `docs/slo.md` (documentation)
- **Function/class:** metric definitions
- **Details:** metrics per instance; alert thresholds tied to NFR budgets (e.g. degraded-rate > 2% for 5 min).
- **Acceptance Criteria:** each documented metric maps to an NFR; each SLO has an alert rule.

### 14. Author verification fixtures & reconciliation check  *(all MOs — see Verification)*
- **Prompt:** "Create deterministic fixtures (normal, stale-feature, model-timeout, duplicate, invalid-amount, cold-start) and a reconciliation check that every score has exactly one audit record."
- **File:** `tests/fixtures/` + `docs/verification.md` (documentation)
- **Function/class:** fixture set + `reconcile_scores_to_audit`
- **Details:** fixtures cover the edge-case table; reconciliation asserts 1:1 score↔audit and no orphan/duplicate records.
- **Acceptance Criteria:** reconciliation finds zero mismatches on the fixture run; each edge-case fixture asserts its expected reason code + degraded flag.

---

## Edge Cases & Failure Modes

Scoped to inline fraud scoring. Each row states **expected behavior** and its **audit/compliance implication**.

| # | Situation | Expected behavior | Audit / compliance implication |
|---|-----------|-------------------|--------------------------------|
| E1 | **Model endpoint timeout/down** | Fail-open: degraded score, `SCORE_UNAVAILABLE`, `degraded=true`, alert | Degradation recorded; degraded-rate is an SLO; regulators can see auth was not silently blocked |
| E2 | **Feature store slow (> budget)** | Skip slow features, `FEATURE_STALE`/`FEATURE_MISSING`, score on what's available | Snapshot records which features were present; explains a lower-confidence score |
| E3 | **Feature store returns stale data** | Use with `FEATURE_STALE` reason if within tolerance; else treat as missing | Freshness timestamp stored; reproducibility preserved |
| E4 | **Duplicate / replayed auth (same idempotency key)** | Return original score, no recompute, no second audit write | Prevents double-counting; audit stays 1:1 |
| E5 | **Concurrent identical requests** | Single computation; both callers get the same score | No duplicate audit records; determinism upheld |
| E6 | **Invalid amount (≤ 0, non-Decimal, wrong currency)** | 4xx client error, no score produced | Rejection audited as invalid input; not counted as a score |
| E7 | **PAN/CVV present in request or attempted in a log** | Reject/redact before persistence; validation error on PAN in card field | Hard compliance stop; never persisted (NFR-5) |
| E8 | **New customer / cold start (no history)** | Score with cold-start reason (`NEW_ACCOUNT`), no crash on missing features | Explains score; flags low-data confidence for ops |
| E9 | **Config store unavailable during scoring** | Use last-known-good config, record that version | Version traceability maintained; no risk logic hot-changed silently |
| E10 | **Malformed model output** | Treat as model failure → degraded path | Distinguished from valid low/high scores in audit |
| E11 | **Unauthorized read of a score/snapshot** | Deny; log the denied attempt | Access audit supports least-privilege compliance |
| E12 | **Clock skew / late event timestamp** | Use event timestamp from request for time-based features (determinism), not wall clock | Reproducible scores independent of processing time |
| E13 | **Deadline exceeded overall** | Fail-open degraded response within budget | `deadline_exceeded` metric; SLO signal |
| E14 | **Fraud-ish velocity spike (many auths, short window)** | High score + `VELOCITY_HIGH`; still returns in budget | Reason code gives ops an explainable signal |
| E15 | **Downstream ledger/account write attempted** | Impossible by design — service is read-only w.r.t. money | Guarantees no side effects; simplifies audit scope |

> **Rejected alternative — fail-closed:** blocking the auth when the scorer/model is unavailable was considered and rejected: an inline dependency outage would deny legitimate spend at scale, harming cardholders and merchants more than the fraud risk of a brief degraded window. Fail-open + alerting + degraded-flag is the chosen policy (NFR-3, MO-5).

---

## Verification

How we know each Mid-Level Objective is met.

| Objective | Verification method |
|-----------|---------------------|
| **MO-1 (inline/budget)** | Latency tests asserting p95/p99 within NFR-1 on the fixture load; deadline test (Task 2). |
| **MO-2 (deterministic/idempotent)** | Same-input-same-output test (Task 6); concurrent-duplicate test (Task 3); reconciliation 1:1 (Task 14). |
| **MO-3 (audit/explainability)** | Every fixture score asserts a matching audit record with reason codes + snapshot ref; PAN-in-log test fails safe (Task 9). |
| **MO-4 (version traceability)** | Assert `model_version` + `config_version` present on every score; reproduce a past score from its snapshot + versions. |
| **MO-5 (fail-open)** | Fault-injection tests for model/feature/config/deadline (E1, E2, E9, E13) each yield degraded 200 + alert + audit. |
| **MO-6 (data protection/RBAC)** | PAN rejection test (E7); RBAC allow/deny + read-audit tests (Task 10). |
| **MO-7 (governed config)** | Dual-control test (Task 12); taxonomy-closure test (Task 11); config version recorded per score. |

**Test categories (as documentation):**
- **Unit:** normalization, reason-code derivation, validators, idempotency logic, redaction.
- **Integration:** endpoint + feature store + model client + audit writer with stubbed dependencies; degradation paths.
- **E2E (documented):** full `/score` call through the fixture set, asserting contract + audit + timing.
- **Reconciliation:** score↔audit 1:1; no orphan/duplicate audit records; version fields non-null.
- **Compliance review checkpoints:** manual sign-off that no PII is persisted, audit is append-only, and config changes are dual-controlled.

**Fixtures:** normal, stale-feature, missing-feature, model-timeout, malformed-model-output, duplicate-key, concurrent-duplicate, invalid-amount, PAN-present, cold-start, config-outage, velocity-spike.

---

## Expected Performance

All values **(assumed target)** — hypothetical but justified for inline FinTech auth.

| Metric | Target | Why reasonable |
|--------|--------|----------------|
| Service latency p50 / p95 / p99 | 80 / 180 / 250 ms | The scorer is one hop inside the card network's low-hundreds-ms auth envelope; must leave headroom for the caller's decision + network. |
| Hard internal deadline | 300 ms → fail-open | Guarantees the auth path is never held hostage by a slow dependency. |
| Feature-assembly p95 | ≤ 60 ms | Leaves ~2/3 of the budget for model call + normalization + audit. |
| Throughput (steady / burst) | 1,500 / 4,000 scores/sec | Reflects a mid-size issuer's daytime auth volume with holiday-peak bursts. |
| Availability | 99.95% / month | Inline dependency; degraded responses count as available (they answer in time). |
| Degraded-rate SLO | < 2% sustained | Above this, the model/feature dependency needs attention; alertable. |
| Config read-your-writes | ≤ 5 s across instances | Risk-logic changes must take effect quickly but consistently; until then, prior version is used and recorded. |
| Idempotency key retention | ≥ 24 h | Covers retry/replay windows within an auth lifecycle. |
| Audit / snapshot retention | ~400 days | Covers chargeback/dispute windows plus regulatory audit lookback. |

---

## Traceability Summary

- **MO-1** → Tasks 1, 2, 4, 13 · NFR-1, NFR-4 · Verification (latency) · Edge E13
- **MO-2** → Tasks 3, 6, 14 · Edge E4, E5, E12
- **MO-3** → Tasks 1, 6, 9, 14 · NFR-7 · Edge E7
- **MO-4** → Tasks 5, 6, 7 · Edge E9, E10
- **MO-5** → Tasks 2, 5, 8 · NFR-3 · Edge E1, E2, E13 · fail-open policy
- **MO-6** → Tasks 1, 9, 10 · NFR-5, NFR-6 · Edge E7, E11
- **MO-7** → Tasks 6, 7, 11, 12 · NFR-8 · Edge E9
