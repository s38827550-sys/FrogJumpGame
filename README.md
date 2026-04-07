# 🐸 Frog Jump Game (Final Polished Version)

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Pygame](https://img.shields.io/badge/Library-Pygame-green.svg)

개구리를 점프시켜 하늘을 나는 파리를 잡아 전 세계 사용자들과 경쟁하는 아케이드 게임입니다. 

## ✨ 최신 업데이트 (v1.2.3 / Latest Release)
- **빌드 및 실행 구조 개선**: PyInstaller 빌드 시 자산(Assets)과 사용자 데이터(Data) 경로를 분리하여 실행 환경의 안정성을 극대화했습니다.
- **데이터 영속성 강화**: 이제 게임 데이터(`ranking.txt`, `pending_scores.json`)가 임시 폴더가 아닌 실행 파일이 위치한 폴더에 안전하게 저장됩니다.
- **리소스 경로 감지 자동화**: `core/constants.py`를 통해 개발 환경과 EXE 실행 환경을 자동으로 구분하여 경로를 매핑합니다.
- **네트워크 안정화**: 오프라인 상태에서 발생한 점수 큐잉(Queuing) 및 재전송 로직을 개선했습니다.

## 📦 실행 파일 빌드 (Deployment)
본 게임은 `PyInstaller`를 통해 단일 실행 파일로 배포할 수 있습니다.
```powershell
# 단일 파일 빌드 (아이콘 및 자산 포함)
pyinstaller --onefile --windowed --add-data "assets;assets" --add-data "config.json;." --icon "assets/frog.ico" --name "FrogJump_v1.2.3" main.py
```
*참고: `v1.2.3`부터는 별도의 경로 수정 없이 빌드 후 바로 정상 작동합니다.*

## 🎮 게임 조작법
- **이동**: 좌우 방향키 (`←`, `→`)
- **점프 차징**: `Space` 키 길게 누르기
- **점프**: `Space` 키 떼기 (높이는 차징 시간에 비례)
- **재시작**: 게임 오버 화면에서 `R` 키

## 🚀 시작하기

### 1. 필수 라이브러리 설치
```bash
pip install pygame
```

### 2. 게임 실행
```bash
python main.py
```

## 📁 프로젝트 구조
- **`main.py`**: 게임 실행 진입점.
- **`core/engine.py`**: UI 애니메이션 및 메인 게임 루프.
- **`core/network.py`**: 서버 연동 및 펜딩 점수 처리.
- **`core/assets.py`**: 리소스(이미지, 폰트) 관리자.
- **`core/constants.py`**: 전역 설정 및 경로 상수 (환경별 경로 감지 포함).
