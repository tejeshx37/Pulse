import os
import time

import psycopg2

from probe import check
from tracker import IncidentTracker

TARGET = os.environ["TARGET_URL"]
INTERVAL = int(os.environ.get("CHECK_INTERVAL", "10"))
THRESHOLD = int(os.environ.get("FAIL_THRESHOLD", "3"))
DSN = os.environ["DATABASE_URL"]

SCHEMA = """
CREATE TABLE IF NOT EXISTS checks (
    id          BIGSERIAL PRIMARY KEY,
    target      TEXT NOT NULL,
    checked_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    ok          BOOLEAN NOT NULL,
    status_code INT,
    latency_ms  INT,
    error       TEXT
);
CREATE INDEX IF NOT EXISTS idx_checks_checked_at ON checks (checked_at);

CREATE TABLE IF NOT EXISTS incidents (
    id            BIGSERIAL PRIMARY KEY,
    target        TEXT NOT NULL,
    opened_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at   TIMESTAMPTZ,
    status        TEXT NOT NULL DEFAULT 'open',
    trigger_error TEXT
);
"""


def connect():
    while True:
        try:
            return psycopg2.connect(DSN)
        except psycopg2.OperationalError:
            print("waiting for database...", flush=True)
            time.sleep(2)


def main():
    conn = connect()
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(SCHEMA)

    tracker = IncidentTracker(THRESHOLD)
    # Survive restarts: if an incident is already open in the database, remember it.
    with conn.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM incidents WHERE target = %s AND status = 'open'", (TARGET,)
        )
        tracker.is_open = cur.fetchone() is not None

    while True:
        ok, code, ms, err = check(TARGET)
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO checks (target, ok, status_code, latency_ms, error) "
                "VALUES (%s, %s, %s, %s, %s)",
                (TARGET, ok, code, ms, err),
            )
            action = tracker.update(ok)
            if action == "open":
                cur.execute(
                    "INSERT INTO incidents (target, trigger_error) VALUES (%s, %s)",
                    (TARGET, err),
                )
                print("INCIDENT OPENED", flush=True)
            elif action == "resolve":
                cur.execute(
                    "UPDATE incidents SET status = 'resolved', resolved_at = now() "
                    "WHERE target = %s AND status = 'open'",
                    (TARGET,),
                )
                print("INCIDENT RESOLVED", flush=True)
        print(f"ok={ok} status={code} latency={ms}ms error={err}", flush=True)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
