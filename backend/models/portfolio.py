"""
포트폴리오 분석 API 데이터 모델

이 모듈은 포트폴리오 분석 API의 요청/응답을 위한 Pydantic 모델들을 정의합니다.
마크다운 텍스트 출력 방식에 최적화된 간단한 구조를 제공합니다.
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Dict, Union, Any
from enum import Enum
import time
from datetime import datetime

class AnalysisStatus(str, Enum):
    """분석 상태"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class AnalysisRequest(BaseModel):
    """분석 요청 정보"""
    filename: Optional[str] = Field(None, description="파일명")
    file_size: Optional[int] = Field(None, description="파일 크기 (bytes)")
    content_type: Optional[str] = Field(None, description="파일 타입")

class AnalysisResponse(BaseModel):
    """마크다운 텍스트 분석 결과 응답"""
    content: str = Field(..., description="expected_result.md와 동일한 형식의 마크다운 텍스트")
    processing_time: float = Field(..., description="처리 시간 (초)")
    request_id: str = Field(..., description="요청 ID")
    images_processed: int = Field(default=1, description="처리된 이미지 수")
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        if not v or len(v.strip()) < 100:
            raise ValueError('분석 결과는 최소 100자 이상이어야 합니다.')
        return v.strip()

class ErrorResponse(BaseModel):
    """에러 응답"""
    error: str = Field(..., description="에러 메시지")
    detail: Optional[str] = Field(None, description="상세 에러 정보")
    code: Optional[str] = Field(None, description="에러 코드")
    timestamp: str = Field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"), description="발생 시간")

# 검증용 샘플 마크다운 데이터
SAMPLE_MARKDOWN_CONTENT = """**AI 총평:** 샘플 포트폴리오는 **'기술 혁신 중심형'** 전략을 따르고 있으며, 높은 성장 잠재력을 보유하고 있으나 **변동성에 다소 취약**합니다.

**포트폴리오 종합 리니아 스코어: 75 / 100**

**3대 핵심 기준 스코어:**

- **성장 잠재력:** 85 / 100
- **안정성 및 방어력:** 60 / 100
- **전략적 일관성:** 80 / 100

**[1] 포트폴리오 리니아 스코어 심층 분석**

**1.1 성장 잠재력 분석 (85 / 100): 혁신 기술에 대한 강력한 집중**

샘플 포트폴리오는 AI, 클라우드, 반도체 등 미래 성장 동력이 될 기술 분야의 선두 기업들에 집중 투자되어 있어 높은 성장 잠재력을 보여줍니다. 특히 기술 혁신을 주도하는 기업들의 비중이 전체 포트폴리오의 상당 부분을 차지하고 있습니다.

**1.2 안정성 및 방어력 분석 (60 / 100): 기술주 특유의 변동성**

대부분의 종목이 성장 단계의 기술 기업들로 구성되어 있어 시장 변동성에 노출되어 있습니다. 안정적인 현금흐름을 창출하는 기업의 비중을 높이면 방어력을 개선할 수 있습니다.

**1.3 전략적 일관성 분석 (80 / 100): 명확한 투자 테마**

'기술 혁신'이라는 일관된 투자 철학이 포트폴리오 전반에 반영되어 있어 높은 전략적 일관성을 보여줍니다.

**[2] 포트폴리오 강점 및 약점, 그리고 기회**

**💪 강점**

- **미래 기술 투자:** 차세대 기술 분야의 선도 기업들에 대한 전략적 투자
- **명확한 투자 철학:** 일관된 기술 혁신 테마로 포트폴리오 구성

**📉 약점**

- **높은 변동성:** 기술주 중심의 포트폴리오로 인한 시장 변동성 노출
- **섹터 집중:** 특정 기술 분야에 대한 의존도가 높음

**💡 기회 및 개선 방안**

- **안정성 보강:** 안정적인 배당주나 대형주의 비중을 높여 포트폴리오 안정성 개선
- **지역 분산:** 글로벌 기술 기업들로 지역적 분산 투자 확대

**[3] 개별 종목 리니아 스코어 상세 분석**

**3.1 스코어 요약 테이블**

| 주식 | Overall (100점 만점) | 펀더멘탈 | 기술 잠재력 | 거시경제 | 시장심리 | CEO/리더십 |
| --- | --- | --- | --- | --- | --- | --- |
| **샘플 기술주 A** | **80** | 75 | 90 | 75 | 85 | 85 |
| **샘플 기술주 B** | **78** | 80 | 85 | 70 | 80 | 85 |

**3.2 개별 종목 분석 카드**

**1. 샘플 기술주 A - Overall: 80 / 100**

- **펀더멘탈 (75/100):** 꾸준한 매출 성장과 수익성 개선을 보여주는 안정적인 재무 구조
- **기술 잠재력 (90/100):** 차세대 기술 분야에서 독보적인 기술력과 특허 포트폴리오 보유
- **거시경제 (75/100):** 글로벌 디지털 전환 가속화의 직접적인 수혜
- **시장심리 (85/100):** 기술 혁신에 대한 시장의 높은 기대감
- **CEO/리더십 (85/100):** 비전 있는 리더십과 혁신적인 경영 전략"""

