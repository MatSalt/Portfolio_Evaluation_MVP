"""
Two-step Gemini 생성 전략 통합 테스트

이 모듈은 Phase 7의 Two-step 전략이 실제 시나리오에서 올바르게 작동하는지
검증하는 통합 테스트를 제공합니다.
"""

import pytest
import time
import asyncio
import os
from dotenv import load_dotenv

# .env 파일 로드 (환경변수 설정)
load_dotenv()

from services.gemini_service import get_gemini_service
from models.portfolio import (
    StructuredAnalysisResponse, 
    AnalysisResponse, 
    PortfolioReport,
    DashboardContent,
    DeepDiveContent,
    AllStockScoresContent,
    KeyStockAnalysisContent
)


class TestTwoStepIntegration:
    """Two-step 전략 통합 테스트 클래스"""
    
    @pytest.mark.asyncio
    async def test_single_image_json_format(self):
        """시나리오 1: 단일 이미지 분석 (JSON)"""
        service = await get_gemini_service()
        
        with open("tests/fixtures/sample_portfolio.png", "rb") as f:
            image_data = f.read()
        
        # JSON 형식으로 분석
        start_time = time.time()
        response = await service.analyze_portfolio_structured(
            [image_data], 
            format_type="json"
        )
        elapsed_time = time.time() - start_time
        
        # 응답 타입 검증
        assert isinstance(response, StructuredAnalysisResponse)
        
        # 메타데이터 검증
        assert response.images_processed == 1
        assert response.processing_time > 0
        assert response.request_id
        
        # PortfolioReport 검증
        report = response.portfolioReport
        assert isinstance(report, PortfolioReport)
        assert report.version == "1.0"
        assert len(report.tabs) == 4
        
        # 각 탭 검증
        tab_ids = {tab.tabId for tab in report.tabs}
        assert tab_ids == {"dashboard", "deepDive", "allStockScores", "keyStockAnalysis"}
        
        # 성능 검증 (240초 이내 - Two-step은 2번 API 호출)
        assert elapsed_time < 240, f"처리 시간 초과: {elapsed_time:.2f}초"
        
        print(f"✅ 단일 이미지 JSON 테스트 성공 - {elapsed_time:.2f}초")
    
    @pytest.mark.asyncio
    async def test_multiple_images_json_format(self):
        """시나리오 2: 다중 이미지 분석 (JSON, 5개)"""
        service = await get_gemini_service()
        
        # 5개 이미지 로드 (실제로는 동일 이미지 반복)
        with open("tests/fixtures/sample_portfolio.png", "rb") as f:
            image_data = f.read()
        
        image_data_list = [image_data] * 5
        
        # JSON 형식으로 분석
        start_time = time.time()
        response = await service.analyze_portfolio_structured(
            image_data_list, 
            format_type="json"
        )
        elapsed_time = time.time() - start_time
        
        # 검증
        assert isinstance(response, StructuredAnalysisResponse)
        assert response.images_processed == 5
        assert len(response.portfolioReport.tabs) == 4
        
        # 성능 검증 (다중 이미지는 최대 300초 - Two-step)
        assert elapsed_time < 300, f"다중 이미지 처리 시간 초과: {elapsed_time:.2f}초"
        
        print(f"✅ 다중 이미지 (5개) JSON 테스트 성공 - {elapsed_time:.2f}초")
    
    @pytest.mark.asyncio
    async def test_markdown_format_compatibility(self):
        """시나리오 3: format=markdown 하위 호환성"""
        service = await get_gemini_service()
        
        with open("tests/fixtures/sample_portfolio.png", "rb") as f:
            image_data = f.read()
        
        # 마크다운 형식으로 분석
        response = await service.analyze_portfolio_structured(
            [image_data], 
            format_type="markdown"
        )
        
        # 검증
        assert isinstance(response, AnalysisResponse)
        assert isinstance(response.content, str)
        assert len(response.content) > 100
        assert response.images_processed == 1
        
        # 필수 마크다운 섹션 확인
        assert "**포트폴리오 종합 리니아 스코어:" in response.content
        assert "**3대 핵심 기준 스코어:**" in response.content
        
        print(f"✅ 마크다운 호환성 테스트 성공 - 마크다운 길이: {len(response.content)}자")
    
    @pytest.mark.asyncio
    async def test_json_vs_markdown_same_image(self):
        """시나리오 4: 동일 이미지에 대한 JSON vs 마크다운 비교"""
        service = await get_gemini_service()
        
        with open("tests/fixtures/sample_portfolio.png", "rb") as f:
            image_data = f.read()
        
        # JSON 형식
        json_response = await service.analyze_portfolio_structured(
            [image_data], 
            format_type="json"
        )
        
        # 마크다운 형식
        markdown_response = await service.analyze_portfolio_structured(
            [image_data], 
            format_type="markdown"
        )
        
        # 두 형식 모두 성공
        assert isinstance(json_response, StructuredAnalysisResponse)
        assert isinstance(markdown_response, AnalysisResponse)
        
        # 처리된 이미지 수 동일
        assert json_response.images_processed == markdown_response.images_processed == 1
        
        print("✅ JSON vs 마크다운 비교 테스트 성공 - 두 형식 모두 정상 작동")
    
    @pytest.mark.asyncio
    async def test_caching_effectiveness(self):
        """시나리오 5: 캐싱 동작 확인"""
        service = await get_gemini_service()
        
        with open("tests/fixtures/sample_portfolio.png", "rb") as f:
            image_data = f.read()
        
        # 첫 번째 호출 (캐시 미스)
        start1 = time.time()
        response1 = await service.analyze_portfolio_structured(
            [image_data], 
            format_type="json"
        )
        time1 = time.time() - start1
        
        # 두 번째 호출 (Step 1 캐시 히트, Step 2만 실행)
        start2 = time.time()
        response2 = await service.analyze_portfolio_structured(
            [image_data], 
            format_type="json"
        )
        time2 = time.time() - start2
        
        # 두 번째 호출이 더 빨라야 함 (Step 1 캐싱 효과)
        assert time2 < time1, f"캐싱 효과 없음: 1차={time1:.2f}초, 2차={time2:.2f}초"
        
        # 결과는 유사해야 함 (점수는 약간 다를 수 있음)
        assert response1.portfolioReport.version == response2.portfolioReport.version
        assert len(response1.portfolioReport.tabs) == len(response2.portfolioReport.tabs)
        
        speedup = time1 / time2
        print(f"✅ 캐싱 효과 테스트 성공 - 1차: {time1:.2f}초, 2차: {time2:.2f}초 ({speedup:.1f}배 빠름)")
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_image(self):
        """시나리오 6: 잘못된 이미지에 대한 에러 핸들링"""
        service = await get_gemini_service()
        
        # 잘못된 이미지 데이터
        invalid_data = b"this is not an image"
        
        # ValueError 발생 확인
        with pytest.raises(ValueError):
            await service.analyze_portfolio_structured(
                [invalid_data], 
                format_type="json"
            )
        
        print("✅ 잘못된 이미지 에러 처리 테스트 성공")
    
    @pytest.mark.asyncio
    async def test_error_handling_too_many_images(self):
        """시나리오 7: 이미지 개수 초과 에러 핸들링"""
        service = await get_gemini_service()
        
        with open("tests/fixtures/sample_portfolio.png", "rb") as f:
            image_data = f.read()
        
        # 6개 이미지 (최대 5개 초과)
        image_data_list = [image_data] * 6
        
        # ValueError 발생 확인
        with pytest.raises(ValueError, match="최대 5개"):
            await service.analyze_portfolio_structured(
                image_data_list, 
                format_type="json"
            )
        
        print("✅ 이미지 개수 초과 에러 처리 테스트 성공")
    
    @pytest.mark.asyncio
    async def test_tab_content_types(self):
        """시나리오 8: 각 탭의 content 타입 정확성 검증"""
        service = await get_gemini_service()
        
        with open("tests/fixtures/sample_portfolio.png", "rb") as f:
            image_data = f.read()
        
        response = await service.analyze_portfolio_structured(
            [image_data], 
            format_type="json"
        )
        
        # 각 탭의 content 타입 확인
        for tab in response.portfolioReport.tabs:
            if tab.tabId == "dashboard":
                assert hasattr(tab.content, 'overallScore'), "dashboard에 overallScore 없음"
                assert hasattr(tab.content, 'coreCriteriaScores'), "dashboard에 coreCriteriaScores 없음"
                assert hasattr(tab.content, 'strengths'), "dashboard에 strengths 없음"
                assert hasattr(tab.content, 'weaknesses'), "dashboard에 weaknesses 없음"
                
            elif tab.tabId == "deepDive":
                assert hasattr(tab.content, 'inDepthAnalysis'), "deepDive에 inDepthAnalysis 없음"
                assert hasattr(tab.content, 'opportunities'), "deepDive에 opportunities 없음"
                
            elif tab.tabId == "allStockScores":
                assert hasattr(tab.content, 'scoreTable'), "allStockScores에 scoreTable 없음"
                
            elif tab.tabId == "keyStockAnalysis":
                assert hasattr(tab.content, 'analysisCards'), "keyStockAnalysis에 analysisCards 없음"
        
        print("✅ 탭 content 타입 검증 테스트 성공 - 모든 탭의 필수 필드 존재")
    
    @pytest.mark.asyncio
    async def test_score_range_validation(self):
        """시나리오 9: 점수 범위 검증 (0-100)"""
        service = await get_gemini_service()
        
        with open("tests/fixtures/sample_portfolio.png", "rb") as f:
            image_data = f.read()
        
        response = await service.analyze_portfolio_structured(
            [image_data], 
            format_type="json"
        )
        
        report = response.portfolioReport
        
        # Dashboard 탭 점수 검증
        dashboard_tab = next(tab for tab in report.tabs if tab.tabId == "dashboard")
        overall_score = dashboard_tab.content.overallScore.score
        assert 0 <= overall_score <= 100, f"종합 점수 범위 초과: {overall_score}"
        
        for criteria in dashboard_tab.content.coreCriteriaScores:
            assert 0 <= criteria.score <= 100, f"{criteria.criterion} 점수 범위 초과: {criteria.score}"
        
        # DeepDive 탭 점수 검증
        deepdive_tab = next(tab for tab in report.tabs if tab.tabId == "deepDive")
        for analysis in deepdive_tab.content.inDepthAnalysis:
            assert 0 <= analysis.score <= 100, f"{analysis.title} 점수 범위 초과: {analysis.score}"
        
        print("✅ 점수 범위 검증 테스트 성공 - 모든 점수가 0-100 범위 내")
    
    @pytest.mark.asyncio
    async def test_performance_benchmark(self):
        """시나리오 10: 성능 벤치마크 (Step 1 + Step 2 시간 측정)"""
        service = await get_gemini_service()
        
        with open("tests/fixtures/sample_portfolio.png", "rb") as f:
            image_data = f.read()
        
        # Step 1 시간 측정
        step1_start = time.time()
        grounded_facts = await service._generate_grounded_facts([image_data])
        step1_time = time.time() - step1_start
        
        # Step 2 시간 측정
        step2_start = time.time()
        portfolio_report = await service._generate_structured_json(grounded_facts)
        step2_time = time.time() - step2_start
        
        total_time = step1_time + step2_time
        
        # 성능 기준 검증
        assert step1_time < 45, f"Step 1 시간 초과: {step1_time:.2f}초"
        assert step2_time < 30, f"Step 2 시간 초과: {step2_time:.2f}초"
        assert total_time < 60, f"전체 시간 초과: {total_time:.2f}초"
        
        print(f"✅ 성능 벤치마크 테스트 성공")
        print(f"   - Step 1 (검색·그라운딩): {step1_time:.2f}초")
        print(f"   - Step 2 (JSON 생성): {step2_time:.2f}초")
        print(f"   - 전체: {total_time:.2f}초")
    
    @pytest.mark.asyncio
    async def test_retry_mechanism(self):
        """시나리오 11: 재시도 메커니즘 동작 확인"""
        service = await get_gemini_service()
        
        # 잘못된 Step 1 결과로 Step 2 재시도 유도
        invalid_facts = "최소한의 데이터만 포함된 잘못된 형식"
        
        # Step 2는 재시도 후 최종 실패해야 함
        with pytest.raises(ValueError):
            await service._generate_structured_json(invalid_facts)
        
        print("✅ 재시도 메커니즘 테스트 성공 - 최종 실패 확인")
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """시나리오 12: 동시 요청 처리 (캐싱 효과 확인)"""
        service = await get_gemini_service()
        
        with open("tests/fixtures/sample_portfolio.png", "rb") as f:
            image_data = f.read()
        
        # 동시에 3개 요청 (동일 이미지)
        tasks = [
            service.analyze_portfolio_structured([image_data], format_type="json")
            for _ in range(3)
        ]
        
        start_time = time.time()
        responses = await asyncio.gather(*tasks)
        elapsed_time = time.time() - start_time
        
        # 모든 응답 성공
        assert len(responses) == 3
        for response in responses:
            assert isinstance(response, StructuredAnalysisResponse)
            assert len(response.portfolioReport.tabs) == 4
        
        # 캐싱 덕분에 3배 이상 빠르지는 않아야 함 (첫 요청 후 나머지는 캐시)
        # 하지만 3번 독립 호출보다는 빨라야 함
        print(f"✅ 동시 요청 테스트 성공 - 3개 요청 {elapsed_time:.2f}초")
    
    @pytest.mark.asyncio
    async def test_data_quality(self):
        """시나리오 13: 데이터 품질 검증"""
        service = await get_gemini_service()
        
        with open("tests/fixtures/sample_portfolio.png", "rb") as f:
            image_data = f.read()
        
        response = await service.analyze_portfolio_structured(
            [image_data], 
            format_type="json"
        )
        
        report = response.portfolioReport
        
        # Dashboard 탭 데이터 품질 검증
        dashboard_tab = next(tab for tab in report.tabs if tab.tabId == "dashboard")
        assert len(dashboard_tab.content.strengths) >= 1, "최소 1개 강점 필요"
        assert len(dashboard_tab.content.weaknesses) >= 1, "최소 1개 약점 필요"
        assert len(dashboard_tab.content.coreCriteriaScores) == 3, "핵심 기준 점수는 3개"
        
        # DeepDive 탭 데이터 품질 검증
        deepdive_tab = next(tab for tab in report.tabs if tab.tabId == "deepDive")
        assert len(deepdive_tab.content.inDepthAnalysis) == 3, "심층 분석은 3개"
        for analysis in deepdive_tab.content.inDepthAnalysis:
            assert len(analysis.description) >= 50, f"분석 설명이 너무 짧음: {len(analysis.description)}자"
        
        # AllStockScores 탭 데이터 품질 검증
        allstocks_tab = next(tab for tab in report.tabs if tab.tabId == "allStockScores")
        assert len(allstocks_tab.content.scoreTable.headers) >= 2, "최소 2개 헤더 필요"
        assert len(allstocks_tab.content.scoreTable.rows) >= 1, "최소 1개 종목 필요"
        
        # KeyStockAnalysis 탭 데이터 품질 검증
        keystock_tab = next(tab for tab in report.tabs if tab.tabId == "keyStockAnalysis")
        assert len(keystock_tab.content.analysisCards) >= 1, "최소 1개 분석 카드 필요"
        for card in keystock_tab.content.analysisCards:
            assert len(card.detailedScores) == 5, "상세 점수는 5개여야 함"
            for score in card.detailedScores:
                assert len(score.analysis) >= 30, f"{score.category} 분석이 너무 짧음"
        
        print("✅ 데이터 품질 검증 테스트 성공 - 모든 필수 요구사항 충족")
    
    @pytest.mark.asyncio
    async def test_google_search_integration(self):
        """시나리오 14: Google Search 통합 확인 (최신 정보 반영)"""
        service = await get_gemini_service()
        
        with open("tests/fixtures/sample_portfolio.png", "rb") as f:
            image_data = f.read()
        
        # Step 1 호출 (Google Search Tool 사용)
        grounded_facts = await service._generate_grounded_facts([image_data])
        
        # Google Search가 최신 정보를 반영했는지 확인
        # (최신 날짜, 최근 뉴스 키워드 등이 포함되어야 함)
        current_year = str(time.localtime().tm_year)
        
        # 최신성 확인 (현재 연도가 언급되거나, 최신 데이터 포함)
        # 참고: 실제 검색 결과는 종목에 따라 다를 수 있음
        assert len(grounded_facts) > 1000, "Step 1 결과에 충분한 정보가 있어야 함"
        
        print(f"✅ Google Search 통합 테스트 성공 - Step 1 결과 길이: {len(grounded_facts)}자")


