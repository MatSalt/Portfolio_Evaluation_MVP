네, 좋습니다. 이전 논의를 종합하여 개발자("Cursor"와 같은 AI 어시스턴트 포함)가 바로 이해하고 작업을 시작할 수 있도록, **이미지 분석 기반 포트폴리오 추출 MVP**에 대한 상세 PRD(제품 요구사항 명세서)를 작성해 드리겠습니다.

-----

## **PRD: AI 포트폴리오 추출 MVP**

  * **제품명:** 포트폴리오 스코어 (Portfolio Score) - 추출 기능 MVP
  * **버전:** 0.2 (탭 기반 UI 및 구조화된 출력 지원)
  * **목표:** 사용자가 포트폴리오 화면 캡처(단일 또는 다중)를 업로드하면, AI Vision 모델로 보유 종목 데이터를 추출하고 이를 기반으로 **구조화된 JSON 데이터**를 생성하여 **4개 탭으로 구성된 인터랙티브 UI**에 표시한다.

-----

### ## 1. 사용자 플로우 (User Flow)

1.  **[진입]** 메인 페이지 진입 → 업로드 영역 표시.
2.  **[업로드]** 스크린샷 업로드(버튼/드래그 앤 드롭, 최대 5개 이미지 지원).
3.  **[처리]** 프론트엔드가 이미지(단일/다중)를 백엔드 `/api/analyze`로 전송, 로딩 인디케이터 표시.
4.  **[AI 분석 출력]** 백엔드 분석 완료 후, **구조화된 JSON 데이터**를 받아 **4개 탭으로 구성된 인터랙티브 UI**에 표시.

### ## 2. 핵심 기능 명세 (Core Feature Specifications)

#### **2.1. 프론트엔드 (Frontend - Next.js)**

  * **개발 가이드라인:** Next.js 관련 코드 작성 시 항상 공식 문서 참고 필수
      * 공식 문서: https://nextjs.org/docs
      * GitHub 저장소: https://github.com/vercel/next.js
      * **Next.js LLMS 상세 정보**: `/Users/choongheon/Desktop/Rinia/projects/Portfolio_Evaluation_MVP/Docs/nextjs-llms-full.txt`

  * **페이지 구성:** 단일 페이지 애플리케이션 (SPA)

      * `src/app/page.tsx`: 메인 페이지 컴포넌트

  * **컴포넌트 명세:**

      * **`ImageUploader.tsx`**

          * **기능:** 이미지 파일을 입력받고 상태를 관리한다.
          * **요구사항:**
              * `<input type="file" accept="image/png, image/jpeg" multiple />`를 포함해야 한다.
              * 드래그 앤 드롭 기능을 지원해야 한다 (다중 파일 지원).
              * 파일이 선택되면 이미지 썸네일을 미리 보여줘야 한다 (최대 5개).
              * 상태 관리: `idle`, `loading`, `success`, `error` 4가지 상태를 가져야 한다.
          * **API 호출:**
              * '분석하기' 버튼 클릭 시 `loading` 상태로 변경.
              * 단일/다중 이미지 모두 백엔드의 `/api/analyze` 엔드포인트로 `multipart/form-data` 형식의 `POST` 요청을 보낸다.

      * **`TabbedAnalysisDisplay.tsx`** (신규)

          * **기능:** LLM이 생성한 구조화된 JSON 데이터를 4개 탭으로 나누어 표시한다.
          * **요구사항:** 
              * **탭 1: 총괄 요약 (Dashboard)** - 종합 점수, 핵심 기준 점수, 강점/약점
              * **탭 2: 포트폴리오 심층 분석 (Deep Dive)** - 각 기준별 상세 분석, 기회 및 개선 방안
              * **탭 3: 개별 종목 스코어 (All Stock Scores)** - 모든 종목의 점수 테이블
              * **탭 4: 핵심 종목 상세 분석 (Key Stock Analysis)** - 주요 종목들의 상세 분석 카드
              * 탭 전환 시 부드러운 애니메이션 효과
              * 반응형 디자인으로 모바일/데스크톱 모두 지원
              * 점수 시각화 (프로그레스 바, 차트 등)

      * **`AnalysisDisplay.tsx`** (기존 - 하위 호환성 유지)

          * **기능:** LLM이 생성한 최종 분석 리포트(마크다운)를 화면에 렌더링한다. `format=markdown` 쿼리 파라미터로 요청 시 사용된다.
          * **요구사항:** 
              * `react-markdown` 라이브러리를 사용하여 API로부터 받은 마크다운 텍스트를 HTML로 변환한다.
              * `expected_result.md` 예시와 같이 테이블, 리스트, 강조 등 마크다운 요소가 올바르게 스타일링되어야 한다.
              * 코드 블록이나 복잡한 시각화 없이 텍스트 중심으로 렌더링한다.

