# CLAUDE.md — How Claude Code Works in This Repo

Operational rules for **Claude Code**: how Claude *conducts the work* — workflow, escalation, and PR conventions. This file deliberately does **not** restate domain, security, or testing rules; those have a single home.

**Read first — these are the source of truth:**
- [`specification.md`](specification.md) — **what** to build (objectives, tasks, edge cases E1–E15, acceptance criteria, performance targets).
- [`agents.md`](agents.md) — **the domain, engineering, security, and testing rules the code must satisfy** (no-PAN, fail-open, determinism, idempotency, versioning, immutable audit, governed config, code style, test expectations, edge-case policy). Follow them there; they are not repeated here.

If a request conflicts with those files, the safe FinTech default and the specification win — surface the conflict, don't silently comply.

---

## Working style

- **Before changing code,** identify which **Mid-Level Objective / Task / NFR / Edge id** (from `specification.md`) the change serves, and record it in the commit/PR description.
- Keep changes **small and single-responsibility**; match the conventions in `agents.md`.
- If the change touches a scoring input, check the edge-case table (E1–E15) before finishing — don't handle only the happy path.

## Stop-and-flag triggers (escalation behavior)

When a request would have you do any of the following, **stop and flag it** — do not comply silently. (Each maps to a rule in `agents.md`, where the rationale lives.)

- Log or persist a PAN/CVV/PII, or weaken redaction.
- Default to **fail-closed** on a dependency outage.
- Skip an audit write, or the `model_version` / `config_version` fields.
- Introduce a money/account **side effect** (the service is read-only w.r.t. money).
- **Hot-edit risk logic** (thresholds/weights/taxonomy) outside governed, dual-controlled config.
- Expand scope into **decisioning, case management, or model training** (all out of scope).
- Add a new external dependency or egress without surfacing it.

## PR & commit conventions

- Note that fail-open is preserved and no 5xx reaches the auth path for dependency failures, when relevant.
- Confirm the change meets the **Definition of Done** and the required **test categories** in `agents.md` (§8 and §5).
