import os
import time

import psycopg2
import requests

TARGET = os.environ["TARGET_URL"]
INTERVAL = int(os.environ.get("CHECK_INTERVAL", "10"))
TIMEOUT = 3
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
"""


def connect():
    while True:
        try:
            return psycopg2.connect(DSN)
        except psycopg2.OperationalError:
            print("waiting for database...", flush=True)
            time.sleep(2)


def check():
    start = time.time()
    try:
        r = requests.get(TARGET, timeout=TIMEOUT)
        ms = int((time.time() - start) * 1000)
        return r.status_code < 400, r.status_code, ms, None
    except requests.RequestException as e:
        ms = int((time.time() - start) * 1000)
        return False, None, ms, type(e).__name__


def main():
    conn = connect()
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(SCHEMA)
    while True:
        ok, code, ms, err = check()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO checks (target, ok, status_code, latency_ms, error) "
                "VALUES (%s, %s, %s, %s, %s)",
                (TARGET, ok, code, ms, err),
            )
        print(f"ok={ok} status={code} latency={ms}ms error={err}", flush=True)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