#### **2.2. 백엔드 (Backend - Python/FastAPI)**

  * **개발 가이드라인:** FastAPI 관련 코드 작성 시 항상 공식 문서 참고 필수
      * 공식 문서: https://fastapi.tiangolo.com/reference/
      * GitHub 저장소: https://github.com/fastapi/fastapi

  * **엔드포인트 명세:**
      * **`POST /api/analyze`** (단일/다중 이미지 통합)
          * **요청 (Request):**
              * **Content-Type:** `multipart/form-data`
              * **Body:** `files` (이미지 파일 배열, 1-5개)
              * **Query Parameter:** `format` (선택사항: `markdown` 또는 `json`, 기본값: `json`)
      * **처리 로직 (Processing Logic):**
            1.  요청으로부터 이미지 파일 배열(`List[UploadFile]`)을 받는다.
            2.  이미지 파일들을 메모리에서 읽어 **Base64**로 인코딩한다.
            3.  Google Gen AI Python SDK를 사용해 2‑스텝 파이프라인으로 호출한다.
               - 3.1 [스텝1: 검색·그라운딩] Google Search Tool 활성화, 마크다운/플레인텍스트로 최신 정보와 사실(facts), 출처(sources), 표(table rows)를 추출한다. `response_mime_type` 미지정.
               - 3.2 [스텝2: 구조화 JSON] 스텝1 산출물(facts/sources/rows)을 컨텍스트로 주고 툴 없이 `response_mime_type="application/json"`으로 순수 JSON을 생성한다. 필요 시 `<JSON_START>/<JSON_END>` 태그 지시와 서버측 안전 추출로 노이즈 제거.
            4.  서버에서 **Pydantic**으로 JSON을 검증한다(범위·필수 필드·스키마 일치).
            5.  실패 시 1회 자동 보정 재시도(누락 필드·범위 오류만 수정 유도). 최종 실패면 사용자 친화적 400 응답.
            6.  성공 시, 상태 코드 `200 OK`와 함께 **구조화된 JSON 데이터**를 반환한다.
          * **에러 핸들링 (Error Handling):**
              * 이미지 파일이 아닐 경우: `400 Bad Request`
              * 파일 개수가 1-5개 범위를 벗어날 경우: `400 Bad Request`
              * LLM API 호출 실패 시: `503 Service Unavailable`
              * LLM 응답 형식 오류 시: `500 Internal Server Error`
          * **응답 (Response):** 아래 **3. 데이터 요구사항** 참조

### ## 3. 데이터 요구사항 (Data & API Specification)

#### **3.1. Gemini API 통합 및 구조화된 출력 (Gemini API Integration & Structured Output)**

백엔드가 Google Gen AI Python SDK를 사용하여 Gemini 모델을 호출할 때 사용할 구조화된 출력 설정입니다. [공식 문서](https://ai.google.dev/gemini-api/docs/structured-output?hl=ko#generating-json)를 참고하여 Pydantic 모델을 사용한 스키마 정의를 적용합니다.

**Two-step 생성 전략(권장):**

1) 스텝1: 검색·그라운딩 호출 (Tool 사용)
- 목적: 최신 정보/사실 수집, 표준화된 facts/sources/rows 생성
- 설정: Google Search Tool 활성화, `response_mime_type` 미지정(텍스트 응답)
- 출력 예: `{ facts: [...], sources: [...], rows: [...] }` 텍스트(또는 마크다운)

2) 스텝2: 구조화 JSON 생성 (Tool 미사용)
- 목적: Pydantic 스키마에 100% 일치하는 순수 JSON 생성
- 설정: `response_mime_type: application/json`, Tool 비활성화
- 프롬프트: 스키마 필드별 채우기, 0–100 정수 범위 강제, 한국어, 추가 텍스트 금지, 필요 시 `<JSON_START>/<JSON_END>` 태그 지시
- 서버는 태그·코드블록 제거/브레이스 매칭으로 JSON만 추출 후 Pydantic 검증

이 방식은 Tool과 `application/json` 동시 사용 제한을 우회하면서 최신성(검색)과 스키마 정확성(JSON)을 모두 만족합니다.

