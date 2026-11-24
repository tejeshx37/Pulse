import time

import requests


def check(target, timeout=3):
    """Hit the target once. Returns (ok, status_code, latency_ms, error)."""
    start = time.time()
    try:
        r = requests.get(target, timeout=timeout)
        ms = int((time.time() - start) * 1000)
        ok = r.status_code < 400
        return ok, r.status_code, ms, None if ok else f"HTTP {r.status_code}"
    except requests.RequestException as e:
        ms = int((time.time() - start) * 1000)
        return False, None, ms, type(e).__name__