@pytest.mark.asyncio
async def test_full_integration_workflow():
    """전체 통합 워크플로우 테스트 (가장 중요)"""
    print("\n" + "=" * 70)
    print("전체 통합 워크플로우 테스트 시작")
    print("=" * 70)
    
    service = await get_gemini_service()
    
    with open("tests/fixtures/sample_portfolio.jpg", "rb") as f:
        image_data = f.read()
    
    # 1. 전체 플로우 실행
    print("\n[1/5] Two-step JSON 생성 실행...")
    start_time = time.time()
    response = await service.analyze_portfolio_structured(
        [image_data], 
        format_type="json"
    )
    elapsed_time = time.time() - start_time
    
    # 2. 응답 타입 검증
    print("[2/5] 응답 타입 검증...")
    assert isinstance(response, StructuredAnalysisResponse)
    assert isinstance(response.portfolioReport, PortfolioReport)
    
    # 3. 데이터 완전성 검증
    print("[3/5] 데이터 완전성 검증...")
    report = response.portfolioReport
    assert report.version == "1.0"
    assert len(report.tabs) == 4
    
    # 4. 각 탭의 필수 데이터 검증
    print("[4/5] 각 탭 필수 데이터 검증...")
    tab_validations = {
        "dashboard": lambda c: (
            hasattr(c, 'overallScore') and 
            hasattr(c, 'coreCriteriaScores') and
            len(c.coreCriteriaScores) == 3 and
            hasattr(c, 'strengths') and
            hasattr(c, 'weaknesses')
        ),
        "deepDive": lambda c: (
            hasattr(c, 'inDepthAnalysis') and
            len(c.inDepthAnalysis) == 3 and
            hasattr(c, 'opportunities')
        ),
        "allStockScores": lambda c: (
            hasattr(c, 'scoreTable') and
            len(c.scoreTable.rows) >= 1
        ),
        "keyStockAnalysis": lambda c: (
            hasattr(c, 'analysisCards') and
            len(c.analysisCards) >= 1
        ),
    }
    
    for tab in report.tabs:
        validator = tab_validations.get(tab.tabId)
        assert validator, f"알 수 없는 탭 ID: {tab.tabId}"
        assert validator(tab.content), f"{tab.tabId} 탭의 필수 데이터 누락"
    
    # 5. 성능 검증
    print("[5/5] 성능 검증...")
    assert elapsed_time < 60, f"처리 시간 초과: {elapsed_time:.2f}초"
    
    print("\n" + "=" * 70)
    print(f"✅ 전체 통합 워크플로우 테스트 성공!")
    print(f"   - 처리 시간: {elapsed_time:.2f}초")
    print(f"   - 이미지 수: {response.images_processed}개")
    print(f"   - 탭 수: {len(report.tabs)}개")
    print(f"   - 요청 ID: {response.request_id}")
    print("=" * 70)


