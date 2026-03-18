# 🐸 Frog Jump Game (Production Version)

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Pygame](https://img.shields.io/badge/Library-Pygame-green.svg)

개구리를 점프시켜 파리를 잡는 아케이드 게임의 최종 진화형 버전입니다. 전문적인 모듈화 설계를 통해 성능과 유지보수성을 극대화했습니다.

## ✨ 핵심 기술 특징
- **완전 모듈화 (Modular Architecture)**: 모든 핵심 로직이 `core/` 패키지에 부품화되어 관리됩니다.
- **고급 네트워크 엔진**: 서버 통신을 `network.py`로 분리하여 비동기적인 업로드와 큐잉 시스템을 더 안정적으로 처리합니다.
- **최적화된 게임 루프**: `GameEngine` 클래스를 통해 입력 처리, 데이터 업데이트, 화면 렌더링이 명확하게 분리되어 실행됩니다.
- **한글 및 아이콘 지원**: 맑은 고딕 폰트 적용 및 전용 아이콘 설정으로 완성도를 높였습니다.

## 🚀 시작하기
### 1. 필수 라이브러리 설치
```bash
pip install pygame
```
*기존에 필요했던 requests 라이브러리는 표준 라이브러리(urllib) 사용으로 더 이상 필요하지 않습니다.*

### 2. 게임 실행
```bash
python main.py
```

## 📁 파일 구조 가이드
- **`main.py`**: 게임 실행 진입점.
- **`core/`**: 게임의 두뇌 역할을 하는 패키지
  - `engine.py`: 게임의 전체 흐름(Loop)과 상태 관리 엔진.
  - `network.py`: 서버 점수 업로드 및 오프라인 보관(Queueing) 관리.
  - `constants.py`: 물리 상수 및 전역 설정.
  - `assets.py`: 이미지 및 사운드 리소스 관리자.
  - `models.py`: 개구리, 파리 등 게임 객체 설계도.
  - `utils.py`: 로컬 프로필 및 기록 저장 유틸리티.
- **`assets/`**: 게임 그래픽 리소스 폴더.

## 🛠 서버 설정 (`config.json`)
서버와 연동하기 위해 루트 폴더의 `config.json`에서 주소를 수정하세요.
```json
{
  "api_base": "https://frogjump-leaderboard.onrender.com"
}
```