**Google Gen AI Python SDK 구조화된 출력 사용법(예시):**
```python
from google import genai
from pydantic import BaseModel

# Pydantic 모델 정의
class PortfolioReport(BaseModel):
    version: str = "1.0"
    reportDate: str
    tabs: List[Tab]

class ApiResponse(BaseModel):
    portfolioReport: PortfolioReport
    processing_time: float
    request_id: str
    images_processed: int

# API 키 설정
client = genai.Client(api_key='YOUR_GEMINI_API_KEY')

# 구조화된 출력 설정
config = {
    "response_mime_type": "application/json",
    "response_schema": PortfolioReport,
    "tools": [{"google_search": {}}]  # Google Search 통합
}

# 이미지와 프롬프트로 포트폴리오 분석 요청
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=[prompt_text, image_data],
    config=config
)

# 구조화된 응답 받기
structured_data = response.parsed
```

**구조화된 출력의 장점:**
- **일관된 데이터 형식**: JSON 스키마를 통해 항상 동일한 구조의 데이터 보장
- **타입 안전성**: Pydantic 모델을 통한 자동 검증 및 타입 체크
- **프론트엔드 최적화**: 탭 기반 UI에 바로 사용 가능한 구조화된 데이터
- **확장성**: 새로운 필드나 탭 추가 시 스키마만 수정하면 됨

**Google Search 기능 특징:**
- **실시간 정보 검색**: 최신 시장 동향, 뉴스, 재무 정보를 실시간으로 검색
- **정확성 향상**: 웹 기반 최신 데이터로 분석의 정확성과 신뢰성 향상
- **출처 제공**: 검색된 정보의 출처를 자동으로 포함하여 투명성 확보
- **환각 현상 방지**: 실제 웹 데이터 기반으로 응답하여 부정확한 정보 생성 방지

**참고 자료**: 
- Gemini API 상세 정보: `/Users/choongheon/Desktop/Rinia/projects/Portfolio_Evaluation_MVP/Docs/gemini_llms.txt`
- 구조화된 출력: https://ai.google.dev/gemini-api/docs/structured-output?hl=ko#generating-json
- Google Search 통합: https://ai.google.dev/gemini-api/docs/google-search?hl=ko

#### **3.2. 구조화된 JSON 스키마 (Structured JSON Schema)**

