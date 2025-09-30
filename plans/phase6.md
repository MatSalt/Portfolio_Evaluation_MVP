# Phase 6: 탭 기반 UI 통합 및 구조화된 출력 구현

**목표**: PRD.md의 4개 탭 UI와 구조화된 JSON 출력을 기존 마크다운 시스템과 호환되도록 안전하게 통합

**예상 기간**: 3-4일  
**우선순위**: 하위 호환성 최우선, 점진적 마이그레이션

---

## 📋 전체 구현 체크리스트

### Day 1: 백엔드 Pydantic 모델 및 API 확장
- [ ] Pydantic 구조화된 출력 모델 정의
- [ ] Gemini 서비스 구조화된 출력 메서드 추가
- [ ] API 엔드포인트 format 파라미터 지원
- [ ] 단위 테스트 작성

### Day 2: 프론트엔드 타입 정의 및 탭 컴포넌트
- [ ] TypeScript 타입 정의
- [ ] 4개 탭 컴포넌트 구현
- [ ] TabbedAnalysisDisplay 메인 컴포넌트
- [ ] 컴포넌트 테스트

### Day 3: 통합 및 상태 관리
- [ ] ImageUploader format props 추가
- [ ] page.tsx format 토글 UI
- [ ] API 호출 로직 통합
- [ ] E2E 테스트

### Day 4: 검증 및 최적화
- [ ] 하위 호환성 테스트
- [ ] 성능 최적화
- [ ] 에러 처리 보강
- [ ] 문서 업데이트

---

## 🔧 Day 1: 백엔드 구현

### 1.1 Pydantic 모델 정의

**파일**: `backend/models/portfolio.py`

**주의사항**:
- 기존 `AnalysisResponse` 모델은 절대 수정하지 않음
- 새로운 모델을 추가만 함
- 모든 필드에 기본값 또는 Optional 설정으로 안전성 확보

```python
# backend/models/portfolio.py 하단에 추가

from typing import List, Dict, Union, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator

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
    criterion: str = Field(..., description="기준명: 성장 잠재력, 안정성 및 방어력, 전략적 일관성")
    score: int = Field(..., ge=0, le=100, description="0-100 사이 점수")
    maxScore: int = Field(default=100, description="최대 점수")

class DashboardContent(BaseModel):
    """탭 1: 총괄 요약 컨텐츠"""
    overallScore: ScoreData = Field(..., description="종합 점수")
    coreCriteriaScores: List[CoreCriteriaScore] = Field(..., description="3대 핵심 기준 점수")
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
    inDepthAnalysis: List[InDepthAnalysisItem] = Field(..., min_items=3, max_items=3, description="3개 기준별 심층 분석")
    opportunities: Opportunities = Field(..., description="기회 및 개선 방안")

class ScoreTable(BaseModel):
    """점수 테이블"""
    headers: List[str] = Field(..., description="테이블 헤더")
    rows: List[Dict[str, Union[str, int]]] = Field(..., description="테이블 행 데이터")
    
    @field_validator('headers')
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
    category: str = Field(..., description="평가 기준: 펀더멘탈, 기술 잠재력, 거시경제, 시장심리, CEO/리더십")
    score: int = Field(..., ge=0, le=100, description="0-100 사이 점수")
    analysis: str = Field(..., min_length=30, description="상세 분석")

class AnalysisCard(BaseModel):
    """종목 분석 카드"""
    stockName: str = Field(..., description="종목명")
    overallScore: int = Field(..., ge=0, le=100, description="종합 점수")
    detailedScores: List[DetailedScore] = Field(..., min_items=5, max_items=5, description="5개 기준별 점수")

class KeyStockAnalysisContent(BaseModel):
    """탭 4: 핵심 종목 상세 분석 컨텐츠"""
    analysisCards: List[AnalysisCard] = Field(..., min_items=1, description="핵심 종목 분석 카드")

class Tab(BaseModel):
    """탭 데이터"""
    tabId: str = Field(..., description="탭 ID: dashboard, deepDive, allStockScores, keyStockAnalysis")
    tabTitle: str = Field(..., description="탭 제목")
    # dict를 임시로 허용하고, model_validator에서 올바른 서브모델로 변환
    content: Union[DashboardContent, DeepDiveContent, AllStockScoresContent, KeyStockAnalysisContent, dict] = Field(..., description="탭 컨텐츠")

    @model_validator(mode='before')
    @classmethod
    def infer_content_model_from_tab_id(cls, data: Any) -> Any:
        # 데이터 전처리 단계에서 tabId에 따라 content를 올바른 모델로 변환
        if not isinstance(data, dict):
            return data

        tab_id = data.get('tabId')
        content = data.get('content')
        if not (tab_id and isinstance(content, dict)):
            return data

        model_map = {
            "dashboard": DashboardContent,
            "deepDive": DeepDiveContent,
            "allStockScores": AllStockScoresContent,
            "keyStockAnalysis": KeyStockAnalysisContent,
        }

        if tab_id in model_map:
            data['content'] = model_map[tab_id].model_validate(content)

        return data

    @field_validator('tabId')
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
    
    @field_validator('reportDate')
    @classmethod
    def validate_date(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"잘못된 날짜 형식: {v}. YYYY-MM-DD 형식이어야 함")
        return v
    
    @field_validator('tabs')
    @classmethod
    def validate_tabs(cls, v):
        tab_ids = [tab.tabId for tab in v]
        required_ids = ["dashboard", "deepDive", "allStockScores", "keyStockAnalysis"]
        if set(tab_ids) != set(required_ids):
            raise ValueError(f"필수 탭 누락. 필요: {required_ids}, 현재: {tab_ids}")
        return v

class StructuredAnalysisResponse(BaseModel):
    """구조화된 분석 응답 (Phase 6)"""
    portfolioReport: PortfolioReport = Field(..., description="포트폴리오 리포트")
    processing_time: float = Field(..., description="처리 시간 (초)")
    request_id: str = Field(..., description="요청 ID")
    images_processed: int = Field(default=1, description="처리된 이미지 수")
```

