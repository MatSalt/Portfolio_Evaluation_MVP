"""
구조화된 출력 테스트

Phase 6: 구조화된 JSON 스키마에 대한 기본 검증 테스트를 포함합니다.
"""

import pytest
from models.portfolio import (
    StructuredAnalysisResponse,
    PortfolioReport,
    DashboardContent,
    ScoreData,
    CoreCriteriaScore,
)


def test_structured_response_validation():
    """구조화된 응답 검증 테스트 (4개 탭 포함)"""
    valid_data = {
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
                            "maxScore": 100,
                        },
                        "coreCriteriaScores": [
                            {"criterion": "성장 잠재력", "score": 88, "maxScore": 100},
                            {"criterion": "안정성 및 방어력", "score": 55, "maxScore": 100},
                            {"criterion": "전략적 일관성", "score": 74, "maxScore": 100},
                        ],
                        "strengths": ["강점1", "강점2"],
                        "weaknesses": ["약점1", "약점2"],
                    },
                },
                {
                    "tabId": "deepDive",
                    "tabTitle": "심층 분석",
                    "content": {
                        "inDepthAnalysis": [
                            {"title": "성장 잠재력", "score": 80, "description": "a" * 60},
                            {"title": "안정성 및 방어력", "score": 60, "description": "b" * 60},
                            {"title": "전략적 일관성", "score": 70, "description": "c" * 60},
                        ],
                        "opportunities": {
                            "title": "기회 및 개선 방안",
                            "items": [
                                {"summary": "요약1", "details": "d" * 40},
                                {"summary": "요약2", "details": "e" * 40},
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
                                "주식",
                                "Overall",
                                "펀더멘탈",
                                "기술 잠재력",
                                "거시경제",
                                "시장심리",
                                "CEO/리더십",
                            ],
                            "rows": [
                                {
                                    "주식": "ABC",
                                    "Overall": 75,
                                    "펀더멘탈": 70,
                                    "기술 잠재력": 80,
                                    "거시경제": 65,
                                    "시장심리": 60,
                                    "CEO/리더십": 85,
                                }
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
                },
            ],
        },
        "processing_time": 15.2,
        "request_id": "test-123",
        "images_processed": 1,
    }

    response = StructuredAnalysisResponse(**valid_data)
    assert response.portfolioReport.version == "1.0"
    assert len(response.portfolioReport.tabs) == 4


def test_invalid_score_validation():
    """잘못된 점수 검증 테스트"""
    invalid_data = {
        "title": "테스트",
        "score": 150,  # 100 초과
        "maxScore": 100,
    }

    with pytest.raises(ValueError):
        ScoreData(**invalid_data)


