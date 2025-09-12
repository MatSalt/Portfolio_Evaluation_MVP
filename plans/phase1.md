# Phase 1: 프로젝트 초기 설정 및 환경 구축 - 구체적 구현 계획

## 📋 Phase 1 개요
**목표**: 2025년 9월 12일 기준 최신 기술 스택으로 개발 환경을 완벽하게 구축하고, 기본 프로젝트 구조를 설정합니다.
**소요 시간**: 1-2일
**핵심**: 최신 기술 스택 (Next.js 15.5.3, FastAPI 0.116.1, Python 3.13.7) 환경 구축

---

## 🎯 1단계: 프로젝트 루트 구조 생성

### 1.1 디렉토리 구조 생성
```bash
# 현재 위치에서 프론트엔드와 백엔드 디렉토리 생성
mkdir -p frontend backend

# 최종 프로젝트 구조
Portfolio_Evaluation_MVP/
├── frontend/          # Next.js 15.5.3 프로젝트
├── backend/           # FastAPI 0.116.1 프로젝트
├── .cursor/          # Cursor 설정 파일들 (이미 존재)
├── Docs/             # 프로젝트 문서들 (이미 존재)
├── plans/            # 단계별 계획 문서들 (이미 존재)
└── .gitignore        # Git 무시 파일 (이미 존재)
```

---

## 🎨 2단계: 프론트엔드 환경 구축 (Next.js 15.5.3)

### 2.1 Next.js 프로젝트 생성
```bash
# frontend 디렉토리로 이동 후 Next.js 프로젝트 생성
cd frontend
npx create-next-app@latest . --typescript --tailwind --app --src-dir --import-alias "@/*"
```

**생성 옵션 설명**:
- `--typescript`: TypeScript 사용
- `--tailwind`: Tailwind CSS 포함
- `--app`: App Router 사용 (Next.js 13+ 권장)
- `--src-dir`: src 디렉토리 사용
- `--import-alias "@/*"`: 절대 경로 import 설정

### 2.2 필수 의존성 설치
```bash
# 마크다운 렌더링 관련 패키지 설치
npm install react-markdown remark-gfm

# 개발 도구 설치 (이미 포함되어 있을 수 있음)
npm install -D eslint prettier @typescript-eslint/eslint-plugin @typescript-eslint/parser
```

### 2.3 TypeScript 설정 강화 (tsconfig.json)
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    // ... 기존 설정 유지
  }
}
```

### 2.4 ESLint 및 Prettier 설정
**.eslintrc.json**:
```json
{
  "extends": ["next/core-web-vitals", "@typescript-eslint/recommended"],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/explicit-function-return-type": "warn"
  }
}
```

**.prettierrc**:
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "tabWidth": 2,
  "useTabs": false
}
```

### 2.5 기본 컴포넌트 구조 생성
```bash
# 프론트엔드 컴포넌트 디렉토리 구조 생성
mkdir -p src/components src/hooks src/types src/utils

# 기본 파일 생성 (빈 파일로 시작)
touch src/components/ImageUploader.tsx
touch src/components/AnalysisDisplay.tsx
touch src/hooks/usePortfolioAnalysis.tsx
touch src/types/portfolio.ts
touch src/utils/api.ts
```

---

## 🔧 3단계: 백엔드 환경 구축 (Python 3.13.7 + FastAPI 0.116.1)

### 3.1 Python 가상환경 생성 및 활성화
```bash
# 백엔드 디렉토리로 이동
cd ../backend

# Python 3.13.7 가상환경 생성
python3.13 -m venv venv

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate

# 가상환경 활성화 확인
python --version  # Python 3.13.7 출력 확인
```

### 3.2 FastAPI 프로젝트 구조 생성
```bash
# 백엔드 디렉토리 구조 생성
mkdir -p api models services utils tests

# 기본 파일 생성
touch main.py
touch api/__init__.py
touch api/analyze.py
touch models/__init__.py
touch models/portfolio.py
touch services/__init__.py
touch services/gemini_service.py
touch utils/__init__.py
touch utils/image_utils.py
touch tests/__init__.py
```

### 3.3 requirements.txt 작성
```txt
# FastAPI 및 서버
fastapi
uvicorn[standard]

# 파일 업로드 처리
python-multipart

# Gemini API
google-genai

# 데이터 검증 및 설정
pydantic
pydantic-settings

# 환경변수 관리
python-dotenv

# 이미지 처리
Pillow

# 테스트
pytest
pytest-asyncio
httpx

# 개발 도구
black
isort
flake8
```

### 3.4 필수 패키지 설치
```bash
# requirements.txt의 모든 패키지 설치 (최신 버전 자동 설치)
pip install -r requirements.txt

# 설치 확인
pip list | grep fastapi  # FastAPI 최신 버전 확인

# 패키지 업데이트 (필요시)
pip install --upgrade -r requirements.txt
```

### 3.5 환경변수 파일 설정
**.env** (백엔드 루트에 생성):
```env
# Gemini API 설정
GEMINI_API_KEY=your_gemini_api_key_here

# FastAPI 설정
DEBUG=True
HOST=0.0.0.0
PORT=8000

# CORS 설정
FRONTEND_URL=http://localhost:3000
```

**.env.example** (Git에 포함할 예시 파일):
```env
# Gemini API 설정
GEMINI_API_KEY=your_gemini_api_key_here

# FastAPI 설정
DEBUG=True
HOST=0.0.0.0
PORT=8000

# CORS 설정
FRONTEND_URL=http://localhost:3000
```

