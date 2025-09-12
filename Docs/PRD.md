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
4.  **[AI 분석 출력]** 백엔드 분석 완료 후, **AI 총평/종합 스코어/3대 기준 스코어/종목별 분석 카드**를 **마크다운 형식**으로 화면에 표시.

### \#\# 2. 핵심 기능 명세 (Core Feature Specifications)

#### **2.1. 프론트엔드 (Frontend - Next.js)**

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

  * **엔드포인트 명세:**
      * **`POST /api/analyze`**
          * **요청 (Request):**
              * **Content-Type:** `multipart/form-data`
              * **Body:** `file` (이미지 파일)
          * **처리 로직 (Processing Logic):**
            1.  요청으로부터 이미지 파일(`UploadFile`)을 받는다.
            2.  이미지 파일을 메모리에서 읽어 **Base64**로 인코딩한다.
            3.  Vision LLM API(Google Gemini 2.5 Flash)에 보낼 \*\*프롬프트(Prompt)\*\*와 인코딩된 이미지를 포함하여 요청을 구성한다.
            4.  LLM API를 호출하고 응답을 기다린다. (비동기 처리 `async/await`)
            5.  LLM이 반환한 JSON 형식의 텍스트 응답을 파싱(Parsing)한다.
            6.  파싱된 데이터가 \*\*요구되는 데이터 형식(아래 3.2. 참조)\*\*을 따르는지 검증한다.
            7.  성공 시, 상태 코드 `200 OK`와 함께 추출된 JSON 데이터를 반환한다.
          * **에러 핸들링 (Error Handling):**
              * 이미지 파일이 아닐 경우: `400 Bad Request`
              * LLM API 호출 실패 시: `503 Service Unavailable`
              * LLM 응답 파싱/검증 실패 시: `500 Internal Server Error`
          * **응답 (Response):** 아래 **3. 데이터 요구사항** 참조

### \#\# 3. 데이터 요구사항 (Data & API Specification)

#### **3.1. Vision LLM 프롬프트 (Prompt for Vision LLM)**

백엔드가 LLM을 호출할 때 사용할 프롬프트 예시입니다. 이 프롬프트는 캡처 이미지에서 포트폴리오를 인식·정규화하고, 요구 JSON 스키마에 맞춘 **분석 결과**를 생성하도록 지시합니다.

```text
You are an expert portfolio analyst specializing in comprehensive investment analysis. From the provided brokerage screenshot(s), extract holdings and produce a detailed analysis following the exact format below.

Output strictly the following JSON object (no extra text):
{
  "aiSummary": string,
  "overallScore": integer,
  "dimensionScores": {
    "growthPotential": integer,
    "stabilityDefense": integer,
    "strategicConsistency": integer
  },
  "detailedAnalysis": {
    "growthAnalysis": string,
    "stabilityAnalysis": string,
    "consistencyAnalysis": string
  },
  "strengths": Array<string>,
  "weaknesses": Array<string>,
  "opportunities": Array<string>,
  "stocks": Array<{
    "stockName": string,
    "overallScore": integer,
    "fundamentalScore": integer,
    "techPotentialScore": integer,
    "macroScore": integer,
    "marketSentimentScore": integer,
    "leadershipScore": integer,
    "detailedAnalysis": string
  }>
}

Rules:
- aiSummary: 2-3 sentences describing portfolio strategy and main risks
- detailedAnalysis: Each section should be 3-4 sentences with specific insights
- strengths/weaknesses/opportunities: Each item should be 1-2 sentences with actionable insights. Include a simple "What-if" scenario within the opportunities.
- stocks: Include comprehensive 5-criteria scoring (0-100) and detailed analysis per stock
- All text must be Korean
- Use professional investment analysis language
- Include specific examples and data points when possible
```

