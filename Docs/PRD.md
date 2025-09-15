네, 좋습니다. 이전 논의를 종합하여 개발자("Cursor"와 같은 AI 어시스턴트 포함)가 바로 이해하고 작업을 시작할 수 있도록, **이미지 분석 기반 포트폴리오 추출 MVP**에 대한 상세 PRD(제품 요구사항 명세서)를 작성해 드리겠습니다.

-----

## **PRD: AI 포트폴리오 추출 MVP**

  * **제품명:** 포트폴리오 스코어 (Portfolio Score) - 추출 기능 MVP
  * **버전:** 0.1
  * **목표:** 사용자가 포트폴리오 화면 캡처를 업로드하면, AI Vision 모델로 보유 종목 데이터를 추출하고 이를 기반으로 **AI 총평, 포트폴리오 종합 리니아 스코어, 3대 핵심 기준 스코어, 종목별 상세 분석 카드**를 생성·제공한다. (사용자 편집 플로우 제외)

-----

### \#\# 1. 사용자 플로우 (User Flow)

1.  **[진입]** 메인 페이지 진입 → 업로드 영역 표시.
2.  **[업로드]** 스크린샷 업로드(버튼/드래그 앤 드롭).
3.  **[처리]** 프론트엔드가 이미지를 백엔드 `/api/analyze`로 전송, 로딩 인디케이터 표시.
4.  **[AI 분석 출력]** 백엔드 분석 완료 후, **AI 총평/종합 스코어/3대 기준 스코어/종목별 분석 카드**를 **마크다운 텍스트**로 화면에 표시.

### \#\# 2. 핵심 기능 명세 (Core Feature Specifications)

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
              * `<input type="file" accept="image/png, image/jpeg" />`를 포함해야 한다.
              * 드래그 앤 드롭 기능을 지원해야 한다.
              * 파일이 선택되면 이미지 썸네일을 미리 보여줘야 한다.
              * 상태 관리: `idle`, `loading`, `success`, `error` 4가지 상태를 가져야 한다.
          * **API 호출:**
              * '분석하기' 버튼 클릭 시 `loading` 상태로 변경.
              * 백엔드의 `/api/analyze` 엔드포인트로 `multipart/form-data` 형식의 `POST` 요청을 보낸다.

      * **`AnalysisDisplay.tsx`**

          * **기능:** LLM이 생성한 최종 분석 리포트(마크다운)를 화면에 렌더링한다.
          * **요구사항:** 
              * `react-markdown` 라이브러리를 사용하여 API로부터 받은 마크다운 텍스트를 HTML로 변환한다.
              * `expected_result.md` 예시와 같이 테이블, 리스트, 강조 등 마크다운 요소가 올바르게 스타일링되어야 한다.
              * 코드 블록이나 복잡한 시각화 없이 텍스트 중심으로 렌더링한다.

#### **2.2. 백엔드 (Backend - Python/FastAPI)**

  * **개발 가이드라인:** FastAPI 관련 코드 작성 시 항상 공식 문서 참고 필수
      * 공식 문서: https://fastapi.tiangolo.com/reference/
      * GitHub 저장소: https://github.com/fastapi/fastapi

  * **엔드포인트 명세:**
      * **`POST /api/analyze`**
          * **요청 (Request):**
              * **Content-Type:** `multipart/form-data`
              * **Body:** `file` (이미지 파일)
          * **처리 로직 (Processing Logic):**
            1.  요청으로부터 이미지 파일(`UploadFile`)을 받는다.
            2.  이미지 파일을 메모리에서 읽어 **Base64**로 인코딩한다.
            3.  Google Gen AI Python SDK를 사용하여 Gemini 2.5 Flash 모델에 보낼 \*\*프롬프트(Prompt)\*\*와 인코딩된 이미지를 포함하여 요청을 구성한다.
            4.  LLM API를 호출하고 응답을 기다린다. (비동기 처리 `async/await`)
            5.  LLM이 반환한 **마크다운 형식의 텍스트 응답**을 그대로 받는다.
            6.  성공 시, 상태 코드 `200 OK`와 함께 **마크다운 텍스트**를 반환한다.
          * **에러 핸들링 (Error Handling):**
              * 이미지 파일이 아닐 경우: `400 Bad Request`
              * LLM API 호출 실패 시: `503 Service Unavailable`
              * LLM 응답 형식 오류 시: `500 Internal Server Error`
          * **응답 (Response):** 아래 **3. 데이터 요구사항** 참조

### \#\# 3. 데이터 요구사항 (Data & API Specification)

