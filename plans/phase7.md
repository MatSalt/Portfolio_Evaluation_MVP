# Phase 7: 백엔드 Two-step 생성 전략 전환

## 📋 개요

**목표**: PRD.md의 2‑스텝 전략(검색·그라운딩 → 구조화 JSON)을 백엔드 파이프라인에 반영하여 최신 정보 반영과 스키마 정확성을 동시에 확보.

**배경**: Gemini API는 Google Search Tool과 `response_mime_type="application/json"`을 동시에 사용할 수 없음. 이를 해결하기 위해 두 단계로 분리:
- **Step 1**: Google Search Tool로 최신 정보 수집 (마크다운/텍스트)
- **Step 2**: Step 1 결과를 컨텍스트로 순수 JSON 생성 (Tool 없이, JSON 모드)

---

## 🏗️ 전체 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│  analyze_portfolio_structured(format_type="json")          │
└─────────────────────┬───────────────────────────────────────┘
                      │
         ┌────────────▼────────────┐
         │  이미지 검증 및 준비    │
         └────────────┬────────────┘
                      │
         ┌────────────▼────────────────────────────────────┐
         │  Step 1: _generate_grounded_facts()             │
         │  - Google Search Tool 활성화                     │
         │  - response_mime_type 미지정 (텍스트)            │
         │  - 점수, 테이블, 분석 등 구조화된 마크다운 생성   │
         │  - 캐시 저장 (이미지 해시 기반)                  │
         └────────────┬────────────────────────────────────┘
                      │
                      │ (구조화된 마크다운 텍스트)
                      │
         ┌────────────▼────────────────────────────────────┐
         │  Step 2: _generate_structured_json()            │
         │  - Google Search Tool 비활성화                   │
         │  - response_mime_type="application/json"        │
         │  - Step 1 결과를 컨텍스트로 JSON 생성            │
         │  - <JSON_START>/<JSON_END> 태그로 안전 추출     │
         │  - Pydantic 검증                                │
         └────────────┬────────────────────────────────────┘
                      │
         ┌────────────▼────────────┐
         │  StructuredAnalysisResponse  │
         │  반환                    │
         └─────────────────────────┘
