# Portfolio Evaluation MVP 구현 계획

## 📋 프로젝트 개요
포트폴리오 화면 캡처를 업로드하면 AI가 종합적인 투자 분석을 수행하여 expected_result.md와 동일한 형식의 마크다운 텍스트로 전문가 수준의 포트폴리오 평가 리포트를 제공하는 MVP

**목표**: 2025년 9월 12일 기준 최신 기술 스택(Next.js 15.5.3, FastAPI 0.116.1, Python 3.13.7)으로 간단하고 안정적인 MVP 구현

---

## 🎯 Phase 1: 프로젝트 초기 설정 및 환경 구축 (1-2일)

### 1.1 개발 환경 설정
```bash
# 프로젝트 루트 구조 생성
mkdir -p frontend backend
```

#### **프론트엔드 설정**
- [ ] Next.js 15.5.3 프로젝트 생성 (`npx create-next-app@latest frontend --typescript --tailwind --app`)
- [ ] **Next.js 공식 문서 참고 필수**: https://nextjs.org/docs, https://github.com/vercel/next.js
- [ ] **Next.js LLMS 상세 정보 참고**: `/Users/choongheon/Desktop/Rinia/projects/Portfolio_Evaluation_MVP/Docs/nextjs-llms-full.txt`
- [ ] 필수 의존성 설치:
  - `react-markdown` (마크다운 렌더링)
  - `remark-gfm` (마크다운 확장)
- [ ] ESLint, Prettier 설정
- [ ] TypeScript strict 모드 활성화

#### **백엔드 설정**
- [ ] Python 3.13.7 가상환경 생성
- [ ] FastAPI 0.116.1 프로젝트 구조 생성
- [ ] **FastAPI 공식 문서 참고 필수**: https://fastapi.tiangolo.com/reference/, https://github.com/fastapi/fastapi
- [ ] 필수 의존성 설치:
  - `fastapi`
  - `uvicorn`
  - `python-multipart`
  - `google-genai`
  - `pydantic`
  - `python-dotenv`
- [ ] 환경변수 파일 (.env) 설정

#### **API 키 설정**
- [ ] Google AI Studio에서 Gemini API 키 발급
- [ ] 환경변수 설정 (GEMINI_API_KEY)
- [ ] API 키 보안 검증 (키 권한, 사용량 제한 확인)

---

## 🔧 Phase 2: 백엔드 핵심 기능 구현 (3-4일)

**참고 자료**: Gemini API 상세 정보는 `/Users/choongheon/Desktop/Rinia/projects/Portfolio_Evaluation_MVP/Docs/gemini_llms.txt` 파일을 참고하세요.

### 2.1 FastAPI 기본 구조 구축 (공식 문서 참고 필수)
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
- [ ] **AnalysisResponse** 모델: 분석 결과 응답
  - content: str (마크다운 텍스트)
  - processing_time: float
  - request_id: str
- [ ] **ErrorResponse** 모델: 에러 응답
  - error: str
  - detail: Optional[str]
  - code: Optional[str]

### 2.3 Gemini API 연동 서비스 (services/gemini_service.py)
- [ ] **이미지 전처리 함수**:
  - 파일 유효성 검증 (PNG, JPEG만 허용)
  - 파일 크기 제한 (10MB)
  - Base64 인코딩
- [ ] **프롬프트 엔지니어링**:
  - 포트폴리오 분석 전문가 역할 정의
  - expected_result.md와 동일한 마크다운 형식으로 출력 요청
  - 한국어 분석 결과 생성 지시
- [ ] **API 호출 최적화**:
  - Google Gen AI Python SDK 사용
  - **Gemini LLMS 상세 정보 참고**: `/Users/choongheon/Desktop/Rinia/projects/Portfolio_Evaluation_MVP/Docs/gemini_llms.txt`
  - 비동기 처리 (async/await)
  - 타임아웃 설정 (30초)
  - 재시도 로직 (최대 3회)
  - 응답 캐싱 (동일 이미지 해시 기반)

