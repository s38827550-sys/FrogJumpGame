# core/network.py
import json
import os
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# 상위 폴더(Root)를 기준으로 경로 설정
CORE_DIR = Path(__file__).resolve().parent
BASE_DIR = CORE_DIR.parent
PENDING_FILE = BASE_DIR / "pending_scores.json"
CONFIG_FILE = BASE_DIR / "config.json"

def _load_api_base() -> str:
    try:
        if CONFIG_FILE.exists():
            cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            if isinstance(cfg, dict) and cfg.get("api_base"):
                return str(cfg["api_base"]).rstrip("/")
    except: pass
    return "http://127.0.0.1:8000"

API_BASE = _load_api_base()
TIMEOUT = 3.0

def _http_json(method: str, url: str, payload: Optional[dict] = None) -> Any:
    body = json.dumps(payload).encode("utf-8") if payload else None
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    req = Request(url=url, data=body, method=method.upper(), headers=headers)
    with urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))

def upload_score(nickname: str, score: int) -> bool:
    url = f"{API_BASE}/scores"
    payload = {"nickname": nickname[:16], "score": max(0, int(score))}
    try:
        _http_json("POST", url, payload)
        return True
    except:
        _enqueue(nickname, score)
        return False

def _enqueue(nickname: str, score: int):
    items = _read_pending()
    items.append({"nickname": nickname, "score": score, "ts": int(time.time())})
    if len(items) > 100: items = items[-100:] # 최대 100개 저장
    _write_pending(items)

def _read_pending() -> List[Dict]:
    if not PENDING_FILE.exists(): return []
    try: return json.loads(PENDING_FILE.read_text(encoding="utf-8"))
    except: return []

def _write_pending(items: List):
    PENDING_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

def flush_pending(force: bool = False):
    items = _read_pending()
    if not items: return
    
    still_pending = []
    for it in items:
        if not upload_score(it["nickname"], it["score"]):
            still_pending.append(it)
    _write_pending(still_pending)
