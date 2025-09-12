# Portfolio Evaluation MVP 구현 계획

## 📋 프로젝트 개요
포트폴리오 화면 캡처를 업로드하면 AI가 종합적인 투자 분석을 수행하여 전문가 수준의 포트폴리오 평가 리포트를 제공하는 MVP

**목표**: 2025년 9월 12일 기준 최신 기술 스택으로 안정적이고 확장 가능한 MVP 구현

---

## 🎯 Phase 1: 프로젝트 초기 설정 및 환경 구축 (1-2일)

### 1.1 개발 환경 설정
```bash
# 프로젝트 루트 구조 생성
mkdir -p frontend backend
```

#### **프론트엔드 설정**
- [ ] Next.js 15.3 프로젝트 생성 (`npx create-next-app@latest frontend --typescript --tailwind --app`)
- [ ] 필수 의존성 설치:
  - `react-markdown` (마크다운 렌더링)
  - `remark-gfm` (마크다운 확장)
- [ ] ESLint, Prettier 설정
- [ ] TypeScript strict 모드 활성화

#### **백엔드 설정**
- [ ] Python 3.12 가상환경 생성
- [ ] FastAPI 0.110.0 프로젝트 구조 생성
- [ ] 필수 의존성 설치:
  - `fastapi`
  - `uvicorn`
  - `python-multipart`
  - `google-generativeai`
  - `pydantic`
  - `python-dotenv`
- [ ] 환경변수 파일 (.env) 설정

#### **API 키 설정**
- [ ] Google AI Studio에서 Gemini API 키 발급
- [ ] 환경변수 설정 (GEMINI_API_KEY)
- [ ] API 키 보안 검증 (키 권한, 사용량 제한 확인)

---

## 🔧 Phase 2: 백엔드 핵심 기능 구현 (3-4일)

### 2.1 FastAPI 기본 구조 구축
```
backend/
├── main.py                  # FastAPI 앱 진입점
├── api/
│   └── analyze.py          # 포트폴리오 분석 API
├── models/
│   └── portfolio.py        # Pydantic 모델 정의
├── services/
│   └── gemini_service.py   # Gemini API 연동 서비스
├── utils/
│   └── image_utils.py      # 이미지 처리 유틸리티
└── requirements.txt
```

### 2.2 데이터 모델 정의 (models/portfolio.py)
- [ ] **AnalysisRequest** 모델: 이미지 업로드 요청
- [ ] **PortfolioAnalysis** 모델: 분석 결과 응답
  - aiSummary: str
  - overallScore: int (0-100)
  - dimensionScores: DimensionScores
  - detailedAnalysis: DetailedAnalysis
  - strengths: List[str]
  - weaknesses: List[str]
  - opportunities: List[str]
  - stocks: List[StockAnalysis]
- [ ] **StockAnalysis** 모델: 개별 종목 분석
  - stockName: str
  - overallScore: int
  - fundamentalScore: int
  - techPotentialScore: int
  - macroScore: int
  - marketSentimentScore: int
  - leadershipScore: int
  - detailedAnalysis: str

### 2.3 Gemini API 연동 서비스 (services/gemini_service.py)
- [ ] **이미지 전처리 함수**:
  - 파일 유효성 검증 (PNG, JPEG만 허용)
  - 파일 크기 제한 (10MB)
  - Base64 인코딩
- [ ] **프롬프트 엔지니어링**:
  - 포트폴리오 분석 전문가 역할 정의
  - expected_result.md 형식에 맞춘 구조화된 JSON 응답 요청
  - 한국어 분석 결과 생성 지시
- [ ] **API 호출 최적화**:
  - 비동기 처리 (async/await)
  - 타임아웃 설정 (30초)
  - 재시도 로직 (최대 3회)
  - 응답 캐싱 (동일 이미지 해시 기반)

### 2.4 API 엔드포인트 구현 (api/analyze.py)
- [ ] **POST /api/analyze** 구현:
  - multipart/form-data 파일 수신
  - 이미지 유효성 검증
  - Gemini API 호출
  - JSON 응답 파싱 및 검증
  - 에러 핸들링 (400, 500, 503)
