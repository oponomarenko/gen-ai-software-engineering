#!/usr/bin/env bash
# Curl examples for the Banking Transactions API.
# Run individual commands, or execute this script to run all of them in sequence.
# Prerequisites: curl, jq (optional — used for pretty-printing JSON responses)
#
# Start the API first:
#   ./demo/run.sh          (Docker — recommended)
#   ./demo/run-local.sh    (local Python)

BASE_URL="http://localhost:8000"
BOLD='\033[1m'
RESET='\033[0m'

header() { echo -e "\n${BOLD}▶ $*${RESET}"; }

# ─── Create Transactions ──────────────────────────────────────────────────────

header "Create a deposit (201)"
curl -s -X POST "$BASE_URL/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC-SRC01",
    "toAccount":   "ACC-DST01",
    "amount":      500.00,
    "currency":    "USD",
    "type":        "deposit"
  }' | jq .

header "Create a withdrawal (201)"
curl -s -X POST "$BASE_URL/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC-DST01",
    "toAccount":   "ACC-SRC02",
    "amount":      150.00,
    "currency":    "USD",
    "type":        "withdrawal"
  }' | jq .

header "Create a transfer in EUR with explicit timestamp (201)"
curl -s -X POST "$BASE_URL/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC-SRC01",
    "toAccount":   "ACC-DST02",
    "amount":      1200.50,
    "currency":    "EUR",
    "type":        "transfer",
    "timestamp":   "2024-01-15T10:30:00Z"
  }' | jq .

header "Create a transfer with explicit status=pending (201)"
curl -s -X POST "$BASE_URL/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC-SRC02",
    "toAccount":   "ACC-DST01",
    "amount":      75.25,
    "currency":    "USD",
    "type":        "transfer",
    "status":      "pending"
  }' | jq .

# ─── Validation Errors ────────────────────────────────────────────────────────

header "Negative amount → 400"
curl -s -X POST "$BASE_URL/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC-SRC01",
    "toAccount":   "ACC-DST01",
    "amount":      -10,
    "currency":    "USD",
    "type":        "deposit"
  }' | jq .

header "Invalid currency → 400"
curl -s -X POST "$BASE_URL/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC-SRC01",
    "toAccount":   "ACC-DST01",
    "amount":      100,
    "currency":    "XYZ",
    "type":        "deposit"
  }' | jq .

header "Invalid account format → 400"
curl -s -X POST "$BASE_URL/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "12345",
    "toAccount":   "ACC-DST01",
    "amount":      100,
    "currency":    "USD",
    "type":        "deposit"
  }' | jq .

header "Amount with more than 2 decimal places → 400"
curl -s -X POST "$BASE_URL/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC-SRC01",
    "toAccount":   "ACC-DST01",
    "amount":      10.999,
    "currency":    "USD",
    "type":        "deposit"
  }' | jq .

# ─── List & Filter Transactions ───────────────────────────────────────────────

header "List all transactions (200)"
curl -s "$BASE_URL/transactions" | jq .

header "Filter by accountId (200)"
curl -s "$BASE_URL/transactions?accountId=ACC-DST01" | jq .

header "Filter by type=transfer (200)"
curl -s "$BASE_URL/transactions?type=transfer" | jq .

header "Filter by date range (200)"
curl -s "$BASE_URL/transactions?from=2024-01-01&to=2024-01-31" | jq .

header "Combined filter: accountId + type (200)"
curl -s "$BASE_URL/transactions?accountId=ACC-SRC01&type=transfer" | jq .

header "Invalid date range: from > to → 400"
curl -s "$BASE_URL/transactions?from=2024-12-31&to=2024-01-01" | jq .

# ─── Get Transaction by ID ────────────────────────────────────────────────────

header "Get transaction by ID — capture a real ID first"
TX_ID=$(curl -s -X POST "$BASE_URL/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC-SRC01",
    "toAccount":   "ACC-DST01",
    "amount":      99.00,
    "currency":    "USD",
    "type":        "deposit"
  }' | jq -r '.id')

echo "Created transaction ID: $TX_ID"

header "Get transaction by valid ID (200)"
curl -s "$BASE_URL/transactions/$TX_ID" | jq .

header "Get transaction by unknown ID → 404"
curl -s "$BASE_URL/transactions/00000000-0000-0000-0000-000000000000" | jq .

# ─── Account Balance ──────────────────────────────────────────────────────────

header "Get balance for ACC-DST01 (200)"
curl -s "$BASE_URL/accounts/ACC-DST01/balance" | jq .

header "Get balance for unknown account → 404"
curl -s "$BASE_URL/accounts/ACC-ZZZZZ/balance" | jq .

header "Get balance with invalid account format → 400"
curl -s "$BASE_URL/accounts/badformat/balance" | jq .

# ─── Account Summary ──────────────────────────────────────────────────────────

header "Get summary for ACC-DST01 (200)"
curl -s "$BASE_URL/accounts/ACC-DST01/summary" | jq .

header "Get summary for unknown account → 404"
curl -s "$BASE_URL/accounts/ACC-ZZZZZ/summary" | jq .

header "Get summary with invalid account format → 400"
curl -s "$BASE_URL/accounts/badformat/summary" | jq .
