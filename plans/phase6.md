# Phase 6: 탭 기반 UI 통합 및 구조화된 출력 구현

**목표**: PRD.md의 4개 탭 UI와 구조화된 JSON 출력을 기존 마크다운 시스템과 호환되도록 안전하게 통합

**예상 기간**: 3-4일  
**우선순위**: 하위 호환성 최우선, 점진적 마이그레이션

---

## 📋 전체 구현 체크리스트 (진행 현황)

### Day 1: 백엔드 Pydantic 모델 및 API 확장
- [x] Pydantic 구조화된 출력 모델 정의
- [x] Gemini 서비스 구조화된 출력 메서드 추가 (JSON 검증, 프롬프트 스키마 명시)
- [x] API 엔드포인트 format 파라미터 지원 (json/markdown, 단일·다중 업로드 호환)
- [x] 단위/통합 테스트 작성

### Day 2: 프론트엔드 타입 정의 및 탭 컴포넌트
- [x] TypeScript 타입 정의
- [x] 4개 탭 컴포넌트 중 Dashboard, AllStockScores 구현
- [x] TabbedAnalysisDisplay 메인 컴포넌트
- [x] DeepDiveTab 컴포넌트 구현 (카드 + 아코디언 방식)
- [ ] KeyStockAnalysisTab 컴포넌트 구현 (종목 카드 + 내부 아코디언 방식)
- [ ] 컴포넌트 테스트 (추가 예정)

### Day 3: 통합 및 상태 관리
- [x] ImageUploader 이후 format 선택 토글 (json/markdown)
- [x] page.tsx 포맷 토글 UI 연동
- [x] API 호출 로직 통합 (에러 처리 강화)
- [ ] E2E 테스트 (추가 예정)

### Day 4: 검증 및 최적화
- [x] 하위 호환성 테스트 (markdown 기본값 유지)
- [ ] 성능 최적화 (후속)
- [x] 에러 처리 보강 (스키마 불일치/타임아웃 케이스)
- [x] 문서 업데이트 (이슈 원인/해결 포함)

---

## 🧭 진행 요약 (간단 정리)
- 백엔드: response_schema 제거 + 프롬프트 스키마 명시, Google Search 툴 유지, JSON 텍스트 파싱 후 Pydantic 검증. 단일/다중 업로드, 상태코드 일관화.
- 프론트엔드: json/markdown 토글, 구조화 응답 시 탭 UI 렌더 (Dashboard/AllStockScores 완료, DeepDive 구현 완료, KeyStockAnalysis 계획 완료). 훅에 format·analysisResult 추가.
- 테스트: 총 42개 통과. json 성공/스키마 불일치(400)/타임아웃(503) 포함.
- 문서: known issue, 단계별 해결, 테스트 절차 반영.
- **완료 작업**: 
  - DeepDiveTab 컴포넌트 (카드 + 아코디언 방식) 구현 완료 ✅
  - KeyStockAnalysisTab 컴포넌트 (종목 카드 + 내부 아코디언 방식) 상세 계획 추가 ✅

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

**파일**: `frontend/src/components/tabs/DeepDiveTab.tsx`

```typescript
// frontend/src/components/tabs/DeepDiveTab.tsx
'use client';

import React, { useState } from 'react';
import { DeepDiveContent } from '@/types/portfolio';
import { TrendingUp, Lightbulb, ChevronDown, ChevronUp } from 'lucide-react';

interface DeepDiveTabProps {
  content: DeepDiveContent;
}

export default function DeepDiveTab({ content }: DeepDiveTabProps) {
  const { inDepthAnalysis, opportunities } = content;
  const [expandedIndex, setExpandedIndex] = useState<number | null>(0); // 첫 번째 항목 기본 확장
  
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100 border-green-300';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100 border-yellow-300';
    return 'text-red-600 bg-red-100 border-red-300';
  };
  
  const getProgressColor = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };
  
  const toggleOpportunity = (index: number) => {
    setExpandedIndex(expandedIndex === index ? null : index);
  };
  
  return (
    <div className="space-y-8">
      {/* 심층 분석 섹션 */}
      <div>
        <div className="flex items-center mb-6">
          <TrendingUp className="h-6 w-6 text-blue-600 mr-2" />
          <h3 className="text-xl font-semibold text-gray-900">3대 기준 심층 분석</h3>
        </div>
        
        <div className="grid grid-cols-1 gap-6">
          {inDepthAnalysis.map((item, index) => (
            <div 
              key={index} 
              className="bg-white rounded-lg shadow-md border border-gray-200 p-6 hover:shadow-lg transition-shadow"
            >
              {/* 카드 헤더: 제목 + 점수 */}
              <div className="flex items-start justify-between mb-4">
                <h4 className="text-lg font-semibold text-gray-900 flex-1">
                  {item.title}
                </h4>
                <div className={`ml-4 px-4 py-2 rounded-full border-2 font-bold text-lg ${getScoreColor(item.score)}`}>
                  {item.score}점
                </div>
              </div>
              
              {/* 진행 바 */}
              <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
                <div 
                  className={`h-2 rounded-full transition-all duration-500 ${getProgressColor(item.score)}`}
                  style={{ width: `${item.score}%` }}
                ></div>
              </div>
              
              {/* 상세 설명 */}
              <p className="text-gray-700 leading-relaxed text-sm">
                {item.description}
              </p>
            </div>
          ))}
        </div>
      </div>
      
      {/* 기회 및 개선 방안 섹션 */}
      <div>
        <div className="flex items-center mb-6">
          <Lightbulb className="h-6 w-6 text-yellow-600 mr-2" />
          <h3 className="text-xl font-semibold text-gray-900">{opportunities.title}</h3>
        </div>
        
        <div className="space-y-3">
          {opportunities.items.map((opportunity, index) => (
            <div 
              key={index}
              className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg border border-yellow-200 overflow-hidden"
            >
              {/* 아코디언 헤더 */}
              <button
                onClick={() => toggleOpportunity(index)}
                className="w-full px-6 py-4 flex items-center justify-between hover:bg-yellow-100 transition-colors"
              >
                <div className="flex items-start flex-1 text-left">
                  <span className="flex-shrink-0 w-6 h-6 bg-yellow-400 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3 mt-0.5">
                    {index + 1}
                  </span>
                  <h4 className="font-semibold text-gray-900 flex-1">
                    {opportunity.summary}
                  </h4>
                </div>
                {expandedIndex === index ? (
                  <ChevronUp className="h-5 w-5 text-gray-600 ml-2 flex-shrink-0" />
                ) : (
                  <ChevronDown className="h-5 w-5 text-gray-600 ml-2 flex-shrink-0" />
                )}
              </button>
              
              {/* 아코디언 본문 */}
              {expandedIndex === index && (
                <div className="px-6 pb-4 pt-2 bg-white border-t border-yellow-200">
                  <div className="pl-9">
                    <p className="text-gray-700 leading-relaxed text-sm whitespace-pre-line">
                      {opportunity.details}
                    </p>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
      
      {/* 안내 메시지 */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          💡 <strong>Tip:</strong> 기회 항목을 클릭하면 상세한 What-if 시나리오를 확인할 수 있습니다.
        </p>
      </div>
    </div>
  );
}
```