### 2.4 API 엔드포인트 구현 (api/analyze.py)
- [ ] **POST /api/analyze** 구현:
  - multipart/form-data 파일 수신
  - 이미지 유효성 검증
  - Gemini API 호출
  - 마크다운 텍스트 응답 반환
  - 에러 핸들링 (400, 500, 503)
- [ ] **Health Check 엔드포인트** (GET /health)
- [ ] **CORS 설정** (프론트엔드 도메인 허용)

---

## 🎨 Phase 3: 프론트엔드 UI/UX 구현 (3-4일)

**참고 자료**: Next.js LLMS 상세 정보는 `/Users/choongheon/Desktop/Rinia/projects/Portfolio_Evaluation_MVP/Docs/nextjs-llms-full.txt` 파일을 참고하세요.

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

## 🔍 Phase 4: Google Search 기능 통합 (2-3일)

**목표**: Gemini API에 Google Search 도구를 통합하여 실시간 웹 검색을 통한 최신 시장 정보 기반 포트폴리오 분석 제공

### 4.1 Google Search API 통합 설정
- [ ] **Gemini API Google Search 도구 활성화**:
  - `google_search` 도구를 모델 구성에 추가
  - 공식 문서 참고: https://ai.google.dev/gemini-api/docs/google-search?hl=ko
  - Live API 도구 사용 가이드: https://ai.google.dev/gemini-api/docs/live-tools?hl=ko
- [ ] **API 호출 코드 수정**:
  ```python
  tools = [{"google_search": {}}]
  config = {"tools": tools}
  response = client.models.generate_content(
      model='gemini-2.5-flash',
      contents=[prompt_text, image_data],
      tools=tools
  )
  ```

### 4.2 프롬프트 엔지니어링 업데이트
- [ ] **기존 프롬프트 유지**: 복잡한 Google Search 지침 없이 기본 분석 프롬프트 사용
- [ ] **단순한 분석 결과 형식**: expected_result.md와 동일한 형식으로 출력

### 4.3 백엔드 API 응답 형식 유지
- [ ] **기존 AnalysisResponse 모델 유지**:
  ```python
  class AnalysisResponse(BaseModel):
      content: str  # 마크다운 텍스트
      processing_time: float
      request_id: str
  ```
- [ ] **복잡한 메타데이터 추출 로직 제거**: 단순한 응답 형식 유지

### 4.4 기본 캐싱 시스템 구현
- [ ] **이미지 분석 결과 캐싱**:
  - 동일한 이미지 해시에 대해 일정 시간 동안 캐시된 결과 활용
  - 메모리 기반 간단한 캐싱 구현
- [ ] **캐시 무효화 전략**:
  - 시간 기반 자동 만료 (예: 1시간)

### 4.5 성능 최적화 및 모니터링
- [ ] **응답 시간 최적화**:
  - 타임아웃 설정 (분석: 30초)
  - 부분 실패 시 기본 분석 결과 제공
- [ ] **모니터링 시스템 구축**:
  - Gemini API 사용량 추적
  - 응답 시간 모니터링

### 4.6 에러 처리 및 Fallback 메커니즘
- [ ] **기본 에러 처리**:
  - Gemini API 호출 실패 시 적절한 에러 메시지 제공
  - 분석 실패 시 사용자 친화적 메시지 표시
- [ ] **에러 응답 형식 유지**:
  - 기존 에러 코드 유지 (400, 500, 503)
  - 에러 로그에 기본 정보 포함

### 4.7 테스트 및 검증
- [ ] **Google Search 통합 테스트**:
  - Google Search 도구 활성화 테스트
  - 기본 분석 기능 테스트
  - 캐싱 시스템 동작 테스트
