# Implementation Plan — Banking Transactions API

**Stack:** Python 3.11+ · FastAPI · Pydantic v2 · Uvicorn  
**Storage:** In-memory (plain dict, no database)  
**Optional Feature Selected:** Option A — Transaction Summary Endpoint  
**Runtime (primary):** Docker / Docker Compose  
**Runtime (secondary):** Local Python virtualenv  

> **Session walkthrough:** The full step-by-step Claude Code interaction that produced this plan and the entire implementation is documented in [UI_INTERACTION_WALKTHROUGH.md](UI_INTERACTION_WALKTHROUGH.md).

---

## Stack Rationale

| Concern | Why FastAPI wins here |
|---|---|
| Task 2 validation | Pydantic v2 field validators match the required error shape almost 1-to-1 |
| Task 3 filtering | FastAPI `Query` params with `Optional` types, zero boilerplate |
| Deliverable screenshots | Auto-generated Swagger UI at `/docs` is a free demo surface |
| Type safety | Full type annotations; IDE and runtime both catch mistakes |
| Familiarity | Pure Python, no build step, runs with a single `uvicorn` command |

---

## Directory Layout (target state after all phases)

```
homework-1/
├── README.md
├── HOWTORUN.md
├── TASKS.md
├── requirements.txt
├── Dockerfile                ← Production-style image (python:3.11-slim)
├── docker-compose.yml        ← One-command local run via Docker
├── .dockerignore             ← Exclude .venv, __pycache__, docs, etc.
├── .gitignore
├── src/
│   ├── main.py               ← FastAPI app factory + server entry point
│   ├── models.py             ← Pydantic models & enums
│   ├── storage.py            ← In-memory store singleton
│   ├── validators.py         ← Reusable validation helpers
│   └── routers/
│       ├── transactions.py   ← /transactions routes
│       └── accounts.py       ← /accounts routes
├── demo/
│   ├── run.sh                ← PRIMARY: starts app via Docker Compose
│   ├── run-local.sh          ← SECONDARY: starts app with local Python venv
│   ├── sample-requests.http
│   └── sample-data.json
└── docs/
    ├── IMPLEMENTATION_PLAN.md   ← this file
    └── screenshots/
```

---

## Phase 1 — Project Bootstrap

**Goal:** Runnable "hello world" FastAPI app reachable via Docker Compose; local Python path also works.

### Steps

1. Create `requirements.txt` with pinned versions:
   ```
   fastapi>=0.111.0
   uvicorn[standard]>=0.29.0
   pydantic>=2.7.0
   ```

2. Create `.gitignore` covering: `__pycache__/`, `*.pyc`, `.venv/`, `.env`, `*.egg-info/`

3. Create `src/main.py` — minimal FastAPI app.

4. Create `Dockerfile`:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY src/ ./src/
   EXPOSE 8000
   CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

5. Create `.dockerignore`:
   ```
   .venv/
   __pycache__/
   *.pyc
   .git/
   .env
   docs/
   demo/
   *.md
   ```

6. Create `docker-compose.yml`:
   ```yaml
   services:
     api:
       build: .
       ports:
         - "8000:8000"
       volumes:
         - ./src:/app/src   # hot-reload friendly during development
       command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   > The `volumes` mount + `--reload` flag gives live code reloading inside the container during development. In a "production" local run, drop the volume and reload flag.

7. Create `demo/run.sh` — a convenience script to drive the Docker infra so it's runnable from the very first phase (this is the PRIMARY run path; it is finalized/verified again in Phase 7). Make it executable with `chmod +x demo/run.sh`:
   ```bash
   #!/usr/bin/env bash
   # Run the Banking Transactions API via Docker Compose (primary run path).
   # Usage:
   #   ./demo/run.sh          → build (if needed) and start in the foreground
   #   ./demo/run.sh up       → same as above
   #   ./demo/run.sh build    → force a clean rebuild, then start
   #   ./demo/run.sh down     → stop and remove the container
   #   ./demo/run.sh logs     → tail container logs
   set -euo pipefail
   cd "$(dirname "$0")/.."   # run from the homework-1 project root

   case "${1:-up}" in
     up)    docker compose up ;;
     build) docker compose up --build ;;
     down)  docker compose down ;;
     logs)  docker compose logs -f ;;
     *)     echo "Unknown command: $1 (use up | build | down | logs)"; exit 1 ;;
   esac
   ```
   > Requires Docker Desktop ≥ 24 (Compose v2). The script `cd`s to the project root so it works regardless of the caller's working directory.

8. Verify Docker path: `./demo/run.sh build` (or `docker compose up --build`) → container starts; Swagger UI loads at `http://localhost:8000/docs`. Then `./demo/run.sh down` stops it cleanly.

