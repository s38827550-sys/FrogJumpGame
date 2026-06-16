# FrogJump Game Client

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Pygame](https://img.shields.io/badge/Library-Pygame-green.svg)

<img width="1393" height="704" alt="Image" src="https://github.com/user-attachments/assets/55dc879f-e0a9-41b8-9a8b-5b05f9de3530" />

pygame 기반 점프 게임 클라이언트
FastAPI 서버와 연동하여 사용자 인증 및 온라인 웹 서비스를 제공합니다.

## 최신 업데이트 (v.1.2.4)
1.JWT 기반 로그인 기능을 도입하면서 별도의 닉네임 입력 화면을 제거
기존에는 로컬 랭킹 저장을 위해 닉네임을 직접 입력받았지만, 현재는 로그인한 계정의 사용자 정보를 사용하므로 중복 입력이 필요 없어졌습니다.

2.랭킹 저장소를 PostgreSQL로 통합
기존에는 ranking.txt를 이용한 로컬 저장과 PostgreSQL을 동시에 사용했지만, 현재는 PostgreSQL을 단일 데이터 저장소(Single Source of Truth)로 사용하도록 변경하였습니다.
이에 따라 utils.py의 로컬 랭킹 저장 및 조회 기능은 제거하였습니다.

## 실행 파일 빌드 (Deployment)
본 게임은 `PyInstaller`를 통해 단일 실행 파일로 배포할 수 있습니다.
```powershell
# 단일 파일 빌드 (아이콘 및 자산 포함)
pyinstaller --onefile --windowed --add-data "assets;assets" --add-data "config.json;." --icon "assets/frog.ico" --name "FrogJump_v1.2.4" main.py
```
Github Action으로 자동화 예정 중에 있습니다.

## 게임 조작법
- **이동**: 좌우 방향키 (`←`, `→`)
- **점프 차징**: `Space` 키 길게 누르기
- **점프**: `Space` 키 떼기 (높이는 차징 시간에 비례)
- **재시작**: 게임 오버 화면에서 `R` 키

## 시작하기

### 1. 필수 라이브러리 설치
```bash
pip install pygame
```

### 2. 게임 실행
```bash
python main.py
```

## 프로젝트 구조

```directory
FrogJump-Client/
├──  assets/                  # 이미지, 사운드 등 게임 리소스 디렉토리
├──  core/                    # 게임 핵심 로직 및 모듈
│   ├──  __init__.py
│   ├──  assets.py            # 리소스 로드 및 관리 매니저
│   ├──  constants.py         # 게임 내 전역 상수 (화면 크기, 프레임 등)
│   ├──  engine.py            # 메인 게임 루프 및 상태 관리 엔진
│   ├──  models.py            # 게임 객체(Entity) 모델
│   └──  network.py           # 서버 통신 및 패킷 처리를 위한 네트워크 모듈
├──  config.json              # 서버 IP, 포트 및 클라이언트 설정 파일
├──  main.py                  # 애플리케이션 진입점 (Entry Point)
└──  README.md                # 프로젝트 문서
