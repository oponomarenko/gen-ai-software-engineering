# 📐 Implementation Plan — Intelligent Customer Support System

> **Living document.** Update on any requirement change and mark phase progress here.
> **Status legend:** ⬜ Not started · 🟡 In progress · ✅ Done · ⛔ Blocked
> **Last updated:** 2026-07-04 (Phase 11 complete — all phases done)

---

## 0. Summary of TASKS.md

Build a customer-support ticket management system that:

1. **Multi-format import API** — REST CRUD for tickets + bulk import from CSV/JSON/XML,
   with full validation, correct HTTP status codes, and a per-record import summary.
2. **Auto-classification** — deterministic category + priority assignment with
   confidence, reasoning, and matched keywords; optional auto-run on create, manual
   override, decision logging.
3. **AI-generated test suite** — 8 test files (~56 tests) with **>85% coverage**.
4. **Multi-level documentation** — README, API_REFERENCE, ARCHITECTURE, TESTING_GUIDE
   (≥3 Mermaid diagrams total; different AI models for different doc types).
5. **Front-end** — React SPA: list+filter, create/edit, detail, bulk import,
   trigger classification, success/error feedback, responsive, API-driven only.
6. **Integration & performance tests** — lifecycle, import+classify, concurrency
   (20+), combined filtering; benchmarks.

**Deliverables:** source code, coverage report + screenshot (`docs/screenshots/test_coverage.png`),
UI screenshot (`docs/screenshots/ui.png`), sample data (50 CSV / 20 JSON / 30 XML +
invalid files).

### Locked technical decisions
- **Backend:** Python / FastAPI · **Frontend:** React (Vite + TS)
- **Structure:** `src/backend`, `src/frontend`, `src/tests`
- **Persistence:** in-memory repository (abstracted for future DB)
- **Classification:** rule-based keyword engine
- **Delivery:** local dev (`uvicorn` + `vite`) + `docker-compose`

---

## Phase 1 — Project Scaffolding & Tooling  ✅
**Goal:** runnable skeletons for both apps and a green CI-style test command.

- [x] Backend skeleton in `src/backend`: FastAPI app, `main.py`, `/health`, package layout from ARCHITECTURE §7.
- [x] Dependency + tooling setup: `pyproject.toml`/`requirements.txt` (fastapi, uvicorn, pydantic v2, python-multipart, defusedxml, pytest, pytest-cov, httpx), ruff/black optional.
- [x] Frontend skeleton in `src/frontend`: Vite + React + TS, base routing, API base-URL config via env.
- [x] `docker-compose.yml` (backend + frontend) and per-app `Dockerfile`s.
- [x] `.gitignore`, `.env.example`, CORS config.
- **Exit criteria:** `uvicorn` serves `/health`; `vite` serves a placeholder page; `docker-compose up` starts both; `pytest` runs (0 tests OK). ✅ Verified manually via preview servers + local `pytest --cov`.

## Phase 2 — Domain Models & Repository  ✅
**Goal:** validated data model and storage seam.

- [x] Enums: Category, Priority, Status, Source, DeviceType.
- [x] Pydantic models: `TicketMetadata`, `ClassificationResult`, `Ticket`, `TicketCreate`, `TicketUpdate`, `ImportSummary`.
- [x] Validation: email format, subject 1–200, description 10–2000, enum membership, timestamps.
- [x] `TicketRepository` interface + thread-safe `InMemoryTicketRepository`.
- **Exit criteria:** models validate/reject sample inputs; repository CRUD works in a REPL/unit test. ✅ Verified via ad-hoc script.

## Phase 3 — Ticket CRUD API  ✅
**Goal:** the core REST endpoints.

- [x] `TicketService` CRUD + filtering (category/priority/status, combinable).
- [x] Routers: POST/GET(list)/GET(id)/PUT/DELETE with status codes 201/200/200/200/204.
- [x] Central error handling → 400/404/422 with structured messages.
- **Exit criteria:** all CRUD + filter endpoints work via `/docs` and curl. ✅ Verified: `/health`, `/docs` (200), ticket create/list smoke-tested.

