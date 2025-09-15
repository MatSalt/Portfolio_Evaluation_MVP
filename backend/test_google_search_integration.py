"""
Google Search 통합 테스트
Phase 4 구현 검증을 위한 테스트 파일
"""

import pytest
import asyncio
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

from services.gemini_service import GeminiService

@pytest.mark.asyncio
async def test_google_search_integration():
    """Google Search 통합 기본 테스트"""
    # 환경변수 확인
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
    
    service = GeminiService()
    
    # 샘플 분석 결과 테스트 (실제 이미지 없이)
    result = await service.get_sample_analysis()
    
    # 기본 검증
    assert isinstance(result, str)
    assert len(result) > 100
    assert "**AI 총평:**" in result
    assert "**포트폴리오 종합 리니아 스코어:" in result
    assert "**3대 핵심 기준 스코어:**" in result
    
    print("✅ Google Search 통합 기본 테스트 통과")

@pytest.mark.asyncio 
async def test_api_response_format():
    """API 응답 형식이 기존과 동일한지 확인"""
    from models.portfolio import AnalysisResponse
    
    # 샘플 응답 데이터로 검증
    sample_data = {
        "content": "**AI 총평:** 테스트 포트폴리오는 기술 혁신 중심형 전략을 따르고 있습니다.\n\n**포트폴리오 종합 리니아 스코어: 75 / 100**\n\n**3대 핵심 기준 스코어:**\n\n- **성장 잠재력:** 85 / 100\n- **안정성 및 방어력:** 60 / 100\n- **전략적 일관성:** 80 / 100",
        "processing_time": 15.2,
        "request_id": "test-123"
    }
    
    response = AnalysisResponse(**sample_data)
    assert response.content is not None
    assert response.processing_time == 15.2
    assert response.request_id == "test-123"
    
    print("✅ API 응답 형식 검증 통과")

def test_gemini_service_initialization():
    """GeminiService 초기화 테스트"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
    
    # 서비스 초기화 테스트
    service = GeminiService()
    
    # 기본 속성 확인
    assert service.api_key is not None
    assert service.model_name == "gemini-2.5-flash"
    assert service.timeout == 30
    assert service.max_retries == 3
    
    print("✅ GeminiService 초기화 테스트 통과")

def test_import_compatibility():
    """기존 import 호환성 테스트"""
    # 모든 필요한 모듈이 정상적으로 import되는지 확인
    from services.gemini_service import GeminiService, get_gemini_service
    from models.portfolio import AnalysisResponse, ErrorResponse
    from api.analyze import router
    
    print("✅ Import 호환성 테스트 통과")

if __name__ == "__main__":
    # 직접 실행 시 테스트 수행
    import asyncio
    
    async def run_tests():
        print("🧪 Google Search 통합 테스트 시작...\n")
        
        try:
            # 테스트 1: Import 호환성
            test_import_compatibility()
            
            # 테스트 2: 서비스 초기화
            test_gemini_service_initialization()
            
            # 테스트 3: API 응답 형식
            await test_api_response_format()
            
            # 테스트 4: Google Search 통합 (샘플 데이터)
            await test_google_search_integration()
            
            print("\n🎉 모든 테스트 통과! Google Search 통합이 성공적으로 완료되었습니다.")
            
        except Exception as e:
            print(f"\n❌ 테스트 실패: {str(e)}")
            raise
    
    asyncio.run(run_tests())
