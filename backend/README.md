# 포트폴리오 스코어 백엔드 API

AI 기반 포트폴리오 분석 서비스의 백엔드 API입니다. Google Gemini 2.5 Flash를 사용하여 포트폴리오 이미지를 분석하고 전문가 수준의 투자 분석 리포트를 마크다운 형식으로 제공합니다.

## 🚀 주요 기능

- **다중 이미지 분석**: 최대 5개의 포트폴리오 이미지를 동시에 분석
- **AI 기반 분석**: Google Gemini 2.5 Flash API를 활용한 전문가 수준의 포트폴리오 분석
- **마크다운 출력**: 구조화된 분석 리포트를 마크다운 형식으로 제공
- **실시간 처리**: 비동기 처리를 통한 빠른 응답 시간
- **이미지 최적화**: 업로드된 이미지 자동 압축 및 최적화

## 🛠 기술 스택

### 핵심 프레임워크
- **FastAPI**: 고성능 웹 API 프레임워크
- **Python 3.13**: 최신 Python 버전
- **Uvicorn**: ASGI 서버

### AI & 분석
- **Google Gemini 2.5 Flash**: 최신 AI 모델을 활용한 이미지 분석
- **google-genai**: Google Gemini API 클라이언트

### 데이터 처리
- **Pydantic**: 데이터 검증 및 설정 관리
- **Pillow**: 이미지 처리 및 최적화
- **python-multipart**: 파일 업로드 처리

### 개발 도구
- **pytest**: 테스트 프레임워크
- **black**: 코드 포매팅
- **flake8**: 코드 린팅
- **isort**: import 정렬

## 📁 프로젝트 구조

```
backend/
├── api/                    # API 엔드포인트
│   ├── __init__.py
│   └── analyze.py         # 포트폴리오 분석 API
├── models/                # 데이터 모델
│   ├── __init__.py
│   └── portfolio.py       # 포트폴리오 관련 모델
├── services/              # 비즈니스 로직
│   ├── __init__.py
│   └── gemini_service.py  # Gemini API 연동
├── utils/                 # 유틸리티 함수
│   ├── __init__.py
│   └── image_utils.py     # 이미지 처리 유틸
├── tests/                 # 테스트 파일
│   ├── __init__.py
│   ├── test_analyze_api.py
│   ├── test_gemini_service.py
│   └── test_image_utils.py
├── main.py               # FastAPI 애플리케이션 진입점
└── requirements.txt      # 의존성 목록
```

## 🔧 설치 및 실행

### 1. 환경 설정

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경변수 설정

`.env` 파일을 생성하고 다음 변수들을 설정하세요:

```env
# Gemini API 키 (필수)
GEMINI_API_KEY=your_gemini_api_key_here

# 서버 설정 (선택사항)
HOST=0.0.0.0
PORT=8000
DEBUG=True
ENVIRONMENT=development

# 프론트엔드 URL (CORS 설정용)
FRONTEND_URL=http://localhost:3000
```

### 3. 서버 실행

```bash
# 개발 서버 실행
python main.py

# 또는 uvicorn으로 직접 실행
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

서버가 실행되면 다음 URL에서 접근할 수 있습니다:
- API 문서: http://localhost:8000/docs
- ReDoc 문서: http://localhost:8000/redoc
- 헬스 체크: http://localhost:8000/health

## 📚 API 문서

### 주요 엔드포인트

#### `POST /api/analyze`
포트폴리오 이미지를 분석하여 마크다운 리포트를 생성합니다.

**요청:**
```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@portfolio1.jpg" \
  -F "files=@portfolio2.jpg"
```

**응답:**
```json
{
  "content": "# AI 총평: 본 포트폴리오는 안정적인 대형 기술주 중심의 고성장 고위험 투자 전략을 기초로...",
  "processing_time": 45.2,
  "images_processed": 2,
  "analysis_id": "uuid-string"
}
```

#### `GET /health`
서버 상태를 확인합니다.

**응답:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "gemini_api_key": "configured",
  "environment": "development"
}
```

## 🧪 테스트

```bash
# 전체 테스트 실행
pytest

# 특정 테스트 파일 실행
pytest tests/test_analyze_api.py

# 커버리지 포함 테스트
pytest --cov=. --cov-report=html
```

## 🚀 배포

### Render.com 배포 설정

1. **환경변수 설정**: Render 대시보드에서 다음 환경변수들을 설정
   - `GEMINI_API_KEY`: Google Gemini API 키
   - `ENVIRONMENT`: `production`
   - `PORT`: `10000` (Render 기본값)

2. **빌드 명령어**: `pip install -r requirements.txt`

3. **시작 명령어**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Docker 배포 (선택사항)

```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔒 보안 고려사항

- **API 키 보안**: `.env` 파일을 `.gitignore`에 추가하여 버전 관리에서 제외
- **CORS 설정**: 프로덕션에서는 특정 도메인만 허용하도록 CORS 설정 수정
- **파일 업로드 제한**: 이미지 파일 크기 및 형식 제한 (최대 10MB, PNG/JPEG만 허용)
- **요청 제한**: 실제 서비스에서는 rate limiting 구현 권장

## 📊 모니터링

### 로깅
- 구조화된 로깅을 통한 요청/응답 추적
- 에러 발생 시 상세한 스택 트레이스 기록
- Gemini API 호출 성공/실패 모니터링

### 헬스 체크
- `/health` 엔드포인트를 통한 서버 상태 확인
- Gemini API 키 설정 상태 확인
- 환경별 설정 정보 제공

## 🤝 기여하기

1. 이슈 생성 또는 기존 이슈 확인
2. 피처 브랜치 생성: `git checkout -b feature/amazing-feature`
3. 변경사항 커밋: `git commit -m 'Add amazing feature'`
4. 브랜치에 푸시: `git push origin feature/amazing-feature`
5. Pull Request 생성

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🆘 문제 해결

### 자주 발생하는 문제들

1. **Gemini API 키 오류**
   ```
   Error: GEMINI_API_KEY environment variable is not set
   ```
   → `.env` 파일에 올바른 API 키를 설정했는지 확인

2. **이미지 업로드 실패**
   ```
   Error: File size exceeds maximum limit
   ```
   → 이미지 파일 크기가 10MB를 초과하지 않는지 확인

3. **CORS 오류**
   ```
   Access-Control-Allow-Origin error
   ```
   → `main.py`의 CORS 설정에서 프론트엔드 URL이 포함되어 있는지 확인

### 지원

문제가 발생하면 다음을 확인해주세요:
1. 로그 파일에서 상세한 오류 메시지 확인
2. `/health` 엔드포인트로 서버 상태 확인
3. 환경변수 설정이 올바른지 확인
4. 의존성이 모두 설치되었는지 확인

---

**포트폴리오 스코어 팀** | AI 기반 포트폴리오 분석 서비스