- [ ] **통합 테스트**:
  - 실제 포트폴리오 이미지로 Google Search 통합 분석 테스트
  - API 실패 시나리오 테스트
  - 성능 부하 테스트

---

## 🖼️ Phase 5: 다중 이미지 업로드 기능 (2-3일)

### 목표
단일 요청으로 여러 포트폴리오 이미지를 업로드하고 종합 분석을 받을 수 있는 기능을 구현합니다.

### 5.1 백엔드 API 확장 (1일)
- [ ] **기존 엔드포인트 수정**: `POST /api/analyze`를 단일/다중 이미지 통합으로 수정
  - `file: UploadFile` → `files: List[UploadFile]` (1-5개)
  - 파일 개수 검증 로직 추가
- [ ] **Gemini 서비스 확장**: 다중 이미지 분석 메서드 구현
  - 여러 이미지를 단일 contents 배열로 구성
  - 다중 이미지 분석 프롬프트 설계
  - Google Search 도구 통합 유지
- [ ] **에러 처리 강화**: 파일 개수 범위 검증, 폴백 메커니즘

### 5.2 프론트엔드 UI 개선 (1일)
- [ ] **타입 정의 업데이트**: 다중 파일 관련 인터페이스 수정
- [ ] **ImageUploader 컴포넌트 수정**:
  - `multiple` 속성 추가
  - 다중 파일 드래그 앤 드롭 지원
  - 이미지 갤러리 형태로 미리보기 표시
  - 개별 이미지 삭제 기능
- [ ] **상태 관리 로직**: 다중 파일 처리 및 미리보기 생성
- [ ] **API 호출 로직 수정**: 단일/다중 파일 통합 처리

### 5.3 사용자 경험 최적화 (0.5일)
- [ ] **로딩 상태 개선**: 다중 이미지 업로드 진행률 표시
- [ ] **결과 표시 개선**: 처리된 이미지 수 표시, 예상 처리 시간 안내

### 성능 고려사항
- **처리 시간**: 단일 2분 → 다중(5개) 4-5분
- **토큰 사용량**: 이미지당 258 토큰, 5개 이미지 약 2,000 토큰
- **최적화**: 이미지 압축, 캐싱, 점진적 로딩

### 테스트 계획
- [ ] **단위 테스트**: 다중 파일 업로드 로직, 이미지 개수 검증
- [ ] **통합 테스트**: 단일/다중 이미지 API 호출, 분석 품질 테스트
- [ ] **사용자 테스트**: 다양한 이미지 조합, UI/UX 사용성 테스트

---

## 🎨 Phase 6: 탭 기반 UI 통합 및 구조화된 출력 구현 (3-4일)

**목표**: PRD.md에 명시된 4개 탭으로 구성된 인터랙티브 UI와 구조화된 JSON 출력을 기존 코드에 통합

### 6.1 백엔드 구조화된 출력 구현 (1.5일)

#### **6.1.1 Pydantic 모델 정의 (models/portfolio.py)**
- [ ] **기존 모델 확장**: 기존 AnalysisRequest, AnalysisResponse 모델 유지하면서 새로운 구조화된 출력 모델 추가
- [ ] **4개 탭별 데이터 모델 정의**:
  - DashboardContent: 종합 점수, 핵심 기준 점수, 강점/약점
  - DeepDiveContent: 심층 분석, 기회 및 개선 방안
  - AllStockScoresContent: 종목 스코어 테이블
  - KeyStockAnalysisContent: 핵심 종목 상세 분석 카드
- [ ] **PortfolioReport 모델**: 4개 탭을 포함하는 최상위 구조
- [ ] **StructuredAnalysisResponse 모델**: API 응답 형식 정의
- [ ] **TabContent Union 모델 최적화**: `Field(discriminator='tabId')`를 사용하여 tabId 기반으로 명확한 모델 구분