- [ ] **Health Check 엔드포인트** (GET /health)
- [ ] **CORS 설정** (프론트엔드 도메인 허용)

---

## 🎨 Phase 3: 프론트엔드 UI/UX 구현 (3-4일)

### 3.1 컴포넌트 구조 설계
```
frontend/src/
├── app/
│   ├── page.tsx            # 메인 페이지
│   └── layout.tsx          # 레이아웃
├── components/
│   ├── ImageUploader.tsx   # 이미지 업로드
│   └── AnalysisDisplay.tsx # 마크다운 결과 표시
├── hooks/
│   └── usePortfolioAnalysis.tsx # 분석 API 호출 훅
├── types/
│   └── portfolio.ts        # TypeScript 타입 정의
└── utils/
    └── api.ts              # API 유틸리티
```

### 3.2 ImageUploader 컴포넌트
- [ ] **드래그 앤 드롭 기능**:
  - 시각적 드롭존 디자인
  - 드래그 상태 피드백
  - 파일 타입 검증 (클라이언트 사이드)
- [ ] **파일 선택 UI**:
  - 스타일링된 파일 입력 버튼
  - 이미지 썸네일 미리보기
  - 파일 정보 표시 (이름, 크기)
- [ ] **상태 관리**:
  - idle, loading, success, error 상태
  - 상태별 UI 변화
  - 에러 메시지 표시

### 3.3 AnalysisDisplay 컴포넌트
- [ ] **마크다운 렌더링**:
  - `react-markdown`으로 API 응답 텍스트를 직접 렌더링
  - `remark-gfm` 플러그인으로 테이블, 주석 등 확장 마크다운 지원
  - 시각적 컴포넌트(게이지, 차트) 없이 텍스트와 테이블 중심으로 결과 표시
  - 반응형 레이아웃

### 3.4 상태 관리 및 API 연동
- [ ] **usePortfolioAnalysis 훅**:
  - 파일 업로드 및 분석 요청
  - 로딩 상태 관리
  - 에러 핸들링
  - 결과 데이터 캐싱
- [ ] **API 유틸리티**:
  - fetch 기반 API 호출
  - FormData 구성
  - 응답 에러 처리

---

## 🧪 Phase 4: 테스트 및 검증 (2일)

### 4.1 백엔드 테스트
- [ ] **단위 테스트** (pytest):
  - 이미지 처리 함수 테스트
  - Gemini API 모킹 테스트
  - 데이터 모델 검증 테스트
- [ ] **통합 테스트**:
  - API 엔드포인트 전체 플로우 테스트
  - 실제 샘플 이미지로 E2E 테스트
  - 에러 케이스 테스트 (잘못된 파일, API 오류 등)

### 4.2 프론트엔드 테스트
- [ ] **컴포넌트 테스트** (Jest + React Testing Library):
  - ImageUploader 상호작용 테스트
  - AnalysisDisplay 렌더링 테스트
  - 상태 변화 테스트
- [ ] **E2E 테스트**:
  - 전체 사용자 플로우 테스트
  - 다양한 브라우저 호환성 테스트

### 4.3 성능 및 보안 테스트
- [ ] **성능 테스트**:
  - 이미지 처리 속도 측정
  - Gemini API 응답 시간 분석
  - 메모리 사용량 모니터링
- [ ] **보안 테스트**:
  - 파일 업로드 보안 검증
  - API 키 노출 방지 확인
  - CORS 정책 테스트

---

## 🚀 Phase 5: 배포 및 운영 설정 (1-2일)

### 5.1 배포 환경 구성
#### **프론트엔드 (Vercel)**
- [ ] Vercel 프로젝트 연결
- [ ] 환경변수 설정 (API 엔드포인트)
- [ ] 빌드 최적화 설정
- [ ] 도메인 연결

#### **백엔드 (Render)**
- [ ] Render 서비스 생성
- [ ] 환경변수 설정 (GEMINI_API_KEY)
- [ ] Dockerfile 또는 requirements.txt 설정
- [ ] Health Check 설정

