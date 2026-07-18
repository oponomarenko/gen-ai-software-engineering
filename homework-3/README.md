# Homework 3 — Specification-Driven Design: Real-Time Fraud Detection Scoring

## Student & Task Summary

- **Student:** Oleksandr Ponomarenko
- **Homework:** #3 — Specification-Driven Design (no implementation).
- **Chosen feature:** a **real-time, inline fraud detection scoring service** for card authorization.
- **AI tool targeted:** **Claude Code** (project rules delivered as [`CLAUDE.md`](CLAUDE.md)).
- **What I delivered:** a layered specification package — a spec team and an AI agent could execute it without guessing — plus agent guidelines and Claude Code rules. The graded artifact is the specification and its traceability from goals → tasks, with edge cases, verification, and performance treated as first-class.

### Deliverables in this folder

| File | Purpose |
|------|---------|
| [`specification.md`](specification.md) | The layered spec: objectives → non-functional/policy → implementation notes → context → low-level tasks, with edge-cases, verification, and performance integrated. |
| [`agents.md`](agents.md) | AI agent guidelines: stack, banking domain rules, style, testing/verification, security/compliance, edge-case handling. |
| [`CLAUDE.md`](CLAUDE.md) | How Claude Code *operates* here: working style, stop-and-flag escalation triggers, PR/commit conventions. Defers to `agents.md` for domain rules (no duplication). |
| `README.md` | This file — rationale and industry best-practice mapping. |

### Scope in one line

The service **produces and explains a risk score (0–1000) for a single authorization**; it does **not** decide approve/challenge/deny, apply fraud actions, or run case management — and the ML model is an external dependency. This deliberate narrow boundary is what makes the spec tractable and deeply specified rather than broad and shallow.

---

## Rationale — why the specification is written this way

- **Layering over prose.** I followed the banking template's skeleton in [`specification-TEMPLATE-example.md`](specification-TEMPLATE-example.md) (High-/Mid-level → Implementation Notes → Context → Low-level tasks in `prompt / file / function / details` form) and then went beyond it: I added a dedicated **Non-Functional & Policy** layer, a **Stakeholders** table, and standalone **Edge Cases**, **Verification**, and **Performance** sections. The template alone is too thin for a regulated feature.

- **Observable mid-level objectives.** Each of MO-1…MO-7 states *what changes in the world* (a score returned in budget, an audit record written, a version recorded), so each is directly verifiable — see the Verification table that maps every MO to a method.

- **Scope narrowed to "score only."** Fraud programs sprawl (decisioning, case queues, model training). By fixing the boundary at *scoring + explanation*, the spec can go deep on the hard parts — latency, determinism, degradation, auditability — instead of thin across many. The rejected fail-closed alternative and the excluded systems are stated explicitly so the boundary is intentional, not accidental.

- **How I chose the performance targets.** All numbers are labeled **(assumed target)** and justified in the Performance table: the scorer sits inside the card network's low-hundreds-of-milliseconds auth envelope, so I set **p99 ≤ 250 ms** with a hard **300 ms fail-open deadline** to leave the caller headroom, and gave feature assembly ≤ 60 ms so the model call + normalization + audit fit the rest. Throughput (1,500/4,000 tps), availability (99.95%), degraded-rate SLO (<2%), and retention (~400 days, to cover chargeback/dispute + audit lookback) were chosen the same way — defensible ranges tied to FinTech UX and ops reality, not round numbers.

- **How I chose verification depth.** Because this is regulated and inline, the risky behaviors are *failure* behaviors. So verification emphasizes **fault-injection** (each dependency failure must prove fail-open), **reconciliation** (score↔audit 1:1, version fields non-null), and **compliance checkpoints** (no PII persisted, append-only audit, dual-control config). Several low-level tasks end in checkable **Acceptance Criteria** so an implementer can tick them off.

- **`agents.md` vs `CLAUDE.md` — one home per concern.** To avoid repeating rules across files, `agents.md` is the single source of truth for the *domain, engineering, security, and testing rules the code must satisfy* (tool-agnostic), while `CLAUDE.md` covers only *how Claude Code operates* — working style, stop-and-flag escalation, and PR conventions — and defers to `agents.md` for the substance. Both files open with the same "division of responsibility" note so the boundary is explicit.

- **Traceability by construction.** The spec ends with a Traceability Summary mapping every MO → tasks + NFRs + edge cases, so nothing is orphaned and every task earns its place.

---

## Industry best practices — what I added and where it appears

| Best practice | Where it appears |
|---------------|------------------|
| **Fail-open for inline dependencies** (never block legitimate spend on a scorer outage) | `specification.md` → Implementation Notes, MO-5, NFR-3, Edge E1/E13, "rejected alternative" note; `agents.md` §3; `CLAUDE.md` Stop-and-flag triggers |
| **Never store/log PAN/CVV; tokenized card refs + masking** | `specification.md` → NFR-5, Edge E7, Tasks 1 & 9; `agents.md` §3; `CLAUDE.md` Stop-and-flag triggers |
| **Immutable, append-only, tamper-evident audit trail; audit reads too** | `specification.md` → MO-3, NFR-7, Tasks 9 & 10, Edge E11; `agents.md` §3/§6; `CLAUDE.md` Stop-and-flag triggers |
| **Idempotency on retries/replays** | `specification.md` → MO-2, Implementation Notes, Task 3, Edge E4/E5; `agents.md` §3 |
| **Determinism & reproducibility of scores** | `specification.md` → MO-2, Implementation Notes, Task 6, Edge E12; `agents.md` §3 |
| **Model & config version traceability** | `specification.md` → MO-4, Tasks 5/6/7, Edge E9/E10; `agents.md` §3; `CLAUDE.md` Stop-and-flag triggers |
| **Dual-control change governance for risk logic** | `specification.md` → MO-7, NFR-8, Tasks 11/12, Edge E9; `agents.md` §3; `CLAUDE.md` Stop-and-flag triggers |
| **Decimal money handling + ISO-4217 currency** | `specification.md` → Implementation Notes, Task 1, Edge E6; `agents.md` §2/§4 |
| **Least-privilege RBAC + deny-by-default on sensitive reads** | `specification.md` → MO-6, NFR-5, Task 10, Edge E11; `agents.md` §6 |
| **SLOs & golden-signal observability tied to budgets** | `specification.md` → NFR-1/3/9, Task 13, Performance table; `agents.md` §5 |
| **Data minimization & retention/purge (GDPR/CCPA-aware)** | `specification.md` → NFR-6; `agents.md` §6 |
| **Explainability via a closed, versioned reason-code taxonomy** | `specification.md` → MO-3, Implementation Notes, Task 11; `agents.md` §3/§4 |
| **Read-only w.r.t. money (no side effects on funds/accounts)** | `specification.md` → NFR-8, Edge E15; `agents.md` §1; `CLAUDE.md` Stop-and-flag triggers |
| **Graceful degradation with explicit stale/missing-feature handling** | `specification.md` → NFR-4, MO-5, Tasks 4/8, Edge E2/E3/E8 |

---

*No code was written for this homework, per the assignment. Depth, traceability from goals to tasks, and clarity of rationale and best practices are the intended contributions.*