**구현 예시:**
```python
from pydantic import BaseModel, Field
from typing import Union, List, Dict, Any

class TabContent(BaseModel):
    __root__: Union[DashboardContent, DeepDiveContent, AllStockScoresContent, KeyStockAnalysisContent] = Field(
        discriminator='tabId'  # tabId를 기준으로 모델 구분
    )

# 또는 더 명시적인 방식
class Tab(BaseModel):
    tabId: str
    tabTitle: str
    content: Union[
        Annotated[DashboardContent, Field(discriminator='type')],
        Annotated[DeepDiveContent, Field(discriminator='type')],
        Annotated[AllStockScoresContent, Field(discriminator='type')],
        Annotated[KeyStockAnalysisContent, Field(discriminator='type')]
    ]
```

#### **6.1.2 Gemini 서비스 구조화된 출력 통합 (services/gemini_service.py)**
- [ ] **기존 analyze_portfolio 메서드 확장**: format 파라미터로 JSON/마크다운 출력 선택
- [ ] **Google Gen AI SDK 구조화된 출력 설정**: response_mime_type="application/json", response_schema 적용
- [ ] **Google Search 통합 유지**: 기존 검색 기능을 구조화된 출력과 함께 사용
- [ ] **4개 탭별 상세 프롬프트 설계**: 각 탭의 데이터 구조에 맞는 프롬프트 엔지니어링
- [ ] **마크다운 출력 시 완전한 응답 데이터 제공**: processing_time과 request_id를 실제 값으로 반환하여 기존 AnalysisResponse 모델과 호환성 보장

**구현 예시:**
```python
async def analyze_portfolio_structured(
    self, 
    images: List[bytes], 
    format_type: str = "json"
) -> Union[StructuredAnalysisResponse, AnalysisResponse]:
    """
    구조화된 JSON 출력 또는 마크다운 출력을 지원하는 포트폴리오 분석
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    if format_type == "json":
        result = await self._analyze_with_structured_output(images)
        return StructuredAnalysisResponse(
            portfolioReport=result,
            processing_time=time.time() - start_time,
            request_id=request_id,
            images_processed=len(images)
        )
    else:
        result = await self._analyze_with_markdown_output(images)
        return AnalysisResponse(
            content=result,
            processing_time=time.time() - start_time,  # 실제 처리 시간
            request_id=request_id,  # 실제 요청 ID
            images_processed=len(images)
        )
```

#### **6.1.3 API 엔드포인트 확장 (api/analyze.py)**
- [ ] **기존 엔드포인트 수정**: format 쿼리 파라미터 추가 (json/markdown)
- [ ] **하위 호환성 보장**: 기존 마크다운 출력 방식 유지
- [ ] **에러 처리 강화**: 구조화된 출력 실패 시 fallback 메커니즘
- [ ] **응답 형식 통일**: format=markdown일 때도 processing_time과 request_id를 실제 값으로 반환하여 기존 AnalysisResponse 모델과 완전 호환

### 6.2 프론트엔드 탭 기반 UI 구현 (1.5일)

#### **6.2.1 TypeScript 타입 정의 (types/portfolio.ts)**
- [ ] **백엔드 Pydantic 모델과 일치하는 TypeScript 타입 정의**
- [ ] **4개 탭별 인터페이스 정의**: DashboardContent, DeepDiveContent, AllStockScoresContent, KeyStockAnalysisContent
- [ ] **StructuredAnalysisResponse 타입**: API 응답 타입 정의

#### **6.2.2 TabbedAnalysisDisplay 컴포넌트 구현 (components/TabbedAnalysisDisplay.tsx)**
- [ ] **4개 탭으로 구성된 메인 컴포넌트**: 탭 네비게이션과 콘텐츠 영역
- [ ] **탭 전환 애니메이션**: 부드러운 탭 전환 효과
- [ ] **반응형 디자인**: 모바일/데스크톱 모두 지원