## Phase 4 — Multi-Format Import  ✅
**Goal:** bulk import with graceful error reporting.

- [x] Parser interface + `csv`, `json`, `xml` parsers (XML via `defusedxml`).
- [x] `ImportService`: dispatch by format, per-record validation, aggregate `ImportSummary` (total/successful/failed + error detail); malformed-file handling.
- [x] `POST /tickets/import` multipart endpoint (format from extension/content-type).
- **Exit criteria:** importing sample + invalid files returns a correct summary; malformed files give meaningful 400s, not 500s. ✅ Verified against `sample_data/` and `sample_data/invalid/`.

## Phase 5 — Auto-Classification Engine  ✅
**Goal:** deterministic category + priority with explainability.

- [x] Keyword config for 6 categories + priority rules from TASKS.md.
- [x] Rule engine → `ClassificationResult` (category, priority, confidence 0–1, reasoning, keywords_found).
- [x] `ClassificationService` + decision logging; manual override support.
- [x] `POST /tickets/{id}/auto-classify`; `?auto_classify=true` on create; wire into import (§6.1).
- **Exit criteria:** representative tickets classify to expected category/priority with sensible confidence + reasoning. ✅ Verified with sample tickets end-to-end.

## Phase 6 — Sample & Fixture Data  ✅
**Goal:** realistic datasets for demos and tests.

- [x] `sample_data/sample_tickets.csv` (50), `.json` (20), `.xml` (30).
- [x] `sample_data/invalid/` negative-test files (bad email, out-of-range lengths, bad enums, malformed CSV/JSON/XML).
- [x] Mirror minimal fixtures under `src/tests/fixtures/`.
- **Exit criteria:** all sample files import successfully; invalid files fail with clear errors. ✅ Verified: 50/50, 20/20, 30/30 import; all 6 invalid files fail with 400 or per-record errors as expected.

## Phase 7 — Frontend Application  ✅
**Goal:** agent-facing SPA, API-driven, responsive.

- [x] Typed API client + data hooks; shared TS types matching backend schema.
- [x] Ticket **List** page with combined category/priority/status filters.
- [x] **Create/Edit** forms with client-side validation mirroring API rules.
- [x] **Detail** view: metadata + classification result.
- [x] **Bulk Import** widget with summary display.
- [x] **Auto-classify** action showing category/priority/confidence/reasoning.
- [x] Toast/inline success + error feedback; responsive desktop/mobile layout.
- **Exit criteria:** full agent workflow runs against the live API with no hardcoded ticket data. ✅
- **Covers:** Task 5.

## Phase 8 — Automated Tests & Coverage (>85%)  ✅
**Goal:** the required unit/API/parsing/classification suite, green, over the 85% threshold.

**Test-file quota (from TASKS.md Task 3):** 6 files, **46 tests** total. Counts below are
the minimum required per file; add more only if coverage demands it.

- [x] **`test_ticket_model` — 9 tests** (Pydantic validation, Phase 2):
  1. Valid ticket builds with all fields populated.
  2. `subject` length boundaries — reject empty and >200 chars, accept 1 & 200.
  3. `description` length boundaries — reject <10 and >2000, accept 10 & 2000.
  4. Invalid `customer_email` format rejected.
  5. Invalid `category` enum value rejected.
  6. Invalid `priority` enum value rejected.
  7. Invalid `status` enum value rejected.
  8. `metadata` validation — bad `source`/`device_type` enum rejected.
  9. Defaults & nullables — `resolved_at`/`assigned_to` optional, `tags` defaults to `[]`, timestamps auto-set.
- [x] **`test_ticket_api` — 11 tests** (endpoints, Phase 3):
  1. `POST /tickets` → 201 with generated id + timestamps.
  2. `POST /tickets?auto_classify=true` populates `classification`.
  3. `POST /tickets` invalid payload → 422 with field errors.
  4. `GET /tickets` → 200 lists all.
  5. `GET /tickets?category=` filters by category.
  6. `GET /tickets?priority=` filters by priority.
  7. `GET /tickets?status=` filters by status.
  8. `GET /tickets/{id}` → 200 for existing.
  9. `GET /tickets/{id}` → 404 for unknown id.
  10. `PUT /tickets/{id}` → 200 updates; unknown id → 404.
  11. `DELETE /tickets/{id}` → 204; unknown id → 404.