**포트폴리오 리포트 JSON 구조:**
```json
{
  "portfolioReport": {
    "version": "1.0",
    "reportDate": "2025-09-30",
    "tabs": [
      {
        "tabId": "dashboard",
        "tabTitle": "총괄 요약",
        "content": {
          "overallScore": {
            "title": "포트폴리오 종합 스코어",
            "score": 72,
            "maxScore": 100
          },
          "coreCriteriaScores": [
            {
              "criterion": "성장 잠재력",
              "score": 88,
              "maxScore": 100
            },
            {
              "criterion": "안정성 및 방어력",
              "score": 55,
              "maxScore": 100
            },
            {
              "criterion": "전략적 일관성",
              "score": 74,
              "maxScore": 100
            }
          ],
          "strengths": [
            "선구적인 미래 기술 투자",
            "명확하고 일관된 투자 테마",
            "높은 잠재 수익률"
          ],
          "weaknesses": [
            "극심한 변동성 노출",
            "기술 섹터 집중 리스크",
            "재무적 안정성 부족"
          ]
        }
      },
      {
        "tabId": "deepDive",
        "tabTitle": "포트폴리오 심층 분석",
        "content": {
          "inDepthAnalysis": [
            {
              "title": "성장 잠재력 분석: 미래 기술에 대한 강력한 베팅",
              "score": 88,
              "description": "문영님의 포트폴리오는 '기술 잠재력' 및 'CEO/리더십' 인덱스 점수가 매우 높은 종목들에 집중적으로 투자되어 있어..."
            },
            {
              "title": "안정성 및 방어력 분석: 기술주 특유의 변동성 노출",
              "score": 55,
              "description": "포트폴리오의 안정성 및 방어력 점수는 55점으로 상대적으로 낮은 수준입니다..."
            },
            {
              "title": "전략적 일관성 분석: 명확한 테마 속 집중도 리스크",
              "score": 74,
              "description": "문영님의 포트폴리오는 '양자 컴퓨팅'과 'AI'라는 명확한 투자 테마를 중심으로 구성되어 있어..."
            }
          ],
          "opportunities": {
            "title": "기회 및 개선 방안",
            "items": [
              {
                "summary": "안정적인 '핵심' 자산 추가",
                "details": "현재 포트폴리오에는 변동성을 상쇄할 강력한 '핵심' 자산이 부족합니다..."
              },
              {
                "summary": "What-if 시나리오",
                "details": "만약 TIGER 미국S&P500 ETF 비중을 현재 5백만원대에서 1천만원대로 높인다면..."
              },
              {
                "summary": "유사 테마 내 분산 투자",
                "details": "양자 컴퓨팅 및 AI 테마는 유지하되, 관련 산업 내에서도 서로 다른 세부 기술 분야나 지역에 분산 투자하여..."
              },
              {
                "summary": "리스크 관리 전략 도입",
                "details": "시장의 변동성에 대비하여 일정 비율의 현금을 보유하거나, 방어적인 섹터의 ETF를 소액 편입하는 등의 전략을..."
              }
            ]
          }
        }
      },
      {
        "tabId": "allStockScores",
        "tabTitle": "개별 종목 스코어",
        "content": {
          "scoreTable": {
            "headers": ["주식", "Overall", "펀더멘탈", "기술 잠재력", "거시경제", "시장심리", "CEO/리더십"],
            "rows": [
              {"주식": "팔란티어 (PLTR)", "Overall": 78, "펀더멘탈": 70, "기술 잠재력": 95, "거시경제": 75, "시장심리": 85, "CEO/리더십": 85},
              {"주식": "브로드컴 (AVGO)", "Overall": 82, "펀더멘탈": 85, "기술 잠재력": 80, "거시경제": 80, "시장심리": 80, "CEO/리더십": 85}
              // ... 이하 모든 종목 데이터
            ]
          }
        }
      },
      {
        "tabId": "keyStockAnalysis",
        "tabTitle": "핵심 종목 상세 분석",
        "content": {
          "analysisCards": [
            {
              "stockName": "팔란티어 테크놀로지스 (PLTR)",
              "overallScore": 78,
              "detailedScores": [
                { "category": "펀더멘탈", "score": 70, "analysis": "꾸준한 매출 성장과 최근 GAAP 기준 흑자 전환 성공은 긍정적이나..." },
                { "category": "기술 잠재력", "score": 95, "analysis": "빅데이터 분석 및 AI 분야 독보적인 기술력으로 고담(정부) 및 AIP(상업) 플랫폼 모두에서..." },
                { "category": "거시경제", "score": 75, "analysis": "전 세계적인 AI 도입 가속화의 직접 수혜주..." },
                { "category": "시장심리", "score": 85, "analysis": "CEO의 적극적인 소통과 AI 시장 성장에 대한 기대로 개인 투자자들의 높은 지지를 받습니다..." },
                { "category": "CEO/리더십", "score": 85, "analysis": "독특한 비전과 강력한 리더십으로 혁신을 주도하고 있습니다..." }
              ]
            }
            // ... 이하 다른 핵심 종목 카드
          ]
        }
      }
    ]
  }
}
```

#### **3.3. API 응답 형식 (API Response Schema)**

  * **성공 (Success - `200 OK`):**

    ```json
    {
      "portfolioReport": {
        "version": "1.0",
        "reportDate": "2025-09-30",
        "tabs": [
          // 위의 JSON 구조와 동일
        ]
      },
      "processing_time": 15.2,
      "request_id": "uuid-string",
      "images_processed": 3
    }
    ```

  * **실패 (Error - `4xx` or `5xx`):**

    ```json
    {
      "error": "분석 중 오류가 발생했습니다.",
      "detail": "구체적인 오류 내용",
      "code": "400"
    }
    ```

#### **3.4. 탭 기반 UI 구조 (Tab-based UI Structure)**

**탭 1: 총괄 요약 (Dashboard)**
- 포트폴리오 종합 스코어 (큰 숫자로 강조)
- 3대 핵심 기준 스코어 (프로그레스 바 형태)
- 강점/약점 (아이콘과 함께 카드 형태)

**탭 2: 포트폴리오 심층 분석 (Deep Dive)**
- 각 기준별 상세 분석 (점수와 함께 설명)
- 기회 및 개선 방안 (액션 아이템 형태)

**탭 3: 개별 종목 스코어 (All Stock Scores)**
- 모든 종목의 점수 테이블 (정렬 가능)
- 점수별 색상 코딩 (높은 점수: 녹색, 낮은 점수: 빨간색)

**탭 4: 핵심 종목 상세 분석 (Key Stock Analysis)**
- 주요 종목들의 상세 분석 카드
- 각 종목별 5가지 기준 점수와 분석

-----