```

---

## 📝 Step 1: 검색·그라운딩 구현

### Step 1.1: 프롬프트 설계

**목적**: Google Search로 최신 정보를 수집하여 구조화된 마크다운 형태로 정리

```python
def _get_grounding_prompt(self) -> str:
    """Step 1: 검색·그라운딩용 프롬프트 (구조화된 마크다운 출력)"""
    return """
당신은 전문 포트폴리오 분석가입니다. 제공된 포트폴리오 이미지를 분석하여 
다음 구조화된 마크다운 형식으로 정리하세요.

**중요**: Google Search를 활용하여 최신 시장 정보, 재무 데이터, 뉴스를 반영하세요.

출력 형식:

---

### **포트폴리오 종합 스코어**

* **포트폴리오 종합 리니아 스코어: [0-100 정수] / 100**

### **포트폴리오 심층 분석**

**1. 3대 핵심 기준 스코어**
* 성장 잠재력: [0-100 정수] / 100
* 안정성 및 방어력: [0-100 정수] / 100
* 전략적 일관성: [0-100 정수] / 100

**2. 개별 종목 리니아 스코어**
| 주식 | Overall (100점 만점) | 펀더멘탈 | 기술 잠재력 | 거시경제 | 시장심리 | CEO/리더십 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **[종목명]** | [점수] | [점수] | [점수] | [점수] | [점수] | [점수] |

**3. 개별 종목 분석 설명 (분석 카드)**

**1. [종목명] - Overall: [점수] / 100**
* **펀더멘탈 ([점수]/100):** [최소 30자 분석 - 최신 재무 데이터 포함]
* **기술 잠재력 ([점수]/100):** [최소 30자 분석 - 최신 기술 동향 포함]
* **거시경제 ([점수]/100):** [최소 30자 분석 - 최신 경제 전망 포함]
* **시장심리 ([점수]/100):** [최소 30자 분석 - 최신 시장 동향 포함]
* **CEO/리더십 ([점수]/100):** [최소 30자 분석]

### **심층 분석 설명**

* **1.1 성장 잠재력 분석 ([점수] / 100): [제목]**
    [최소 50자 상세 분석 - Google Search로 최신 성장 전망 반영]

* **1.2 안정성 및 방어력 분석 ([점수] / 100): [제목]**
    [최소 50자 상세 분석 - 최신 리스크 요인 포함]

* **1.3 전략적 일관성 분석 ([점수] / 100): [제목]**
    [최소 50자 상세 분석]

### **포트폴리오 강점, 약점 및 기회 (설명)**

* **💪 강점**
    * **[강점 1 제목]:** [1-2문장]
    * **[강점 2 제목]:** [1-2문장]

* **📉 약점**
    * **[약점 1 제목]:** [1-2문장]
    * **[약점 2 제목]:** [1-2문장]

* **💡 기회 및 개선 방안**
    * **[기회 1 제목]:** [What-if 시나리오 포함, 최소 30자]
    * **[기회 2 제목]:** [구체적 실행 방안, 최소 30자]

---

분석 규칙:
1. 모든 점수는 0-100 사이의 정수로만 표기
2. Google Search로 각 종목의 최신 뉴스, 재무 데이터, 시장 동향 반영
3. 분석은 구체적이고 전문적인 내용으로 작성
4. 모든 텍스트는 한국어로 작성
5. 위 마크다운 형식을 정확히 따르되, 추가 설명이나 코멘트는 넣지 마세요
"""
```

### Step 1.2: API 호출 메서드 구현

```python
async def _generate_grounded_facts(self, image_data_list: List[bytes]) -> str:
    """
    Step 1: Google Search Tool로 최신 정보 수집 및 구조화된 마크다운 생성
    
    Args:
        image_data_list: 이미지 바이트 데이터 리스트
        
    Returns:
        str: 구조화된 마크다운 형식의 분석 결과 (점수, 테이블, 상세 분석 포함)
        
    Raises:
        ValueError: API 호출 실패
    """
    # 캐시 키 생성 (이미지 해시 기반)
    cache_key = f"grounded_{self._generate_multiple_cache_key(image_data_list)}"
    if cache_key in self._cache:
        logger.info("Step 1 캐시된 결과 반환")
        return self._cache[cache_key]
    
    for attempt in range(self.max_retries):
        try:
            logger.info(
                f"Step 1: 검색·그라운딩 호출 시도 {attempt + 1}/{self.max_retries}"
            )
            
            # Contents 배열 구성
            contents: List[Union[str, Part]] = []
            
            # 1) 이미지 파트들 추가
            for i, image_data in enumerate(image_data_list):
                image_part = Part.from_bytes(data=image_data, mime_type="image/jpeg")
                contents.append(image_part)
                logger.debug(f"Step 1: 이미지 {i+1}/{len(image_data_list)} 추가")
            
            # 2) 그라운딩 프롬프트 추가
            contents.append(self._get_grounding_prompt())
            
            # 3) Google Search Tool 설정
            from google.genai import types
            grounding_tool = types.Tool(google_search=types.GoogleSearch())
            
            # 4) 설정: Google Search 활성화, response_mime_type 미지정
            config = GenerateContentConfig(
                temperature=0.1,  # 일관된 정보 수집을 위해 낮은 온도
                max_output_tokens=8192,
                tools=[grounding_tool],
                # response_mime_type 미지정 - 텍스트 응답
            )
            
            # 5) API 호출
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )
            
            # 6) 응답 검증 및 반환
            if response and getattr(response, "text", None):
                result_text = response.text.strip()
                
                # 기본 검증 (최소 길이, 필수 섹션 확인)
                if len(result_text) < 500:
                    raise ValueError("Step 1 응답이 너무 짧습니다.")
                
                # 필수 섹션 확인
                required_sections = [
                    "포트폴리오 종합 리니아 스코어:",
                    "3대 핵심 기준 스코어",
                    "개별 종목 리니아 스코어",
                    "개별 종목 분석 설명",
                    "심층 분석 설명",
                    "포트폴리오 강점, 약점 및 기회"
                ]
                
                for section in required_sections:
                    if section not in result_text:
                        logger.warning(f"Step 1: 필수 섹션 누락 - {section}")
                
                # 캐시 저장
                self._cache[cache_key] = result_text
                
                # 결과 미리보기 로깅 (300자)
                preview = result_text[:300] + "..." if len(result_text) > 300 else result_text
                logger.info(f"Step 1 성공 - 응답 미리보기: {preview}")
                
                return result_text
            
            raise ValueError("Step 1: Gemini API에서 빈 응답 받음")
            
        except Exception as e:
            logger.error(f"Step 1 호출 실패 (시도 {attempt + 1}): {str(e)}")
            if attempt == self.max_retries - 1:
                raise ValueError(f"Step 1 검색·그라운딩 실패: {str(e)}")
            await asyncio.sleep(2 ** attempt)