- [x] **`test_import_csv` — 6 tests** (Phase 4):
  1. Valid CSV → summary `total==successful`, `failed==0`.
  2. Mixed file → valid rows imported, invalid rows reported per-record with error detail.
  3. Malformed CSV structure → 400 with meaningful message (not 500).
  4. Empty file → summary `total==0`.
  5. Missing required column → per-record validation errors.
  6. Auto-classification applied to imported rows.
- [x] **`test_import_json` — 5 tests** (Phase 4):
  1. Valid JSON array → all successful.
  2. Invalid JSON syntax → 400 meaningful error.
  3. Per-record validation errors reported (bad email/length/enum).
  4. Wrong shape (object instead of array / missing fields) → 400 or per-record error.
  5. Empty array → summary `total==0`.
- [x] **`test_import_xml` — 5 tests** (Phase 4):
  1. Valid XML → all successful.
  2. Malformed XML → 400 meaningful error.
  3. Per-record validation errors reported.
  4. **Security:** XXE / external-entity payload is neutralized by `defusedxml` (no file read, safe rejection).
  5. Empty document / no `<ticket>` records → summary `total==0`.
- [x] **`test_categorization` — 10 tests** (rule engine, Phase 5):
  1–6. Correct category for each of the 6 categories (`account_access`, `technical_issue`, `billing_question`, `feature_request`, `bug_report`, `other`).
  7. Urgent priority keywords (`can't access`, `critical`, `production down`, `security`).
  8. High priority keywords (`important`, `blocking`, `asap`).
  9. Low keywords (`minor`, `cosmetic`, `suggestion`) and Medium as default fallback.
  10. Result completeness — `confidence` in [0,1], non-empty `reasoning`, correct `keywords_found`, and manual override preserved (not overwritten).
- [x] `pytest-cov` config with `--cov=app --cov-report=term-missing --cov-fail-under=85`.
- [x] Capture coverage screenshot → `docs/screenshots/test_coverage.png`.
- **Exit criteria:** all 46 tests green; overall coverage **>85%** reported; screenshot saved.
  ✅ 54 tests pass (46+ required plus parametrized extras), coverage **93%**, screenshot saved to
  `docs/screenshots/test_coverage.png`.
- **Covers:** Task 3.

## Phase 9 — Integration & Performance Tests  ✅
**Goal:** end-to-end confidence and documented benchmarks.

**Test-file quota (from TASKS.md Task 3 & 6):** 2 files, **10 tests** total. Task 6 names
4 integration scenarios; a 5th is added to meet the file's 5-test quota.

- [x] **`test_integration` — 5 tests** (end-to-end, Phase 3–5):
  1. **Full ticket lifecycle** — create → auto-classify → status transitions (`new`→`in_progress`→`resolved`, sets `resolved_at`) → delete.
  2. **Bulk import + auto-classify verification** — import a sample file, then assert imported tickets carry expected category/priority/classification.
  3. **Concurrent operations** — 20+ simultaneous requests (mixed create/read) stay consistent; no lost writes or id collisions.
  4. **Combined filtering** — `GET /tickets?category=&priority=` returns only tickets matching *both* criteria.
  5. **(Added)** Manual-override persistence — override a classified ticket via `PUT`, re-fetch, confirm override survives and is not re-computed.
- [x] **`test_performance` — 5 tests** (benchmarks, Phase 3–5):
  1. Single `POST /tickets` create latency under budget.
  2. `GET /tickets` list latency over a seeded dataset under budget.
  3. Bulk import throughput (e.g., 50-record CSV) under budget.
  4. `POST /tickets/{id}/auto-classify` latency under budget.
  5. Concurrent throughput — 20+ simultaneous requests complete within an aggregate time budget.
