"""
Gemini 서비스 테스트

이 모듈은 GeminiService 클래스의 단위 테스트를 제공합니다.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from services.gemini_service import GeminiService, get_gemini_service
from models.portfolio import SAMPLE_MARKDOWN_CONTENT

class TestGeminiService:
    """GeminiService 테스트 클래스"""
    
    @pytest.fixture
    def mock_image_data(self):
        """테스트용 이미지 데이터"""
        return b"fake_image_data_for_testing"
    
    @pytest.fixture
    def sample_markdown_response(self):
        """샘플 마크다운 응답"""
        return """**AI 총평:** 테스트 포트폴리오는 **'기술 혁신 중심형'** 전략을 따르고 있습니다.

**포트폴리오 종합 리니아 스코어: 75 / 100**

**3대 핵심 기준 스코어:**

- **성장 잠재력:** 80 / 100
- **안정성 및 방어력:** 60 / 100
- **전략적 일관성:** 85 / 100

**[1] 포트폴리오 리니아 스코어 심층 분석**

**1.1 성장 잠재력 분석 (80 / 100): 높은 기술 혁신 잠재력**

테스트 포트폴리오는 혁신 기술 분야의 선도 기업들로 구성되어 있습니다."""
    
    @patch.dict('os.environ', {'GEMINI_API_KEY': 'test_api_key'})
    def test_gemini_service_init(self):
        """GeminiService 초기화 테스트"""
        service = GeminiService()
        assert service.api_key == 'test_api_key'
        assert service.model_name == 'gemini-2.5-flash'
    
    @patch.dict('os.environ', {}, clear=True)
    def test_gemini_service_init_no_api_key(self):
        """API 키 없이 초기화 시 예외 발생 테스트"""
        with pytest.raises(ValueError, match="GEMINI_API_KEY"):
            GeminiService()
    
    @patch.dict('os.environ', {'GEMINI_API_KEY': 'test_api_key'})
    @patch('services.gemini_service.validate_image')
    @patch('services.gemini_service.optimize_image')
    @pytest.mark.asyncio
    async def test_analyze_portfolio_image_success(
        self, mock_optimize, mock_validate, mock_image_data, sample_markdown_response
    ):
        """포트폴리오 이미지 분석 성공 테스트"""
        # Mock 설정
        mock_validate.return_value = None
        mock_optimize.return_value = mock_image_data
        
        service = GeminiService()
        
        # Gemini API 호출 모킹
        with patch.object(service, '_call_gemini_api') as mock_api:
            mock_api.return_value = sample_markdown_response
            
            result = await service.analyze_portfolio_image(mock_image_data)
            
            assert isinstance(result, str)
            assert "**AI 총평:**" in result
            assert "**포트폴리오 종합 리니아 스코어:" in result
            assert "**3대 핵심 기준 스코어:**" in result
    
    @patch.dict('os.environ', {'GEMINI_API_KEY': 'test_api_key'})
    @pytest.mark.asyncio
    async def test_get_sample_analysis(self):
        """샘플 분석 결과 반환 테스트"""
        service = GeminiService()
        result = await service.get_sample_analysis()
        
        assert isinstance(result, str)
        assert len(result) > 100
        assert "**AI 총평:**" in result

@pytest.mark.asyncio
async def test_get_gemini_service_singleton():
    """GeminiService 싱글톤 테스트"""
    with patch.dict('os.environ', {'GEMINI_API_KEY': 'test_api_key'}):
        service1 = await get_gemini_service()
        service2 = await get_gemini_service()
        
        assert service1 is service2