### 5.2 CI/CD 파이프라인
- [ ] **GitHub Actions 설정**:
  - 코드 푸시 시 자동 테스트 실행
  - 테스트 통과 시 자동 배포
  - 환경별 배포 분리 (dev, prod)

### 5.3 모니터링 및 로깅
- [ ] **백엔드 로깅**:
  - API 호출 로그
  - 에러 로그 수집
  - Gemini API 사용량 모니터링
- [ ] **프론트엔드 모니터링**:
  - 사용자 행동 분석
  - 성능 메트릭 수집
  - 에러 추적

---

## 📊 Phase 6: 최종 검증 및 문서화 (1일)

### 6.1 최종 테스트
- [ ] **다양한 포트폴리오 이미지 테스트**:
  - 국내 주요 증권사 앱 스크린샷
  - 해외 브로커리지 앱 스크린샷
  - 다양한 해상도 및 품질의 이미지
- [ ] **사용자 시나리오 테스트**:
  - 정상 플로우 테스트
  - 에러 상황 대응 테스트
  - 성능 부하 테스트

### 6.2 문서 업데이트
- [ ] README.md 작성 (설치, 실행, 배포 방법)
- [ ] API 문서 생성 (FastAPI 자동 생성 활용)
- [ ] 사용자 가이드 작성
- [ ] 개발자 문서 업데이트

---

## 🔧 기술적 고려사항

### 보안
- 업로드된 이미지 즉시 삭제 (처리 완료 후)
- API 키 환경변수 관리
- 파일 크기 및 형식 제한
- [ ] Rate Limiting 적용

### 성능 최적화
- **분석 품질 최우선**: API 호출 시 비용이나 속도보다 상세하고 정확한 분석 결과를 얻도록 설정
- **이미지 압축**: 클라이언트/서버 사이드에서 이미지 압축
- **API 응답 캐싱**: 동일 이미지 해시 기반으로 캐싱

### 에러 처리
- 네트워크 오류 재시도 로직
- 사용자 친화적 에러 메시지
- 로그 수집 및 모니터링
- Graceful degradation

---

## 📅 전체 일정 요약

| Phase | 작업 내용 | 소요 시간 | 핵심 산출물 |
|-------|----------|----------|------------|
| 1 | 프로젝트 초기 설정 | 1-2일 | 개발 환경, API 키 |
| 2 | 백엔드 구현 | 3-4일 | FastAPI 서버, Gemini 연동 |
| 3 | 프론트엔드 구현 | 3-4일 | React 컴포넌트, UI/UX |
| 4 | 테스트 및 검증 | 2일 | 테스트 코드, 성능 검증 |
| 5 | 배포 및 운영 | 1-2일 | 프로덕션 환경 |
| 6 | 최종 검증 | 1일 | 완성된 MVP |

**총 예상 소요 시간: 11-15일**

---

## 🎯 성공 기준

1. **기능적 요구사항**:
   - 포트폴리오 이미지 업로드 및 분석 완료
   - expected_result.md 수준의 상세한 분석 결과 제공
   - 마크다운 형식의 시각적 결과 표시

2. **비기능적 요구사항**:
   - 이미지 처리 시간 30초 이내
   - 99% 이상의 서비스 가용성
   - 모바일/데스크톱 반응형 지원

3. **품질 요구사항**:
   - 80% 이상의 테스트 커버리지
   - 보안 취약점 0개
   - 성능 최적화 완료

---

## 🚨 리스크 관리

### 고위험 요소
1. **Gemini API 호출 실패**: 재시도 로직 및 fallback 메커니즘
2. **이미지 인식 정확도**: 다양한 샘플로 충분한 테스트
3. **API 비용 관리**: 사용량 모니터링 및 제한 설정

### 중위험 요소
1. **성능 병목**: 비동기 처리 및 캐싱 적용
2. **브라우저 호환성**: 최신 브라우저 기준 개발

### 저위험 요소
1. **UI/UX 개선**: 점진적 개선 가능
2. **추가 기능**: MVP 완료 후 확장

---

이 계획을 따라 단계별로 구현하면 안정적이고 확장 가능한 Portfolio Evaluation MVP를 성공적으로 완성할 수 있습니다.
