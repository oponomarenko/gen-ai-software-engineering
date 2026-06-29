# ▶️ How to Run the application

---

## Option 1 — Docker (recommended)

**Prerequisites:** Docker Desktop >= 24 (includes Compose v2)

```bash
# Build the image and start the API
docker compose up --build

# Or use the convenience script (supports: up | build | down | logs)
./demo/run.sh build
```

The API is available at **http://localhost:8000**  
Swagger UI (interactive docs) at **http://localhost:8000/docs**

Stop the container:
```bash
docker compose down
# or
./demo/run.sh down
```

---

## Option 2 — Local Python

**Prerequisites:** Python 3.11+

```bash
./demo/run-local.sh
```

The API is available at **http://localhost:8000**

Stop the server:
```bash
Ctrl+C
```

---

## Sample Requests

- **[demo/sample-requests.http](demo/sample-requests.http)** — HTTP request file covering all endpoints and edge cases. Requires the [REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client) extension for VS Code (`humao.rest-client`). Once installed, open the file and click **Send Request** above any request block. Works with either startup method — both expose the API on port 8000.
- **[demo/curl-examples.sh](demo/curl-examples.sh)** — Curl commands for all endpoints. Run the whole script (`./demo/curl-examples.sh`) or copy individual commands. Requires `curl`; `jq` is optional for pretty-printing.
- **[demo/sample-data.json](demo/sample-data.json)** — Reference JSON for pre-built transaction objects.
