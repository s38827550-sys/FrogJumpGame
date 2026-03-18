# core/constants.py
import os
import sys
import pygame

def get_base_dir() -> str:
    # core 폴더 안에 있으므로, 한 단계 위인 root를 반환
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASE_DIR = get_base_dir()
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
PROFILE_FILE = os.path.join(BASE_DIR, "player_profile.json")
RANK_FILE = os.path.join(BASE_DIR, "ranking.txt")

# 화면 설정
DESIGN_W, DESIGN_H = 1200, 673
SCREEN_WIDTH, SCREEN_HEIGHT = 1400, 680
SX = SCREEN_WIDTH / DESIGN_W
SY = SCREEN_HEIGHT / DESIGN_H

# 게임 파라미터
GAME_TIME = 60
MAX_JUMP_HEIGHT = 220
MOVE_SPEED = 4.2
AIR_CONTROL = 0.6
GRAVITY = 1.2
JUMP_SPEED = 16

# 게임 상태
STATE_NAME_ENTRY = "name_entry"
STATE_PROLOGUE = "prologue"
STATE_START = "start"
STATE_GAME = "game"
STATE_GAMEOVER = "gameover"

# UI 좌표 (스케일링 적용 헬퍼)
def Sx(x): return int(round(x * SX))
def Sy(y): return int(round(y * SY))
def scale_rect(x, y, w, h):
    return pygame.Rect(Sx(x), Sy(y), Sx(w), Sy(h))

NAME_BOX_RECT = scale_rect(333, 316, 532, 50)
OK_BTN_RECT   = scale_rect(288, 432, 262, 60)
EXIT_BTN_RECT = scale_rect(621, 433, 273, 57)