```

---

## 📝 Step 2: 구조화된 JSON 생성 구현

### Step 2.1: 프롬프트 설계

**목적**: Step 1의 마크다운 결과를 Pydantic 스키마에 맞는 순수 JSON으로 변환

**참고**: [Gemini API 공식 문서 - 구조화된 출력](https://ai.google.dev/gemini-api/docs/structured-output?hl=ko#generating-json)에 따르면, `response_schema`를 사용하면 스키마 준수가 자동으로 강제되므로 프롬프트를 간소화할 수 있습니다.

```python
def _get_json_generation_prompt(self, grounded_facts: str) -> str:
    """Step 2: JSON 스키마 생성용 프롬프트 (간소화 버전 - response_schema 활용)"""
    return f"""
당신은 데이터 변환 전문가입니다. 아래 분석 결과를 읽고 정확히 JSON으로 변환하세요.

## 입력 데이터 (Step 1에서 수집된 분석 결과):
```
{grounded_facts}
```

## 변환 규칙:
1. 모든 점수는 0-100 사이의 정수값으로 추출 (범위 표기 금지)
2. 텍스트는 그대로 복사하되, 불필요한 마크다운 문법(*, **, #, |) 제거
3. 제공된 스키마에 정확히 맞춰 변환
4. 누락된 필드가 없도록 주의
5. reportDate는 오늘 날짜 (YYYY-MM-DD 형식)
6. tabs는 정확히 4개: dashboard, deepDive, allStockScores, keyStockAnalysis
7. 모든 텍스트는 한국어 유지

참고: response_schema가 자동으로 JSON 형식을 강제하므로, 순수한 데이터 변환에만 집중하세요.
"""
```

**개선 사항**:
- ✅ `response_schema` 사용을 전제로 프롬프트 간소화 (1/3 길이로 단축)
- ✅ JSON 스키마 상세 설명 제거 (API가 자동으로 강제)
- ✅ 핵심 변환 규칙에만 집중
- ✅ `<JSON_START>/<JSON_END>` 태그 불필요 (자동 파싱)

### Step 2.2: API 호출 메서드 구현

**참고**: [Gemini API 공식 문서](https://ai.google.dev/gemini-api/docs/structured-output?hl=ko#generating-json)에 따르면, `response_schema`를 사용하면 `response.parsed`로 자동 파싱된 Pydantic 객체를 받을 수 있습니다.

```python
async def _generate_structured_json(self, grounded_facts: str) -> PortfolioReport:
    """
    Step 2: 구조화된 JSON 생성 (response_schema 사용 - 공식 권장 방식)
    
    Args:
        grounded_facts: Step 1에서 생성된 구조화된 마크다운 텍스트
        
    Returns:
        PortfolioReport: Pydantic 검증된 포트폴리오 리포트
        
    Raises:
        ValueError: JSON 생성 또는 검증 실패
    """
    for attempt in range(self.max_retries):
        try:
            logger.info(
                f"Step 2: JSON 생성 호출 시도 {attempt + 1}/{self.max_retries}"
            )
            
            # 1) 프롬프트 생성 (Step 1 결과를 컨텍스트로 포함)
            prompt = self._get_json_generation_prompt(grounded_facts)
            
            # 2) 설정: response_schema 사용 (공식 권장 방식)
            config = GenerateContentConfig(
                temperature=0.0,  # 결정론적 변환을 위해 온도 0
                max_output_tokens=8192,
                response_mime_type="application/json",  # JSON 모드
                response_schema=PortfolioReport,  # Pydantic 모델 직접 전달
                # tools 없음 - Google Search Tool 비활성화
            )
            
            # 3) API 호출 (텍스트만 전달, 이미지 없음)
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt],
                config=config
            )
            
            # 4) 자동 파싱된 객체 반환 (공식 권장 방식)
            if response and hasattr(response, 'parsed') and response.parsed:
                logger.info("Step 2: response.parsed로 자동 파싱 성공")
                return response.parsed  # 이미 PortfolioReport 객체
            
            # Fallback: .parsed가 없으면 수동 파싱
            if response and getattr(response, "text", None):
                logger.warning("Step 2: .parsed 없음, 수동 파싱으로 Fallback")
                response_text = response.text.strip()
                
                try:
                    portfolio_report = PortfolioReport.model_validate_json(response_text)
                    logger.info("Step 2: 수동 Pydantic 검증 성공")
                    return portfolio_report
                except Exception as validation_error:
                    logger.error(f"Step 2: Pydantic 검증 실패 - {str(validation_error)}")
                    
                    # 검증 실패 시 1회 보정 재시도 (첫 시도에서만)
                    if attempt == 0:
                        logger.info("Step 2: 보정 재시도 (누락 필드/범위 오류 수정 유도)")
                        await asyncio.sleep(1)
                        continue
                    
                    # JSON 미리보기 로깅 (디버깅용, 500자만)
                    preview = response_text[:500] if len(response_text) > 500 else response_text
                    logger.debug(f"Step 2: 검증 실패 JSON 미리보기: {preview}...")
                    raise ValueError(
                        f"JSON이 스키마와 일치하지 않습니다: {str(validation_error)}"
                    )
            
            raise ValueError("Step 2: Gemini API에서 응답을 받지 못했습니다.")
            
        except Exception as e:
            logger.error(f"Step 2 호출 실패 (시도 {attempt + 1}): {str(e)}")
            if attempt == self.max_retries - 1:
                raise ValueError(f"Step 2 JSON 생성 실패: {str(e)}")
            await asyncio.sleep(2 ** attempt)