#### **6.2.3 개별 탭 컴포넌트 구현 (components/tabs/)**
- [ ] **DashboardTab.tsx**: 종합 점수, 핵심 기준 스코어, 강점/약점 표시
- [ ] **DeepDiveTab.tsx**: 심층 분석, 기회 및 개선 방안 표시
- [ ] **AllStockScoresTab.tsx**: 종목 스코어 테이블 (정렬 가능, 색상 코딩)
- [ ] **KeyStockAnalysisTab.tsx**: 핵심 종목 상세 분석 카드

#### **6.2.4 기존 컴포넌트 통합 및 호환성 유지**
- [ ] **ImageUploader 컴포넌트 수정**: format props를 받아 동적으로 API 호출
- [ ] **메인 페이지 컴포넌트 수정**: 탭 뷰/마크다운 뷰 선택 토글, format 상태를 ImageUploader에 전달
- [ ] **기존 AnalysisDisplay 컴포넌트 유지**: 하위 호환성 보장
- [ ] **상태 관리 개선**: analysisResult 타입을 Union 타입으로 정의하여 JSON/마크다운 응답 모두 처리

**구현 예시:**
```typescript
// types/portfolio.ts - Union 타입 정의
export type AnalysisResult = StructuredAnalysisResponse | AnalysisResponse;

// ImageUploader.tsx - format props 추가
interface ImageUploaderProps {
  uploadState: UploadState;
  onFileSelect: (files: File[]) => void;
  onRemoveFile: (index: number) => void;
  disabled?: boolean;
  format: 'json' | 'markdown';  // format props 추가
}

// API 호출 시 format 사용
const handleAnalyze = async () => {
  const formData = new FormData();
  files.forEach(file => formData.append('files', file));
  
  // format props를 사용하여 동적으로 URL 생성
  const response = await fetch(`/api/analyze?format=${format}`, {
    method: 'POST',
    body: formData,
  });
  
  const result = await response.json();
  setAnalysisResult(result);
};

// page.tsx - format 상태 관리 및 전달
export default function HomePage() {
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [format, setFormat] = useState<'json' | 'markdown'>('json');
  
  return (
    <div className="container mx-auto px-4 py-8">
      <ImageUploader 
        onAnalysisComplete={setAnalysisResult} 
        format={format}  // format 상태 전달
      />
      
      {/* 형식 선택 토글 */}
      <div className="mt-6 flex justify-center">
        <div className="bg-gray-100 p-1 rounded-lg">
          <button
            onClick={() => setFormat('json')}
            className={`px-4 py-2 rounded-md text-sm font-medium ${
              format === 'json' 
                ? 'bg-white text-gray-900 shadow' 
                : 'text-gray-500'
            }`}
          >
            탭 뷰
          </button>
          <button
            onClick={() => setFormat('markdown')}
            className={`px-4 py-2 rounded-md text-sm font-medium ${
              format === 'markdown' 
                ? 'bg-white text-gray-900 shadow' 
                : 'text-gray-500'
            }`}
          >
            마크다운 뷰
          </button>
        </div>
      </div>
      
      {/* 결과 표시 */}
      {analysisResult && (
        format === 'json' ? (
          <TabbedAnalysisDisplay data={analysisResult as StructuredAnalysisResponse} />
        ) : (
          <AnalysisDisplay content={(analysisResult as AnalysisResponse).content} />
        )
      )}
    </div>
  );
}
```

### 6.3 기존 코드와의 호환성 보장 (1일)

#### **6.3.1 하위 호환성 유지**
- [ ] **기존 AnalysisDisplay 컴포넌트 유지**: format=markdown 쿼리 파라미터로 기존 마크다운 출력 지원
- [ ] **기존 API 응답 형식 유지**: 기존 클라이언트가 계속 작동하도록 보장
- [ ] **점진적 마이그레이션**: 새로운 탭 UI를 기본값으로 하되, 기존 마크다운 뷰도 선택 가능