### 1.2 Gemini 서비스 구조화된 출력 메서드

**파일**: `backend/services/gemini_service.py`

**주의사항**:
- 기존 메서드는 절대 수정하지 않음
- 새로운 메서드만 추가
- Google Gen AI SDK의 구조화된 출력 기능 활용

```python
# backend/services/gemini_service.py에 추가

import time
import uuid
from datetime import datetime
from models.portfolio import (
    StructuredAnalysisResponse, 
    PortfolioReport,
    Tab,
    DashboardContent,
    DeepDiveContent,
    AllStockScoresContent,
    KeyStockAnalysisContent
)

class GeminiService:
    # ... 기존 코드 유지 ...
    
    def _get_structured_prompt(self) -> str:
        """구조화된 JSON 출력용 프롬프트"""
        return """
당신은 전문 포트폴리오 분석가입니다. 제공된 포트폴리오 이미지를 분석하여 다음 JSON 스키마에 맞는 구조화된 데이터를 생성하세요.

**4개 탭 구조:**

1. **dashboard (총괄 요약)**:
   - overallScore: 종합 점수 (0-100)
   - coreCriteriaScores: 성장 잠재력, 안정성 및 방어력, 전략적 일관성 (각 0-100)
   - strengths: 강점 2-3개 (각 간결한 문장)
   - weaknesses: 약점 2-3개 (각 간결한 문장)

2. **deepDive (심층 분석)**:
   - inDepthAnalysis: 3개 기준별 상세 분석 (title, score, description)
   - opportunities: 기회 및 개선 방안 (2-4개 항목, What-if 시나리오 포함)

3. **allStockScores (종목 스코어)**:
   - scoreTable: 모든 종목의 점수 테이블
     - headers: ["주식", "Overall", "펀더멘탈", "기술 잠재력", "거시경제", "시장심리", "CEO/리더십"]
     - rows: 각 종목의 데이터

4. **keyStockAnalysis (핵심 종목)**:
   - analysisCards: 주요 종목 3-5개의 상세 분석 카드
     - stockName, overallScore
     - detailedScores: 5개 기준별 점수와 분석

**중요**: 
- 모든 점수는 0-100 사이 정수
- description/analysis는 구체적이고 전문적으로 작성
- Google Search를 활용하여 최신 정보 반영
- 한국어로 작성
"""
    
    async def _call_gemini_structured(
        self, 
        image_data_list: List[bytes]
    ) -> PortfolioReport:
        """
        Gemini API 구조화된 출력 호출
        
        공식 문서: https://ai.google.dev/gemini-api/docs/structured-output?hl=ko
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Gemini API 구조화된 출력 호출 시도 {attempt + 1}/{self.max_retries}")
                
                # 1. contents 배열 구성
                contents = []
                
                # 이미지 파트 추가
                for i, image_data in enumerate(image_data_list):
                    image_part = Part.from_bytes(
                        data=image_data,
                        mime_type='image/jpeg'
                    )
                    contents.append(image_part)
                    logger.debug(f"이미지 {i+1}/{len(image_data_list)} 추가")
                
                # 프롬프트 추가
                prompt = self._get_structured_prompt()
                contents.append(prompt)
                
                # 2. Google Search 도구 설정
                from google.genai import types
                grounding_tool = types.Tool(
                    google_search=types.GoogleSearch()
                )
                
                # 3. 구조화된 출력 설정
                config = GenerateContentConfig(
                    temperature=0.1,  # 일관된 구조를 위해 낮은 온도
                    max_output_tokens=8192,
                    response_mime_type="application/json",  # JSON 출력
                    response_schema=PortfolioReport,  # Pydantic 모델을 스키마로 사용
                    tools=[grounding_tool]
                )
                
                # 4. API 호출
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=contents,
                    config=config
                )
                
                # 5. 구조화된 응답 파싱
                if response and hasattr(response, 'parsed') and response.parsed:
                    logger.info("Gemini API 구조화된 응답 성공")
                    return response.parsed  # Pydantic 모델로 자동 파싱됨
                else:
                    raise ValueError("Gemini API에서 구조화된 응답을 받지 못함")
                    
            except Exception as e:
                logger.error(f"구조화된 출력 호출 실패 (시도 {attempt + 1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
    
    async def analyze_portfolio_structured(
        self,
        image_data_list: List[bytes],
        format_type: str = "json"
    ) -> Union[StructuredAnalysisResponse, AnalysisResponse]:
        """
        포트폴리오 분석 - format에 따라 JSON 또는 마크다운 반환
        
        Args:
            image_data_list: 이미지 데이터 리스트 (1-5개)
            format_type: "json" 또는 "markdown"
        
        Returns:
            format_type에 따라 StructuredAnalysisResponse 또는 AnalysisResponse
        """
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        try:
            # 입력 검증
            if not image_data_list or len(image_data_list) == 0:
                raise ValueError("분석할 이미지가 없습니다.")
            
            if len(image_data_list) > 5:
                raise ValueError("최대 5개의 이미지만 분석 가능합니다.")
            
            # 각 이미지 검증
            for i, image_data in enumerate(image_data_list):
                await validate_image(image_data)
            
            if format_type == "json":
                # 구조화된 JSON 출력
                portfolio_report = await self._call_gemini_structured(image_data_list)
                
                return StructuredAnalysisResponse(
                    portfolioReport=portfolio_report,
                    processing_time=time.time() - start_time,
                    request_id=request_id,
                    images_processed=len(image_data_list)
                )
            
            else:
                # 기존 마크다운 출력 (기존 메서드 재사용)
                if len(image_data_list) == 1:
                    markdown_content = await self.analyze_portfolio_image(
                        image_data_list[0],
                        use_cache=True
                    )
                else:
                    markdown_content = await self.analyze_multiple_portfolio_images(
                        image_data_list
                    )
                
                return AnalysisResponse(
                    content=markdown_content,
                    processing_time=time.time() - start_time,
                    request_id=request_id,
                    images_processed=len(image_data_list)
                )
                
        except Exception as e:
            logger.error(f"포트폴리오 분석 실패: {str(e)}")
            raise
```