```

**개선 사항**:
- ✅ `response_schema=PortfolioReport` 추가 (공식 권장 방식)
- ✅ `response.parsed`로 자동 파싱된 객체 직접 반환
- ✅ `<JSON_START>/<JSON_END>` 태그 파싱 로직 제거 (불필요)
- ✅ 코드블록 제거 로직 제거 (불필요)
- ✅ Fallback 로직 유지 (안전성 강화)

---

## 🔄 Step 3: 기존 메서드 리팩터링

### Step 3.1: `analyze_portfolio_structured` 메서드 수정

기존의 단일 호출을 두 단계로 분리:

```python
async def analyze_portfolio_structured(
    self, image_data_list: List[bytes], format_type: str = "json"
) -> Union[StructuredAnalysisResponse, AnalysisResponse]:
    """
    포트폴리오 분석 - format에 따라 JSON 또는 마크다운 반환
    JSON 모드 시 Two-step 전략 사용: 검색·그라운딩 → 구조화 JSON
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())

    # 입력 검증
    if not image_data_list or len(image_data_list) == 0:
        raise ValueError("분석할 이미지가 없습니다.")
    if len(image_data_list) > 5:
        raise ValueError("최대 5개의 이미지만 분석 가능합니다.")
    for i, image_data in enumerate(image_data_list):
        await validate_image(image_data)

    if format_type == "json":
        try:
            logger.info("=== Two-step JSON 생성 시작 ===")
            
            # Step 1: 검색·그라운딩 (Google Search Tool 사용)
            logger.info("Step 1: 검색·그라운딩 호출")
            grounded_facts = await self._generate_grounded_facts(image_data_list)
            logger.info(f"Step 1 완료 - 구조화된 데이터 길이: {len(grounded_facts)}자")
            
            # Step 2: 구조화된 JSON 생성 (Step 1 결과를 컨텍스트로)
            logger.info("Step 2: JSON 스키마 생성 호출")
            portfolio_report = await self._generate_structured_json(grounded_facts)
            logger.info("Step 2 완료 - Pydantic 검증 성공")
            
            logger.info("=== Two-step JSON 생성 완료 ===")
            
        except ValueError as ve:
            # Step 1 또는 Step 2 실패 시 사용자 친화적 에러
            logger.error(f"Two-step JSON 생성 실패: {str(ve)}")
            raise ValueError("AI 응답이 예상 형식과 다릅니다. 다시 시도해 주세요.")
        
        return StructuredAnalysisResponse(
            portfolioReport=portfolio_report,
            processing_time=time.time() - start_time,
            request_id=request_id,
            images_processed=len(image_data_list),
        )
    else:
        # 기존 마크다운 출력 재사용 (변경 없음)
        if len(image_data_list) == 1:
            markdown_content = await self.analyze_portfolio_image(
                image_data_list[0], use_cache=True
            )
        else:
            markdown_content = await self.analyze_multiple_portfolio_images(
                image_data_list
            )
        return AnalysisResponse(
            content=markdown_content,
            processing_time=time.time() - start_time,
            request_id=request_id,
            images_processed=len(image_data_list),
        )
```

---

## 🧪 Step 4: 테스트 계획

### Step 4.1: 단위 테스트

**테스트 파일**: `backend/tests/test_two_step_gemini.py`

```python
import pytest
from services.gemini_service import GeminiService

@pytest.mark.asyncio
async def test_step1_grounding_success():
    """Step 1: 검색·그라운딩 성공 테스트"""
    service = await get_gemini_service()
    
    # 샘플 이미지 데이터 (실제 이미지 또는 목 데이터)
    with open("tests/fixtures/sample_portfolio.jpg", "rb") as f:
        image_data = f.read()
    
    # Step 1 호출
    result = await service._generate_grounded_facts([image_data])
    
    # 검증
    assert isinstance(result, str)
    assert len(result) > 500
    assert "포트폴리오 종합 리니아 스코어:" in result
    assert "3대 핵심 기준 스코어" in result
    assert "개별 종목 리니아 스코어" in result

@pytest.mark.asyncio
async def test_step2_json_generation_success():
    """Step 2: JSON 생성 성공 테스트"""
    service = await get_gemini_service()
    
    # Step 1 샘플 결과 (위 예시 마크다운 사용)
    grounded_facts = """
    ### **포트폴리오 종합 스코어**
    * **포트폴리오 종합 리니아 스코어: 72 / 100**
    
    ### **포트폴리오 심층 분석**
    **1. 3대 핵심 기준 스코어**
    * 성장 잠재력: 88 / 100
    * 안정성 및 방어력: 55 / 100
    * 전략적 일관성: 74 / 100
    ...
    """
    
    # Step 2 호출
    portfolio_report = await service._generate_structured_json(grounded_facts)
    
    # Pydantic 검증 (자동)
    assert portfolio_report.version == "1.0"
    assert len(portfolio_report.tabs) == 4
    assert portfolio_report.tabs[0].tabId == "dashboard"

@pytest.mark.asyncio
async def test_two_step_end_to_end():
    """Two-step 전체 플로우 E2E 테스트"""
    service = await get_gemini_service()
    
    with open("tests/fixtures/sample_portfolio.jpg", "rb") as f:
        image_data = f.read()
    
    # 전체 플로우 실행
    response = await service.analyze_portfolio_structured(
        [image_data], 
        format_type="json"
    )
    
    # 검증
    assert isinstance(response, StructuredAnalysisResponse)
    assert response.images_processed == 1
    assert response.portfolioReport.version == "1.0"
    assert len(response.portfolioReport.tabs) == 4

@pytest.mark.asyncio
async def test_step1_caching():
    """Step 1 캐싱 테스트"""
    service = await get_gemini_service()
    
    with open("tests/fixtures/sample_portfolio.jpg", "rb") as f:
        image_data = f.read()
    
    # 첫 호출
    start1 = time.time()
    result1 = await service._generate_grounded_facts([image_data])
    time1 = time.time() - start1
    
    # 두 번째 호출 (캐시 히트)
    start2 = time.time()
    result2 = await service._generate_grounded_facts([image_data])
    time2 = time.time() - start2
    
    # 검증
    assert result1 == result2
    assert time2 < time1 * 0.1  # 캐시는 10배 이상 빨라야 함

@pytest.mark.asyncio
async def test_step2_validation_retry():
    """Step 2 검증 실패 시 1회 보정 재시도 테스트"""
    service = await get_gemini_service()
    
    # 잘못된 형식의 Step 1 결과 (스키마 불일치 유도)
    grounded_facts = "잘못된 데이터"
    
    # 예외 발생 확인
    with pytest.raises(ValueError, match="JSON이 스키마와 일치하지 않습니다"):
        await service._generate_structured_json(grounded_facts)
```

### Step 4.2: 통합 테스트

**테스트 시나리오**:
1. 단일 이미지 분석 (JSON)
2. 다중 이미지 분석 (JSON, 5개)
3. format=markdown와 format=json 비교
4. 캐싱 동작 확인
5. 에러 핸들링 (잘못된 이미지, API 오류 등)

---

## 📊 Step 5: 성능 최적화

### Step 5.1: 캐싱 전략

```python
# 이미지 해시 기반 Step 1 결과 캐싱
cache_key = f"grounded_{self._generate_multiple_cache_key(image_data_list)}"

# 캐시 히트 시 Step 1 건너뛰고 Step 2만 실행
if cache_key in self._cache:
    grounded_facts = self._cache[cache_key]
    # Step 2로 바로 진행
```

### Step 5.2: 로깅 최적화

```python
# Step 1 결과 미리보기만 로깅 (전체 로깅 방지)
preview = grounded_facts[:300] + "..." if len(grounded_facts) > 300 else grounded_facts
logger.info(f"Step 1 성공 - 응답 미리보기: {preview}")

# Step 2 검증 실패 시 필드/이유만 로깅
logger.error(f"Step 2: Pydantic 검증 실패 - {str(validation_error)}")
```

### Step 5.3: 재시도 로직

```python
# Step 1 실패 시: 최대 3회 재시도 (지수 백오프)
# Step 2 실패 시: 첫 실패 시 1회 보정 재시도, 이후 최대 3회 재시도
```

---

## 🐛 Step 6: 에러 처리 및 폴백

### Step 6.1: Step 1 실패 시

```python
try:
    grounded_facts = await self._generate_grounded_facts(image_data_list)
except ValueError as e:
    logger.error(f"Step 1 실패: {str(e)}")
    raise ValueError("최신 정보 수집에 실패했습니다. 다시 시도해 주세요.")
```

### Step 6.2: Step 2 실패 시

```python
try:
    portfolio_report = await self._generate_structured_json(grounded_facts)
except ValueError as e:
    logger.error(f"Step 2 실패: {str(e)}")
    # 옵션: Step 1 결과를 마크다운으로 반환하는 폴백 고려
    raise ValueError("분석 결과 구조화에 실패했습니다. 다시 시도해 주세요.")
```

---

## ✅ Step 7: 체크리스트

### 구현 체크리스트

- [ ] `_get_grounding_prompt()` 메서드 추가
- [ ] `_generate_grounded_facts()` 메서드 추가
- [ ] `_get_json_generation_prompt()` 메서드 추가
- [ ] `_generate_structured_json()` 메서드 추가
- [ ] `analyze_portfolio_structured()` 메서드 수정 (two-step 통합)
- [ ] 캐싱 로직 추가 (Step 1 결과)
- [ ] 로깅 강화 (각 단계별 상세 로그)
- [ ] 에러 처리 강화 (사용자 친화적 메시지)

### 테스트 체크리스트

- [ ] `test_step1_grounding_success` 단위 테스트
- [ ] `test_step2_json_generation_success` 단위 테스트
- [ ] `test_two_step_end_to_end` E2E 테스트
- [ ] `test_step1_caching` 캐싱 테스트
- [ ] `test_step2_validation_retry` 보정 재시도 테스트
- [ ] 다중 이미지 통합 테스트 (5개)
- [ ] format=markdown vs format=json 비교 테스트

### 문서 체크리스트

- [ ] `backend/README.md` 업데이트 (Two-step 전략 설명)
- [ ] API 문서 업데이트 (FastAPI 자동 생성)
- [ ] 로깅 가이드 작성 (각 단계별 로그 해석 방법)

---

## 📌 주요 변경 사항 요약

| 항목 | 변경 전 | 변경 후 |
|------|---------|---------|
| **API 호출 횟수** | 1회 (JSON 직접 생성) | 2회 (Step 1 + Step 2) |
| **Google Search 사용** | JSON 모드에서 에러 발생 | Step 1에서만 사용 (성공) |
| **JSON 스키마 정확성** | 낮음 (노이즈 포함) | 높음 (Step 2에서 정제) |
| **최신 정보 반영** | 제한적 (Tool 미사용) | 완전 (Step 1에서 Search) |
| **캐싱** | 전체 결과만 | Step 1 결과 별도 캐싱 |
| **재시도 효율** | 전체 재시도 | Step 2만 재시도 가능 |
| **에러 메시지** | 기술적 | 사용자 친화적 |

---

## 🚀 배포 및 모니터링

### 배포 전 확인사항

1. ✅ 모든 단위 테스트 통과
2. ✅ E2E 테스트 통과 (최소 5개 다른 포트폴리오 이미지)
3. ✅ 성능 테스트 (Step 1 + Step 2 총 시간 < 60초)
4. ✅ 에러 핸들링 검증 (잘못된 입력, API 오류 등)
5. ✅ 로깅 확인 (각 단계별 상태 추적 가능)

### 모니터링 항목

- Step 1 평균 응답 시간
- Step 2 평균 응답 시간
- Step 1 캐시 히트율
- Step 2 Pydantic 검증 성공률
- Step 2 보정 재시도 발생 빈도
- 전체 Two-step 성공률

---

## 📖 참고 자료

- **PRD.md**: Two-step 전략 상세 설명 (섹션 3.1.1)
- **Gemini API 문서**: https://ai.google.dev/gemini-api/docs
- **Google Search Tool**: https://ai.google.dev/gemini-api/docs/google-search
- **Structured Output**: https://ai.google.dev/gemini-api/docs/structured-output
- **Pydantic 문서**: https://docs.pydantic.dev/

---

## 🎯 예상 결과

### 성공 시나리오

```
[INFO] === Two-step JSON 생성 시작 ===
[INFO] Step 1: 검색·그라운딩 호출
[INFO] Step 1: 검색·그라운딩 호출 시도 1/3
[INFO] Step 1: 이미지 1/1 추가
[INFO] Step 1 성공 - 응답 미리보기: 
---

### **포트폴리오 종합 스코어**

* **포트폴리오 종합 리니아 스코어: 72 / 100**

### **포트폴리오 심층 분석**

**1. 3대 핵심 기준 스코어**
* 성장 잠재력: 88 / 100
* 안정성 및 방어력: 55 / 100
* 전략적 일관성: 74 / 100...

[INFO] Step 1 완료 - 구조화된 데이터 길이: 8543자
[INFO] Step 2: JSON 스키마 생성 호출
[INFO] Step 2: JSON 생성 호출 시도 1/3
[INFO] Step 2: JSON 응답 수신, 추출 및 검증 시작
[INFO] Step 2: Pydantic 검증 성공
[INFO] Step 2 완료 - Pydantic 검증 성공
[INFO] === Two-step JSON 생성 완료 ===
```

### 실패 시나리오 (Step 2 검증 실패 → 보정 재시도)

```
[INFO] Step 2: JSON 생성 호출 시도 1/3
[ERROR] Step 2: Pydantic 검증 실패 - 1 validation error for PortfolioReport
tabs -> 0 -> content -> overallScore -> score
  Input should be a valid integer [type=int_type, input_value='72-100', input_type=str]
[INFO] Step 2: 보정 재시도 (누락 필드/범위 오류 수정 유도)
[INFO] Step 2: JSON 생성 호출 시도 2/3
[INFO] Step 2: Pydantic 검증 성공
[INFO] Step 2 완료 - Pydantic 검증 성공
```

---

## 📈 Step 8: 테스트 결과 기반 추가 개선 사항

### 테스트 결과 분석

**통합 테스트 결과**: 15개 중 11개 통과 (73%)

**주요 발견 사항**:
1. ⏱️ **타임아웃 문제**: Step 1 + Step 2 합산 시간이 5분 초과 (최대 329초 관측)
2. 🚀 **Step 2 캐싱 부재**: Step 1은 캐싱되지만 Step 2는 매번 재생성 (117초 소요)
3. 📊 **성능 변동성**: 동일 입력에도 80-120초 범위로 변동

---

### Step 8.1: 타임아웃 설정 개선

**문제**: 
- 현재 `GEMINI_TIMEOUT=180` (3분)으로 설정
- Two-step 전략: Step 1 (60-150초) + Step 2 (60-120초) = **최대 270초 필요**
- 재시도 포함 시 최대 5분 이상 소요 가능
- 복잡한 다중 이미지 분석 시 10분까지 소요될 수 있음

**해결 방안**:

```python
# backend/services/gemini_service.py

class GeminiService:
    def __init__(self):
        # 기존
        self.timeout = int(os.getenv("GEMINI_TIMEOUT", "180"))
        
        # 개선: Two-step 전략에 맞춰 타임아웃 대폭 증가 (통합 관리)
        self.timeout = int(os.getenv("GEMINI_TIMEOUT", "600"))  # 10분으로 통합
```

**환경변수 업데이트** (`.env`):
```bash
# Gemini API 타임아웃 설정 (통합 관리)
GEMINI_TIMEOUT=600  # 전체 타임아웃: 10분 (Two-step 통합)
```

**API 호출 시 타임아웃 적용**:
```python
async def _generate_grounded_facts(self, image_data_list: List[bytes]) -> str:
    # ... 기존 코드 ...
    
    # 통합 타임아웃 설정 적용
    import asyncio
    
    try:
        response = await asyncio.wait_for(
            self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            ),
            timeout=self.timeout  # 10분 통합 타임아웃
        )
    except asyncio.TimeoutError:
        raise ValueError(f"API 호출 타임아웃: {self.timeout}초 초과")
```

**프론트엔드 타임아웃 설정 업데이트**:

```javascript
// frontend/src/utils/api.ts
const API_TIMEOUT = 600000; // 10분으로 증가 (기존 5분)

// 다중 파일용 타임아웃도 동일하게 조정
const timeoutId = setTimeout(() => controller.abort(), 600000); // 10분으로 증가
```

**UI 텍스트 업데이트 필요 사항**:

1. **frontend/src/components/AnalysisDisplay.tsx** (43번째 줄):
   ```javascript
   // 변경 전
   다중 이미지 포함 최대 5분 소요됩니다
   
   // 변경 후  
   다중 이미지 포함 최대 10분 소요됩니다
   ```

2. **frontend/src/app/page.tsx** (288번째 줄):
   ```javascript
   // 변경 전
   이미지 업로드 후 2분 이내에
   
   // 변경 후
   이미지 업로드 후 10분 이내에
   ```

3. **백엔드 에러 메시지 업데이트**:
   ```python
   # 사용자 친화적 에러 메시지
   raise ValueError("분석 시간이 초과되었습니다. 복잡한 포트폴리오의 경우 최대 10분까지 소요될 수 있습니다. 다시 시도해 주세요.")
   ```

**예상 성능 개선**:

| 시나리오 | 기존 타임아웃 | 개선 후 타임아웃 | 개선 효과 |
|----------|--------------|-----------------|-----------|
| **단순 포트폴리오** | 3분 (180초) | 10분 (600초) | 타임아웃 에러 해결 |
| **복잡한 다중 이미지** | 5분 후 타임아웃 | 10분까지 허용 | 완전한 분석 가능 |
| **재시도 포함** | 3회 재시도 시 실패 | 안정적 완료 | 성공률 대폭 향상 |

---

### Step 8.2: Step 2 결과 캐싱 구현

**현재 상태**:
- ✅ Step 1: 캐시 적용됨 (이미지 해시 기반)
- ❌ Step 2: 캐시 없음 (매번 재생성)

**문제**:
- 동일한 `grounded_facts`에 대해 매번 80-120초 소요
- Step 1이 캐시 히트해도 전체 응답 시간이 여전히 느림 (117초)

**해결 방안**:

#### 8.2.1: Step 2 캐시 키 생성

```python
def _generate_step2_cache_key(self, grounded_facts: str) -> str:
    """Step 2용 캐시 키 생성 (grounded_facts 해시 기반)"""
    import hashlib
    
    # grounded_facts의 해시 생성
    facts_hash = hashlib.md5(grounded_facts.encode('utf-8')).hexdigest()
    return f"step2_json_{facts_hash}"
```

#### 8.2.2: Step 2 캐싱 로직 추가

```python
async def _generate_structured_json(self, grounded_facts: str) -> PortfolioReport:
    """
    Step 2: 구조화된 JSON 생성 (캐싱 추가)
    """
    # 🆕 캐시 확인
    cache_key = self._generate_step2_cache_key(grounded_facts)
    if cache_key in self._cache:
        logger.info("Step 2 캐시된 결과 반환")
        cached_json = self._cache[cache_key]
        # 캐시된 JSON을 PortfolioReport로 변환
        return PortfolioReport.model_validate_json(cached_json)
    
    for attempt in range(self.max_retries):
        try:
            logger.info(
                f"Step 2: JSON 생성 호출 시도 {attempt + 1}/{self.max_retries}"
            )
            
            # ... 기존 API 호출 로직 ...
            
            # 성공 시 캐시 저장 (JSON 문자열로 저장)
            portfolio_json = portfolio_report.model_dump_json()
            self._cache[cache_key] = portfolio_json
            logger.info(f"Step 2: 캐시 저장 완료 (키: {cache_key[:16]}...)")
            
            return portfolio_report
            
        except Exception as e:
            # ... 기존 에러 처리 ...
```

#### 8.2.3: 예상 성능 개선

| 시나리오 | 기존 | 개선 후 | 개선율 |
|----------|------|---------|--------|
| **첫 호출** | 230초 (Step1: 110초 + Step2: 120초) | 230초 (동일) | - |
| **Step 1 캐시 히트** | 120초 (Step1: 0.001초 + Step2: 120초) | **0.002초** (Step1: 0.001초 + Step2: 0.001초) | **99.9% ↓** |
| **동일 이미지 재분석** | 120초 | **0.002초** | **60,000배 빠름** |

**로그 예시 (캐시 히트)**:
```
[INFO] === Two-step JSON 생성 시작 ===
[INFO] Step 1: 검색·그라운딩 호출
[INFO] Step 1 캐시된 결과 반환
[INFO] Step 1 완료 - 구조화된 데이터 길이: 16098자
[INFO] Step 2: JSON 스키마 생성 호출
[INFO] Step 2 캐시된 결과 반환  <--- 🆕
[INFO] Step 2 완료 - Pydantic 검증 성공
[INFO] === Two-step JSON 생성 완료 ===
처리 시간: 0.002초  <--- 🚀 극적 개선
```

---

### Step 8.3: 캐시 관리 전략

#### 8.3.1: 캐시 크기 제한

```python
class GeminiService:
    def __init__(self):
        # ... 기존 코드 ...
        
        # 캐시 설정
        self._cache: Dict[str, str] = {}
        self.max_cache_size = int(os.getenv("MAX_CACHE_SIZE", "100"))  # 최대 100개
        self._cache_access_time: Dict[str, float] = {}  # LRU용
    
    def _add_to_cache(self, key: str, value: str):
        """LRU 캐시 추가 (크기 제한)"""
        import time
        
        # 캐시 크기 초과 시 가장 오래된 항목 제거
        if len(self._cache) >= self.max_cache_size:
            oldest_key = min(self._cache_access_time, key=self._cache_access_time.get)
            del self._cache[oldest_key]
            del self._cache_access_time[oldest_key]
            logger.debug(f"캐시 크기 제한: {oldest_key[:16]}... 제거")
        
        self._cache[key] = value
        self._cache_access_time[key] = time.time()
        logger.debug(f"캐시 추가: {key[:16]}... (총 {len(self._cache)}개)")
```

#### 8.3.2: 캐시 통계 로깅

```python
def get_cache_stats(self) -> dict:
    """캐시 통계 반환"""
    step1_keys = [k for k in self._cache.keys() if k.startswith("grounded_")]
    step2_keys = [k for k in self._cache.keys() if k.startswith("step2_json_")]
    
    return {
        "total_cached": len(self._cache),
        "step1_cached": len(step1_keys),
        "step2_cached": len(step2_keys),
        "max_cache_size": self.max_cache_size,
        "cache_usage_percent": (len(self._cache) / self.max_cache_size) * 100
    }
```

---

### Step 8.4: 구현 체크리스트

**타임아웃 개선**:
- [ ] `GEMINI_TIMEOUT` 180 → 360초 업데이트
- [ ] `STEP1_TIMEOUT`, `STEP2_TIMEOUT` 환경변수 추가
- [ ] `.env.example` 업데이트
- [ ] `README.md` 환경변수 설명 업데이트
- [ ] `_generate_grounded_facts`에 `asyncio.wait_for` 적용
- [ ] `_generate_structured_json`에 `asyncio.wait_for` 적용

**Step 2 캐싱**:
- [ ] `_generate_step2_cache_key` 메서드 추가
- [ ] `_generate_structured_json`에 캐시 조회 로직 추가
- [ ] `_generate_structured_json`에 캐시 저장 로직 추가
- [ ] LRU 캐시 관리 로직 구현 (`_add_to_cache`)
- [ ] 캐시 통계 API 엔드포인트 추가 (`/api/cache-stats`)
- [ ] 캐시 무효화 API 엔드포인트 추가 (`/api/cache-clear`)

**테스트**:
- [ ] 타임아웃 테스트 (대용량 이미지)
- [ ] Step 2 캐싱 효과 테스트 (동일 이미지 재분석)
- [ ] LRU 캐시 제거 테스트 (101개 이상 캐시)
- [ ] 캐시 통계 API 테스트

---

### Step 8.5: 배포 전 성능 검증

**검증 시나리오**:

1. **첫 분석** (캐시 미스):
   - 예상 시간: 200-300초
   - 검증: Step 1, Step 2 모두 API 호출

2. **동일 이미지 재분석** (Step 1 + Step 2 캐시 히트):
   - 예상 시간: <0.01초
   - 검증: 캐시 로그 2개 출력

3. **다른 이미지 분석** (캐시 미스):
   - 예상 시간: 200-300초
   - 검증: 새로운 캐시 키 생성

4. **100개 이상 캐시**:
   - 예상: 가장 오래된 캐시 자동 제거
   - 검증: 로그에서 "캐시 크기 제한" 메시지 확인

---

### Step 8.6: 모니터링 지표

배포 후 다음 지표 추적:

| 지표 | 목표 | 측정 방법 |
|------|------|-----------|
| **평균 응답 시간** | <120초 (캐시 미스) | `/api/analyze` 처리 시간 |
| **캐시 히트율** | >50% | Step 1 + Step 2 캐시 히트 / 전체 요청 |
| **타임아웃 발생률** | <1% | 타임아웃 에러 / 전체 요청 |
| **Step 2 캐시 효과** | >99% 시간 절감 | 캐시 히트 시 응답 시간 |

---

이 문서는 Phase 7의 완전한 구현 가이드입니다. 각 단계를 순서대로 따라가면 버그 없이 Two-step 전략을 성공적으로 통합할 수 있습니다.

**Step 8 추가 개선 사항**은 프로덕션 환경에서의 안정성과 성능을 크게 향상시킵니다.