# ============================================
# 구조화된 출력 모델 (Phase 6 추가)
# ============================================


class ScoreData(BaseModel):
    """점수 데이터 기본 모델"""
    title: str = Field(..., description="점수 항목 제목")
    score: int = Field(..., ge=0, le=100, description="0-100 사이 점수")
    maxScore: int = Field(default=100, description="최대 점수")


class CoreCriteriaScore(BaseModel):
    """핵심 기준 점수"""
    criterion: str = Field(
        ..., description="기준명: 성장 잠재력, 안정성 및 방어력, 전략적 일관성"
    )
    score: int = Field(..., ge=0, le=100, description="0-100 사이 점수")
    maxScore: int = Field(default=100, description="최대 점수")


class DashboardContent(BaseModel):
    """탭 1: 총괄 요약 컨텐츠"""
    overallScore: ScoreData = Field(..., description="종합 점수")
    coreCriteriaScores: List[CoreCriteriaScore] = Field(
        ..., description="3대 핵심 기준 점수"
    )
    strengths: List[str] = Field(..., min_items=1, description="강점 목록")
    weaknesses: List[str] = Field(..., min_items=1, description="약점 목록")


class InDepthAnalysisItem(BaseModel):
    """심층 분석 항목"""
    title: str = Field(..., description="분석 제목")
    score: int = Field(..., ge=0, le=100, description="해당 기준 점수")
    description: str = Field(..., min_length=50, description="상세 분석 내용")


class OpportunityItem(BaseModel):
    """기회 항목"""
    summary: str = Field(..., description="기회 요약")
    details: str = Field(..., min_length=30, description="상세 설명 (What-if 시나리오 포함)")


class Opportunities(BaseModel):
    """기회 및 개선 방안"""
    title: str = Field(default="기회 및 개선 방안", description="섹션 제목")
    items: List[OpportunityItem] = Field(..., min_items=1, description="기회 항목 목록")


class DeepDiveContent(BaseModel):
    """탭 2: 포트폴리오 심층 분석 컨텐츠"""
    inDepthAnalysis: List[InDepthAnalysisItem] = Field(
        ..., min_items=3, max_items=3, description="3개 기준별 심층 분석"
    )
    opportunities: Opportunities = Field(..., description="기회 및 개선 방안")


class StockScoreRow(BaseModel):
    """종목 스코어 행"""
    주식: str = Field(..., description="종목명")
    Overall: int = Field(..., ge=0, le=100, description="종합 점수")
    펀더멘탈: int = Field(..., ge=0, le=100, description="펀더멘탈 점수")
    기술_잠재력: int = Field(..., ge=0, le=100, alias="기술 잠재력", description="기술 잠재력 점수")
    거시경제: int = Field(..., ge=0, le=100, description="거시경제 점수")
    시장심리: int = Field(..., ge=0, le=100, description="시장심리 점수")
    CEO_리더십: int = Field(..., ge=0, le=100, alias="CEO/리더십", description="CEO/리더십 점수")

    class Config:
        populate_by_name = True  # alias와 field name 모두 허용


class ScoreTable(BaseModel):
    """점수 테이블"""
    headers: List[str] = Field(..., description="테이블 헤더")
    rows: List[StockScoreRow] = Field(
        ..., description="테이블 행 데이터"
    )

    @field_validator("headers")
    @classmethod
    def validate_headers(cls, v):
        required = ["주식", "Overall"]
        if not all(h in v for h in required):
            raise ValueError(f"필수 헤더 누락: {required}")
        return v