### 1.3 API 엔드포인트 확장

**파일**: `backend/api/analyze.py`

**주의사항**:
- 기존 엔드포인트 동작을 변경하지 않음
- format 파라미터 기본값은 "markdown" (하위 호환성)

```python
# backend/api/analyze.py 수정

from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from typing import List, Union
from models.portfolio import AnalysisResponse, StructuredAnalysisResponse, ErrorResponse
from services.gemini_service import get_gemini_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/analyze",
    response_model=Union[AnalysisResponse, StructuredAnalysisResponse],
    responses={
        200: {"description": "분석 성공"},
        400: {"model": ErrorResponse, "description": "잘못된 요청"},
        500: {"model": ErrorResponse, "description": "서버 오류"}
    }
)
async def analyze_portfolio(
    files: List[UploadFile] = File(..., description="포트폴리오 이미지 파일 (1-5개)"),
    format: str = Query(
        default="markdown",  # 기본값: 마크다운 (하위 호환성)
        description="출력 형식: 'json' (구조화된 출력) 또는 'markdown' (기존 방식)",
        regex="^(json|markdown)$"
    )
):
    """
    포트폴리오 이미지 분석 API
    
    - format=markdown: 기존 마크다운 텍스트 출력 (AnalysisResponse)
    - format=json: 4개 탭 구조화된 JSON 출력 (StructuredAnalysisResponse)
    """
    try:
        # 1. 파일 개수 검증
        if not files or len(files) == 0:
            raise HTTPException(
                status_code=400,
                detail="분석할 파일이 없습니다."
            )
        
        if len(files) > 5:
            raise HTTPException(
                status_code=400,
                detail="최대 5개의 파일만 업로드 가능합니다."
            )
        
        # 2. 파일 읽기
        image_data_list = []
        for i, file in enumerate(files):
            # 파일 타입 검증
            if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"파일 {i+1}: PNG 또는 JPEG 파일만 지원됩니다."
                )
            
            # 파일 크기 검증 (10MB)
            content = await file.read()
            if len(content) > 10 * 1024 * 1024:
                raise HTTPException(
                    status_code=400,
                    detail=f"파일 {i+1}: 파일 크기는 10MB 이하만 허용됩니다."
                )
            
            image_data_list.append(content)
            logger.info(f"파일 {i+1}/{len(files)} 읽기 완료: {file.filename}")
        
        # 3. Gemini 서비스 호출
        gemini_service = await get_gemini_service()
        result = await gemini_service.analyze_portfolio_structured(
            image_data_list=image_data_list,
            format_type=format
        )
        
        logger.info(f"분석 완료 - format: {format}, 이미지: {len(files)}개")
        return result
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"분석 실패 (ValueError): {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except TimeoutError as e:
        logger.error(f"분석 실패 (Timeout): {str(e)}")
        raise HTTPException(status_code=503, detail="분석 시간이 초과되었습니다. 잠시 후 다시 시도해 주세요.")
    except Exception as e:
        logger.error(f"분석 실패 (예외): {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="분석 중 오류가 발생했습니다.")
```