#### **3.2. API 응답 형식 (API Response Schema)**

  * **성공 (Success - `200 OK`):**

    ```json
    {
      "aiSummary": "문영님의 포트폴리오는 '양자 컴퓨팅 및 AI 기술 혁신 추구형' 전략을 명확히 따르고 있으며, 잠재력은 높으나 기술주의 높은 변동성과 신흥 기술 리스크에 다소 취약합니다.",
      "overallScore": 72,
      "dimensionScores": {
        "growthPotential": 88,
        "stabilityDefense": 55,
        "strategicConsistency": 74
      },
      "detailedAnalysis": {
        "growthAnalysis": "문영님의 포트폴리오는 '기술 잠재력' 및 'CEO/리더십' 인덱스 점수가 매우 높은 종목들에 집중적으로 투자되어 있어 압도적인 성장 잠재력을 보여줍니다. 특히, 팔란티어(PLTR), 디파이언스 양자컴퓨터 ETF(QQC), 아이온큐(IONQ) 등 양자 컴퓨팅, AI, 데이터 인프라 등 미래 핵심 기술 분야의 선두 주자들에 대한 투자 비중이 전체의 상당 부분을 차지하고 있습니다.",
        "stabilityAnalysis": "포트폴리오의 안정성 및 방어력 점수는 55점으로 상대적으로 낮은 수준입니다. 이는 대부분의 종목들이 아직 상업적 성공을 확정 짓지 못한 성장 단계의 기술 기업들이거나, 높은 변동성을 특징으로 하는 ETF로 구성되어 있기 때문입니다.",
        "consistencyAnalysis": "문영님의 포트폴리오는 '양자 컴퓨팅'과 'AI'라는 명확한 투자 테마를 중심으로 구성되어 있어 높은 전략적 일관성을 가집니다. 하지만, 동시에 특정 기술 섹터에 대한 과도한 집중은 또 다른 형태의 리스크로 작용할 수 있습니다."
      },
      "strengths": [
        "선구적인 미래 기술 투자: 양자 컴퓨팅, AI, 바이오 신약 등 미래 성장 동력에 대한 과감하고 선구적인 투자를 통해 시장의 흐름을 앞서 나갈 잠재력을 보유하고 있습니다.",
        "명확하고 일관된 투자 테마: '기술 혁신'이라는 뚜렷한 투자 철학이 포트폴리오 전반에 걸쳐 일관되게 적용되어, 문영님의 신념이 반영된 투자를 하고 있습니다."
      ],
      "weaknesses": [
        "극심한 변동성 노출: 대부분의 종목이 성장주 및 신흥 기술주에 속하여 시장의 작은 움직임에도 포트폴리오 가치가 크게 요동칠 수 있습니다.",
        "기술 섹터 집중 리스크: 양자 컴퓨팅 및 AI라는 특정 기술 분야에 대한 의존도가 높아, 해당 분야에 예상치 못한 악재 발생 시 포트폴리오 전체가 심각한 타격을 입을 수 있습니다."
      ],
      "opportunities": [
        "안정적인 '핵심' 자산 추가: TIGER 미국S&P500 ETF의 비중을 높이거나, 마이크로소프트(MSFT)나 엔비디아(NVDA)와 같이 AI 시대의 필수 인프라를 제공하며 동시에 안정적인 재무구조를 가진 초대형 기술주를 편입하여 '안정성 및 방어력' 점수를 높이는 것을 고려할 수 있습니다.",
        "유사 테마 내 분산 투자: 양자 컴퓨팅 및 AI 테마는 유지하되, 관련 산업 내에서도 서로 다른 세부 기술 분야나 지역(글로벌 다변화)에 분산 투자하여 리스크를 줄일 수 있습니다."
      ],
      "stocks": [
        {
          "stockName": "팔란티어 테크놀로지스 (PLTR)",
          "overallScore": 78,
          "fundamentalScore": 70,
          "techPotentialScore": 95,
          "macroScore": 75,
          "marketSentimentScore": 85,
          "leadershipScore": 85,
          "detailedAnalysis": "꾸준한 매출 성장과 최근 GAAP 기준 흑자 전환 성공은 긍정적이나, 여전히 높은 밸류에이션 부담이 존재합니다. 빅데이터 분석 및 AI 분야 독보적인 기술력으로 고담(정부) 및 AIP(상업) 플랫폼 모두에서 빠른 성장을 보입니다."
        }
      ]
    }
    ```

  * **실패 (Error - `4xx` or `5xx`):**

    ```json
    {
      "error": "An informative error message."
    }
    ```

-----

### \#\# 4. 기술 스택 (Technology Stack)

  * **프론트엔드:** Next.js 15.3 (TypeScript)
  * **마크다운 렌더링:** react-markdown, remark-gfm
  * **백엔드:** Python 3.12, FastAPI 0.110.0
  * **AI 모델:** Google Gemini 2.5 Flash API
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
  * API 키는 환경 변수로 관리하고 서버 사이드에서만 사용한다.
  * 파일 크기 제한(예: 10MB)과 허용 확장자(PNG, JPEG) 검증을 수행한다.

-----

### ## 7. 성능 최적화 (Performance)

  * Gemini 2.5 Flash API의 설정을 조절하여 비용이나 속도보다 **분석의 상세함과 품질**을 최우선으로 한다.
  * 동일 이미지 반복 분석에 대한 캐싱 전략(해시 기반 중복 방지)을 적용한다.
  * 비동기 I/O로 업로드/LLM 호출/파싱 파이프라인을 병렬화한다.

-----

### ## 8. 테스트 및 배포 (Testing & CI/CD)

  * 단위 테스트: 파싱/스키마 검증 로직, 프롬프트 유효성 테스트.
  * 통합 테스트: 실제 샘플 스크린샷으로 엔드투엔드 검증.
  * 사용자 수용 테스트(UAT): 다양한 브로커리지 UI 스킨에 대한 견고성 확인.
  * CI/CD: 메인 병합 시 자동 빌드/배포(프론트: Vercel, 백엔드: Render), 시크릿 관리.