### ## 4. 기술 스택 (Technology Stack)

  * **프론트엔드:** Next.js 15.5.3 (TypeScript)
  * **UI 라이브러리:** Tailwind CSS, Headless UI (탭 컴포넌트)
  * **차트/시각화:** Chart.js 또는 Recharts (점수 시각화)
  * **백엔드:** Python 3.13.7, FastAPI 0.116.1
    * 공식 문서: https://fastapi.tiangolo.com/reference/
    * GitHub 저장소: https://github.com/fastapi/fastapi
    * 특징: 고성능, 자동 문서화, 타입 힌트 지원
  * **AI 모델:** Google Gemini 2.5 Flash API (google-genai Python SDK)
    * **구조화된 출력**: Pydantic 모델을 사용한 JSON 스키마 정의
    * **Google Search 통합**: Gemini API의 `google_search` 도구를 활용한 실시간 웹 검색
    * **그라운딩 기능**: 검색된 정보를 기반으로 한 정확한 분석 제공
  * **데이터 검증:** Pydantic (백엔드), Zod (프론트엔드)
  * **클라우드 스토리지:** Google Cloud Storage
  * **배포:** Vercel (Frontend), Render (Backend)

-----

### ## 5. 범위 외 (Out of Scope for MVP)

  * 사용자 회원가입 및 로그인
  * 포트폴리오 데이터 저장 및 이력 관리
  * 추출된 데이터를 기반으로 한 **2차 분석** (위험도, 자산 배분 시각화 등)
  * 실시간 시세 연동
  * 다크 모드 등 UI 테마 기능
  * 탭 간 데이터 공유 및 비교 기능

-----

### ## 6. 보안 및 개인정보 보호 (Security & Privacy)

  * 업로드된 이미지는 처리 완료 후 즉시 삭제한다. (프로덕션 기본값)
  * 선택적 스토리지(GCS)는 개발/디버깅 목적의 일시 보관에만 사용하며 만료 정책을 적용한다.
  * Gemini API 키는 환경 변수로 관리하고 서버 사이드에서만 사용한다.
  * Google Gen AI SDK의 안전 설정을 적용하여 부적절한 콘텐츠 생성을 방지한다.
  * 파일 크기 제한(예: 10MB)과 허용 확장자(PNG, JPEG) 검증을 수행한다.
  * 다중 이미지 업로드 시 최대 5개 파일 제한을 적용한다.

-----

### ## 7. 성능 최적화 (Performance)

  * Google Gen AI Python SDK를 통한 Gemini 2.5 Flash API의 설정을 조절하여 비용이나 속도보다 **분석의 상세함과 품질**을 최우선으로 한다.
  * **구조화된 출력 최적화**: JSON 스키마를 통한 일관된 데이터 형식으로 프론트엔드 렌더링 성능 향상
  * **Google Search 최적화**: 검색 쿼리를 효율적으로 구성하여 관련성 높은 정보만 검색하고 응답 시간을 단축한다.
  * **다중 이미지 처리 최적화**: 단일 API 요청으로 여러 이미지를 처리하여 효율성을 극대화한다.
  * 동일 이미지 반복 분석에 대한 캐싱 전략(해시 기반 중복 방지)을 적용한다.
  * 비동기 I/O로 업로드/LLM 호출/Google Search 파이프라인을 병렬화한다.
  * **검색 결과 캐싱**: 동일한 검색 쿼리에 대해 일정 시간 동안 캐시된 결과를 활용하여 API 호출 비용을 절약한다.
  * **탭 기반 렌더링**: 필요한 탭만 렌더링하여 초기 로딩 시간 단축

-----

### ## 8. 테스트 및 배포 (Testing & CI/CD)

  * 단위 테스트: 이미지 처리 로직, 프롬프트 유효성 테스트, Google Search API 호출 테스트, JSON 스키마 검증 테스트
  * 통합 테스트: 실제 샘플 스크린샷으로 엔드투엔드 검증, Google Search 결과 검증, 탭 UI 렌더링 테스트
  * **구조화된 출력 테스트**: JSON 스키마 준수, Pydantic 모델 검증, 프론트엔드 파싱 테스트
  * **Google Search 테스트**: 검색 쿼리 생성, 결과 파싱, 출처 정보 추출 테스트
  * 사용자 수용 테스트(UAT): 다양한 브로커리지 UI 스킨에 대한 견고성 확인, 검색 결과 정확성 검증, 탭 UI 사용성 테스트
  * CI/CD: 메인 병합 시 자동 빌드/배포(프론트: Vercel, 백엔드: Render), 시크릿 관리, Google Search API 키 관리