---

## 🎨 Day 2: 프론트엔드 구현

### 2.1 TypeScript 타입 정의

**파일**: `frontend/src/types/portfolio.ts`

```typescript
// frontend/src/types/portfolio.ts에 추가

// ============================================
// 구조화된 출력 타입 (Phase 6 추가)
// ============================================

export interface ScoreData {
  title: string;
  score: number;
  maxScore: number;
}

export interface CoreCriteriaScore {
  criterion: string;
  score: number;
  maxScore: number;
}

export interface DashboardContent {
  overallScore: ScoreData;
  coreCriteriaScores: CoreCriteriaScore[];
  strengths: string[];
  weaknesses: string[];
}

export interface InDepthAnalysisItem {
  title: string;
  score: number;
  description: string;
}

export interface OpportunityItem {
  summary: string;
  details: string;
}

export interface Opportunities {
  title: string;
  items: OpportunityItem[];
}

export interface DeepDiveContent {
  inDepthAnalysis: InDepthAnalysisItem[];
  opportunities: Opportunities;
}

export interface ScoreTable {
  headers: string[];
  rows: Record<string, string | number>[];
}

export interface AllStockScoresContent {
  scoreTable: ScoreTable;
}

export interface DetailedScore {
  category: string;
  score: number;
  analysis: string;
}

export interface AnalysisCard {
  stockName: string;
  overallScore: number;
  detailedScores: DetailedScore[];
}

export interface KeyStockAnalysisContent {
  analysisCards: AnalysisCard[];
}

export type TabContent = 
  | DashboardContent 
  | DeepDiveContent 
  | AllStockScoresContent 
  | KeyStockAnalysisContent;

export interface Tab {
  tabId: string;
  tabTitle: string;
  content: TabContent;
}

export interface PortfolioReport {
  version: string;
  reportDate: string;
  tabs: Tab[];
}

export interface StructuredAnalysisResponse {
  portfolioReport: PortfolioReport;
  processing_time: number;
  request_id: string;
  images_processed: number;
}

// Union 타입 정의
export type AnalysisResult = StructuredAnalysisResponse | AnalysisResponse;

// 타입 가드 함수
export function isStructuredResponse(
  response: AnalysisResult
): response is StructuredAnalysisResponse {
  return 'portfolioReport' in response;
}
```

### 2.2 탭 컴포넌트 구현

**파일**: `frontend/src/components/tabs/DashboardTab.tsx`

