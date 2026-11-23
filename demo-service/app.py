import json
import logging
import os
import sys
import time

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()
MODE = {"state": "healthy"}  # healthy | slow | error | crash


class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "ts": self.formatTime(record),
            "level": record.levelname,
            "msg": record.getMessage(),
        })


handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
log = logging.getLogger("demo")
log.addHandler(handler)
log.setLevel(logging.INFO)


@app.get("/health")
def health():
    state = MODE["state"]
    if state == "slow":
        log.warning("slow response injected, sleeping 5s")
        time.sleep(5)
    elif state == "error":
        log.error("db timeout: connection to orders-db timed out after 30s")
        return JSONResponse({"status": "error"}, status_code=500)
    elif state == "crash":
        log.critical("out of memory, process exiting")
        os._exit(1)
    log.info("health check ok")
    return {"status": "ok"}


@app.post("/break/{mode}")
def set_mode(mode: str):
    if mode not in ("healthy", "slow", "error", "crash"):
        return JSONResponse({"error": "unknown mode"}, status_code=400)
    MODE["state"] = mode
    log.warning(f"mode set to {mode}")
    return {"mode": mode}
