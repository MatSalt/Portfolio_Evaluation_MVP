"""
분석 API 엔드포인트 테스트

이 모듈은 포트폴리오 분석 API 엔드포인트의 통합 테스트를 제공합니다.
"""

import pytest
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app
from models.portfolio import SAMPLE_MARKDOWN_CONTENT
from models.portfolio import StructuredAnalysisResponse

# 테스트용 환경변수 설정
os.environ['GEMINI_API_KEY'] = 'test_api_key'

client = TestClient(app)

class TestAnalyzeAPI:
    """분석 API 테스트 클래스"""
    
    @pytest.fixture
    def sample_image_file(self):
        """테스트용 이미지 파일"""
        from PIL import Image
        from io import BytesIO
        
        # 실제 이미지 생성
        img = Image.new('RGB', (500, 500), color='red')
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        image_data = buffer.getvalue()
        
        return {
            "file": ("test.jpg", image_data, "image/jpeg")
        }
    
    @patch('services.gemini_service.GeminiService.analyze_portfolio_image')
    @patch('utils.image_utils.validate_image')
    @patch('utils.image_utils.get_image_info')
    def test_analyze_portfolio_success(
        self, mock_get_info, mock_validate, mock_analyze, sample_image_file
    ):
        """포트폴리오 분석 성공 테스트"""
        # Mock 설정
        mock_validate.return_value = None
        mock_get_info.return_value = {"format": "JPEG", "size": (1024, 768)}
        mock_analyze.return_value = SAMPLE_MARKDOWN_CONTENT
        
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

    @patch('utils.image_utils.validate_image')
    @patch('services.gemini_service.GeminiService.analyze_portfolio_structured')
    def test_analyze_portfolio_json_success(self, mock_analyze_structured, mock_validate, sample_image_file):
        """format=json 구조화 출력 성공 테스트"""
        mock_validate.return_value = None

        # 최소 유효 구조화 응답 생성 (4개 탭 포함)
        valid_structured = {
            "portfolioReport": {
                "version": "1.0",
                "reportDate": "2025-09-30",
                "tabs": [
                    {
                        "tabId": "dashboard",
                        "tabTitle": "총괄 요약",
                        "content": {
                            "overallScore": {"title": "종합", "score": 70, "maxScore": 100},
                            "coreCriteriaScores": [
                                {"criterion": "성장 잠재력", "score": 80, "maxScore": 100},
                                {"criterion": "안정성 및 방어력", "score": 60, "maxScore": 100},
                                {"criterion": "전략적 일관성", "score": 70, "maxScore": 100},
                            ],
                            "strengths": ["강점1"],
                            "weaknesses": ["약점1"],
                        },
                    },
                    {
                        "tabId": "deepDive",
                        "tabTitle": "심층 분석",
                        "content": {
                            "inDepthAnalysis": [
                                {"title": "성장", "score": 80, "description": "a" * 60},
                                {"title": "안정성", "score": 60, "description": "b" * 60},
                                {"title": "일관성", "score": 70, "description": "c" * 60},
                            ],
                            "opportunities": {
                                "title": "기회 및 개선 방안",
                                "items": [
                                    {"summary": "요약1", "details": "d" * 40},
                                ],
                            },
                        },
                    },
                    {
                        "tabId": "allStockScores",
                        "tabTitle": "종목 스코어",
                        "content": {
                            "scoreTable": {
                                "headers": [
                                    "주식", "Overall", "펀더멘탈", "기술 잠재력", "거시경제", "시장심리", "CEO/리더십"
                                ],
                                "rows": [
                                    {"주식": "ABC", "Overall": 75, "펀더멘탈": 70, "기술 잠재력": 80, "거시경제": 65, "시장심리": 60, "CEO/리더십": 85}
                                ],
                            }
                        },
                    },
                    {
                        "tabId": "keyStockAnalysis",
                        "tabTitle": "핵심 종목",
                        "content": {
                            "analysisCards": [
                                {
                                    "stockName": "ABC",
                                    "overallScore": 75,
                                    "detailedScores": [
                                        {"category": "펀더멘탈", "score": 70, "analysis": "x" * 40},
                                        {"category": "기술 잠재력", "score": 80, "analysis": "y" * 40},
                                        {"category": "거시경제", "score": 65, "analysis": "z" * 40},
                                        {"category": "시장심리", "score": 60, "analysis": "m" * 40},
                                        {"category": "CEO/리더십", "score": 85, "analysis": "n" * 40},
                                    ],
                                }
                            ]
                        },
                    }
                ]
            },
            "processing_time": 1.23,
            "request_id": "test-req-id",
            "images_processed": 1
        }

        # 서비스 메서드를 직접 모킹하여 구조화 응답 반환
        mock_analyze_structured.return_value = StructuredAnalysisResponse(**valid_structured)

        response = client.post("/api/analyze?format=json", files=sample_image_file)

        assert response.status_code == 200
        data = response.json()
        assert "portfolioReport" in data
        assert "tabs" in data["portfolioReport"]
        assert len(data["portfolioReport"]["tabs"]) == 4

    @patch('utils.image_utils.validate_image')
    @patch('services.gemini_service.GeminiService.analyze_portfolio_structured')
    def test_analyze_portfolio_json_schema_error(self, mock_analyze_structured, mock_validate, sample_image_file):
        """format=json 구조화 출력 시 스키마 불일치 -> 400"""
        mock_validate.return_value = None
        mock_analyze_structured.side_effect = ValueError("invalid schema")

        response = client.post("/api/analyze?format=json", files=sample_image_file)
        assert response.status_code == 400

    @patch('utils.image_utils.validate_image')
    @patch('services.gemini_service.GeminiService.analyze_portfolio_structured')
    def test_analyze_portfolio_json_timeout(self, mock_analyze_structured, mock_validate, sample_image_file):
        """format=json 구조화 출력 시 타임아웃 -> 503"""
        mock_validate.return_value = None
        mock_analyze_structured.side_effect = TimeoutError("timeout")

        response = client.post("/api/analyze?format=json", files=sample_image_file)
        assert response.status_code == 503
    
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