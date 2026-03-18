# core/utils.py
import json
import os
from .constants import PROFILE_FILE, RANK_FILE

def load_profile():
    if not os.path.exists(PROFILE_FILE):
        return None
    try:
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def save_profile(nickname: str):
    data = {"nickname": nickname}
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_ranking():
    if not os.path.exists(RANK_FILE):
        return []
    with open(RANK_FILE, "r", encoding="utf-8") as f:
        ranks = []
        for line in f.readlines():
            line = line.strip()
            if line.isdigit():
                ranks.append(int(line))
        return ranks

def save_score_local(new_score: int):
    ranks = load_ranking()
    ranks.append(int(new_score))
    ranks = sorted(ranks, reverse=True)[:5]
    with open(RANK_FILE, "w", encoding="utf-8") as f:
        for r in ranks:
            f.write(str(r) + "\n")
    return ranks
