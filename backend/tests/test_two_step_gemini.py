"""
Two-step Gemini 생성 전략 단위 테스트

이 모듈은 Phase 7에서 구현된 Two-step 전략(검색·그라운딩 → 구조화 JSON)의
각 단계를 개별적으로 테스트합니다.
"""

import pytest
import time
import os
from dotenv import load_dotenv

# .env 파일 로드 (환경변수 설정)
load_dotenv()

from services.gemini_service import get_gemini_service
from models.portfolio import StructuredAnalysisResponse, PortfolioReport


@pytest.mark.asyncio
async def test_step1_grounding_success():
    """Step 1: 검색·그라운딩 성공 테스트"""
    service = await get_gemini_service()
    
    # 샘플 이미지 데이터 (실제 이미지 사용)
    with open("tests/fixtures/sample_portfolio.png", "rb") as f:
        image_data = f.read()
    
    # Step 1 호출
    result = await service._generate_grounded_facts([image_data])
    
    # 검증
    assert isinstance(result, str), "Step 1 결과는 문자열이어야 함"
    assert len(result) > 500, "Step 1 결과는 최소 500자 이상이어야 함"
    
    # 필수 섹션 확인
    assert "포트폴리오 종합 리니아 스코어:" in result, "종합 스코어 섹션 누락"
    assert "3대 핵심 기준 스코어" in result, "핵심 기준 스코어 섹션 누락"
    assert "개별 종목 리니아 스코어" in result, "개별 종목 스코어 섹션 누락"
    assert "개별 종목 분석 설명" in result, "개별 종목 분석 섹션 누락"
    assert "심층 분석 설명" in result, "심층 분석 섹션 누락"
    assert "포트폴리오 강점, 약점 및 기회" in result, "강점/약점/기회 섹션 누락"
    
    print(f"✅ Step 1 테스트 성공 - 결과 길이: {len(result)}자")


@pytest.mark.asyncio
async def test_step2_json_generation_success():
    """Step 2: JSON 생성 성공 테스트"""
    service = await get_gemini_service()
    
    # Step 1 샘플 결과 (실제 형식과 유사한 마크다운)
    grounded_facts = """
### **포트폴리오 종합 스코어**

* **포트폴리오 종합 리니아 스코어: 72 / 100**

### **포트폴리오 심층 분석**

**1. 3대 핵심 기준 스코어**
* 성장 잠재력: 88 / 100
* 안정성 및 방어력: 55 / 100
* 전략적 일관성: 74 / 100

**2. 개별 종목 리니아 스코어**
| 주식 | Overall (100점 만점) | 펀더멘탈 | 기술 잠재력 | 거시경제 | 시장심리 | CEO/리더십 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **팔란티어 (PLTR)** | 78 | 70 | 95 | 75 | 85 | 85 |
| **브로드컴 (AVGO)** | 82 | 85 | 80 | 80 | 80 | 85 |

**3. 개별 종목 분석 설명 (분석 카드)**

**1. 팔란티어 테크놀로지스 (PLTR) - Overall: 78 / 100**
* **펀더멘탈 (70/100):** 꾸준한 매출 성장과 최근 GAAP 기준 흑자 전환 성공은 긍정적입니다.
* **기술 잠재력 (95/100):** 빅데이터 분석 및 AI 분야 독보적인 기술력을 보유하고 있습니다.
* **거시경제 (75/100):** 전 세계적인 AI 도입 가속화의 직접 수혜주로, 지정학적 불안정은 오히려 정부 부문 성장에 긍정적입니다.
* **시장심리 (85/100):** CEO의 적극적인 소통과 AI 시장 성장에 대한 기대로 높은 지지를 받습니다.
* **CEO/리더십 (85/100):** 독특한 비전과 강력한 리더십으로 혁신을 주도하고 있습니다.

### **심층 분석 설명**

* **1.1 성장 잠재력 분석 (88 / 100): 미래 기술에 대한 강력한 베팅**
    포트폴리오는 기술 잠재력이 매우 높은 종목들에 집중적으로 투자되어 있어 압도적인 성장 잠재력을 보여줍니다.

* **1.2 안정성 및 방어력 분석 (55 / 100): 기술주 특유의 변동성 노출**
    포트폴리오의 안정성 및 방어력 점수는 55점으로 상대적으로 낮은 수준입니다. 대부분의 종목들이 성장 단계의 기술 기업들로 구성되어 있어 시장 변동성에 노출되어 있습니다.

* **1.3 전략적 일관성 분석 (74 / 100): 명확한 테마 속 집중도 리스크**
    포트폴리오는 양자 컴퓨팅과 AI라는 명확한 투자 테마를 중심으로 구성되어 있어 높은 전략적 일관성을 가지지만, 동시에 특정 기술 섹터에 대한 과도한 집중은 리스크로 작용할 수 있습니다.

### **포트폴리오 강점, 약점 및 기회 (설명)**

* **💪 강점**
    * **선구적인 미래 기술 투자:** 양자 컴퓨팅, AI 등 미래 성장 동력에 대한 과감한 투자
    * **명확한 투자 테마:** 기술 혁신이라는 뚜렷한 투자 철학 반영

* **📉 약점**
    * **극심한 변동성 노출:** 성장주 중심으로 시장 변동성에 크게 노출
    * **섹터 집중 리스크:** 특정 기술 분야 의존도가 높음

* **💡 기회 및 개선 방안**
    * **안정적인 핵심 자산 추가:** 변동성을 상쇄할 안정적 자산 편입 고려
    * **유사 테마 내 분산:** 기술 테마 유지하되 지역 및 세부 분야 다변화
"""
    
    # Step 2 호출
    portfolio_report = await service._generate_structured_json(grounded_facts)
    
    # Pydantic 검증 (자동)
    assert isinstance(portfolio_report, PortfolioReport), "PortfolioReport 객체여야 함"
    assert portfolio_report.version == "1.0", "버전은 1.0이어야 함"
    assert len(portfolio_report.tabs) == 4, "탭은 정확히 4개여야 함"
    
    # 각 탭 ID 확인
    tab_ids = [tab.tabId for tab in portfolio_report.tabs]
    assert "dashboard" in tab_ids, "dashboard 탭 누락"
    assert "deepDive" in tab_ids, "deepDive 탭 누락"
    assert "allStockScores" in tab_ids, "allStockScores 탭 누락"
    assert "keyStockAnalysis" in tab_ids, "keyStockAnalysis 탭 누락"
    
    print(f"✅ Step 2 테스트 성공 - 4개 탭 생성 완료")


