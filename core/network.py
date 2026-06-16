# core/network.py
import json
import time
import sys
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

logger = logging.getLogger(__name__)

def get_data_dir() -> Path:
    if getattr(sys, "frozen", False):  # PyInstaller로 빌드된 exe면
        return Path(sys.executable).parent  # exe 옆 폴더
    return Path(__file__).resolve().parent.parent  # 개발 환경이면 프로젝트 루트

BASE_DIR = Path(__file__).resolve().parent.parent 
DATA_DIR = get_data_dir()

PENDING_FILE = DATA_DIR / "pending_scores.json"
CONFIG_FILE = BASE_DIR / "config.json" 
TOKEN_FILE = Path.home() / ".frogjump_token.json"

def _load_api_base() -> str:
    try:
        if CONFIG_FILE.exists():
            cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            if isinstance(cfg, dict) and cfg.get("api_base"):
                return str(cfg["api_base"]).rstrip("/")
    except Exception:
        logger.exception("Config load failed")
    return "https://frogjump-leaderboard-remake.onrender.com"

API_BASE = _load_api_base()
TIMEOUT = 5.0

# 내부 HTTP 클라이언트
def _http_json(method: str, url: str, payload: Optional[dict] = None, headers_extra: Optional[dict] = None) -> Any:
    body = json.dumps(payload).encode("utf-8") if payload else None
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "FrogJumpGame/1.2.4"
    }
    if headers_extra:
        headers.update(headers_extra)

    safe_headers = {}
    for k, v in headers.items():
        try:
            v.encode('latin-1')
            safe_headers[k] = v
        except (UnicodeEncodeError, AttributeError):
            safe_headers[k] = v.encode('utf-8').decode('latin-1', errors='ignore')

    req = Request(url=url, data=body, method=method.upper(), headers=safe_headers)
    try:
        with urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        logger.error(
            "HTTP Error %s: %s",
            e.code,
            e.read().decode("utf-8", "ignore")
        )
        raise

    except URLError as e:
        logger.error("URL Error: %s", e.reason)
        raise

    except Exception:
        logger.exception("Unexpected HTTP client error")
        raise

# ── 토큰 저장/불러오기 ──────────────────────────────

def save_token(data: dict):
    TOKEN_FILE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

def load_token() -> Optional[Dict]:
    try:
        if TOKEN_FILE.exists():
            return json.loads(TOKEN_FILE.read_text(encoding="utf-8"))
    except Exception:
        logger.exception("Token load failed")
    return None

def clear_token():
    try:
        if TOKEN_FILE.exists():
            TOKEN_FILE.unlink()
    except Exception:
        logger.exception("Token clear failed")

def is_token_valid() -> bool:  # 클라이언트 사이드 JWT 검증
    """토큰 만료 여부 확인"""
    import base64
    token = load_token()
    if not token or not token.get("access_token"):
        return False
    try:
        payload = token["access_token"].split(".")[1]
        payload += "=" * (4 - len(payload) % 4)
        decoded = json.loads(base64.b64decode(payload).decode("utf-8"))
        return decoded.get("exp", 0) > time.time()
    except Exception:
        return False

# ── 인증 ────────────────────────────────────────────

def login(username: str, password: str) -> Optional[Dict]:
    """FastAPI 서버에 로그인 → JWT 토큰 저장"""
    try:
        url = f"{API_BASE}/auth/login"
        result = _http_json("POST", url, {
            "username": username,
            "password": password
        })
        if result.get("access_token"):
            token_data = {
                "access_token": result["access_token"],
                "username": username
            }
            save_token(token_data)
            logger.info("Login success: %s", username)
            return token_data
        logger.warning("Login failed: no token in response")
        return None
    except Exception:
        logger.exception("Login request failed")
        return None

def signup(username: str, password: str) -> bool:
    """FastAPI 서버에 회원가입"""
    try:
        url = f"{API_BASE}/auth/signup"
        result = _http_json("POST", url, {
            "username": username,
            "password": password
        })
        return result.get("ok", False)
    except Exception:
        logger.exception("Signup request failed")
        return False

def logout():
    """로그아웃 - 토큰 삭제"""
    clear_token()
    logger.info("User logged out")

def get_username() -> Optional[str]:
    """현재 로그인된 유저명 반환"""
    token = load_token()
    if token:
        return token.get("username")
    return None

# ── 점수 ────────────────────────────────────────────

def upload_score(score: int) -> bool:
    """인증된 유저의 점수 등록"""
    if not is_token_valid():
        logger.warning("Upload skipped: token missing or expired")
        _enqueue_score(score)
        return False

    token = load_token()
    try:
        url = f"{API_BASE}/scores"
        headers = {"Authorization": f"Bearer {token['access_token']}"}
        result = _http_json("POST", url, {"score": score}, headers)
        if result.get("ok"):
            logger.info(
                "Score uploaded: score=%d best=%s",
                score,
                result.get("best"),
            )
            return True
        return False
    except Exception:
        logger.exception("Score upload failed")
        _enqueue_score(score)
        return False

# ── 오프라인 큐 ──────────────────────────────────────

def _enqueue_score(score: int):
    items = _read_pending()
    items.append({"score": score, "ts": int(time.time())})
    if len(items) > 50:
        items = items[-50:]
    _write_pending(items)

def _read_pending() -> List[Dict]:
    if not PENDING_FILE.exists():
        return []
    try:
        data = PENDING_FILE.read_text(encoding="utf-8")
        return json.loads(data) if data.strip() else []
    except Exception:
        return []

def _write_pending(items: List):
    try:
        PENDING_FILE.write_text(
            json.dumps(items, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    except Exception:
        logger.exception("Pending queue write failed")

def flush_pending():
    """오프라인 중 쌓인 점수 일괄 업로드"""
    items = _read_pending()
    if not items:
        return
    logger.info("Flushing %d pending scores...", len(items))
    still_pending = []
    for it in items:
        time.sleep(0.5)
        if not upload_score(it["score"]):
            still_pending.append(it)
    _write_pending(still_pending)