**디자인 특징:**
- **심층 분석 카드**: 3개 기준을 큰 카드로 표현, 점수 배지 + 진행 바 + 상세 설명
- **기회 아코디언**: 클릭 시 확장되는 인터랙티브 UI, 번호 배지로 식별성 향상
- **색상 시스템**: 점수별 색상 구분 (80+ 녹색, 60+ 노란색, 60 미만 빨간색)
- **일관성**: DashboardTab, AllStockScoresTab과 동일한 디자인 패턴 유지

---

**파일**: `frontend/src/components/TabbedAnalysisDisplay.tsx`

```typescript
// frontend/src/components/TabbedAnalysisDisplay.tsx
'use client';

import React, { useState } from 'react';
import { StructuredAnalysisResponse } from '@/types/portfolio';
import { BarChart3, TrendingUp, Table, FileText } from 'lucide-react';
import DashboardTab from './tabs/DashboardTab';
import AllStockScoresTab from './tabs/AllStockScoresTab';
import DeepDiveTab from './tabs/DeepDiveTab';

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
      case 'deepDive':
        return <DeepDiveTab content={activeTab.content as any} />;
      case 'allStockScores':
        return <AllStockScoresTab content={activeTab.content as any} />;
      // keyStockAnalysis는 추후 구현 (현재는 JSON 표시)
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

## 🎯 DeepDiveTab 구현 가이드 (상세 계획)

### 목표
'포트폴리오 심층 분석' 탭의 JSON 데이터를 시각적으로 보기 좋게 렌더링하여 사용자 경험 향상

### 구현 방식 선정 이유

**카드 + 아코디언 조합 방식**을 선택한 이유:

1. **정보 계층 구조**:
   - 심층 분석 (inDepthAnalysis): 항상 표시되어야 하는 핵심 정보 → 카드형
   - 기회 방안 (opportunities): 선택적으로 확장하여 볼 수 있는 보조 정보 → 아코디언형

2. **가독성**:
   - 3개 기준 분석을 카드로 세로 배치하여 스크롤 시 자연스럽게 읽힘
   - 긴 What-if 시나리오는 아코디언으로 접어서 페이지 길이 최적화

3. **일관성**:
   - DashboardTab의 카드 스타일과 통일
   - AllStockScoresTab의 색상 시스템 재사용

4. **인터랙션**:
   - 아코디언 클릭으로 사용자 참여도 향상
   - 첫 번째 기회 항목 기본 확장으로 사용성 개선

### 구현 단계

#### Step 1: DeepDiveTab 컴포넌트 생성

**파일 생성**: `frontend/src/components/tabs/DeepDiveTab.tsx`

**주요 기능**:
- ✅ inDepthAnalysis 3개 항목을 카드로 렌더링
- ✅ 각 카드에 제목, 점수 배지, 진행 바, 상세 설명 표시
- ✅ opportunities를 아코디언으로 렌더링
- ✅ 아코디언 상태 관리 (useState)
- ✅ 점수별 색상 구분 (getScoreColor, getProgressColor)
- ✅ 반응형 디자인 (모바일 지원)

**사용 아이콘**:
- TrendingUp (심층 분석 섹션 헤더)
- Lightbulb (기회 섹션 헤더)
- ChevronDown/ChevronUp (아코디언 토글)

#### Step 2: TabbedAnalysisDisplay 수정

**파일 수정**: `frontend/src/components/TabbedAnalysisDisplay.tsx`

**변경 사항**:
1. DeepDiveTab import 추가
2. renderTabContent의 switch에 'deepDive' case 추가

```typescript
case 'deepDive':
  return <DeepDiveTab content={activeTab.content as any} />;
