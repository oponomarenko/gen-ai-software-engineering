# 🏦 Homework 1: Banking Transactions API

> **Student Name**: Oleksandr Ponomarenko
> **Date Submitted**:
> **AI Tools Used**: Claude Code (claude-sonnet-4-6)

A RESTful banking transactions API built with **FastAPI** and **Pydantic v2**, running in Docker.

---

## Features

| Task | Description |
|---|---|
| Task 1 — Core endpoints | `POST /transactions`, `GET /transactions`, `GET /transactions/{id}`, `GET /accounts/{accountId}/balance` |
| Task 2 — Validation | Field-level error responses for amount, account format, and currency |
| Task 3 — Filtering | `GET /transactions` supports `accountId`, `type`, `from`, and `to` query params (AND logic) |
| Task 4 — Summary (Option A) | `GET /accounts/{accountId}/summary` with deposit/withdrawal totals and transaction count |

---

## Quick Start

```bash
# Start with Docker (recommended)
docker compose up --build

# Or via the convenience script
./demo/run.sh build
```

API: **http://localhost:8000**  
Swagger UI: **http://localhost:8000/docs**

See [HOWTORUN.md](HOWTORUN.md) for full instructions including the local Python option.

---

## Architecture

- **FastAPI** — request routing, query param parsing, automatic OpenAPI docs
- **Pydantic v2** — schema definition and field-level validation via `@field_validator`
- **In-memory store** — plain `dict[str, Transaction]` singleton; no database required
- **Routers** — `src/routers/transactions.py` and `src/routers/accounts.py` keep route logic separate
- **Validators** — reusable helpers in `src/validators/` for amount, account regex, and currency

---

## Project Layout

```
homework-1/
├── src/
│   ├── main.py               ← FastAPI app factory
│   ├── storage.py            ← In-memory store + filter helper
│   ├── models/
│   │   ├── transaction.py    ← Transaction models & enums
│   │   └── account.py        ← Balance & summary response models
│   ├── routers/
│   │   ├── transactions.py   ← /transactions routes
│   │   └── accounts.py       ← /accounts routes
│   ├── validators/
│   │   ├── transactionValidator.py  ← Amount & currency validation
│   │   └── accountValidator.py      ← Account ID format validation
│   └── utils/
│       └── errorHandlers.py  ← Global validation error handler
├── demo/
│   ├── run.sh                ← Docker Compose convenience script
│   ├── run-local.sh          ← Local Python convenience script
│   ├── sample-requests.http  ← VS Code REST Client file
│   ├── curl-examples.sh      ← Curl commands for all endpoints
│   └── sample-data.json      ← Reference transaction objects
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── HOWTORUN.md
```
