# Pulse

Uptime checks + incident workflow + AI log triage (built in layers).

## Week 1: run locally
    docker compose up --build

Break the demo service:
    curl -X POST localhost:8000/break/error
    curl -X POST localhost:8000/break/healthy

See results:
    docker compose exec db psql -U pulse -c "SELECT checked_at, ok, status_code, latency_ms, error FROM checks ORDER BY id DESC LIMIT 10;"
