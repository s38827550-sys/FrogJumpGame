# main.py
import os
import sys

# 현재 실행 파일의 폴더를 시스템 경로에 추가하여 
# core 패키지를 어디서든 불러올 수 있게 합니다.
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from core.engine import GameEngine
except ImportError as e:
    print(f"모듈 로드 오류: {e}")
    print("core 폴더가 main.py와 같은 위치에 있는지 확인하세요.")
    sys.exit(1)

def main():
    try:
        game = GameEngine()
        game.run()
    except Exception as e:
        print(f"게임 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
