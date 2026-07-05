# CLAUDE.md — Homework 2

Guidance for AI coding sessions in this folder. Read this and the two living docs
before making changes.

## What this is
Intelligent Customer Support System: FastAPI backend + React (Vite/TS) frontend for
importing, auto-classifying, and managing support tickets. Requirements are in
[TASKS.md](TASKS.md).

## Source of truth
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — design, structure, data model, flows.
- **[docs/PLAN.md](docs/PLAN.md)** — phased implementation plan + progress tracker.
- Keep both **updated** as code changes. Mark phase progress in PLAN.md; log design
  changes in ARCHITECTURE.md §10.

## Locked decisions (do not change without asking)
- Backend: **Python / FastAPI**, Pydantic v2.
- Frontend: **React + Vite + TypeScript**.
- Structure: `src/backend`, `src/frontend`, `src/tests`.
- Persistence: **in-memory repository** behind a `TicketRepository` interface.
- Classification: **rule-based keyword engine** (deterministic, offline).
- Delivery: local `uvicorn` + `vite`, plus `docker-compose`.

## Conventions
- Keep business logic in the **service layer**, framework glue in the **API layer**.
- All data access goes through the repository interface — no direct store access.
- Parse XML with **`defusedxml`**, never the stdlib parser (XXE risk).
- Validation lives in Pydantic models; return 422/400 for bad input, 404 for missing.
- Frontend must be **API-driven** — no hardcoded ticket data.

## Commands (fill in as scaffolding lands)
- Backend dev: `uvicorn app.main:app --reload` (from `src/backend`)
- Frontend dev: `npm run dev` (from `src/frontend`)
- Tests + coverage: `pytest --cov=app --cov-report=term-missing --cov-fail-under=85`
- Full stack: `docker-compose up`

## Guardrails
- **Do not begin implementation until the plan is reviewed/approved by the user.**
- Do **not** use `homework-1` or any other homework folder as reference or input.
- Target **>85%** test coverage (Task 3).
