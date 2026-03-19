# core/network.py
import json
import os
import time
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
    except Exception as e:
        print(f"[Network] Config load error: {e}")
    return "https://frogjump-leaderboard.onrender.com" # 기본값

API_BASE = _load_api_base()
TIMEOUT = 5.0 # 타임아웃 약간 증가

def _http_json(method: str, url: str, payload: Optional[dict] = None) -> Any:
    body = json.dumps(payload).encode("utf-8") if payload else None
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "FrogJumpGame/2.0"
    }
    req = Request(url=url, data=body, method=method.upper(), headers=headers)
    
    try:
        with urlopen(req, timeout=TIMEOUT) as resp:
            data = resp.read().decode("utf-8")
            return json.loads(data)
    except HTTPError as e:
        print(f"[Network] HTTP Error {e.code}: {e.read().decode('utf-8', 'ignore')}")
        raise
    except URLError as e:
        print(f"[Network] URL Error: {e.reason}")
        raise
    except Exception as e:
        print(f"[Network] Unexpected Error: {e}")
        raise

def upload_score(nickname: str, score: int) -> bool:
    url = f"{API_BASE}/scores"
    payload = {"nickname": nickname.strip()[:16], "score": max(0, int(score))}
    try:
        result = _http_json("POST", url, payload)
        if result.get("ok"):
            print(f"[Network] Score uploaded. Best: {result.get('best')}")
            return True
        return False
    except Exception as e:
        print(f"[Network] Failed to upload score, enqueuing: {e}")
        _enqueue(nickname, score)
        return False

def _enqueue(nickname: str, score: int):
    items = _read_pending()
    # 중복 저장 방지 (최신 점수 위주)
    items.append({"nickname": nickname, "score": score, "ts": int(time.time())})
    if len(items) > 50: items = items[-50:] 
    _write_pending(items)

def _read_pending() -> List[Dict]:
    if not PENDING_FILE.exists(): return []
    try:
        data = PENDING_FILE.read_text(encoding="utf-8")
        return json.loads(data) if data.strip() else []
    except Exception:
        return []

def _write_pending(items: List):
    try:
        PENDING_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"[Network] Pending write error: {e}")

def flush_pending(force: bool = False):
    items = _read_pending()
    if not items: return
    
    print(f"[Network] Attempting to flush {len(items)} pending scores...")
    still_pending = []
    for it in items:
        # 1초 간격으로 시도하여 서버 부하 방지
        time.sleep(0.5)
        if not upload_score(it["nickname"], it["score"]):
            still_pending.append(it)
    
    _write_pending(still_pending)