9. Verify local path (secondary): `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn src.main:app --reload` → same result.

### Acceptance criteria
- `./demo/run.sh build` brings the API up; Swagger UI loads at `http://localhost:8000/docs` in both Docker and local cases
- `./demo/run.sh down` (or `docker compose down`) cleanly stops the container
- `demo/run.sh` is executable

---

## Phase 2 — Domain Models & In-Memory Storage

**Goal:** Define the canonical data shapes and the shared store before writing any route logic.

### Steps

1. **`src/models.py`** — Define the following with Pydantic `BaseModel`:

   ```python
   # Enums
   class TransactionType(str, Enum): deposit | withdrawal | transfer
   class TransactionStatus(str, Enum): pending | completed | failed

   # Request body — every model field EXCEPT the auto-generated `id`.
   # Per TASKS.md only `id` is annotated "(auto-generated)", so `timestamp`
   # and `status` are accepted from the payload but are OPTIONAL: if the
   # client omits them (as the TASKS.md sample POST does), the server fills
   # sensible defaults.
   class TransactionCreate(BaseModel):
       fromAccount: str
       toAccount: str
       amount: float
       currency: str
       type: TransactionType
       timestamp: datetime | None = None        # optional; defaults to UTC now
       status: TransactionStatus | None = None  # optional; defaults to completed

   # Full stored record — server guarantees `id`, `timestamp`, `status` are set.
   class Transaction(BaseModel):
       id: str
       fromAccount: str
       toAccount: str
       amount: float
       currency: str
       type: TransactionType
       timestamp: datetime
       status: TransactionStatus
   ```

2. **`src/storage.py`** — Single module-level `dict[str, Transaction]` acting as the store. Expose:
   - `add_transaction(tx: Transaction) -> Transaction`
   - `get_transaction(tx_id: str) -> Transaction | None`
   - `list_transactions() -> list[Transaction]`

3. Wire storage into `main.py` (import only; no routes yet).

### Acceptance criteria
- Models import cleanly; no circular dependencies
- Storage functions covered by a quick interactive Python check (`python -c "from src.storage import list_transactions; print(list_transactions())"`)

---

## Phase 3 — Core API Endpoints (Task 1)

**Goal:** Implement all four required endpoints with in-memory persistence and correct HTTP status codes.

### Endpoints

| Method | Path | Status codes |
|---|---|---|
| `POST` | `/transactions` | 201 Created · 400 Bad Request |
| `GET` | `/transactions` | 200 OK |
| `GET` | `/transactions/{id}` | 200 OK · 404 Not Found |
| `GET` | `/accounts/{accountId}/balance` | 200 OK · 404 Not Found |

### Steps

