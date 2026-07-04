#!/usr/bin/env bash
# Starts the Banking Transactions API with a local Python virtualenv (no Docker required).
# Usage: ./demo/run-local.sh
set -euo pipefail
cd "$(dirname "$0")/.."   # run from the homework-1 project root

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