---

## 🔑 4단계: Gemini API 키 설정

### 4.1 Google AI Studio에서 API 키 발급
1. [Google AI Studio](https://aistudio.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. API 키 생성
4. 사용량 제한 및 권한 설정 확인

### 4.2 API 키 보안 설정
```bash
# .env 파일에 실제 API 키 추가
echo "GEMINI_API_KEY=actual_api_key_here" > backend/.env

# .env 파일이 .gitignore에 포함되어 있는지 확인
grep -q "\.env" .gitignore || echo ".env" >> .gitignore
```

### 4.3 API 키 테스트 스크립트 작성
**backend/test_gemini.py**:
```python
import os
from dotenv import load_dotenv
from google import genai

# 환경변수 로드
load_dotenv()

def test_gemini_api():
    """Gemini API 연결 테스트"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
        return False
    
    try:
        client = genai.Client(api_key=api_key)
        # 간단한 텍스트 생성 테스트
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents='안녕하세요! API 연결 테스트입니다.'
        )
        print("✅ Gemini API 연결 성공!")
        print(f"응답: {response.text[:50]}...")
        return True
    except Exception as e:
        print(f"❌ Gemini API 연결 실패: {e}")
        return False

if __name__ == "__main__":
    test_gemini_api()
```

---

## 🧪 5단계: 기본 설정 검증

### 5.1 프론트엔드 실행 테스트
```bash
# frontend 디렉토리에서
cd frontend
npm run dev
# http://localhost:3000 에서 Next.js 기본 페이지 확인
```

### 5.2 백엔드 실행 테스트
```bash
# backend 디렉토리에서 (가상환경 활성화 상태)
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# http://localhost:8000/docs 에서 FastAPI 문서 확인
```

### 5.3 Gemini API 연결 테스트
```bash
# backend 디렉토리에서
python test_gemini.py
# "✅ Gemini API 연결 성공!" 메시지 확인
```

---

## 📋 Phase 1 완료 체크리스트

### ✅ 프로젝트 구조
- [x] frontend/ 디렉토리 생성 완료
- [x] backend/ 디렉토리 생성 완료
- [x] 기본 파일 구조 생성 완료

### ✅ 프론트엔드 설정
- [x] Next.js 15.5.3 프로젝트 생성 완료
- [x] TypeScript strict 모드 활성화 완료
- [x] react-markdown, remark-gfm 설치 완료
- [x] ESLint, Prettier 설정 완료
- [x] 기본 컴포넌트 파일 생성 완료

### ✅ 백엔드 설정
- [x] Python 3.13.7 가상환경 생성 완료
- [x] FastAPI 최신 버전 설치 완료
- [x] 필수 의존성 설치 완료 (최신 버전 자동 설치)
- [x] 프로젝트 구조 생성 완료
- [x] requirements.txt 작성 완료 (최신 버전 자동 설치 설정)

### ✅ API 키 설정
- [x] Google AI Studio에서 Gemini API 키 발급 완료
- [x] .env 파일 설정 완료
- [x] API 키 보안 검증 완료
- [x] Gemini API 연결 테스트 완료

### ✅ 실행 테스트
- [x] 프론트엔드 개발 서버 실행 확인
- [x] 백엔드 FastAPI 서버 실행 확인
- [x] Gemini API 연결 테스트 통과

---

## 🚨 문제 해결 가이드

### Python 버전 문제
```bash
# Python 3.13.7이 설치되지 않은 경우
# macOS (Homebrew 사용)
brew install python@3.13

# Ubuntu/Debian
sudo apt update && sudo apt install python3.13 python3.13-venv

# 설치 확인
python3.13 --version
```

### Node.js 버전 문제
```bash
# Node.js 최신 LTS 버전 사용 권장
node --version  # v18.x 이상 권장
npm --version   # v9.x 이상 권장

# nvm을 사용한 Node.js 버전 관리
nvm install --lts
nvm use --lts
```

### Gemini API 키 오류
1. API 키 형식 확인 (AIza로 시작하는 39자리 문자열)
2. Google AI Studio에서 키 활성화 상태 확인
3. 사용량 제한 설정 확인
4. 네트워크 연결 상태 확인

### 패키지 버전 문제
```bash
# 특정 패키지의 최신 버전 확인
pip show package_name

# 모든 패키지를 최신 버전으로 업데이트
pip install --upgrade -r requirements.txt

# requirements.txt에서 특정 패키지만 업데이트
pip install --upgrade package_name
```

---

## 📚 참고 자료

### 공식 문서 링크
- **Next.js**: https://nextjs.org/docs
- **FastAPI**: https://fastapi.tiangolo.com/reference/
- **Gemini API**: 프로젝트 내 `Docs/gemini_llms.txt` 참고
- **Next.js LLMS**: 프로젝트 내 `Docs/nextjs-llms-full.txt` 참고

### 다음 단계 준비
Phase 1 완료 후 Phase 2 (백엔드 핵심 기능 구현)을 위한 준비:
1. Pydantic 모델 설계 검토
2. Gemini API 프롬프트 엔지니어링 계획
3. FastAPI 엔드포인트 설계 검토

**Phase 1 완료 시점**: 모든 체크리스트 항목이 완료되고, 프론트엔드와 백엔드가 정상적으로 실행되며, Gemini API 연결이 확인된 상태