- [x] Record measured numbers into a **benchmark table** for `docs/TESTING_GUIDE.md` (Phase 10).
- **Exit criteria:** all 10 tests pass; benchmark numbers captured for the testing guide.
  ✅ 64 tests total pass (54 from Phase 8 + 10 new), coverage 94.77%. Measured locally
  (TestClient, in-memory repo, single dev machine — see table below):

  | Operation | Measured | Budget in test |
  |---|---|---|
  | `POST /tickets` single create | ~29 ms | < 500 ms |
  | `GET /tickets` list (100 seeded) | ~1.4 ms | < 1000 ms |
  | Bulk import 50-record CSV (+classify) | ~7 ms | < 3000 ms |
  | `POST /tickets/{id}/auto-classify` | ~1.2 ms | < 500 ms |
  | 20 concurrent creates (aggregate) | ~23 ms | < 5000 ms |

  **Note (gap found & fixed during Phase 9):** TASKS.md Task 2 requires "allow manual
  override" of classification, but it was never wired up through the API — `TicketUpdate`
  had no way to set `classification`, and `ClassificationService.override()` was dead
  code. Fixed by having `TicketService.update()` call `override()` whenever `PUT
  /tickets/{id}` changes `category` and/or `priority`, marking
  `classification.manual_override=true`. No new endpoint added — matches the API
  surface already documented in ARCHITECTURE.md §5. See ARCHITECTURE.md §10 for the
  change-log entry.
- **Covers:** Task 6 (and the integration/benchmark portions of Task 3).

## Phase 10 — Documentation  ✅
**Goal:** four audience-specific docs, ≥3 Mermaid diagrams.

- [x] `README.md` (developers): overview, features, Mermaid architecture diagram, install/setup, run tests, structure. *(Replaces the current homework-1 placeholder README.)*
- [x] `docs/API_REFERENCE.md`: every endpoint with request/response + curl, schemas, error formats. ✅ Clear, consumer-friendly, no complex tech terms, curl examples for all endpoints.
- [x] `docs/ARCHITECTURE.md`: **already drafted** — keep in sync as code lands.
  ✅ Architect review passed: all Task 4.3 requirements present — Mermaid high-level
  diagram (§2), component descriptions (§3), two Mermaid sequence diagrams (§6),
  design decisions & trade-offs (§1), security (§8) and performance (§9)
  considerations. Claims spot-checked against code (routes, defusedxml, CORS,
  repo lock, `auto_classify` flag); fixed one drift — frontend `pages/` dir
  doesn't exist, page views live in `components/`.
- [x] `docs/TESTING_GUIDE.md`: test-pyramid Mermaid, how to run, fixture locations, manual checklist, benchmark table. ✅
  Written for QA Engineers: Mermaid test pyramid (4 layers, 64 tests), run commands
  (local + coverage gate + docker-compose), suite overview table cross-checked
  against `pytest --collect-only` (64 tests, 8 files), sample vs. fixture data
  locations, 40+ item manual checklist (CRUD, import, classification, security/XXE,
  frontend, cross-cutting), the Phase 9 benchmark table, and a coverage-gaps table
  (94.77% measured, verified via a live `pytest --cov` run) so QA doesn't mistake
  defensive-branch gaps for untested features.
- [x] Note which AI model produced which doc. ✅ Recorded in the README.md header
  (doc-per-model table) and echoed as a `Generated by:` line at the top of each of
  the four docs: README.md & TESTING_GUIDE.md → Claude Sonnet 5; API_REFERENCE.md →
  Claude Haiku 4.5; ARCHITECTURE.md → Claude Opus 4.8 (initial draft in
  `c80e13d`), reviewed by Claude Fable 5 (`690691e`). Matches the `Co-Authored-By`
  trailers on the commits that introduced/touched each file.
- **Exit criteria:** all four docs complete; ≥3 Mermaid diagrams total across docs. ✅
  README (1 diagram) + ARCHITECTURE (4 diagrams: high-level, data-model ER, 2
  sequence flows) + TESTING_GUIDE (1 test-pyramid diagram) = 6 Mermaid diagrams
  total, exceeding the ≥3 requirement.
- **Covers:** Task 4.

## Phase 11 — Final Verification & Deliverables  ✅
**Goal:** everything demonstrably works and is captured.