```

#### Step 3: 테스트 및 검증

**확인 사항**:
- [ ] DeepDiveTab이 정상적으로 렌더링되는지 확인
- [ ] 3개 심층 분석 카드가 올바르게 표시되는지 확인
- [ ] 점수별 색상이 올바르게 적용되는지 확인 (80+: 녹색, 60+: 노란색, 60 미만: 빨간색)
- [ ] 아코디언이 정상적으로 확장/축소되는지 확인
- [ ] 첫 번째 기회 항목이 기본으로 확장되어 있는지 확인
- [ ] 모바일 반응형이 정상 작동하는지 확인
- [ ] 다른 탭과 디자인 일관성이 유지되는지 확인

#### Step 4: 타입 안전성 확보

**현재 상태**:
- DeepDiveContent 타입 정의 완료 (frontend/src/types/portfolio.ts)
- InDepthAnalysisItem, OpportunityItem, Opportunities 타입 정의 완료

**추가 작업 불필요**: 타입 정의는 이미 Phase 6 초기에 완료됨

### UI/UX 개선 포인트

1. **시각적 계층**:
   - 섹션 헤더에 아이콘 추가로 구분성 향상
   - 카드 hover 효과로 인터랙션 암시
   - 그라데이션 배경으로 중요도 강조

2. **정보 전달**:
   - 점수를 숫자 + 진행 바로 이중 표현하여 직관성 향상
   - 번호 배지로 기회 항목 순서 명확화
   - Tip 메시지로 사용법 안내

3. **접근성**:
   - 충분한 색상 대비 (WCAG AA 이상)
   - 키보드 네비게이션 지원 (button 태그 사용)
   - 의미론적 HTML (h3, h4 태그 활용)

### 예상 렌더링 결과

```
┌─────────────────────────────────────────────┐
│ 📈 3대 기준 심층 분석                         │
├─────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────┐ │
│ │ 성장 잠재력               [85점]        │ │
│ │ ████████████████░░░░░ 85%              │ │
│ │ 포트폴리오의 약 62.7%가 KODEX 미국...   │ │
│ └─────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────┐ │
│ │ 안정성 및 방어력          [70점]        │ │
│ │ ██████████████░░░░░░░ 70%              │ │
│ │ KODEX CD금리액티브(합성) ETF에...       │ │
│ └─────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────┐ │
│ │ 전략적 일관성             [80점]        │ │
│ │ ████████████████░░░░ 80%               │ │
│ │ 본 포트폴리오는 미국 대형주 중심...     │ │
│ └─────────────────────────────────────────┘ │
├─────────────────────────────────────────────┤
│ 💡 기회 및 개선 방안                         │
├─────────────────────────────────────────────┤
│ ┌─ ① 포트폴리오 지역 및 자산군... ▼ ────┐ │
│ │ 현재 포트폴리오는 미국 S&P 500...       │ │
│ └─────────────────────────────────────────┘ │
│ ┌─ ② 환헤지 전략 재검토           ▶ ────┐ │
│ └─────────────────────────────────────────┘ │
│ ┌─ ③ 배당 성장 및 인컴 전략...    ▶ ────┐ │
│ └─────────────────────────────────────────┘ │
├─────────────────────────────────────────────┤
│ 💡 Tip: 기회 항목을 클릭하면...             │
└─────────────────────────────────────────────┘
```

---

## 🎯 KeyStockAnalysisTab 구현 가이드 (상세 계획)

### 목표
'핵심 종목 상세 분석' 탭의 JSON 데이터를 종목별 카드 + 내부 아코디언 방식으로 시각화하여 각 종목의 5개 기준 분석을 효과적으로 전달

### 구현 방식 선정 이유

**종목 카드 + 내부 아코디언 조합 방식**을 선택한 이유:

1. **정보 밀도**:
   - 각 종목마다 5개 기준 × 상세 분석 = 많은 정보량
   - 카드로 종목 구분, 아코디언으로 정보 접기/펴기 → 정보 과부하 방지

2. **탐색성**:
   - 사용자가 관심 있는 종목만 선택하여 확장
   - 한 번에 모든 정보를 보여주지 않아 가독성 향상

3. **계층 구조**:
   - 1차 계층: 종목 (카드)
   - 2차 계층: 5개 평가 기준 (아코디언)
   - 3차 계층: 점수 + 진행 바 + 상세 분석

4. **일관성**:
   - DeepDiveTab의 아코디언 패턴 재사용
   - DashboardTab의 점수 배지 및 색상 시스템 재사용

5. **확장성**:
   - 3-5개 종목을 동일한 패턴으로 표시
   - 종목 수가 늘어나도 UI가 깨지지 않음

### 데이터 구조

```typescript
{
  "analysisCards": [
    {
      "stockName": "KODEX 미국S&P500",
      "overallScore": 88,
      "detailedScores": [
        {"category": "펀더멘탈", "score": 90, "analysis": "..."},
        {"category": "기술 잠재력", "score": 85, "analysis": "..."},
        {"category": "거시경제", "score": 88, "analysis": "..."},
        {"category": "시장심리", "score": 92, "analysis": "..."},
        {"category": "CEO/리더십", "score": 85, "analysis": "..."}
      ]
    }
  ]
}
```

### 구현 단계

#### Step 1: KeyStockAnalysisTab 컴포넌트 생성

**파일 생성**: `frontend/src/components/tabs/KeyStockAnalysisTab.tsx`

**주요 기능**:
- ✅ analysisCards 배열을 순회하여 종목별 카드 렌더링
- ✅ 각 카드에 종목명 + 종합 점수 배지 표시
- ✅ 5개 평가 기준을 아코디언으로 렌더링
- ✅ 아코디언 상태 관리 (카드별 독립적인 상태)
- ✅ 각 기준마다 점수 + 진행 바 + 상세 분석 표시
- ✅ 점수별 색상 구분 (getScoreColor, getProgressColor)
- ✅ 반응형 디자인 (모바일: 1열, 태블릿: 2열, 데스크톱: 2-3열)

**사용 아이콘**:
- FileText (페이지 헤더)
- TrendingUp (점수 상승 표시)
- ChevronDown/ChevronUp (아코디언 토글)
- BarChart (평가 기준 아이콘)

**파일**: `frontend/src/components/tabs/KeyStockAnalysisTab.tsx`

```typescript
// frontend/src/components/tabs/KeyStockAnalysisTab.tsx
'use client';