class AllStockScoresContent(BaseModel):
    """탭 3: 개별 종목 스코어 컨텐츠"""
    scoreTable: ScoreTable = Field(..., description="종목 스코어 테이블")


class DetailedScore(BaseModel):
    """상세 점수"""
    category: str = Field(
        ..., description="평가 기준: 펀더멘탈, 기술 잠재력, 거시경제, 시장심리, CEO/리더십"
    )
    score: int = Field(..., ge=0, le=100, description="0-100 사이 점수")
    analysis: str = Field(..., min_length=30, description="상세 분석")


class AnalysisCard(BaseModel):
    """종목 분석 카드"""
    stockName: str = Field(..., description="종목명")
    overallScore: int = Field(..., ge=0, le=100, description="종합 점수")
    detailedScores: List[DetailedScore] = Field(
        ..., min_items=5, max_items=5, description="5개 기준별 점수"
    )


class KeyStockAnalysisContent(BaseModel):
    """탭 4: 핵심 종목 상세 분석 컨텐츠"""
    analysisCards: List[AnalysisCard] = Field(
        ..., min_items=1, description="핵심 종목 분석 카드"
    )


class Tab(BaseModel):
    """탭 데이터"""
    tabId: str = Field(
        ..., description="탭 ID: dashboard, deepDive, allStockScores, keyStockAnalysis"
    )
    tabTitle: str = Field(..., description="탭 제목")
    # Union 타입만 사용 (dict 제거 - response_schema 호환성)
    content: Union[
        DashboardContent,
        DeepDiveContent,
        AllStockScoresContent,
        KeyStockAnalysisContent,
    ] = Field(..., description="탭 컨텐츠")

    @model_validator(mode="before")
    @classmethod
    def infer_content_model_from_tab_id(cls, data: Any) -> Any:
        # 데이터 전처리 단계에서 tabId에 따라 content를 올바른 모델로 변환
        if not isinstance(data, dict):
            return data

        tab_id = data.get("tabId")
        content = data.get("content")
        if not (tab_id and isinstance(content, dict)):
            return data

        model_map = {
            "dashboard": DashboardContent,
            "deepDive": DeepDiveContent,
            "allStockScores": AllStockScoresContent,
            "keyStockAnalysis": KeyStockAnalysisContent,
        }

        if tab_id in model_map:
            data["content"] = model_map[tab_id].model_validate(content)

        return data

    @field_validator("tabId")
    @classmethod
    def validate_tab_id(cls, v):
        valid_ids = ["dashboard", "deepDive", "allStockScores", "keyStockAnalysis"]
        if v not in valid_ids:
            raise ValueError(f"유효하지 않은 탭 ID: {v}. 허용값: {valid_ids}")
        return v


class PortfolioReport(BaseModel):
    """포트폴리오 리포트"""
    version: str = Field(default="1.0", description="리포트 버전")
    reportDate: str = Field(..., description="리포트 생성 날짜 (YYYY-MM-DD)")
    tabs: List[Tab] = Field(..., min_items=4, max_items=4, description="4개 탭 데이터")

    @field_validator("reportDate")
    @classmethod
    def validate_date(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"잘못된 날짜 형식: {v}. YYYY-MM-DD 형식이어야 함")
        return v

    @field_validator("tabs")
    @classmethod
    def validate_tabs(cls, v):
        tab_ids = [tab.tabId for tab in v]
        required_ids = ["dashboard", "deepDive", "allStockScores", "keyStockAnalysis"]
        if set(tab_ids) != set(required_ids):
            raise ValueError(
                f"필수 탭 누락. 필요: {required_ids}, 현재: {tab_ids}"
            )
        return v


class StructuredAnalysisResponse(BaseModel):
    """구조화된 분석 응답 (Phase 6)"""
    portfolioReport: PortfolioReport = Field(..., description="포트폴리오 리포트")
    processing_time: float = Field(..., description="처리 시간 (초)")
    request_id: str = Field(..., description="요청 ID")
    images_processed: int = Field(default=1, description="처리된 이미지 수")