- [x] UI screenshot with real data → `docs/screenshots/ui.png`. ✅ Captured against
  the live dev servers with 100 imported tickets (50 CSV + 20 JSON + 30 XML sample
  data), showing the ticket list with category/priority/status tags and filters.
- [x] Confirm coverage screenshot present and >85%. ✅ Regenerated
  `docs/screenshots/test_coverage.png` from a fresh `pytest --cov` run (64 tests,
  the full Phase 8+9 suite) — now shows **95%**, superseding the stale 93%
  screenshot captured before Phase 9's tests were added.
- [x] `docker-compose up` sanity check end-to-end. ✅ `docker compose up --build`
  builds and starts both containers; verified `GET /health` → `200`, frontend
  `/` → `200`, and a JSON sample import (20/20 successful) followed by
  `GET /tickets` confirming persistence — then `docker compose down` cleaned up.
- [x] Update README student/AI-tools header; final ARCHITECTURE/PLAN sync. ✅
  Header already complete from Phase 10 (student name, date, AI-tools note,
  doc-per-model table) — verified current, no changes needed. ARCHITECTURE.md §10
  and this file updated with the Phase 11 verification log.
- **Exit criteria:** all TASKS.md deliverables present and verified. ✅ All six
  TASKS.md deliverables confirmed: source code, coverage report + screenshot,
  UI screenshot, and sample data (50/20/30 + invalid) all present under
  `docs/screenshots/` and `sample_data/`.

---

## Requirements → Phase Traceability

| TASKS.md item | Phase(s) |
|---------------|----------|
| Task 1 — Import API (model, CRUD, import) | 2, 3, 4 |
| Task 2 — Auto-classification | 5 |
| Task 3 — Test suite >85% | 8 |
| Task 4 — Documentation | 10 (ARCHITECTURE started) |
| Task 5 — Front-end | 7 |
| Task 6 — Integration & performance | 9 |
| Deliverable — coverage report + screenshot | 8, 11 |
| Deliverable — UI screenshot | 11 |
| Deliverable — sample data (50/20/30 + invalid) | 6 |

---

## Progress Tracker

| Phase | Status | Notes |
|-------|--------|-------|
| 1 — Scaffolding | ✅ | FastAPI + Vite/React/TS skeletons, docker-compose, Dockerfiles verified locally |
| 2 — Models & Repository | ✅ | Pydantic v2 models + thread-safe in-memory repo |
| 3 — CRUD API | ✅ | Full CRUD + combinable filters, 400/404/422 handling |
| 4 — Import | ✅ | CSV/JSON/XML parsers + ImportService, defusedxml for XML |
| 5 — Classification | ✅ | Rule engine + ClassificationService, wired into create/import/auto-classify |
| 6 — Sample data | ✅ | 50 CSV / 20 JSON / 30 XML + 6 invalid files, all verified against the live API |
| 7 — Frontend | ✅ | Full React SPA: list/CRUD/import/detail/classification, responsive, API-driven, toast notifications |
| 8 — Tests & coverage | ✅ | 54 tests (6 files) green, 93% coverage, screenshot saved |
| 9 — Integration & perf | ✅ | 10 tests (5 integration + 5 performance) green; benchmark table recorded; fixed dead manual-override wiring |
| 10 — Documentation | ✅ | README, API_REFERENCE.md, ARCHITECTURE.md, and TESTING_GUIDE.md complete; doc-per-model table added to README + `Generated by:` line on each doc; 6 Mermaid diagrams total |
| 11 — Final verification | ✅ | UI screenshot (100 real tickets) + refreshed coverage screenshot (95%) saved to `docs/screenshots/`; `docker-compose up` end-to-end sanity verified and torn down; README header confirmed current |

---

## Open Questions / Assumptions

- **Assumption:** no authentication/authorization required (not in TASKS.md).
- **Assumption:** `metadata` fields (browser, device_type) are optional on import.
- **Assumption:** "different AI models for different doc types" is satisfied by
  noting the model used per doc; no functional impact.
- Raise a question here if any requirement changes during implementation.