```typescript
// frontend/src/components/tabs/DashboardTab.tsx
'use client';

import React from 'react';
import { DashboardContent } from '@/types/portfolio';
import { TrendingUp, TrendingDown, CheckCircle, AlertCircle } from 'lucide-react';

interface DashboardTabProps {
  content: DashboardContent;
}

export default function DashboardTab({ content }: DashboardTabProps) {
  const { overallScore, coreCriteriaScores, strengths, weaknesses } = content;
  
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };
  
  return (
    <div className="space-y-8">
      {/* 종합 스코어 */}
      <div className="text-center bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-8 border border-blue-100">
        <h3 className="text-lg font-medium text-gray-700 mb-2">{overallScore.title}</h3>
        <div className="text-6xl font-bold text-blue-600 mb-2">
          {overallScore.score}
        </div>
        <div className="text-sm text-gray-600">/ {overallScore.maxScore}점</div>
      </div>
      
      {/* 핵심 기준 스코어 */}
      <div>
        <h3 className="text-xl font-semibold text-gray-900 mb-4">3대 핵심 기준</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {coreCriteriaScores.map((criteria, index) => (
            <div key={index} className="bg-white rounded-lg shadow-sm border p-5">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-900">{criteria.criterion}</h4>
                <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getScoreColor(criteria.score)}`}>
                  {criteria.score}점
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3 mt-3">
                <div 
                  className={`h-3 rounded-full transition-all duration-500 ${
                    criteria.score >= 80 ? 'bg-green-500' :
                    criteria.score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${(criteria.score / criteria.maxScore) * 100}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* 강점/약점 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* 강점 */}
        <div className="bg-green-50 rounded-lg p-6 border border-green-200">
          <div className="flex items-center mb-4">
            <CheckCircle className="h-6 w-6 text-green-600 mr-2" />
            <h3 className="text-lg font-semibold text-green-900">강점</h3>
          </div>
          <ul className="space-y-3">
            {strengths.map((strength, index) => (
              <li key={index} className="flex items-start">
                <TrendingUp className="h-5 w-5 text-green-600 mr-2 flex-shrink-0 mt-0.5" />
                <span className="text-gray-800">{strength}</span>
              </li>
            ))}
          </ul>
        </div>
        
        {/* 약점 */}
        <div className="bg-red-50 rounded-lg p-6 border border-red-200">
          <div className="flex items-center mb-4">
            <AlertCircle className="h-6 w-6 text-red-600 mr-2" />
            <h3 className="text-lg font-semibold text-red-900">약점</h3>
          </div>
          <ul className="space-y-3">
            {weaknesses.map((weakness, index) => (
              <li key={index} className="flex items-start">
                <TrendingDown className="h-5 w-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" />
                <span className="text-gray-800">{weakness}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
```

**파일**: `frontend/src/components/tabs/AllStockScoresTab.tsx`

```typescript
// frontend/src/components/tabs/AllStockScoresTab.tsx
'use client';

import React, { useState, useMemo } from 'react';
import { AllStockScoresContent } from '@/types/portfolio';
import { ChevronUp, ChevronDown } from 'lucide-react';

interface AllStockScoresTabProps {
  content: AllStockScoresContent;
}

export default function AllStockScoresTab({ content }: AllStockScoresTabProps) {
  const { scoreTable } = content;
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-700 bg-green-100';
    if (score >= 60) return 'text-yellow-700 bg-yellow-100';
    return 'text-red-700 bg-red-100';
  };
  
  const handleSort = (column: string) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('desc');
    }
  };
  
  const sortedRows = useMemo(() => {
    if (!sortColumn) return scoreTable.rows;
    
    return [...scoreTable.rows].sort((a, b) => {
      const aValue = a[sortColumn];
      const bValue = b[sortColumn];
      
      // 숫자 비교
      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
      }
      
      // 문자열 비교
      const aStr = String(aValue);
      const bStr = String(bValue);
      return sortDirection === 'asc' 
        ? aStr.localeCompare(bStr, 'ko')
        : bStr.localeCompare(aStr, 'ko');
    });
  }, [scoreTable.rows, sortColumn, sortDirection]);
  
  return (
    <div className="space-y-4">
      <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                {scoreTable.headers.map((header, index) => (
                  <th
                    key={index}
                    onClick={() => handleSort(header)}
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
                  >
                    <div className="flex items-center space-x-1">
                      <span>{header}</span>
                      {sortColumn === header && (
                        sortDirection === 'asc' ? 
                          <ChevronUp className="h-4 w-4" /> : 
                          <ChevronDown className="h-4 w-4" />
                      )}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {sortedRows.map((row, rowIndex) => (
                <tr key={rowIndex} className="hover:bg-gray-50 transition-colors">
                  {scoreTable.headers.map((header, colIndex) => (
                    <td key={colIndex} className="px-6 py-4 whitespace-nowrap">
                      {typeof row[header] === 'number' ? (
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getScoreColor(row[header] as number)}`}>
                          {row[header]}
                        </span>
                      ) : (
                        <div className="text-sm text-gray-900 font-medium">
                          {row[header]}
                        </div>
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      
      <div className="text-sm text-gray-500 text-center">
        총 {scoreTable.rows.length}개 종목 • 클릭하여 정렬
      </div>
    </div>
  );
}
```

**파일**: `frontend/src/components/TabbedAnalysisDisplay.tsx`

```typescript
// frontend/src/components/TabbedAnalysisDisplay.tsx
'use client';