#### **6.3.2 데이터 검증 및 에러 처리**
- [ ] **JSON 스키마 검증**: Pydantic 모델을 통한 자동 검증
- [ ] **Fallback 메커니즘**: 구조화된 출력 실패 시 기존 마크다운 출력으로 대체
- [ ] **에러 바운더리**: 탭 렌더링 실패 시 적절한 에러 메시지 표시

#### **6.3.3 성능 최적화**
- [ ] **탭별 지연 로딩**: 활성 탭만 렌더링하여 초기 로딩 시간 단축
- [ ] **메모이제이션**: React.memo를 활용한 불필요한 리렌더링 방지
- [ ] **이미지 최적화**: 탭 내 차트 및 시각화 요소 최적화

---

## 🧪 Phase 7: 테스트 및 검증 (2일)

### 7.1 백엔드 테스트
- [ ] **단위 테스트** (pytest):
  - 이미지 처리 함수 테스트
  - Gemini API 모킹 테스트
  - 마크다운 텍스트 응답 테스트
  - **구조화된 JSON 출력 테스트**: Pydantic 모델 검증, 4개 탭 데이터 구조 테스트
  - **Google Search 통합 테스트**: 검색 쿼리 생성, 결과 파싱 테스트
  - **응답 형식 통일 테스트**: format=markdown일 때도 processing_time과 request_id가 올바르게 반환되는지 검증
- [ ] **통합 테스트**:
  - API 엔드포인트 전체 플로우 테스트 (JSON/마크다운 출력)
  - 실제 샘플 이미지로 E2E 테스트
  - 에러 케이스 테스트 (잘못된 파일, API 오류 등)
  - **하위 호환성 테스트**: 기존 마크다운 출력과 새로운 JSON 출력 간 호환성
  - **format 파라미터 테스트**: 동일한 이미지에 대해 format=json과 format=markdown 모두 정상 작동하는지 검증

### 7.2 프론트엔드 테스트
- [ ] **컴포넌트 테스트** (Jest + React Testing Library):
  - ImageUploader 상호작용 테스트
  - AnalysisDisplay 렌더링 테스트
  - **TabbedAnalysisDisplay 컴포넌트 테스트**: 탭 전환, 데이터 렌더링 테스트
  - **개별 탭 컴포넌트 테스트**: DashboardTab, DeepDiveTab, AllStockScoresTab, KeyStockAnalysisTab
  - 상태 변화 테스트
  - **format props 전달 테스트**: ImageUploader가 format props를 올바르게 받아 API 호출에 반영하는지 검증
  - **Union 타입 처리 테스트**: AnalysisResult 타입이 JSON/마크다운 응답을 모두 올바르게 처리하는지 검증
- [ ] **E2E 테스트**:
  - 전체 사용자 플로우 테스트 (탭 뷰/마크다운 뷰)
  - 다양한 브라우저 호환성 테스트
  - **탭 UI 사용성 테스트**: 탭 전환, 데이터 표시, 반응형 디자인 테스트
  - **format 토글 테스트**: 사용자가 탭 뷰/마크다운 뷰를 전환할 때 올바른 API 호출과 렌더링이 이루어지는지 검증

### 7.3 성능 및 보안 테스트
- [ ] **성능 테스트**:
  - 이미지 처리 속도 측정
  - Gemini API 응답 시간 분석
  - 메모리 사용량 모니터링
  - **탭 UI 성능 테스트**: 대용량 데이터 렌더링, 탭 전환 속도 측정
  - **구조화된 JSON 출력 성능**: JSON 파싱 및 렌더링 시간 분석
- [ ] **보안 테스트**:
  - 파일 업로드 보안 검증
  - API 키 노출 방지 확인
  - CORS 정책 테스트
  - **JSON 스키마 검증**: 악의적인 JSON 데이터 처리 테스트

---

## 🚀 Phase 8: 배포 및 운영 설정 (1-2일)

