# 기술 스택 목록 및 참고 문서

## 📋 프로젝트 기술 스택 개요

이 문서는 **포트폴리오 평가 MVP** 프로젝트에서 사용되는 모든 기술 스택의 목록, 버전, 공식 문서, 참고 문서 링크를 정리한 것입니다.

---

## 🎨 프론트엔드 (Frontend)

### 1. Next.js
- **버전**: 15.5.3
- **공식 문서**: https://nextjs.org/docs
- **GitHub 저장소**: https://github.com/vercel/next.js
- **참고 문서**: `Docs/nextjs-llms-full.txt`
- **설명**: React 기반의 풀스택 웹 프레임워크, App Router 사용

### 2. TypeScript
- **버전**: 5.x (Next.js 15.5.3과 함께 제공)
- **공식 문서**: https://www.typescriptlang.org/docs/
- **설명**: 정적 타입 검사를 제공하는 JavaScript의 상위 집합

### 3. Tailwind CSS
- **버전**: 3.x (Next.js 15.5.3과 함께 제공)
- **공식 문서**: https://tailwindcss.com/docs
- **설명**: 유틸리티 우선 CSS 프레임워크

### 4. React Markdown
- **버전**: 최신 버전
- **공식 문서**: https://github.com/remarkjs/react-markdown
- **설명**: React에서 마크다운을 렌더링하는 라이브러리

### 5. Remark GFM
- **버전**: 최신 버전
- **공식 문서**: https://github.com/remarkjs/remark-gfm
- **설명**: GitHub Flavored Markdown 지원을 위한 Remark 플러그인

### 6. Headless UI
- **버전**: 최신 버전
- **공식 문서**: https://headlessui.com/
- **설명**: 접근성을 고려한 UI 컴포넌트 라이브러리 (탭 컴포넌트)

### 7. Chart.js
- **버전**: 최신 버전
- **공식 문서**: https://www.chartjs.org/
- **설명**: 점수 시각화를 위한 차트 라이브러리

### 8. Recharts
- **버전**: 최신 버전
- **공식 문서**: https://recharts.org/
- **설명**: React용 차트 라이브러리 (Chart.js 대안)

### 9. Zod
- **버전**: 최신 버전
- **공식 문서**: https://zod.dev/
- **설명**: TypeScript 우선 스키마 검증 라이브러리 (프론트엔드 데이터 검증)

---

## 🔧 백엔드 (Backend)

### 1. Python
- **버전**: 3.13.2
- **공식 문서**: https://docs.python.org/3/
- **설명**: 고급 프로그래밍 언어, FastAPI 백엔드 개발에 사용

### 2. FastAPI
- **버전**: 0.116.1
- **공식 문서**: https://fastapi.tiangolo.com/reference/
- **GitHub 저장소**: https://github.com/fastapi/fastapi
- **설명**: 고성능, 자동 문서화, 타입 힌트를 지원하는 Python 웹 프레임워크

### 3. Uvicorn
- **버전**: 0.35.0
- **공식 문서**: https://www.uvicorn.org/
- **설명**: ASGI 서버, FastAPI 애플리케이션 실행에 사용

### 4. Pydantic
- **버전**: 2.11.7
- **공식 문서**: https://docs.pydantic.dev/
- **설명**: 데이터 검증 및 설정 관리 라이브러리
- **구조화된 출력**: Gemini API의 `response_schema`에 사용되는 Pydantic 모델 정의

### 5. Pydantic Settings
- **버전**: 2.10.1
- **공식 문서**: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
- **설명**: Pydantic 기반 설정 관리 라이브러리

### 6. Python Multipart
- **버전**: 0.0.20
- **공식 문서**: https://github.com/andrew-d/python-multipart
- **설명**: 파일 업로드 처리를 위한 라이브러리

### 7. Python Dotenv
- **버전**: 1.1.1
- **공식 문서**: https://python-dotenv.readthedocs.io/
- **설명**: 환경변수 관리를 위한 라이브러리

### 8. Pillow
- **버전**: 11.3.0
- **공식 문서**: https://pillow.readthedocs.io/
- **설명**: Python 이미지 처리 라이브러리

### 9. Starlette
- **버전**: 0.47.3
- **공식 문서**: https://www.starlette.io/
- **설명**: FastAPI의 기반이 되는 ASGI 프레임워크

### 10. AnyIO
- **버전**: 4.10.0
- **공식 문서**: https://anyio.readthedocs.io/
- **설명**: 비동기 프로그래밍을 위한 라이브러리

### 11. Google Auth
- **버전**: 2.40.3
- **공식 문서**: https://google-auth.readthedocs.io/
- **설명**: Google API 인증을 위한 라이브러리

### 12. Requests
- **버전**: 2.32.5
- **공식 문서**: https://requests.readthedocs.io/
- **설명**: HTTP 요청을 위한 Python 라이브러리

### 13. Tenacity
- **버전**: 9.1.2
- **공식 문서**: https://tenacity.readthedocs.io/
- **설명**: 재시도 로직을 위한 라이브러리

---

## 🤖 AI 및 머신러닝

