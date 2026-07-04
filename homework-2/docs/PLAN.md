# 📐 Implementation Plan — Intelligent Customer Support System

> **Living document.** Update on any requirement change and mark phase progress here.
> **Status legend:** ⬜ Not started · 🟡 In progress · ✅ Done · ⛔ Blocked
> **Last updated:** 2026-07-04

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

## Phase 1 — Project Scaffolding & Tooling  ⬜
**Goal:** runnable skeletons for both apps and a green CI-style test command.

- [ ] Backend skeleton in `src/backend`: FastAPI app, `main.py`, `/health`, package layout from ARCHITECTURE §7.
- [ ] Dependency + tooling setup: `pyproject.toml`/`requirements.txt` (fastapi, uvicorn, pydantic v2, python-multipart, defusedxml, pytest, pytest-cov, httpx), ruff/black optional.
- [ ] Frontend skeleton in `src/frontend`: Vite + React + TS, base routing, API base-URL config via env.
- [ ] `docker-compose.yml` (backend + frontend) and per-app `Dockerfile`s.
- [ ] `.gitignore`, `.env.example`, CORS config.
- **Exit criteria:** `uvicorn` serves `/health`; `vite` serves a placeholder page; `docker-compose up` starts both; `pytest` runs (0 tests OK).

## Phase 2 — Domain Models & Repository  ⬜
**Goal:** validated data model and storage seam.

- [ ] Enums: Category, Priority, Status, Source, DeviceType.
- [ ] Pydantic models: `TicketMetadata`, `ClassificationResult`, `Ticket`, `TicketCreate`, `TicketUpdate`, `ImportSummary`.
- [ ] Validation: email format, subject 1–200, description 10–2000, enum membership, timestamps.
- [ ] `TicketRepository` interface + thread-safe `InMemoryTicketRepository`.
- **Exit criteria:** models validate/reject sample inputs; repository CRUD works in a REPL/unit test.
- **Covers:** Task 1 (model), feeds Task 3 `test_ticket_model` (9 tests).

## Phase 3 — Ticket CRUD API  ⬜
**Goal:** the core REST endpoints.

- [ ] `TicketService` CRUD + filtering (category/priority/status, combinable).
- [ ] Routers: POST/GET(list)/GET(id)/PUT/DELETE with status codes 201/200/200/200/204.
- [ ] Central error handling → 400/404/422 with structured messages.
- **Exit criteria:** all CRUD + filter endpoints work via `/docs` and curl.
- **Covers:** Task 1 (endpoints), feeds `test_ticket_api` (11 tests).

## Phase 4 — Multi-Format Import  ⬜
**Goal:** bulk import with graceful error reporting.

- [ ] Parser interface + `csv`, `json`, `xml` parsers (XML via `defusedxml`).
- [ ] `ImportService`: dispatch by format, per-record validation, aggregate `ImportSummary` (total/successful/failed + error detail); malformed-file handling.
- [ ] `POST /tickets/import` multipart endpoint (format from extension/content-type).
- **Exit criteria:** importing sample + invalid files returns a correct summary; malformed files give meaningful 400s, not 500s.
- **Covers:** Task 1 (import), feeds `test_import_csv` (6), `test_import_json` (5), `test_import_xml` (5).

## Phase 5 — Auto-Classification Engine  ⬜
**Goal:** deterministic category + priority with explainability.

- [ ] Keyword config for 6 categories + priority rules from TASKS.md.
- [ ] Rule engine → `ClassificationResult` (category, priority, confidence 0–1, reasoning, keywords_found).
- [ ] `ClassificationService` + decision logging; manual override support.
- [ ] `POST /tickets/{id}/auto-classify`; `?auto_classify=true` on create; wire into import (§6.1).
- **Exit criteria:** representative tickets classify to expected category/priority with sensible confidence + reasoning.
- **Covers:** Task 2, feeds `test_categorization` (10 tests).

## Phase 6 — Sample & Fixture Data  ⬜
**Goal:** realistic datasets for demos and tests.