#### **3.1. Gemini API 통합 및 프롬프트 (Gemini API Integration & Prompt)**

백엔드가 Google Gen AI Python SDK를 사용하여 Gemini 모델을 호출할 때 사용할 프롬프트 예시입니다. 이 프롬프트는 캡처 이미지에서 포트폴리오를 인식·정규화하고, **Google Search를 통한 실시간 정보 검색**과 함께 **expected_result.md와 동일한 마크다운 형식의 분석 결과**를 생성하도록 지시합니다.

**Google Gen AI Python SDK 사용법 (Google Search 통합):**
```python
from google import genai

# API 키 설정
client = genai.Client(api_key='YOUR_GEMINI_API_KEY')

# Google Search 도구를 포함한 모델 구성
tools = [{"google_search": {}}]
config = {"tools": tools}

# 이미지와 프롬프트로 포트폴리오 분석 요청 (Google Search 활성화)
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=[prompt_text, image_data],
    tools=tools
)
```

**Google Search 기능 특징:**
- **실시간 정보 검색**: 최신 시장 동향, 뉴스, 재무 정보를 실시간으로 검색
- **정확성 향상**: 웹 기반 최신 데이터로 분석의 정확성과 신뢰성 향상
- **출처 제공**: 검색된 정보의 출처를 자동으로 포함하여 투명성 확보
- **환각 현상 방지**: 실제 웹 데이터 기반으로 응답하여 부정확한 정보 생성 방지

**참고 자료**: 
- Gemini API 상세 정보: `/Users/choongheon/Desktop/Rinia/projects/Portfolio_Evaluation_MVP/Docs/gemini_llms.txt`
- Google Search 통합: https://ai.google.dev/gemini-api/docs/google-search?hl=ko
- Live API 도구 사용: https://ai.google.dev/gemini-api/docs/live-tools?hl=ko

```text
당신은 포트폴리오 분석 전문가입니다. 제공된 증권사 앱 스크린샷에서 보유 종목을 추출하고 종합적인 투자 분석을 수행하세요.

다음 마크다운 형식으로 정확히 출력하세요 (추가 텍스트 없이):

**AI 총평:** [포트폴리오 전략과 주요 리스크를 2-3문장으로 요약]

**포트폴리오 종합 리니아 스코어: [0-100] / 100**

**3대 핵심 기준 스코어:**

- **성장 잠재력:** [0-100] / 100
- **안정성 및 방어력:** [0-100] / 100
- **전략적 일관성:** [0-100] / 100

**[1] 포트폴리오 리니아 스코어 심층 분석**

**1.1 성장 잠재력 분석 ([점수] / 100): [제목]**

[3-4문장의 구체적 분석]

**1.2 안정성 및 방어력 분석 ([점수] / 100): [제목]**

[3-4문장의 구체적 분석]

**1.3 전략적 일관성 분석 ([점수] / 100): [제목]**

[3-4문장의 구체적 분석]

**[2] 포트폴리오 강점 및 약점, 그리고 기회**

**💪 강점**

- [강점 1: 1-2문장, 실행 가능한 인사이트]
- [강점 2: 1-2문장, 실행 가능한 인사이트]

**📉 약점**

- [약점 1: 1-2문장, 구체적 개선방안]
- [약점 2: 1-2문장, 구체적 개선방안]

**💡 기회 및 개선 방안**

- [기회 1: What-if 시나리오 포함]
- [기회 2: 구체적 실행 방안]

**[3] 개별 종목 리니아 스코어 상세 분석**

**3.1 스코어 요약 테이블**

| 주식 | Overall (100점 만점) | 펀더멘탈 | 기술 잠재력 | 거시경제 | 시장심리 | CEO/리더십 |
| --- | --- | --- | --- | --- | --- | --- |
| [종목명] | [점수] | [점수] | [점수] | [점수] | [점수] | [점수] |

**3.2 개별 종목 분석 카드**

**[번호]. [종목명] - Overall: [점수] / 100**

- **펀더멘탈 ([점수]/100):** [상세 분석]
- **기술 잠재력 ([점수]/100):** [상세 분석]
- **거시경제 ([점수]/100):** [상세 분석]
- **시장심리 ([점수]/100):** [상세 분석]
- **CEO/리더십 ([점수]/100):** [상세 분석]

분석 규칙:
- 모든 점수는 0-100 사이의 정수로 평가
- 각 분석은 구체적이고 전문적인 내용으로 작성
- 강점/약점/기회는 실행 가능한 인사이트 제공
- 기회에는 간단한 "What-if" 시나리오 포함
- 모든 텍스트는 한국어로 작성
- 전문적인 투자 분석 언어 사용
- 구체적인 예시와 데이터 포인트 포함
```