import React, { useState } from 'react';
import { StructuredAnalysisResponse } from '@/types/portfolio';
import { BarChart3, TrendingUp, Table, FileText } from 'lucide-react';
import DashboardTab from './tabs/DashboardTab';
import AllStockScoresTab from './tabs/AllStockScoresTab';

interface TabbedAnalysisDisplayProps {
  data: StructuredAnalysisResponse;
}

const TAB_ICONS = {
  dashboard: BarChart3,
  deepDive: TrendingUp,
  allStockScores: Table,
  keyStockAnalysis: FileText,
};

export default function TabbedAnalysisDisplay({ data }: TabbedAnalysisDisplayProps) {
  const [activeTabId, setActiveTabId] = useState('dashboard');
  
  const { portfolioReport } = data;
  const activeTab = portfolioReport.tabs.find(tab => tab.tabId === activeTabId);
  
  const renderTabContent = () => {
    if (!activeTab) return null;
    
    switch (activeTab.tabId) {
      case 'dashboard':
        return <DashboardTab content={activeTab.content as any} />;
      case 'allStockScores':
        return <AllStockScoresTab content={activeTab.content as any} />;
      // 나머지 탭들은 간단한 JSON 표시 (Day 3에 구현)
      default:
        return (
          <div className="bg-gray-50 rounded-lg p-6">
            <pre className="text-sm overflow-auto">
              {JSON.stringify(activeTab.content, null, 2)}
            </pre>
          </div>
        );
    }
  };
  
  return (
    <div className="w-full max-w-6xl mx-auto">
      {/* 헤더 정보 */}
      <div className="mb-6 text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          포트폴리오 분석 결과
        </h2>
        <div className="flex items-center justify-center space-x-4 text-sm text-gray-600">
          <span>{portfolioReport.reportDate}</span>
          <span>•</span>
          <span>{data.images_processed}개 이미지 분석</span>
          <span>•</span>
          <span>{data.processing_time.toFixed(1)}초 소요</span>
        </div>
      </div>
      
      {/* 탭 네비게이션 */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-2 overflow-x-auto">
          {portfolioReport.tabs.map((tab) => {
            const Icon = TAB_ICONS[tab.tabId as keyof typeof TAB_ICONS];
            const isActive = activeTabId === tab.tabId;
            
            return (
              <button
                key={tab.tabId}
                onClick={() => setActiveTabId(tab.tabId)}
                className={`
                  flex items-center px-4 py-3 border-b-2 font-medium text-sm whitespace-nowrap transition-colors
                  ${isActive
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                {Icon && <Icon className="h-4 w-4 mr-2" />}
                {tab.tabTitle}
              </button>
            );
          })}
        </nav>
      </div>
      
      {/* 탭 컨텐츠 */}
      <div className="mt-6">
        {renderTabContent()}
      </div>
    </div>
  );
}
```

---

## 🔗 Day 3: 통합 및 상태 관리

### 3.1 API 유틸리티 수정

**파일**: `frontend/src/utils/api.ts`

```typescript
// frontend/src/utils/api.ts 수정

import { AnalysisResponse, StructuredAnalysisResponse, ApiError, AnalysisResult } from '@/types/portfolio';

// 기존 analyzePortfolio 함수를 확장
export async function analyzePortfolio(
  files: File[],
  format: 'json' | 'markdown' = 'markdown'
): Promise<AnalysisResult> {
  // 파일 배열 검증
  if (!files || files.length === 0) {
    throw new ApiException('분석할 파일이 없습니다.', 400);
  }

  if (files.length > 5) {
    throw new ApiException('최대 5개의 파일만 업로드 가능합니다.', 400);
  }

  // FormData 생성 (다중 파일 지원)
  const formData = new FormData();
  files.forEach(file => {
    formData.append('files', file);
  });

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 300000); // 5분

    const response = await fetch(`${API_BASE_URL}/api/analyze?format=${format}`, {
      method: 'POST',
      body: formData,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}`;
      
      try {
        const errorData: ApiError = await response.json();
        errorMessage = errorData.error || errorMessage;
      } catch {
        errorMessage = `서버 오류 (${response.status})`;
      }

      throw new ApiException(errorMessage, response.status);
    }

    const data: AnalysisResult = await response.json();
    
    // 응답 데이터 유효성 검사
    if (format === 'json') {
      const structuredData = data as StructuredAnalysisResponse;
      if (!structuredData.portfolioReport || !structuredData.portfolioReport.tabs) {
        throw new ApiException('잘못된 응답 형식', 500);
      }
    } else {
      const markdownData = data as AnalysisResponse;
      if (!markdownData.content || typeof markdownData.content !== 'string') {
        throw new ApiException('잘못된 응답 형식', 500);
      }
    }

    return data;

  } catch (error: any) {
    if (error.name === 'AbortError') {
      throw new ApiException('요청 시간이 초과되었습니다. 다시 시도해 주세요.', 408);
    }
    
    if (error instanceof ApiException) {
      throw error;
    }

    throw new ApiException('네트워크 오류가 발생했습니다. 인터넷 연결을 확인해 주세요.', 0);
  }
}
```

### 3.2 Hook 수정

**파일**: `frontend/src/hooks/usePortfolioAnalysis.tsx`

```typescript
// frontend/src/hooks/usePortfolioAnalysis.tsx 수정

import { analyzePortfolio } from '@/utils/api';
import { AnalysisResult, isStructuredResponse } from '@/types/portfolio';

export function usePortfolioAnalysis() {
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [format, setFormat] = useState<'json' | 'markdown'>('json'); // 기본값: json
  
  // ... 기존 코드 유지 ...
  
  const analyzeImage = useCallback(async () => {
    if (!uploadState.files || uploadState.files.length === 0) {
      setAnalysisState({
        status: 'error',
        data: null,
        error: '분석할 파일이 없습니다.',
      });
      return;
    }

    setAnalysisState({
      status: 'loading',
      data: null,
      error: null,
    });

    try {
      // format 상태를 사용하여 API 호출
      const result = await analyzePortfolio(uploadState.files, format);
      
      setAnalysisResult(result);
      setAnalysisState({
        status: 'success',
        data: result,
        error: null,
      });
    } catch (error: any) {
      setAnalysisState({
        status: 'error',
        data: null,
        error: error.message || '분석 중 오류가 발생했습니다.',
      });
    }
  }, [uploadState.files, format]);
  
  return {
    // ... 기존 반환값 ...
    analysisResult,
    format,
    setFormat,
  };
}
```

### 3.3 메인 페이지 수정

**파일**: `frontend/src/app/page.tsx`

```typescript
// frontend/src/app/page.tsx 수정

import TabbedAnalysisDisplay from '@/components/TabbedAnalysisDisplay';
import { isStructuredResponse } from '@/types/portfolio';

export default function Home() {
  const {
    uploadState,
    analysisResult,
    format,
    setFormat,
    handleFileSelect,
    analyzeImage,
    reset,
    removeFile,
    isLoading,
    canAnalyze,
  } = usePortfolioAnalysis();

  // ... 기존 코드 유지 ...

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-100">
        {/* ... 헤더 ... */}
        
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8" role="main">
          {/* ... 단계 표시기 ... */}
          
          <div className="space-y-8">
            {/* 업로드 영역 */}
            {!analysisResult && (
              <section>
                <ImageUploader
                  uploadState={uploadState}
                  onFileSelect={handleFileSelect}
                  onRemoveFile={removeFile}
                  disabled={isLoading}
                />

                {canAnalyze && (
                  <div className="text-center mt-6 space-y-4">
                    {/* Format 선택 토글 */}
                    <div className="flex justify-center">
                      <div className="bg-gray-100 p-1 rounded-lg inline-flex">
                        <button
                          onClick={() => setFormat('json')}
                          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                            format === 'json' 
                              ? 'bg-white text-gray-900 shadow' 
                              : 'text-gray-600 hover:text-gray-900'
                          }`}
                        >
                          탭 뷰
                        </button>
                        <button
                          onClick={() => setFormat('markdown')}
                          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                            format === 'markdown' 
                              ? 'bg-white text-gray-900 shadow' 
                              : 'text-gray-600 hover:text-gray-900'
                          }`}
                        >
                          마크다운 뷰
                        </button>
                      </div>
                    </div>
                    
                    <button
                      onClick={analyzeImage}
                      disabled={isLoading}
                      className="inline-flex items-center px-8 py-4 border border-transparent text-lg font-medium rounded-lg text-white bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200 shadow-lg hover:shadow-xl"
                    >
                      <Sparkles className="h-5 w-5 mr-2" />
                      AI 분석 시작하기
                    </button>
                  </div>
                )}
              </section>
            )}

            {/* 분석 결과 영역 */}
            {analysisResult && (
              <section>
                {isStructuredResponse(analysisResult) ? (
                  <TabbedAnalysisDisplay data={analysisResult} />
                ) : (
                  <AnalysisDisplay 
                    analysisState={{
                      status: 'success',
                      data: analysisResult,
                      error: null
                    }}
                    onRetry={analyzeImage}
                  />
                )}

                <div className="text-center mt-8">
                  <button
                    onClick={reset}
                    className="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
                  >
                    새로운 분석 시작하기
                  </button>
                </div>
              </section>
            )}
          </div>

          {/* ... 특징 소개 ... */}
        </main>

        {/* ... 푸터 ... */}
      </div>
    </ErrorBoundary>
  );
}
```

---

## ✅ Day 4: 검증 및 최적화

### 4.1 테스트 스크립트

**파일**: `backend/tests/test_structured_output.py`

```python
# backend/tests/test_structured_output.py
import pytest
from models.portfolio import (
    StructuredAnalysisResponse,
    PortfolioReport,
    DashboardContent,
    ScoreData,
    CoreCriteriaScore
)

def test_structured_response_validation():
    """구조화된 응답 검증 테스트"""
    # 유효한 데이터
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
                            "maxScore": 100
                        },
                        "coreCriteriaScores": [
                            {"criterion": "성장 잠재력", "score": 88, "maxScore": 100},
                            {"criterion": "안정성 및 방어력", "score": 55, "maxScore": 100},
                            {"criterion": "전략적 일관성", "score": 74, "maxScore": 100}
                        ],
                        "strengths": ["강점1", "강점2"],
                        "weaknesses": ["약점1", "약점2"]
                    }
                },
                # ... 나머지 탭들
            ]
        },
        "processing_time": 15.2,
        "request_id": "test-123",
        "images_processed": 1
    }
    
    response = StructuredAnalysisResponse(**valid_data)
    assert response.portfolioReport.version == "1.0"
    assert len(response.portfolioReport.tabs) == 1  # 테스트용으로 1개만