- [ ] `sample_data/sample_tickets.csv` (50), `.json` (20), `.xml` (30).
- [ ] `sample_data/invalid/` negative-test files (bad email, out-of-range lengths, bad enums, malformed CSV/JSON/XML).
- [ ] Mirror minimal fixtures under `src/tests/fixtures/`.
- **Exit criteria:** all sample files import successfully; invalid files fail with clear errors.
- **Covers:** Deliverable 4.

## Phase 7 — Frontend Application  ⬜
**Goal:** agent-facing SPA, API-driven, responsive.

- [ ] Typed API client + data hooks; shared TS types matching backend schema.
- [ ] Ticket **List** page with combined category/priority/status filters.
- [ ] **Create/Edit** forms with client-side validation mirroring API rules.
- [ ] **Detail** view: metadata + classification result.
- [ ] **Bulk Import** widget with summary display.
- [ ] **Auto-classify** action showing category/priority/confidence/reasoning.
- [ ] Toast/inline success + error feedback; responsive desktop/mobile layout.
- **Exit criteria:** full agent workflow runs against the live API with no hardcoded ticket data.
- **Covers:** Task 5.

## Phase 8 — Automated Tests & Coverage (>85%)  ⬜
**Goal:** the required suite, green, over threshold.

- [ ] Unit + API tests: `test_ticket_model`, `test_ticket_api`, `test_import_csv/json/xml`, `test_categorization`.
- [ ] `pytest-cov` config with `--cov-fail-under=85`.
- [ ] Capture coverage screenshot → `docs/screenshots/test_coverage.png`.
- **Exit criteria:** `pytest` green; coverage >85% reported.
- **Covers:** Task 3.

## Phase 9 — Integration & Performance Tests  ⬜
**Goal:** end-to-end confidence and benchmarks.

- [ ] `test_integration` (5): full lifecycle; import+auto-classify verification; combined category+priority filtering; concurrency (20+ simultaneous requests).
- [ ] `test_performance` (5): latency/throughput budgets for create, list, import, classify.
- [ ] Benchmark table for TESTING_GUIDE.
- **Exit criteria:** integration + perf tests pass and produce benchmark numbers.
- **Covers:** Task 6.

## Phase 10 — Documentation  ⬜
**Goal:** four audience-specific docs, ≥3 Mermaid diagrams.

- [ ] `README.md` (developers): overview, features, Mermaid architecture diagram, install/setup, run tests, structure. *(Replaces the current homework-1 placeholder README.)*
- [ ] `docs/API_REFERENCE.md`: every endpoint with request/response + curl, schemas, error formats.
- [ ] `docs/ARCHITECTURE.md`: **already drafted** — keep in sync as code lands.
- [ ] `docs/TESTING_GUIDE.md`: test-pyramid Mermaid, how to run, fixture locations, manual checklist, benchmark table.
- [ ] Note which AI model produced which doc.
- **Exit criteria:** all four docs complete; ≥3 Mermaid diagrams total across docs.
- **Covers:** Task 4.

## Phase 11 — Final Verification & Deliverables  ⬜
**Goal:** everything demonstrably works and is captured.

- [ ] UI screenshot with real data → `docs/screenshots/ui.png`.
- [ ] Confirm coverage screenshot present and >85%.
- [ ] `docker-compose up` sanity check end-to-end.
- [ ] Update README student/AI-tools header; final ARCHITECTURE/PLAN sync.
- **Exit criteria:** all TASKS.md deliverables present and verified.

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
| 1 — Scaffolding | ⬜ | |
| 2 — Models & Repository | ⬜ | |
| 3 — CRUD API | ⬜ | |
| 4 — Import | ⬜ | |
| 5 — Classification | ⬜ | |
| 6 — Sample data | ⬜ | |
| 7 — Frontend | ⬜ | |
| 8 — Tests & coverage | ⬜ | |
| 9 — Integration & perf | ⬜ | |
| 10 — Documentation | ⬜ | ARCHITECTURE.md drafted |
| 11 — Final verification | ⬜ | |

---

## Open Questions / Assumptions

- **Assumption:** no authentication/authorization required (not in TASKS.md).
- **Assumption:** `metadata` fields (browser, device_type) are optional on import.
- **Assumption:** "different AI models for different doc types" is satisfied by
  noting the model used per doc; no functional impact.
- Raise a question here if any requirement changes during implementation.