### 1. Google Gemini API
- **모델**: Gemini 2.5 Flash
- **공식 문서**: https://googleapis.github.io/python-genai/
- **참고 문서**: `Docs/gemini_llms.txt`
- **설명**: Google의 최신 AI 모델, 이미지 분석 및 텍스트 생성에 사용
- **구조화된 출력**: Pydantic 모델을 사용한 JSON 스키마 정의
- **Google Search 통합**: Gemini API의 `google_search` 도구를 활용한 실시간 웹 검색
- **그라운딩 기능**: 검색된 정보를 기반으로 한 정확한 분석 제공

### 2. Google Gen AI Python SDK
- **버전**: 1.36.0
- **공식 문서**: https://googleapis.github.io/python-genai/
- **GitHub 저장소**: https://github.com/googleapis/python-genai
- **설명**: Gemini API를 Python에서 사용하기 위한 공식 SDK
- **구조화된 출력 지원**: `response_mime_type="application/json"` 및 `response_schema` 설정
- **Google Search 도구**: `google_search` 도구를 통한 실시간 웹 검색 기능

---

## 🛠️ 개발 도구 및 유틸리티

### 1. ESLint
- **버전**: 최신 버전
- **공식 문서**: https://eslint.org/docs/latest/
- **설명**: JavaScript/TypeScript 코드 품질 검사 도구

### 2. Prettier
- **버전**: 최신 버전
- **공식 문서**: https://prettier.io/docs/en/
- **설명**: 코드 포맷팅 도구

### 3. Black (Python)
- **버전**: 25.1.0
- **공식 문서**: https://black.readthedocs.io/
- **설명**: Python 코드 포맷팅 도구

### 4. isort (Python)
- **버전**: 6.0.1
- **공식 문서**: https://pycqa.github.io/isort/
- **설명**: Python import 문 정렬 도구

### 5. flake8 (Python)
- **버전**: 7.3.0
- **공식 문서**: https://flake8.pycqa.org/
- **설명**: Python 코드 스타일 검사 도구

---

## 🧪 테스트 도구

### 1. Jest (Next.js)
- **버전**: 최신 버전 (Next.js와 함께 제공)
- **공식 문서**: https://jestjs.io/docs/getting-started
- **설명**: JavaScript 테스트 프레임워크

### 2. React Testing Library
- **버전**: 최신 버전 (Next.js와 함께 제공)
- **공식 문서**: https://testing-library.com/docs/react-testing-library/intro/
- **설명**: React 컴포넌트 테스트 라이브러리

### 3. pytest (Python)
- **버전**: 8.4.2
- **공식 문서**: https://docs.pytest.org/
- **설명**: Python 테스트 프레임워크

### 4. pytest-asyncio
- **버전**: 1.2.0
- **공식 문서**: https://pytest-asyncio.readthedocs.io/
- **설명**: pytest에서 비동기 테스트를 위한 플러그인

### 5. httpx
- **버전**: 0.28.1
- **공식 문서**: https://www.python-httpx.org/
- **설명**: HTTP 클라이언트 라이브러리, 테스트에 사용

---

## 🚀 배포 및 인프라

### 1. Vercel
- **공식 문서**: https://vercel.com/docs
- **설명**: 프론트엔드 배포 플랫폼

### 2. Render
- **공식 문서**: https://render.com/docs
- **설명**: 백엔드 배포 플랫폼

### 3. Google Cloud Storage
- **공식 문서**: https://cloud.google.com/storage/docs
- **설명**: 클라우드 스토리지 서비스 (선택적 사용)

---

## 📚 참고 문서 및 리소스

### 프로젝트 내 참고 문서
- **Next.js LLMS 상세 정보**: `Docs/nextjs-llms-full.txt`
- **Gemini API 상세 정보**: `Docs/gemini_llms.txt`
- **프로젝트 요구사항**: `Docs/PRD.md`
- **구현 계획**: `Docs/plan.md`
- **Phase 1 구현 계획**: `plans/phase1.md`

### 추가 학습 자료
- **React 공식 문서**: https://react.dev/
- **Node.js 공식 문서**: https://nodejs.org/docs/
- **Git 공식 문서**: https://git-scm.com/doc
- **Docker 공식 문서**: https://docs.docker.com/

---

## 🔄 버전 관리 정책

### 기술 스택 최신화 정책
- **검색 기준**: 2025년 9월 12일 기준
- **업데이트 주기**: 프로젝트 시작 전 최신 버전 확인 및 적용
- **호환성**: 모든 기술 스택 간의 호환성 검증 필수

### 버전 확인 방법
1. 각 기술의 공식 문서에서 최신 안정 버전 확인
2. GitHub 저장소의 릴리스 페이지 확인
3. 패키지 매니저(npm, pip)를 통한 최신 버전 확인
4. 프로젝트 요구사항에 맞는 버전 선택

---

## 📝 사용 시 주의사항

### 개발 가이드라인
- **Next.js**: 코드 작성 시 항상 공식 문서 참고 필수
- **FastAPI**: 코드 작성 시 항상 공식 문서 참고 필수
- **Gemini API**: 코드 작성 시 항상 공식 문서 및 `gemini_llms.txt` 참고 필수

### 보안 고려사항
- API 키는 환경 변수로 관리
- 민감한 정보는 `.env` 파일에 저장하고 `.gitignore`에 포함
- 프로덕션 배포 시 보안 설정 검토 필수

---

**문서 작성일**: 2025년 9월 12일  
**최종 업데이트**: 2025년 9월 12일 (requirements.txt 버전 동기화)  
**작성자**: AI Assistant