@pytest.mark.asyncio
async def test_two_step_end_to_end():
    """Two-step 전체 플로우 E2E 테스트"""
    service = await get_gemini_service()
    
    with open("tests/fixtures/sample_portfolio.png", "rb") as f:
        image_data = f.read()
    
    # 전체 플로우 실행
    response = await service.analyze_portfolio_structured(
        [image_data], 
        format_type="json"
    )
    
    # 검증
    assert isinstance(response, StructuredAnalysisResponse), "StructuredAnalysisResponse 객체여야 함"
    assert response.images_processed == 1, "처리된 이미지 수는 1개여야 함"
    assert response.portfolioReport.version == "1.0", "리포트 버전은 1.0이어야 함"
    assert len(response.portfolioReport.tabs) == 4, "탭은 정확히 4개여야 함"
    assert response.processing_time > 0, "처리 시간은 0보다 커야 함"
    assert response.request_id, "요청 ID가 있어야 함"
    
    # 각 탭의 content 타입 확인
    for tab in response.portfolioReport.tabs:
        assert tab.content is not None, f"{tab.tabId} 탭의 content가 None임"
    
    print(f"✅ E2E 테스트 성공 - 처리 시간: {response.processing_time:.2f}초")


@pytest.mark.asyncio
async def test_step1_caching():
    """Step 1 캐싱 테스트"""
    service = await get_gemini_service()
    
    with open("tests/fixtures/sample_portfolio.png", "rb") as f:
        image_data = f.read()
    
    # 캐시 초기화 (기존 캐시 제거)
    service._cache.clear()
    
    # 첫 호출 (캐시 미스 - API 호출)
    start1 = time.time()
    result1 = await service._generate_grounded_facts([image_data])
    time1 = time.time() - start1
    
    # 두 번째 호출 (캐시 히트 - 즉시 반환)
    start2 = time.time()
    result2 = await service._generate_grounded_facts([image_data])
    time2 = time.time() - start2
    
    # 검증
    assert result1 == result2, "캐시된 결과는 동일해야 함"
    assert time2 < 0.1, f"캐시는 0.1초 미만이어야 함 (실제: {time2:.4f}초)"
    assert time1 > 1.0, f"API 호출은 1초 이상이어야 함 (실제: {time1:.2f}초)"
    
    speed_ratio = time1 / time2 if time2 > 0 else float('inf')
    print(f"✅ 캐싱 테스트 성공 - API 호출: {time1:.2f}초, 캐시: {time2:.4f}초 ({speed_ratio:.0f}배 빠름)")