### 8.1 배포 환경 구성
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

### 8.2 CI/CD 파이프라인
- [ ] **GitHub Actions 설정**:
  - 코드 푸시 시 자동 테스트 실행
  - 테스트 통과 시 자동 배포
  - 환경별 배포 분리 (dev, prod)

### 8.3 모니터링 및 로깅
- [ ] **백엔드 로깅**:
  - API 호출 로그
  - 에러 로그 수집
  - Gemini API 사용량 모니터링
- [ ] **프론트엔드 모니터링**:
  - 사용자 행동 분석
  - 성능 메트릭 수집
  - 에러 추적

---

## 📊 Phase 9: 최종 검증 및 문서화 (1일)

### 9.1 최종 테스트
- [ ] **다양한 포트폴리오 이미지 테스트**:
  - 국내 주요 증권사 앱 스크린샷
  - 해외 브로커리지 앱 스크린샷
  - 다양한 해상도 및 품질의 이미지
- [ ] **사용자 시나리오 테스트**:
  - 정상 플로우 테스트 (탭 뷰/마크다운 뷰)
  - 에러 상황 대응 테스트
  - 성능 부하 테스트
- [ ] **탭 기반 UI 최종 검증**:
  - 4개 탭 데이터 정확성 검증
  - 탭 전환 및 사용성 테스트
  - 반응형 디자인 검증 (모바일/데스크톱)
  - 하위 호환성 최종 확인

### 9.2 문서 업데이트
- [ ] README.md 작성 (설치, 실행, 배포 방법)
- [ ] API 문서 생성 (FastAPI 자동 생성 활용)
- [ ] 사용자 가이드 작성 (탭 기반 UI 사용법 포함)
- [ ] 개발자 문서 업데이트 (구조화된 출력 구현 가이드)
- [ ] **탭 기반 UI 문서화**: 4개 탭 구조, 데이터 스키마, 컴포넌트 사용법

---

## 🔧 기술적 고려사항

### 보안
- 업로드된 이미지 즉시 삭제 (처리 완료 후)
- API 키 환경변수 관리
- 파일 크기 및 형식 제한
- [ ] Rate Limiting 적용

### 성능 최적화
- **분석 품질 최우선**: API 호출 시 비용이나 속도보다 상세하고 정확한 구조화된 JSON 분석 결과를 얻도록 설정
- **이미지 압축**: 클라이언트/서버 사이드에서 이미지 압축
- **API 응답 캐싱**: 동일 이미지 해시 기반으로 캐싱
- **탭 기반 렌더링 최적화**: 활성 탭만 렌더링하여 초기 로딩 시간 단축
- **구조화된 JSON 파싱 최적화**: 대용량 JSON 데이터 처리 성능 향상

### 에러 처리
- 네트워크 오류 재시도 로직
- 사용자 친화적 에러 메시지
- 로그 수집 및 모니터링
- Graceful degradation
- **구조화된 출력 실패 시 Fallback**: JSON 출력 실패 시 기존 마크다운 출력으로 대체
- **탭 렌더링 에러 처리**: 개별 탭 렌더링 실패 시 적절한 에러 메시지 표시

---

## 📅 전체 일정 요약

| Phase | 작업 내용 | 소요 시간 | 핵심 산출물 |
|-------|----------|----------|------------|
| 1 | 프로젝트 초기 설정 | 1-2일 | 개발 환경, API 키 |
| 2 | 백엔드 구현 | 3-4일 | FastAPI 서버, Gemini 연동 |
| 3 | 프론트엔드 구현 | 3-4일 | React 컴포넌트, UI/UX |
| 4 | Google Search 기능 통합 | 2-3일 | Google Search API 통합, 캐싱 시스템 |
| 5 | 다중 이미지 업로드 기능 | 2-3일 | 다중 이미지 분석, UI 개선 |
| 6 | 탭 기반 UI 통합 및 구조화된 출력 구현 | 3-4일 | 4개 탭 UI, 구조화된 JSON 출력 |
| 7 | 테스트 및 검증 | 2일 | 테스트 코드, 성능 검증 |
| 8 | 배포 및 운영 | 1-2일 | 프로덕션 환경 |
| 9 | 최종 검증 | 1일 | 완성된 MVP |

