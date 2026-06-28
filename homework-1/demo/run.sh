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