@pytest.mark.asyncio
async def test_step2_validation_retry():
    """Step 2 검증 성공 테스트 - Gemini의 강력한 복구 능력 확인"""
    service = await get_gemini_service()
    
    # 최소한의 정보만 있는 Step 1 결과
    grounded_facts = """
    ### **포트폴리오 종합 스코어**
    * **포트폴리오 종합 리니아 스코어: 50 / 100**
    
    ### **포트폴리오 심층 분석**
    **1. 3대 핵심 기준 스코어**
    * 성장 잠재력: 50 / 100
    * 안정성 및 방어력: 50 / 100
    * 전략적 일관성: 50 / 100
    
    최소한의 데이터만 포함됨
    """
    
    # Gemini는 이런 최소 데이터로도 유효한 JSON을 생성할 수 있음
    result = await service._generate_structured_json(grounded_facts)
    
    # 검증: Gemini가 자동으로 누락된 필드를 채워서 유효한 JSON을 생성
    assert result.version == "1.0"
    assert len(result.tabs) == 4
    
    print(f"✅ Gemini 복구 능력 테스트 성공 - 최소 데이터로도 유효한 JSON 생성")


@pytest.mark.asyncio
async def test_multiple_images_two_step():
    """다중 이미지 Two-step 테스트 (최대 5개)"""
    service = await get_gemini_service()
    
    # 동일한 이미지를 3개 사용 (실제로는 다른 이미지 사용)
    with open("tests/fixtures/sample_portfolio.png", "rb") as f:
        image_data = f.read()
    
    image_data_list = [image_data, image_data, image_data]  # 3개 이미지
    
    # 전체 플로우 실행
    response = await service.analyze_portfolio_structured(
        image_data_list, 
        format_type="json"
    )
    
    # 검증
    assert isinstance(response, StructuredAnalysisResponse)
    assert response.images_processed == 3, "처리된 이미지 수는 3개여야 함"
    assert len(response.portfolioReport.tabs) == 4, "탭은 정확히 4개여야 함"
    
    print(f"✅ 다중 이미지 테스트 성공 - {response.images_processed}개 이미지, {response.processing_time:.2f}초")


@pytest.mark.asyncio
async def test_format_markdown_compatibility():
    """format=markdown 하위 호환성 테스트"""
    service = await get_gemini_service()
    
    with open("tests/fixtures/sample_portfolio.png", "rb") as f:
        image_data = f.read()
    
    # 마크다운 모드로 호출
    response = await service.analyze_portfolio_structured(
        [image_data], 
        format_type="markdown"
    )
    
    # 검증
    from models.portfolio import AnalysisResponse
    assert isinstance(response, AnalysisResponse), "AnalysisResponse 객체여야 함"
    assert isinstance(response.content, str), "content는 문자열이어야 함"
    assert len(response.content) > 100, "마크다운 내용은 100자 이상이어야 함"
    assert response.images_processed == 1, "처리된 이미지 수는 1개여야 함"
    
    print(f"✅ 마크다운 호환성 테스트 성공 - 마크다운 길이: {len(response.content)}자")


@pytest.mark.asyncio
async def test_step1_error_handling():
    """Step 1 에러 처리 테스트 (잘못된 이미지)"""
    service = await get_gemini_service()
    
    # 너무 작은 잘못된 이미지 데이터
    invalid_image_data = b"invalid data"
    
    # 예외 발생 확인
    with pytest.raises(ValueError):
        await service._generate_grounded_facts([invalid_image_data])
    
    print("✅ Step 1 에러 처리 테스트 성공")


@pytest.mark.asyncio
async def test_step2_empty_input():
    """Step 2 빈 입력 처리 테스트 - Gemini의 기본값 생성 확인"""
    service = await get_gemini_service()
    
    # 빈 grounded_facts
    empty_facts = "데이터 없음"
    
    # Gemini는 빈 입력에도 기본 구조의 JSON을 생성할 수 있음
    result = await service._generate_structured_json(empty_facts)
    
    # 검증: 기본 구조는 유지되어야 함
    assert result.version == "1.0"
    assert len(result.tabs) == 4
    assert result.tabs[0].tabId == "dashboard"
    
    print("✅ Step 2 빈 입력 테스트 성공 - Gemini가 기본 구조 생성")