#### **3.2. API 응답 형식 (API Response Schema)**

  * **성공 (Success - `200 OK`):**

    ```json
    {
      "content": "**AI 총평:** 문영님의 포트폴리오는 '양자 컴퓨팅 및 AI 기술 혁신 추구형' 전략을 명확히 따르고 있으며, 잠재력은 높으나 기술주의 높은 변동성과 신흥 기술 리스크에 다소 취약합니다.\n\n**포트폴리오 종합 리니아 스코어: 72 / 100**\n\n**3대 핵심 기준 스코어:**\n\n- **성장 잠재력:** 88 / 100\n- **안정성 및 방어력:** 55 / 100\n- **전략적 일관성:** 74 / 100\n\n... (expected_result.md와 동일한 마크다운 형식의 전체 분석 결과)",
      "processing_time": 15.2,
      "request_id": "uuid-string"
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

-----

### \#\# 4. 기술 스택 (Technology Stack)

  * **프론트엔드:** Next.js 15.5.3 (TypeScript)
  * **마크다운 렌더링:** react-markdown, remark-gfm
  * **백엔드:** Python 3.13.7, FastAPI 0.116.1
    * 공식 문서: https://fastapi.tiangolo.com/reference/
    * GitHub 저장소: https://github.com/fastapi/fastapi
    * 특징: 고성능, 자동 문서화, 타입 힌트 지원
  * **AI 모델:** Google Gemini 2.5 Flash API (google-genai Python SDK)
    * **Google Search 통합**: Gemini API의 `google_search` 도구를 활용한 실시간 웹 검색
    * **그라운딩 기능**: 검색된 정보를 기반으로 한 정확한 분석 제공
  * **클라우드 스토리지:** Google Cloud Storage
  * **배포:** Vercel (Frontend), Render (Backend)

-----

### \#\# 5. 범위 외 (Out of Scope for MVP)

  * 사용자 회원가입 및 로그인
  * 포트폴리오 데이터 저장 및 이력 관리
  * 추출된 데이터를 기반으로 한 **2차 분석** (위험도, 자산 배분 시각화 등)
  * 실시간 시세 연동
  * 다크 모드 등 UI 테마 기능

-----

### ## 6. 보안 및 개인정보 보호 (Security & Privacy)

  * 업로드된 이미지는 처리 완료 후 즉시 삭제한다. (프로덕션 기본값)
  * 선택적 스토리지(GCS)는 개발/디버깅 목적의 일시 보관에만 사용하며 만료 정책을 적용한다.
  * Gemini API 키는 환경 변수로 관리하고 서버 사이드에서만 사용한다.
  * Google Gen AI SDK의 안전 설정을 적용하여 부적절한 콘텐츠 생성을 방지한다.
  * 파일 크기 제한(예: 10MB)과 허용 확장자(PNG, JPEG) 검증을 수행한다.

-----

### ## 7. 성능 최적화 (Performance)

  * Google Gen AI Python SDK를 통한 Gemini 2.5 Flash API의 설정을 조절하여 비용이나 속도보다 **분석의 상세함과 품질**을 최우선으로 한다.
  * **Google Search 최적화**: 검색 쿼리를 효율적으로 구성하여 관련성 높은 정보만 검색하고 응답 시간을 단축한다.
  * 동일 이미지 반복 분석에 대한 캐싱 전략(해시 기반 중복 방지)을 적용한다.
  * 비동기 I/O로 업로드/LLM 호출/Google Search 파이프라인을 병렬화한다.
  * **검색 결과 캐싱**: 동일한 검색 쿼리에 대해 일정 시간 동안 캐시된 결과를 활용하여 API 호출 비용을 절약한다.

-----

### ## 8. 테스트 및 배포 (Testing & CI/CD)

  * 단위 테스트: 이미지 처리 로직, 프롬프트 유효성 테스트, Google Search API 호출 테스트.
  * 통합 테스트: 실제 샘플 스크린샷으로 엔드투엔드 검증, Google Search 결과 검증.
  * **Google Search 테스트**: 검색 쿼리 생성, 결과 파싱, 출처 정보 추출 테스트.
  * 사용자 수용 테스트(UAT): 다양한 브로커리지 UI 스킨에 대한 견고성 확인, 검색 결과 정확성 검증.
  * CI/CD: 메인 병합 시 자동 빌드/배포(프론트: Vercel, 백엔드: Render), 시크릿 관리, Google Search API 키 관리.