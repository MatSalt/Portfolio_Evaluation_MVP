import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app
from models.portfolio import SAMPLE_MARKDOWN_CONTENT

client = TestClient(app)

class TestAnalyzeAPI:
    """분석 API 테스트 클래스"""
    
    @pytest.fixture
    def sample_image_file(self):
        """테스트용 이미지 파일"""
        return {
            "file": ("test.jpg", b"fake_image_data", "image/jpeg")
        }
    
    @patch('api.analyze.get_gemini_service')
    @patch('utils.image_utils.validate_image')
    @patch('utils.image_utils.get_image_info')
    def test_analyze_portfolio_success(
        self, mock_get_info, mock_validate, mock_get_service, sample_image_file
    ):
        """포트폴리오 분석 성공 테스트"""
        # Mock 설정
        mock_validate.return_value = None
        mock_get_info.return_value = {"format": "JPEG", "size": (1024, 768)}
        
        mock_service = AsyncMock()
        mock_service.analyze_portfolio_image.return_value = SAMPLE_MARKDOWN_CONTENT
        mock_get_service.return_value = mock_service
        
        # API 호출
        response = client.post("/api/analyze", files=sample_image_file)
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert "processing_time" in data
        assert "request_id" in data
        assert "**AI 총평:**" in data["content"]
    
    def test_analyze_portfolio_no_file(self):
        """파일 없이 요청 시 오류 테스트"""
        response = client.post("/api/analyze")
        assert response.status_code == 422  # Validation error
    
    def test_analyze_portfolio_invalid_file_type(self):
        """잘못된 파일 타입 테스트"""
        files = {"file": ("test.txt", b"not_an_image", "text/plain")}
        response = client.post("/api/analyze", files=files)
        assert response.status_code == 400
    
    @patch('api.analyze.get_gemini_service')
    def test_get_sample_analysis(self, mock_get_service):
        """샘플 분석 결과 반환 테스트"""
        mock_service = AsyncMock()
        mock_service.get_sample_analysis.return_value = SAMPLE_MARKDOWN_CONTENT
        mock_get_service.return_value = mock_service
        
        response = client.get("/api/analyze/sample")
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert "**AI 총평:**" in data["content"]
    
    def test_health_check(self):
        """헬스 체크 테스트"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["output_format"] == "markdown_text"