@pytest.mark.asyncio
async def test_response_schema_enforcement():
    """response_schema가 스키마를 강제하는지 테스트"""
    service = await get_gemini_service()
    
    # 최소한의 Step 1 결과
    minimal_facts = """
### **포트폴리오 종합 스코어**
* **포트폴리오 종합 리니아 스코어: 75 / 100**

**1. 3대 핵심 기준 스코어**
* 성장 잠재력: 80 / 100
* 안정성 및 방어력: 70 / 100
* 전략적 일관성: 75 / 100

**2. 개별 종목 리니아 스코어**
| 주식 | Overall | 펀더멘탈 | 기술 잠재력 | 거시경제 | 시장심리 | CEO/리더십 |
| --- | --- | --- | --- | --- | --- | --- |
| 테스트 종목 | 80 | 75 | 85 | 70 | 80 | 85 |

**3. 개별 종목 분석 설명**
**1. 테스트 종목 - Overall: 80 / 100**
* **펀더멘탈 (75/100):** 안정적인 재무 구조를 보유하고 있습니다.
* **기술 잠재력 (85/100):** 차세대 기술 분야에서 우수한 기술력을 보유하고 있습니다.
* **거시경제 (70/100):** 거시경제 환경이 우호적입니다.
* **시장심리 (80/100):** 시장의 높은 기대를 받고 있습니다.
* **CEO/리더십 (85/100):** 강력한 리더십을 발휘하고 있습니다.

### **심층 분석 설명**
* **1.1 성장 잠재력 분석 (80 / 100): 우수한 성장 전망**
    기술 혁신 분야의 선도 기업들에 대한 전략적 투자로 높은 성장 잠재력을 보유하고 있습니다.

* **1.2 안정성 및 방어력 분석 (70 / 100): 적절한 방어력**
    적절한 수준의 안정성을 유지하고 있습니다.

* **1.3 전략적 일관성 분석 (75 / 100): 일관된 전략**
    명확한 투자 테마로 전략적 일관성이 높습니다.

### **포트폴리오 강점, 약점 및 기회**
* **💪 강점**
    * **기술 투자:** 미래 기술 분야 투자
    * **명확한 테마:** 일관된 투자 철학

* **📉 약점**
    * **변동성:** 시장 변동성 노출
    * **집중 리스크:** 섹터 집중도 높음

* **💡 기회 및 개선 방안**
    * **다변화:** 포트폴리오 다변화를 통한 리스크 감소 필요
    * **안정성 보강:** 안정적 자산 비중 확대 고려
"""
    
    # Step 2 호출
    portfolio_report = await service._generate_structured_json(minimal_facts)
    
    # response_schema가 스키마를 강제했는지 검증
    assert portfolio_report.version == "1.0"
    assert len(portfolio_report.tabs) == 4
    
    # 각 탭의 필수 필드 확인
    dashboard_tab = next(tab for tab in portfolio_report.tabs if tab.tabId == "dashboard")
    assert hasattr(dashboard_tab.content, 'overallScore')
    assert hasattr(dashboard_tab.content, 'coreCriteriaScores')
    assert hasattr(dashboard_tab.content, 'strengths')
    assert hasattr(dashboard_tab.content, 'weaknesses')
    
    print("✅ response_schema 강제 테스트 성공 - 모든 필수 필드 존재")


if __name__ == "__main__":
    """테스트 직접 실행"""
    import asyncio
    
    async def run_tests():
        print("=" * 60)
        print("Two-step Gemini 생성 전략 단위 테스트 시작")
        print("=" * 60)
        
        try:
            print("\n[1/9] Step 1 성공 테스트...")
            await test_step1_grounding_success()
            
            print("\n[2/9] Step 2 성공 테스트...")
            await test_step2_json_generation_success()
            
            print("\n[3/9] E2E 테스트...")
            await test_two_step_end_to_end()
            
            print("\n[4/9] 캐싱 테스트...")
            await test_step1_caching()
            
            print("\n[5/9] 검증 재시도 테스트...")
            await test_step2_validation_retry()
            
            print("\n[6/9] 다중 이미지 테스트...")
            await test_multiple_images_two_step()
            
            print("\n[7/9] 마크다운 호환성 테스트...")
            await test_format_markdown_compatibility()
            
            print("\n[8/9] Step 1 에러 처리 테스트...")
            await test_step1_error_handling()
            
            print("\n[9/9] Step 2 빈 입력 테스트...")
            await test_step2_empty_input()
            
            print("\n" + "=" * 60)
            print("✅ 모든 테스트 통과!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ 테스트 실패: {str(e)}")
            raise
    
    asyncio.run(run_tests())