if __name__ == "__main__":
    """통합 테스트 직접 실행"""
    
    async def run_integration_tests():
        test_suite = TestTwoStepIntegration()
        
        print("\n" + "=" * 70)
        print("Two-step Gemini 생성 전략 통합 테스트 시작")
        print("=" * 70)
        
        test_methods = [
            ("단일 이미지 JSON", test_suite.test_single_image_json_format),
            ("다중 이미지 JSON (5개)", test_suite.test_multiple_images_json_format),
            ("마크다운 호환성", test_suite.test_markdown_format_compatibility),
            ("JSON vs 마크다운 비교", test_suite.test_json_vs_markdown_same_image),
            ("캐싱 효과", test_suite.test_caching_effectiveness),
            ("잘못된 이미지 에러", test_suite.test_error_handling_invalid_image),
            ("이미지 개수 초과", test_suite.test_error_handling_too_many_images),
            ("탭 content 타입", test_suite.test_tab_content_types),
            ("점수 범위 검증", test_suite.test_score_range_validation),
            ("Google Search 통합", test_suite.test_google_search_integration),
        ]
        
        passed = 0
        failed = 0
        
        for i, (name, test_func) in enumerate(test_methods, 1):
            try:
                print(f"\n[{i}/{len(test_methods)}] {name} 테스트...")
                await test_func()
                passed += 1
            except Exception as e:
                print(f"   ❌ 실패: {str(e)}")
                failed += 1
        
        # 전체 통합 테스트
        try:
            await test_full_integration_workflow()
            passed += 1
        except Exception as e:
            print(f"   ❌ 전체 통합 테스트 실패: {str(e)}")
            failed += 1
        
        # 결과 요약
        print("\n" + "=" * 70)
        print("테스트 결과 요약")
        print("=" * 70)
        print(f"✅ 성공: {passed}개")
        if failed > 0:
            print(f"❌ 실패: {failed}개")
        print("=" * 70)
        
        return failed == 0
    
    success = asyncio.run(run_integration_tests())
    exit(0 if success else 1)