1. **`src/routers/transactions.py`**
   - `POST /transactions`: accept `TransactionCreate`. Always auto-generate `id` (UUID4). For `timestamp`: use the payload value if provided, else UTC now. For `status`: use the payload value if provided, else default to `completed` (so the created transaction immediately counts toward balances/summaries — see resolution of gap #1). Persist via storage, return full `Transaction` with 201.
   - `GET /transactions`: return `list_transactions()` with 200.
   - `GET /transactions/{id}`: call `get_transaction(id)`, raise `HTTPException(404)` if None.

2. **`src/routers/accounts.py`**
   - `GET /accounts/{accountId}/balance`: scan all transactions; compute balance as `sum of inflows − sum of outflows` for the account. Return `{"accountId": ..., "balance": ..., "currency": ...}`. Return 404 if the account has no transactions.

3. Register both routers in `main.py` with appropriate prefixes.

### Balance calculation logic
```
balance += amount   when tx.toAccount == accountId and tx.status == "completed"
balance -= amount   when tx.fromAccount == accountId and tx.status == "completed"
```
Deposits (no fromAccount meaningful) and withdrawals need the same rule applied symmetrically.

### Acceptance criteria
- All four endpoints return correct payloads and status codes via curl/Swagger UI
- 404 is returned for unknown IDs and unknown accounts
- Created transaction is retrievable by the returned `id`

---

## Phase 4 — Validation Layer (Task 2)

**Goal:** Reject invalid input with structured, field-level error messages.

### Validation rules

| Field | Rule |
|---|---|
| `amount` | Positive number; max 2 decimal places |
| `fromAccount` / `toAccount` | Matches regex `^ACC-[A-Z0-9]{5}$` |
| `currency` | Must be in an allowed ISO 4217 set (USD, EUR, GBP, JPY, CHF, CAD, AUD, CNY, INR, BRL — extendable) |

### Steps

1. **`src/validators.py`** — Define reusable functions/constants:
   - `VALID_CURRENCIES: frozenset[str]`
   - `ACCOUNT_RE = re.compile(r"^ACC-[A-Z0-9]{5}$")`
   - `validate_amount(v: float) -> float` — raises `ValueError` if <= 0 or > 2 decimal places

2. Add Pydantic field validators to `TransactionCreate` using `@field_validator`:
   - `amount` → `validate_amount`
   - `fromAccount` / `toAccount` → regex check
   - `currency` → set membership check

3. Add a global FastAPI **exception handler** for `RequestValidationError` that reshapes the default Pydantic error output into the required schema:
   ```json
   {
     "error": "Validation failed",
     "details": [{"field": "amount", "message": "Amount must be a positive number"}]
   }
   ```

### Acceptance criteria
- `POST /transactions` with `amount: -10` → `400` with structured error on `amount` field
- `POST /transactions` with `currency: "XYZ"` → `400` with structured error on `currency` field
- `POST /transactions` with `fromAccount: "12345"` → `400` with structured error on `fromAccount` field
- Valid request → `201` unchanged

---

## Phase 5 — Transaction Filtering (Task 3)

**Goal:** `GET /transactions` accepts query parameters for filtering; multiple filters combine with AND logic.

### Query parameters

| Param | Type | Behaviour |
|---|---|---|
| `accountId` | `str \| None` | Match `fromAccount` OR `toAccount` |
| `type` | `TransactionType \| None` | Match `tx.type` |
| `from` | `date \| None` | `tx.timestamp.date() >= from` |
| `to` | `date \| None` | `tx.timestamp.date() <= to` |

### Steps

1. Update `GET /transactions` signature to accept the four `Query` params (all optional).
2. Implement a `filter_transactions(txs, *, account_id, type_, from_date, to_date)` helper in `storage.py` or a new `src/filters.py`.
3. Apply all active filters in sequence (AND logic).
4. Return filtered list.

### Edge cases to handle
- `from` > `to` → return `400 {"error": "Invalid date range"}`
- No matching transactions → return `200 []` (not 404)

### Acceptance criteria
- `GET /transactions?accountId=ACC-12345` returns only transactions involving that account
- `GET /transactions?type=transfer` returns only transfers
- `GET /transactions?from=2024-01-01&to=2024-01-31` returns only transactions in range
- Combined params apply AND logic
- `from > to` → 400

---

## Phase 6 — Additional Feature: Transaction Summary (Task 4 — Option A)

**Goal:** Implement `GET /accounts/{accountId}/summary`.

### Response shape

```json
{
  "accountId": "ACC-12345",
  "totalDeposits": 500.00,
  "totalWithdrawals": 150.00,
  "transactionCount": 5,
  "mostRecentTransactionDate": "2024-01-15T10:30:00Z"
}
```

### Steps

1. Add `GET /accounts/{accountId}/summary` to `src/routers/accounts.py`.
2. Filter all transactions where `fromAccount == accountId OR toAccount == accountId`.
3. Compute:
   - `totalDeposits`: sum of `amount` where `type == deposit` and `toAccount == accountId`
   - `totalWithdrawals`: sum of `amount` where `type == withdrawal` and `fromAccount == accountId`
   - `transactionCount`: total count of matching transactions
   - `mostRecentTransactionDate`: max `timestamp`
4. Return 404 if account has no transactions.

### Acceptance criteria
- Returns correct aggregates for a seeded set of transactions
- Returns 404 for unknown account

---

## Phase 7 — Demo Files & Documentation

**Goal:** All required deliverable files in place; Docker is the primary path in every script and doc, local Python is documented as the secondary alternative.

### Steps

1. **`demo/run.sh`** (PRIMARY — Docker): already created in Phase 1. Here, just confirm it's present, executable, and documented in `HOWTORUN.md` (supports `up | build | down | logs`). No rewrite needed.

2. **`demo/run-local.sh`** (SECONDARY — local Python):
   ```bash
   #!/usr/bin/env bash
   # Starts the API with a local Python virtualenv (no Docker required).
   cd "$(dirname "$0")/.."
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   Both scripts must be made executable (`chmod +x`).

3. **`demo/sample-requests.http`** — VS Code REST Client format covering:
   - Create deposit, withdrawal, transfer
   - List all, filter by account, filter by type, filter by date range
   - Get by ID, get balance, get summary
   - Base URL variable: `@baseUrl = http://localhost:8000` (same for both Docker and local)

4. **`demo/sample-data.json`** — 5–8 pre-built transaction objects (no code, pure JSON for reference).

5. **`README.md`** — Update with:
   - Project overview
   - Features implemented (Tasks 1–4 Option A)
   - Architecture decisions (in-memory store, Pydantic validation, FastAPI routers)
   - Quick-start section: Docker badge/command first, local option below it
   - Link to `HOWTORUN.md` for full details

6. **`HOWTORUN.md`** — Structured as two clearly labelled sections:

   **Option 1 — Docker (recommended)**
   - Prerequisites: Docker Desktop ≥ 24 (includes Compose v2)
   - `docker compose up --build`  or  `demo/run.sh`
   - API available at `http://localhost:8000`
   - Swagger UI at `http://localhost:8000/docs`
   - Stop: `docker compose down`

   **Option 2 — Local Python**
   - Prerequisites: Python 3.11+
   - `python -m venv .venv && source .venv/bin/activate`
   - `pip install -r requirements.txt`
   - `uvicorn src.main:app --reload`  or  `demo/run-local.sh`
   - API available at `http://localhost:8000`

### Acceptance criteria
- Following the Docker section of `HOWTORUN.md` cold reaches a running API (no Python install needed)
- Following the local section also reaches a running API
- Both `demo/run.sh` and `demo/run-local.sh` are executable
- `sample-requests.http` works identically against both startup methods (same port)

---

## Phase 8 — Manual Testing & Screenshots

**Goal:** Verify golden path + edge cases; capture screenshots for `docs/screenshots/`.

### Test checklist

- [ ] Create transactions (deposit, withdrawal, transfer)
- [ ] Get all transactions (unfiltered)
- [ ] Filter by accountId
- [ ] Filter by type
- [ ] Filter by date range
- [ ] Combined filter
- [ ] Get transaction by valid ID
- [ ] Get transaction by unknown ID → 404
- [ ] Get balance for seeded account
- [ ] Get balance for unknown account → 404
- [ ] Get summary for seeded account
- [ ] Validation: negative amount → 400
- [ ] Validation: bad currency → 400
- [ ] Validation: bad account format → 400
- [ ] Invalid date range (from > to) → 400

### Screenshots to capture (in `docs/screenshots/`)

| Filename | Content |
|---|---|
| `01-docker-compose-up.png` | Terminal showing `docker compose up --build` completing successfully |
| `02-swagger-ui.png` | Swagger UI overview at `/docs` (accessed while container is running) |
| `03-create-transaction.png` | POST via Swagger/curl — 201 response |
| `04-list-transactions.png` | GET all — 200 with data |
| `05-filter-by-account.png` | GET with `?accountId=...` |
| `06-get-balance.png` | GET balance endpoint |
| `07-get-summary.png` | GET summary endpoint |
| `08-validation-error.png` | 400 response with structured error |
| `09-ai-prompt-1.png` | AI interaction (prompt + response) |
| `10-ai-prompt-2.png` | AI interaction (prompt + response) |

---

## Phase Summary

| Phase | Covers | Deliverable |
|---|---|---|
| 1 | Project bootstrap + Docker setup | Runnable skeleton via `docker compose up` and locally |
| 2 | Data models + storage | `models.py`, `storage.py` |
| 3 | Core endpoints | Task 1 complete |
| 4 | Validation | Task 2 complete |
| 5 | Filtering | Task 3 complete |
| 6 | Summary endpoint | Task 4 (Option A) complete |
| 7 | Demo files + docs | `run.sh` (Docker), `run-local.sh`, `HOWTORUN.md` (both paths) |
| 8 | Manual test + screenshots | Submission-ready (Docker startup screenshot included) |

Each phase is independently committable and leaves the API in a working state via both Docker and local Python.