def test_invalid_score_validation():
    """잘못된 점수 검증 테스트"""
    invalid_data = {
        "title": "테스트",
        "score": 150,  # 100 초과
        "maxScore": 100
    }
    
    with pytest.raises(ValueError):
        ScoreData(**invalid_data)
```

---

## 🚨 주의사항 및 체크리스트

### 반드시 확인할 사항

- [ ] 기존 `AnalysisResponse` 모델 절대 수정 금지
- [ ] 기존 `analyze_portfolio_image`, `analyze_multiple_portfolio_images` 메서드 절대 수정 금지
- [ ] API 엔드포인트 기본값은 `format="markdown"` (하위 호환성)
- [ ] 모든 새로운 타입에 기본값 또는 Optional 설정
- [ ] 구조화된 출력 실패 시 적절한 에러 메시지

### 성능 고려사항

- [ ] 구조화된 출력은 마크다운보다 응답 시간이 더 길 수 있음
- [ ] 캐싱 전략 동일하게 적용
- [ ] Google Search 통합 유지

### 보안 고려사항

- [ ] 파일 크기 검증 (10MB)
- [ ] 파일 타입 검증 (PNG, JPEG)
- [ ] 최대 파일 개수 (5개)
- [ ] API 응답 검증

---

## 📚 참고 자료

- Gemini 구조화된 출력: https://ai.google.dev/gemini-api/docs/structured-output?hl=ko
- Google Search 통합: https://ai.google.dev/gemini-api/docs/google-search?hl=ko
- Pydantic V2 문서: https://docs.pydantic.dev/latest/
- Next.js 15 문서: https://nextjs.org/docs

---

## 🎯 완료 기준

- [ ] 백엔드 API가 `format=json`과 `format=markdown` 모두 지원
- [ ] 프론트엔드에서 탭 뷰와 마크다운 뷰 전환 가능
- [ ] 4개 탭 모두 정상 렌더링
- [ ] 기존 마크다운 출력 방식 정상 작동
- [ ] 모든 테스트 통과
- [ ] 에러 처리 완료