**총 예상 소요 시간: 18-25일**

---

## 🎯 성공 기준

1. **기능적 요구사항**:
   - 포트폴리오 이미지 업로드 및 분석 완료
   - Google Search를 통한 실시간 최신 시장 정보 검색 및 분석 반영
   - 4개 탭으로 구성된 구조화된 JSON 출력 및 인터랙티브 UI 제공
   - 기존 마크다운 출력 방식과의 하위 호환성 유지
   - react-markdown을 통한 마크다운 텍스트 렌더링 (선택적)

2. **비기능적 요구사항**:
   - 이미지 처리 + Google Search 시간 30초 이내
   - 99% 이상의 서비스 가용성
   - 모바일/데스크톱 반응형 지원
   - Google Search API 호출 성공률 95% 이상

3. **품질 요구사항**:
   - 80% 이상의 테스트 커버리지
   - 보안 취약점 0개
   - 성능 최적화 완료

---

## 🚨 리스크 관리

### 고위험 요소
1. **Gemini API 호출 실패**: 재시도 로직 및 fallback 메커니즘
2. **Google Search API 호출 실패**: 검색 실패 시 기존 분석 결과 제공
3. **구조화된 JSON 출력 품질**: 4개 탭 데이터 구조의 일관성 및 정확성 보장
4. **API 비용 관리**: Gemini + Google Search 사용량 모니터링 및 제한 설정
5. **하위 호환성 유지**: 기존 마크다운 출력과 새로운 탭 UI 간의 호환성 보장

### 중위험 요소
1. **성능 병목**: 비동기 처리 및 캐싱 적용 (검색 + 분석 병렬 처리)
2. **검색 결과 품질**: 검색 쿼리 최적화 및 결과 필터링
3. **브라우저 호환성**: 최신 브라우저 기준 개발
4. **탭 UI 성능**: 대용량 데이터 렌더링 시 성능 최적화

### 저위험 요소
1. **UI/UX 개선**: 점진적 개선 가능
2. **추가 기능**: MVP 완료 후 확장

---

## 🎯 탭 기반 UI 통합 핵심 포인트

### **기존 코드와의 통합 전략**
1. **하위 호환성 보장**: 기존 마크다운 출력 방식을 유지하면서 새로운 탭 UI를 추가
2. **점진적 마이그레이션**: `format` 쿼리 파라미터로 사용자가 출력 형식을 선택할 수 있도록 구현
3. **기존 컴포넌트 재사용**: AnalysisDisplay 컴포넌트는 그대로 유지하고 TabbedAnalysisDisplay를 새로 추가

### **구조화된 출력의 장점**
1. **일관된 데이터 형식**: JSON 스키마를 통해 항상 동일한 구조의 데이터 보장
2. **타입 안전성**: Pydantic 모델을 통한 자동 검증 및 타입 체크
3. **프론트엔드 최적화**: 탭 기반 UI에 바로 사용 가능한 구조화된 데이터
4. **확장성**: 새로운 필드나 탭 추가 시 스키마만 수정하면 됨

### **4개 탭 구조의 사용자 경험**
1. **총괄 요약**: 한눈에 보는 포트폴리오 전체 평가
2. **심층 분석**: 상세한 분석 내용과 개선 방안
3. **종목 스코어**: 모든 종목의 점수를 테이블로 비교
4. **핵심 종목**: 주요 종목들의 상세 분석 카드

이 계획을 따라 단계별로 구현하면 간단하고 안정적인 Portfolio Evaluation MVP를 성공적으로 완성할 수 있습니다.
