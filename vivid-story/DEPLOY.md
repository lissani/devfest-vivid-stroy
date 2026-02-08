# Vivid Story 배포 가이드

Streamlit UI(`frontend/streamlit_app.py`)와 FastAPI 백엔드를 배포하는 방법입니다.

---

## 아키텍처 요약

- **프론트엔드**: Streamlit → 사용자에게 보이는 웹 UI
- **백엔드**: FastAPI (`app/main.py`) → 스토리 생성 API
- **연결**: 프론트엔드는 `API_URL` 환경 변수로 백엔드 주소를 지정

배포 시 **백엔드를 먼저 배포**한 뒤, 그 URL을 프론트엔드의 `API_URL`로 설정해야 합니다.

---

## 방법 1: Streamlit Community Cloud (프론트) + Render/Railway (백엔드)

가장 간단한 무료 조합입니다.

### 1단계: 백엔드 배포 (Render 예시)

1. [Render](https://render.com) 가입 후 **New → Web Service**
2. GitHub 저장소 연결 후 설정:
   - **Root Directory**: `vivid-story` (또는 저장소 루트가 vivid-story면 비움)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Working Directory**: `vivid-story` (또는 `vivid-story/app`이 아니라 `vivid-story`에서 위 명령 실행되도록)
3. **Environment**에 API 키 추가:
   - `GEMINI_API_KEY`, `ELEVENLABS_API_KEY` 등 (`.env`에 쓰던 값들)
4. Deploy 후 **백엔드 URL** 확인 (예: `https://vivid-story-api.onrender.com`)

> **Render 참고**: 루트가 `Devfest`이고 그 안에 `vivid-story`가 있다면, Root Directory를 `vivid-story`로 두고 Start Command는 `cd app && uvicorn main:app --host 0.0.0.0 --port $PORT` 또는 프로젝트 구조에 맞게 조정하세요.

### 2단계: Streamlit Community Cloud로 프론트엔드 배포

1. [share.streamlit.io](https://share.streamlit.io) 접속 → GitHub 로그인
2. **New app** 선택
3. 설정:
   - **Repository**: 본인 GitHub `Devfest` (또는 vivid-story가 있는 저장소)
   - **Branch**: `main`
   - **Main file path**: `vivid-story/frontend/streamlit_app.py`
   - **App URL**: 원하면 서브경로 지정 (예: `vivid-story`)
4. **Advanced settings**에서 환경 변수 추가:
   - `API_URL` = `https://vivid-story-api.onrender.com` (1단계에서 만든 백엔드 URL)
5. Deploy 클릭

이제 Streamlit이 제공하는 URL(예: `https://xxx.streamlit.app`)로 접속하면 됩니다.

---

## 방법 2: Railway에서 둘 다 배포

[Railway](https://railway.app) 하나로 백엔드 + 프론트엔드 모두 배포할 수 있습니다.

### 백엔드 서비스

1. Railway 대시보드 → **New Project** → **Deploy from GitHub repo** → `Devfest` 선택
2. **Root Directory**: `vivid-story`
3. **Settings**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. **Variables**에 `GEMINI_API_KEY`, `ELEVENLABS_API_KEY` 등 추가
5. **Settings → Generate Domain**으로 URL 생성 (예: `https://vivid-story-api.up.railway.app`)

### 프론트엔드 서비스 (같은 프로젝트에 서비스 추가)

1. 같은 Project에서 **New Service** → **GitHub Repo** 다시 선택
2. **Root Directory**: `vivid-story`
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `streamlit run frontend/streamlit_app.py --server.port $PORT --server.address 0.0.0.0`
5. **Variables**에 `API_URL=https://vivid-story-api.up.railway.app` 추가 (위에서 만든 백엔드 URL)
6. **Generate Domain**으로 Streamlit 앱 URL 생성

---

## 방법 3: Docker로 배포 (VPS, AWS EC2, GCP 등)

서버를 직접 둔다면 Docker로 한 번에 띄울 수 있습니다.

### Dockerfile 예시 (백엔드)

`vivid-story/Dockerfile.api`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
COPY data/ ./data/
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Dockerfile 예시 (Streamlit)

`vivid-story/Dockerfile.streamlit`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY frontend/ ./frontend/
ENV API_URL=http://backend:8000
EXPOSE 8501
CMD ["streamlit", "run", "frontend/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### docker-compose.yml (로컬/서버 테스트)

```yaml
version: "3"
services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8000:8000"
    env_file: .env

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.streamlit
    ports:
      - "8501:8501"
    environment:
      - API_URL=http://backend:8000
    depends_on:
      - backend
```

서버에서:

```bash
cd vivid-story
docker compose up -d
```

- 백엔드: `http://서버IP:8000`
- Streamlit: `http://서버IP:8501`

---

## 체크리스트

| 항목 | 확인 |
|------|------|
| 백엔드 먼저 배포 후 URL 확보 | |
| 프론트엔드 `API_URL`에 백엔드 URL 설정 | |
| `.env`에 있던 API 키들을 배포 환경 변수에 등록 | |
| CORS: 백엔드가 이미 `allow_origins=["*"]`라서 도메인 추가 설정 없음 | |
| `data/` 등 정적 파일이 필요하면 백엔드 서비스에 포함 또는 스토리지 사용 | |

---

## 문제 해결

- **Streamlit에서 API 연결 실패**: `API_URL`이 배포된 백엔드 URL인지, `https`인지 확인. 브라우저와 같은 공개 네트워크에서 접근 가능해야 함.
- **Render 무료 티어**: 15분 비활성 시 슬립 → 첫 요청이 느릴 수 있음. Railway 무료 티어도 유사한 제한 있음.
- **타임아웃**: 스토리 생성이 오래 걸리면 Render/Railway 기본 타임아웃(예: 30초)을 늘리거나, 스트리밍/백그라운드 작업 구조로 변경 검토.

필요하면 사용하는 플랫폼(Render / Railway / Streamlit Cloud 등) 이름을 알려주면 그에 맞춰 명령어와 설정만 더 구체적으로 적어줄 수 있습니다.