import React, { useState } from 'react';
import { KeyStockAnalysisContent } from '@/types/portfolio';
import { FileText, ChevronDown, ChevronUp, BarChart } from 'lucide-react';

interface KeyStockAnalysisTabProps {
  content: KeyStockAnalysisContent;
}

export default function KeyStockAnalysisTab({ content }: KeyStockAnalysisTabProps) {
  const { analysisCards } = content;
  // 각 카드별로 독립적인 아코디언 상태 관리 (카드 인덱스 → 확장된 기준 인덱스)
  const [expandedStates, setExpandedStates] = useState<Record<number, number | null>>(
    Object.fromEntries(analysisCards.map((_, idx) => [idx, 0])) // 각 카드의 첫 번째 기준 기본 확장
  );
  
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100 border-green-300';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100 border-yellow-300';
    return 'text-red-600 bg-red-100 border-red-300';
  };
  
  const getProgressColor = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };
  
  const toggleCriterion = (cardIndex: number, criterionIndex: number) => {
    setExpandedStates(prev => ({
      ...prev,
      [cardIndex]: prev[cardIndex] === criterionIndex ? null : criterionIndex
    }));
  };
  
  return (
    <div className="space-y-6">
      {/* 페이지 헤더 */}
      <div className="flex items-center mb-6">
        <FileText className="h-6 w-6 text-blue-600 mr-2" />
        <h3 className="text-xl font-semibold text-gray-900">핵심 종목 상세 분석</h3>
        <span className="ml-3 text-sm text-gray-500">({analysisCards.length}개 종목)</span>
      </div>
      
      {/* 종목 카드 그리드 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {analysisCards.map((card, cardIndex) => (
          <div
            key={cardIndex}
            className="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden"
          >
            {/* 카드 헤더: 종목명 + 종합 점수 */}
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h4 className="text-lg font-bold text-gray-900">{card.stockName}</h4>
                <div className={`px-4 py-2 rounded-full border-2 font-bold text-lg ${getScoreColor(card.overallScore)}`}>
                  {card.overallScore}점
                </div>
              </div>
              <p className="text-xs text-gray-600 mt-1">종합 평가 점수</p>
            </div>
            
            {/* 5개 평가 기준 아코디언 */}
            <div className="divide-y divide-gray-100">
              {card.detailedScores.map((criterion, criterionIndex) => {
                const isExpanded = expandedStates[cardIndex] === criterionIndex;
                
                return (
                  <div key={criterionIndex}>
                    {/* 아코디언 헤더 */}
                    <button
                      onClick={() => toggleCriterion(cardIndex, criterionIndex)}
                      className="w-full px-6 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-center flex-1">
                        <BarChart className="h-4 w-4 text-gray-400 mr-2" />
                        <span className="font-medium text-gray-900 text-sm">{criterion.category}</span>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${getScoreColor(criterion.score)}`}>
                          {criterion.score}
                        </span>
                        {isExpanded ? (
                          <ChevronUp className="h-4 w-4 text-gray-600" />
                        ) : (
                          <ChevronDown className="h-4 w-4 text-gray-600" />
                        )}
                      </div>
                    </button>
                    
                    {/* 아코디언 본문 */}
                    {isExpanded && (
                      <div className="px-6 pb-4 bg-gray-50">
                        {/* 진행 바 */}
                        <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
                          <div
                            className={`h-2 rounded-full transition-all duration-500 ${getProgressColor(criterion.score)}`}
                            style={{ width: `${criterion.score}%` }}
                          ></div>
                        </div>
                        
                        {/* 상세 분석 */}
                        <p className="text-sm text-gray-700 leading-relaxed">
                          {criterion.analysis}
                        </p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
      
      {/* 안내 메시지 */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          💡 <strong>Tip:</strong> 각 평가 기준을 클릭하면 해당 항목의 상세 분석을 확인할 수 있습니다. 
          5개 기준(펀더멘탈, 기술 잠재력, 거시경제, 시장심리, CEO/리더십)을 종합하여 종합 점수가 산출됩니다.
        </p>
      </div>
    </div>
  );
}
```

**디자인 특징**:
- **종목 카드**: 그리드 레이아웃 (2열), 헤더에 그라데이션 배경
- **종합 점수**: 큰 배지로 강조, 점수별 색상 구분
- **평가 기준 아코디언**: 5개 기준을 접고 펼 수 있음, 기본 첫 번째 확장
- **진행 바 + 분석**: 점수 시각화 + 텍스트 분석 조합
- **일관성**: DashboardTab, DeepDiveTab과 동일한 색상 시스템

#### Step 2: TabbedAnalysisDisplay 수정

**파일 수정**: `frontend/src/components/TabbedAnalysisDisplay.tsx`

**변경 사항**:
1. KeyStockAnalysisTab import 추가
2. renderTabContent의 switch에 'keyStockAnalysis' case 추가

```typescript
import KeyStockAnalysisTab from './tabs/KeyStockAnalysisTab';

// ...

case 'keyStockAnalysis':
  return <KeyStockAnalysisTab content={activeTab.content as any} />;
```

**전체 수정된 코드**:

```typescript
// frontend/src/components/TabbedAnalysisDisplay.tsx
'use client';

import React, { useState } from 'react';
import { StructuredAnalysisResponse } from '@/types/portfolio';
import { BarChart3, TrendingUp, Table, FileText } from 'lucide-react';
import DashboardTab from './tabs/DashboardTab';
import AllStockScoresTab from './tabs/AllStockScoresTab';
import DeepDiveTab from './tabs/DeepDiveTab';
import KeyStockAnalysisTab from './tabs/KeyStockAnalysisTab';

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
      case 'deepDive':
        return <DeepDiveTab content={activeTab.content as any} />;
      case 'allStockScores':
        return <AllStockScoresTab content={activeTab.content as any} />;
      case 'keyStockAnalysis':
        return <KeyStockAnalysisTab content={activeTab.content as any} />;
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

#### Step 3: 테스트 및 검증

**확인 사항**:
- [ ] KeyStockAnalysisTab이 정상적으로 렌더링되는지 확인
- [ ] analysisCards 배열의 모든 종목이 카드로 표시되는지 확인
- [ ] 각 카드의 종목명과 종합 점수가 올바르게 표시되는지 확인
- [ ] 5개 평가 기준이 아코디언으로 정상 표시되는지 확인
- [ ] 아코디언 클릭 시 확장/축소가 정상 작동하는지 확인
- [ ] 각 카드의 아코디언이 독립적으로 작동하는지 확인 (다른 카드에 영향 없음)
- [ ] 점수별 색상이 올바르게 적용되는지 확인 (80+: 녹색, 60+: 노란색, 60 미만: 빨간색)
- [ ] 진행 바가 점수에 맞게 표시되는지 확인
- [ ] 상세 분석 텍스트가 읽기 쉽게 표시되는지 확인
- [ ] 반응형 디자인 확인 (모바일: 1열, 데스크톱: 2열)
- [ ] 다른 탭과 디자인 일관성이 유지되는지 확인
- [ ] 3-5개 종목에 대해 UI가 깨지지 않는지 확인

#### Step 4: 타입 안전성 확보

**현재 상태**:
- KeyStockAnalysisContent 타입 정의 완료 (frontend/src/types/portfolio.ts)
- AnalysisCard, DetailedScore 타입 정의 완료

**추가 작업 불필요**: 타입 정의는 이미 Phase 6 초기에 완료됨

#### Step 5: 에지 케이스 처리

**고려 사항**:
1. **빈 배열**: `analysisCards.length === 0`일 때 빈 상태 메시지 표시
2. **많은 종목**: 5개 이상의 종목도 그리드로 정상 표시
3. **긴 텍스트**: 종목명이나 분석 텍스트가 길 때 줄바꿈 처리
4. **점수 범위**: 0-100 범위 외 값 방어 로직 (백엔드에서 검증하지만 프론트엔드도 안전장치)

**빈 상태 처리 추가**:

```typescript
// KeyStockAnalysisTab.tsx에 추가
if (analysisCards.length === 0) {
  return (
    <div className="bg-gray-50 rounded-lg p-12 text-center">
      <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
      <p className="text-gray-600">핵심 종목 분석 데이터가 없습니다.</p>
    </div>
  );
}
```

### UI/UX 개선 포인트

1. **시각적 계층**:
   - 카드 헤더에 그라데이션 배경으로 구분성 강화
   - 종합 점수를 큰 배지로 시각적 강조
   - 아코디언 hover 효과로 클릭 가능성 암시

2. **정보 전달**:
   - 종합 점수 + 5개 세부 점수로 다층적 정보 제공
   - 점수를 숫자 + 진행 바로 이중 표현
   - 상세 분석 텍스트로 정성적 평가 제공

3. **탐색성**:
   - 아코디언으로 관심 있는 기준만 확장
   - 카드별 독립적 상태로 여러 종목 비교 가능
   - 그리드 레이아웃으로 한눈에 여러 종목 비교

4. **접근성**:
   - 충분한 색상 대비 (WCAG AA 이상)
   - 키보드 네비게이션 지원 (button 태그)
   - 의미론적 HTML (h3, h4, button 태그 활용)

5. **반응형**:
   - 모바일: 1열 세로 배치
   - 태블릿/데스크톱: 2열 그리드
   - 카드 내부는 모든 화면에서 동일한 레이아웃

### 예상 렌더링 결과

```
┌─────────────────────────────────────────────────────────────────┐
│ 📄 핵심 종목 상세 분석 (3개 종목)                                │
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────┐  ┌─────────────────────────┐       │
│ │ KODEX 미국S&P500  [88점]│  │ TIGER 미국S&P500  [85점]│       │
│ │ 종합 평가 점수          │  │ 종합 평가 점수          │       │
│ ├─────────────────────────┤  ├─────────────────────────┤       │
│ │ 📊 펀더멘탈      [90] ▼ │  │ 📊 펀더멘탈      [88] ▶ │       │
│ │   ████████████████ 90%  │  │                         │       │
│ │   S&P 500 지수는...     │  │                         │       │
│ ├─────────────────────────┤  ├─────────────────────────┤       │
│ │ 📊 기술 잠재력   [85] ▶ │  │ 📊 기술 잠재력   [82] ▶ │       │
│ ├─────────────────────────┤  ├─────────────────────────┤       │
│ │ 📊 거시경제      [88] ▶ │  │ 📊 거시경제      [85] ▶ │       │
│ ├─────────────────────────┤  ├─────────────────────────┤       │
│ │ 📊 시장심리      [92] ▶ │  │ 📊 시장심리      [90] ▶ │       │
│ ├─────────────────────────┤  ├─────────────────────────┤       │
│ │ 📊 CEO/리더십    [85] ▶ │  │ 📊 CEO/리더십    [80] ▶ │       │
│ └─────────────────────────┘  └─────────────────────────┘       │
│ ┌─────────────────────────┐                                     │
│ │ KODEX CD금리...  [72점] │                                     │
│ │ 종합 평가 점수          │                                     │
│ ├─────────────────────────┤                                     │
│ │ 📊 펀더멘탈      [75] ▶ │                                     │
│ ├─────────────────────────┤                                     │
│ │ 📊 기술 잠재력   [68] ▶ │                                     │
│ ├─────────────────────────┤                                     │
│ │ 📊 거시경제      [72] ▶ │                                     │
│ ├─────────────────────────┤                                     │
│ │ 📊 시장심리      [70] ▶ │                                     │
│ ├─────────────────────────┤                                     │
│ │ 📊 CEO/리더십    [75] ▶ │                                     │
│ └─────────────────────────┘                                     │
├─────────────────────────────────────────────────────────────────┤
│ 💡 Tip: 각 평가 기준을 클릭하면 해당 항목의 상세 분석을...      │
└─────────────────────────────────────────────────────────────────┘
```

### 구현 시 주의사항

1. **상태 관리**:
   - `expandedStates`는 `Record<number, number | null>` 타입
   - 카드 인덱스를 키로, 확장된 기준 인덱스를 값으로 저장
   - 각 카드가 독립적으로 아코디언 상태를 유지

2. **타입 안전성**:
   - `analysisCards.map()`에서 타입 추론 정상 작동 확인
   - `detailedScores`가 정확히 5개인지 백엔드에서 검증 (프론트엔드는 있는 만큼 렌더링)

3. **성능**:
   - 종목 수가 많아도 (5개 이하) 성능 문제 없음
   - 아코디언 상태 변경 시 해당 카드만 리렌더링

4. **디버깅**:
   - `console.log`로 `analysisCards` 구조 확인
   - `expandedStates` 상태 변화 추적

5. **에러 방지**:
   - `analysisCards`가 undefined/null이면 빈 배열 기본값
   - `detailedScores`가 빈 배열이면 빈 상태 메시지

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

## ⚠️ 알려진 이슈 및 해결 방법

### 이슈: Gemini API "additionalProperties is not supported" 에러

**증상:**
```
POST /api/analyze?format=json → 400 Bad Request
ERROR: additionalProperties is not supported in the Gemini API.
```

**원인:**
Gemini Structured Output API는 다음과 같은 Pydantic 스키마 패턴을 지원하지 않습니다:
1. **동적 키를 가진 Dict**: `Dict[str, Union[str, int]]` (행 데이터의 키가 런타임에 결정됨)
2. **Union 타입에 dict 포함**: `Union[DashboardContent, ..., dict]` (Tab.content)
3. **additionalProperties 허용**: JSON Schema에서 임의의 추가 필드를 허용하는 패턴

현재 `PortfolioReport` 모델의 문제점:
- `Tab.content`가 `Union[..., dict]`로 정의되어 동적 타입 허용
- `ScoreTable.rows`가 `List[Dict[str, Union[str, int]]]`로 컬럼명이 가변적
- 이러한 패턴들이 Gemini의 엄격한 스키마 검증을 통과하지 못함

**해결 방법 (단기 핫픽스):**

Gemini에게 `response_schema`를 직접 전달하지 않고, JSON 형식으로만 응답을 요청한 뒤 서버에서 Pydantic 검증을 수행합니다.

#### Step 1: Gemini 서비스 수정

**파일**: `backend/services/gemini_service.py`

```python
async def _call_gemini_structured(
    self, 
    image_data_list: List[bytes]
) -> PortfolioReport:
    """
    Gemini API 구조화된 출력 호출 (JSON 모드)
    
    주의: response_schema를 직접 전달하지 않고, JSON 형식으로만 요청
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
            
            # 프롬프트 추가 (JSON 스키마를 텍스트로 명시)
            prompt = self._get_structured_prompt()
            contents.append(prompt)
            
            # 2. Google Search 도구 설정
            from google.genai import types
            grounding_tool = types.Tool(
                google_search=types.GoogleSearch()
            )
            
            # 3. JSON 출력 설정 (response_schema 제거)
            config = GenerateContentConfig(
                temperature=0.1,  # 일관된 구조를 위해 낮은 온도
                max_output_tokens=8192,
                response_mime_type="application/json",  # JSON 출력만 지정
                # response_schema=PortfolioReport,  # ← 제거! (additionalProperties 문제)
                tools=[grounding_tool]
            )
            
            # 4. API 호출
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )
            
            # 5. JSON 응답 파싱 및 Pydantic 검증
            if response and response.text:
                logger.info("Gemini API JSON 응답 수신")
                
                # JSON 텍스트를 Pydantic 모델로 검증
                try:
                    portfolio_report = PortfolioReport.model_validate_json(response.text)
                    logger.info("PortfolioReport 검증 성공")
                    return portfolio_report
                except Exception as validation_error:
                    logger.error(f"Pydantic 검증 실패: {str(validation_error)}")
                    logger.debug(f"응답 텍스트: {response.text[:500]}...")
                    raise ValueError(f"Gemini 응답이 스키마와 일치하지 않습니다: {str(validation_error)}")
            else:
                raise ValueError("Gemini API에서 JSON 응답을 받지 못함")
                
        except Exception as e:
            logger.error(f"구조화된 출력 호출 실패 (시도 {attempt + 1}): {str(e)}")
            if attempt == self.max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)
```

#### Step 2: 프롬프트 개선 (JSON 스키마 명시)

**파일**: `backend/services/gemini_service.py`

```python
def _get_structured_prompt(self) -> str:
    """구조화된 JSON 출력용 프롬프트 (스키마 명시)"""
    return """
당신은 전문 포트폴리오 분석가입니다. 제공된 포트폴리오 이미지를 분석하여 다음 JSON 스키마에 **정확히** 맞는 데이터를 생성하세요.

**중요**: 응답은 반드시 유효한 JSON 형식이어야 하며, 아래 스키마를 엄격히 따라야 합니다.

**JSON 스키마:**

```json
{
  "version": "1.0",
  "reportDate": "YYYY-MM-DD",
  "tabs": [
    {
      "tabId": "dashboard",
      "tabTitle": "총괄 요약",
      "content": {
        "overallScore": {
          "title": "포트폴리오 종합 스코어",
          "score": 0-100 사이 정수,
          "maxScore": 100
        },
        "coreCriteriaScores": [
          {"criterion": "성장 잠재력", "score": 0-100, "maxScore": 100},
          {"criterion": "안정성 및 방어력", "score": 0-100, "maxScore": 100},
          {"criterion": "전략적 일관성", "score": 0-100, "maxScore": 100}
        ],
        "strengths": ["강점1", "강점2", ...],
        "weaknesses": ["약점1", "약점2", ...]
      }
    },
    {
      "tabId": "deepDive",
      "tabTitle": "포트폴리오 심층 분석",
      "content": {
        "inDepthAnalysis": [
          {
            "title": "성장 잠재력",
            "score": 0-100,
            "description": "최소 50자 이상의 상세 분석"
          },
          {
            "title": "안정성 및 방어력",
            "score": 0-100,
            "description": "최소 50자 이상의 상세 분석"
          },
          {
            "title": "전략적 일관성",
            "score": 0-100,
            "description": "최소 50자 이상의 상세 분석"
          }
        ],
        "opportunities": {
          "title": "기회 및 개선 방안",
          "items": [
            {
              "summary": "기회 요약",
              "details": "최소 30자 이상의 상세 설명 (What-if 시나리오 포함)"
            }
          ]
        }
      }
    },
    {
      "tabId": "allStockScores",
      "tabTitle": "개별 종목 스코어",
      "content": {
        "scoreTable": {
          "headers": ["주식", "Overall", "펀더멘탈", "기술 잠재력", "거시경제", "시장심리", "CEO/리더십"],
          "rows": [
            {
              "주식": "종목명",
              "Overall": 0-100,
              "펀더멘탈": 0-100,
              "기술 잠재력": 0-100,
              "거시경제": 0-100,
              "시장심리": 0-100,
              "CEO/리더십": 0-100
            }
          ]
        }
      }
    },
    {
      "tabId": "keyStockAnalysis",
      "tabTitle": "핵심 종목 상세 분석",
      "content": {
        "analysisCards": [
          {
            "stockName": "종목명",
            "overallScore": 0-100,
            "detailedScores": [
              {"category": "펀더멘탈", "score": 0-100, "analysis": "최소 30자 분석"},
              {"category": "기술 잠재력", "score": 0-100, "analysis": "최소 30자 분석"},
              {"category": "거시경제", "score": 0-100, "analysis": "최소 30자 분석"},
              {"category": "시장심리", "score": 0-100, "analysis": "최소 30자 분석"},
              {"category": "CEO/리더십", "score": 0-100, "analysis": "최소 30자 분석"}
            ]
          }
        ]
      }
    }
  ]
}
```

**필수 요구사항:**
1. 모든 점수는 0-100 사이의 정수
2. tabs 배열은 정확히 4개 (dashboard, deepDive, allStockScores, keyStockAnalysis)
3. reportDate는 오늘 날짜 (YYYY-MM-DD 형식)
4. description, analysis, details 필드는 구체적이고 전문적으로 작성
5. Google Search를 활용하여 최신 정보 반영
6. 모든 텍스트는 한국어로 작성
7. **JSON 형식을 정확히 지켜서 출력** (추가 텍스트 없이 순수 JSON만)

이미지를 분석하여 위 스키마에 맞는 JSON을 생성하세요.
"""
```

#### Step 3: 에러 처리 개선

**파일**: `backend/services/gemini_service.py`

`analyze_portfolio_structured` 메서드의 예외 처리 부분:

```python
async def analyze_portfolio_structured(
    self,
    image_data_list: List[bytes],
    format_type: str = "json"
) -> Union[StructuredAnalysisResponse, AnalysisResponse]:
    """포트폴리오 분석 - format에 따라 JSON 또는 마크다운 반환"""
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    try:
        # ... 입력 검증 ...
        
        if format_type == "json":
            # 구조화된 JSON 출력
            try:
                portfolio_report = await self._call_gemini_structured(image_data_list)
            except ValueError as ve:
                # Pydantic 검증 실패 또는 스키마 불일치
                logger.error(f"JSON 스키마 검증 실패: {str(ve)}")
                raise ValueError(f"AI 응답이 예상 형식과 다릅니다. 다시 시도해 주세요.")
            
            return StructuredAnalysisResponse(
                portfolioReport=portfolio_report,
                processing_time=time.time() - start_time,
                request_id=request_id,
                images_processed=len(image_data_list)
            )
        
        else:
            # 기존 마크다운 출력
            # ... (변경 없음)
            
    except Exception as e:
        logger.error(f"포트폴리오 분석 실패: {str(e)}")
        raise
```

#### Step 4: 테스트 및 검증

1. **백엔드 테스트 실행:**
```bash
cd backend
./venv/bin/pytest tests/test_structured_output.py -v
```

2. **수동 테스트:**
```bash
# 프론트엔드에서 format=json으로 이미지 업로드 테스트
# 또는 curl로 직접 테스트:
curl -X POST http://localhost:8000/api/analyze?format=json \
  -F "file=@test_portfolio.png"
```

3. **검증 포인트:**
   - [ ] 400 에러가 사라지고 200 응답 반환
   - [ ] 응답 JSON이 4개 탭 포함
   - [ ] 각 탭의 content 구조가 올바름
   - [ ] Pydantic 검증이 정상 작동 (잘못된 JSON이면 ValueError)

#### 주의사항

1. **프롬프트 품질이 중요**: `response_schema`가 없으므로 프롬프트에 JSON 스키마를 명확히 명시해야 함
2. **재시도 로직 유지**: Gemini가 가끔 잘못된 형식을 반환할 수 있으므로 최대 3회 재시도
3. **응답 검증 강화**: `model_validate_json`이 실패하면 적절한 에러 메시지와 함께 400 반환
4. **로깅 강화**: 검증 실패 시 응답 텍스트 일부를 로깅하여 디버깅 용이

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

- [x] 백엔드 API가 `format=json`과 `format=markdown` 모두 지원
- [x] 프론트엔드에서 탭 뷰와 마크다운 뷰 전환 가능
- [ ] 4개 탭 모두 정상 렌더링
  - [x] Dashboard 탭 (총괄 요약)
  - [x] DeepDive 탭 (포트폴리오 심층 분석) ← **구현 완료**
  - [x] AllStockScores 탭 (개별 종목 스코어)
  - [ ] KeyStockAnalysis 탭 (핵심 종목 상세 분석) ← **구현 예정**
- [x] 기존 마크다운 출력 방식 정상 작동
- [x] 모든 테스트 통과 (42개)
- [x] 에러 처리 완료

### DeepDiveTab 구현 완료 기준 (상세)

- [x] DeepDiveTab.tsx 컴포넌트 파일 생성
- [x] TabbedAnalysisDisplay.tsx에 import 및 case 추가
- [ ] inDepthAnalysis 3개 항목이 카드로 정상 렌더링 (실제 데이터로 테스트 필요)
- [ ] 점수 배지와 진행 바가 올바르게 표시 (실제 데이터로 테스트 필요)
- [ ] opportunities 아코디언이 정상 작동 (실제 데이터로 테스트 필요)
- [ ] 점수별 색상 구분 정상 적용 (실제 데이터로 테스트 필요)
- [ ] 모바일 반응형 디자인 정상 작동 (실제 데이터로 테스트 필요)
- [ ] 다른 탭과 디자인 일관성 유지 (실제 데이터로 테스트 필요)

### KeyStockAnalysisTab 구현 완료 기준 (상세)

- [ ] KeyStockAnalysisTab.tsx 컴포넌트 파일 생성
- [ ] TabbedAnalysisDisplay.tsx에 import 및 case 추가
- [ ] analysisCards 배열의 모든 종목이 카드로 정상 렌더링
- [ ] 각 카드의 종목명과 종합 점수가 올바르게 표시
- [ ] 5개 평가 기준이 아코디언으로 정상 표시
- [ ] 아코디언 클릭 시 확장/축소 정상 작동
- [ ] 각 카드의 아코디언이 독립적으로 작동 (다른 카드에 영향 없음)
- [ ] 점수별 색상이 올바르게 적용 (80+: 녹색, 60+: 노란색, 60 미만: 빨간색)
- [ ] 진행 바가 점수에 맞게 표시
- [ ] 상세 분석 텍스트가 읽기 쉽게 표시
- [ ] 반응형 디자인 정상 작동 (모바일: 1열, 데스크톱: 2열)
- [ ] 다른 탭과 디자인 일관성 유지
- [ ] 3-5개 종목에 대해 UI 정상 작동
- [ ] 빈 배열일 때 빈 상태 메시지 정상 표시
