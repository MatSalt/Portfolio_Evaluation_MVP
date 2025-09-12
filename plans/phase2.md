# Phase 2: 백엔드 핵심 기능 구현 (3-4일)

## 📋 개요
이 문서는 Portfolio Evaluation MVP의 백엔드 핵심 기능을 구현하기 위한 상세한 계획과 예시 코드를 제공합니다. Google Gemini 2.5 Flash API를 활용하여 포트폴리오 이미지를 분석하고 **expected_result.md와 동일한 형식의 마크다운 텍스트로 전문적인 투자 분석 리포트를 생성**하는 간단하고 안정적인 MVP 구현이 핵심입니다.

**참고 자료 (필수 확인)**:
- **Gemini API 공식 문서**: https://github.com/googleapis/python-genai, https://googleapis.github.io/python-genai/ [[memory:8821806]]
- **FastAPI 공식 문서**: https://fastapi.tiangolo.com/reference/
- **Gemini LLMS 상세 정보**: `/Users/choongheon/Desktop/Rinia/projects/Portfolio_Evaluation_MVP/Docs/gemini_llms.txt`
- **expected_result.md**: 마크다운 출력 형식 참고

---

## 🏗️ 2.1 FastAPI 기본 구조 구축

### 2.1.1 프로젝트 구조 완성
```
backend/
├── main.py                  # FastAPI 앱 진입점 (기존)
├── .env.example            # 환경변수 예시 파일
├── .env                    # 실제 환경변수 파일 (gitignore)
├── api/
│   ├── __init__.py
│   └── analyze.py          # 포트폴리오 분석 API
├── models/
│   ├── __init__.py
│   └── portfolio.py        # Pydantic 모델 정의
├── services/
│   ├── __init__.py
│   └── gemini_service.py   # Gemini API 연동 서비스
├── utils/
│   ├── __init__.py
│   └── image_utils.py      # 이미지 처리 유틸리티
├── tests/
│   ├── __init__.py
│   ├── test_analyze_api.py
│   ├── test_gemini_service.py
│   └── test_image_utils.py
└── requirements.txt        # 기존
```

### 2.1.2 main.py 개선 (기존 파일 업데이트)
```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import logging
from api.analyze import router as analyze_router

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="Portfolio Evaluation MVP API",
    description="AI 포트폴리오 분석 API - Gemini 2.5 Flash 기반 마크다운 리포트 생성",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("FRONTEND_URL", "http://localhost:3000"),
        "http://localhost:3000",
        "https://portfolio-evaluation-mvp.vercel.app"  # 배포용
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# 글로벌 예외 핸들러
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "내부 서버 오류가 발생했습니다.", "detail": str(exc)}
    )

# 라우터 등록
app.include_router(analyze_router, prefix="/api", tags=["분석"])

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Portfolio Evaluation MVP API", 
        "status": "running",
        "version": "0.1.0",
        "docs": "/docs",
        "output_format": "markdown_text"
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    try:
        # Gemini API 키 확인
        api_key = os.getenv("GEMINI_API_KEY")
        api_key_status = "configured" if api_key else "missing"
        
        return {
            "status": "healthy", 
            "version": "0.1.0",
            "gemini_api_key": api_key_status,
            "environment": os.getenv("ENVIRONMENT", "development"),
            "output_format": "markdown_text"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "False").lower() == "true",
        log_level="info"
    )
```

### 2.1.3 환경변수 설정 (.env.example)
```bash
# Gemini API 설정
GEMINI_API_KEY=your_gemini_api_key_here

# 서버 설정
HOST=0.0.0.0
PORT=8000
DEBUG=True
ENVIRONMENT=development

# CORS 설정
FRONTEND_URL=http://localhost:3000

# 이미지 처리 설정
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_IMAGE_TYPES=image/jpeg,image/png,image/jpg

# Gemini API 설정
GEMINI_MODEL=gemini-2.5-flash
GEMINI_TIMEOUT=30
GEMINI_MAX_RETRIES=3

# 마크다운 출력 설정
OUTPUT_FORMAT=markdown
```

---

## 🔧 2.2 데이터 모델 정의 (models/portfolio.py)

```python
from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum
import time

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
    
    @validator('content')
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
```

---

## 🔨 2.3 Gemini API 연동 서비스 (services/gemini_service.py)

```python
import os
import asyncio
import base64
import hashlib
from typing import Optional, Dict
from io import BytesIO
import logging
from google import genai
from google.genai.types import GenerateContentConfig, Part

from models.portfolio import AnalysisResponse, SAMPLE_MARKDOWN_CONTENT
from utils.image_utils import validate_image, optimize_image

# 로깅 설정
logger = logging.getLogger(__name__)

class GeminiService:
    """Gemini API 연동 서비스 - 마크다운 텍스트 출력"""
    
    def __init__(self):
        """서비스 초기화"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
        
        # Gemini 클라이언트 초기화
        self.client = genai.Client(api_key=self.api_key)
        
        # 설정값
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.timeout = int(os.getenv("GEMINI_TIMEOUT", "30"))
        self.max_retries = int(os.getenv("GEMINI_MAX_RETRIES", "3"))
        
        # 캐시 딕셔너리 (실제 환경에서는 Redis 등 사용)
        self._cache: Dict[str, str] = {}
        
        logger.info(f"GeminiService 초기화 완료 - 모델: {self.model_name}, 출력: 마크다운 텍스트")

    def _generate_image_hash(self, image_data: bytes) -> str:
        """이미지 데이터의 해시값 생성"""
        return hashlib.md5(image_data).hexdigest()

    def _get_portfolio_analysis_prompt(self) -> str:
        """포트폴리오 분석용 마크다운 프롬프트 생성"""
        return """
당신은 전문적인 포트폴리오 분석가입니다. 제공된 증권사 앱 스크린샷에서 보유 종목을 추출하고 종합적인 투자 분석을 수행하세요.

**중요: 다음 마크다운 형식으로 정확히 출력하세요 (JSON 없이 마크다운 텍스트만):**

**AI 총평:** [포트폴리오 전략과 주요 리스크를 2-3문장으로 요약]

**포트폴리오 종합 리니아 스코어: [0-100 사이 정수] / 100**

**3대 핵심 기준 스코어:**

- **성장 잠재력:** [0-100 사이 정수] / 100
- **안정성 및 방어력:** [0-100 사이 정수] / 100  
- **전략적 일관성:** [0-100 사이 정수] / 100

**[1] 포트폴리오 리니아 스코어 심층 분석**

**1.1 성장 잠재력 분석 ([점수] / 100): [제목]**

[성장 잠재력에 대한 3-4문장의 구체적 분석]

**1.2 안정성 및 방어력 분석 ([점수] / 100): [제목]**

[안정성 및 방어력에 대한 3-4문장의 구체적 분석]

**1.3 전략적 일관성 분석 ([점수] / 100): [제목]**

[전략적 일관성에 대한 3-4문장의 구체적 분석]

**[2] 포트폴리오 강점 및 약점, 그리고 기회**

**💪 강점**

- **[강점 1 제목]:** [1-2문장, 실행 가능한 인사이트]
- **[강점 2 제목]:** [1-2문장, 실행 가능한 인사이트]

**📉 약점**

- **[약점 1 제목]:** [1-2문장, 구체적 개선방안]
- **[약점 2 제목]:** [1-2문장, 구체적 개선방안]

**💡 기회 및 개선 방안**

- **[기회 1 제목]:** [What-if 시나리오 포함한 설명]
- **[기회 2 제목]:** [What-if 시나리오 포함한 설명]

**[3] 개별 종목 리니아 스코어 상세 분석**

**3.1 스코어 요약 테이블**

| 주식 | Overall (100점 만점) | 펀더멘탈 | 기술 잠재력 | 거시경제 | 시장심리 | CEO/리더십 |
| --- | --- | --- | --- | --- | --- | --- |
| **[종목명 1]** | **[점수]** | [점수] | [점수] | [점수] | [점수] | [점수] |
| **[종목명 2]** | **[점수]** | [점수] | [점수] | [점수] | [점수] | [점수] |

**3.2 개별 종목 분석 카드**

**1. [종목명] - Overall: [점수] / 100**

- **펀더멘탈 ([점수]/100):** [재무 상태 및 실적 분석]
- **기술 잠재력 ([점수]/100):** [기술력 및 혁신 능력 분석]
- **거시경제 ([점수]/100):** [거시경제적 영향 분석]
- **시장심리 ([점수]/100):** [시장 인식 및 투자 심리 분석]
- **CEO/리더십 ([점수]/100):** [경영진 리더십 및 전략 분석]

분석 규칙:
1. AI 총평: 포트폴리오의 투자 전략과 주요 리스크를 2-3문장으로 명확히 요약
2. 모든 점수는 0-100 사이의 정수로 평가
3. 각 기준별로 3-4문장의 구체적이고 전문적인 분석 제공
4. 강점/약점/기회: 각 항목은 1-2문장으로 실행 가능한 인사이트 제공
5. 기회에는 간단한 "What-if" 시나리오 포함
6. 식별된 모든 종목에 대해 5가지 기준별 상세 평가
7. 모든 텍스트는 한국어로 작성
8. 전문적인 투자 분석 언어 사용
9. 구체적인 예시와 데이터 포인트 포함

**반드시 마크다운 형식만 출력하고, JSON이나 다른 형식은 사용하지 마세요.**
"""

    async def _encode_image_to_base64(self, image_data: bytes) -> str:
        """이미지를 Base64로 인코딩"""
        try:
            # 이미지 최적화
            optimized_data = await optimize_image(image_data)
            return base64.b64encode(optimized_data).decode('utf-8')
        except Exception as e:
            logger.error(f"이미지 Base64 인코딩 실패: {str(e)}")
            raise ValueError(f"이미지 인코딩 실패: {str(e)}")

    async def _call_gemini_api(self, prompt: str, image_base64: str) -> str:
        """Gemini API 호출 - 마크다운 텍스트 반환"""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Gemini API 호출 시도 {attempt + 1}/{self.max_retries}")
                
                # 이미지 파트 생성
                image_part = Part.from_data(
                    data=base64.b64decode(image_base64),
                    mime_type="image/jpeg"
                )
                
                # 설정 생성 - 마크다운 텍스트 생성에 최적화
                config = GenerateContentConfig(
                    temperature=0.3,  # 일관된 분석을 위해 낮은 온도
                    top_p=0.9,
                    top_k=40,
                    max_output_tokens=8192,  # 긴 마크다운 텍스트를 위해 증가
                    response_mime_type="text/plain"  # 플레인 텍스트 (마크다운)
                )
                
                # API 호출
                response = await asyncio.wait_for(
                    self.client.agenerate_content(
                        model=self.model_name,
                        contents=[prompt, image_part],
                        config=config
                    ),
                    timeout=self.timeout
                )
                
                if response and response.text:
                    markdown_text = response.text.strip()
                    logger.info("Gemini API 마크다운 응답 성공")
                    return markdown_text
                else:
                    raise ValueError("Gemini API에서 빈 응답 받음")
                    
            except asyncio.TimeoutError:
                logger.warning(f"Gemini API 타임아웃 (시도 {attempt + 1})")
                if attempt == self.max_retries - 1:
                    raise TimeoutError(f"{self.timeout}초 내에 Gemini API 응답 없음")
                await asyncio.sleep(2 ** attempt)  # 지수적 백오프
                
            except Exception as e:
                logger.error(f"Gemini API 호출 실패 (시도 {attempt + 1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)

    def _validate_markdown_response(self, markdown_text: str) -> str:
        """마크다운 응답 검증 및 정제"""
        try:
            # 기본 검증
            if not markdown_text or len(markdown_text.strip()) < 100:
                raise ValueError("마크다운 텍스트가 너무 짧습니다.")
            
            # 필수 섹션 확인
            required_sections = [
                "**AI 총평:**",
                "**포트폴리오 종합 리니아 스코어:",
                "**3대 핵심 기준 스코어:**",
                "**성장 잠재력:**",
                "**안정성 및 방어력:**",
                "**전략적 일관성:**"
            ]
            
            for section in required_sections:
                if section not in markdown_text:
                    logger.warning(f"필수 섹션 누락: {section}")
            
            logger.info("마크다운 응답 검증 완료")
            return markdown_text.strip()
            
        except Exception as e:
            logger.error(f"마크다운 응답 검증 실패: {str(e)}")
            raise ValueError(f"마크다운 형식이 올바르지 않습니다: {str(e)}")

    async def analyze_portfolio_image(
        self, 
        image_data: bytes, 
        use_cache: bool = True
    ) -> str:
        """
        포트폴리오 이미지 분석 - 마크다운 텍스트 반환
        
        Args:
            image_data: 이미지 바이트 데이터
            use_cache: 캐시 사용 여부
            
        Returns:
            str: expected_result.md와 동일한 형식의 마크다운 텍스트
            
        Raises:
            ValueError: 이미지 검증 실패 또는 API 응답 검증 실패
            TimeoutError: API 호출 타임아웃
            Exception: 기타 예외
        """
        try:
            # 이미지 검증
            await validate_image(image_data)
            
            # 캐시 확인
            if use_cache:
                image_hash = self._generate_image_hash(image_data)
                if image_hash in self._cache:
                    logger.info("캐시된 분석 결과 반환")
                    return self._cache[image_hash]
            
            # 이미지 Base64 인코딩
            image_base64 = await self._encode_image_to_base64(image_data)
            
            # 프롬프트 생성
            prompt = self._get_portfolio_analysis_prompt()
            
            # Gemini API 호출
            markdown_text = await self._call_gemini_api(prompt, image_base64)
            
            # 마크다운 응답 검증
            validated_markdown = self._validate_markdown_response(markdown_text)
            
            # 캐시 저장
            if use_cache:
                self._cache[image_hash] = validated_markdown
                logger.info(f"분석 결과 캐시 저장 (해시: {image_hash[:8]})")
            
            return validated_markdown
            
        except Exception as e:
            logger.error(f"포트폴리오 이미지 분석 실패: {str(e)}")
            raise

    async def get_sample_analysis(self) -> str:
        """샘플 분석 결과 반환 (테스트용) - 마크다운 텍스트"""
        try:
            logger.info("샘플 마크다운 분석 결과 반환")
            return SAMPLE_MARKDOWN_CONTENT
        except Exception as e:
            logger.error(f"샘플 분석 결과 생성 실패: {str(e)}")
            raise ValueError(f"샘플 데이터 오류: {str(e)}")

# 싱글톤 인스턴스
_gemini_service: Optional[GeminiService] = None

async def get_gemini_service() -> GeminiService:
    """GeminiService 싱글톤 인스턴스 반환"""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
```

---

## 🖼️ 2.4 이미지 처리 유틸리티 (utils/image_utils.py)

```python
import os
from typing import Tuple, Optional
from io import BytesIO
from PIL import Image, ImageOps
import logging

logger = logging.getLogger(__name__)

# 설정값
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
ALLOWED_MIME_TYPES = os.getenv("ALLOWED_IMAGE_TYPES", "image/jpeg,image/png,image/jpg").split(",")
MAX_IMAGE_DIMENSION = 2048  # 최대 이미지 크기
JPEG_QUALITY = 85  # JPEG 압축 품질

async def validate_image(image_data: bytes, filename: Optional[str] = None) -> None:
    """
    이미지 파일 검증
    
    Args:
        image_data: 이미지 바이트 데이터
        filename: 파일명 (선택적)
        
    Raises:
        ValueError: 검증 실패
    """
    try:
        # 파일 크기 검증
        if len(image_data) > MAX_FILE_SIZE:
            raise ValueError(f"파일 크기가 {MAX_FILE_SIZE / 1024 / 1024:.1f}MB를 초과합니다.")
        
        if len(image_data) == 0:
            raise ValueError("빈 파일입니다.")
        
        # PIL로 이미지 검증
        try:
            with Image.open(BytesIO(image_data)) as img:
                # 이미지 포맷 검증
                if img.format not in ['JPEG', 'PNG', 'JPG']:
                    raise ValueError(f"지원하지 않는 이미지 형식입니다. (지원: JPEG, PNG)")
                
                # 이미지 크기 검증
                width, height = img.size
                if width < 100 or height < 100:
                    raise ValueError("이미지 크기가 너무 작습니다. (최소 100x100)")
                
                if width > 10000 or height > 10000:
                    raise ValueError("이미지 크기가 너무 큽니다. (최대 10000x10000)")
                
                # 이미지 모드 검증 (RGB, RGBA만 허용)
                if img.mode not in ['RGB', 'RGBA', 'L']:
                    logger.warning(f"이미지 모드 변환 필요: {img.mode} -> RGB")
                
                logger.info(f"이미지 검증 성공: {width}x{height}, {img.format}, {img.mode}")
                
        except Exception as e:
            raise ValueError(f"유효하지 않은 이미지 파일입니다: {str(e)}")
            
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"이미지 검증 중 오류: {str(e)}")
        raise ValueError(f"이미지 검증 실패: {str(e)}")

async def optimize_image(image_data: bytes) -> bytes:
    """
    이미지 최적화 (크기 조정 및 압축)
    
    Args:
        image_data: 원본 이미지 바이트 데이터
        
    Returns:
        bytes: 최적화된 이미지 바이트 데이터
        
    Raises:
        ValueError: 이미지 처리 실패
    """
    try:
        with Image.open(BytesIO(image_data)) as img:
            original_size = len(image_data)
            original_dimensions = img.size
            
            # EXIF 정보 기반 회전 수정
            img = ImageOps.exif_transpose(img)
            
            # RGBA를 RGB로 변환 (JPEG 호환성)
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])  # 알파 채널을 마스크로 사용
                img = background
            elif img.mode not in ['RGB', 'L']:
                img = img.convert('RGB')
            
            # 이미지 크기 조정
            if max(img.size) > MAX_IMAGE_DIMENSION:
                img.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION), Image.Resampling.LANCZOS)
                logger.info(f"이미지 크기 조정: {original_dimensions} -> {img.size}")
            
            # 최적화된 이미지 저장
            output_buffer = BytesIO()
            
            if img.format == 'PNG' or any(band.mode == 'RGBA' for band in [img]):
                # PNG는 무손실 압축
                img.save(output_buffer, format='PNG', optimize=True)
                format_used = 'PNG'
            else:
                # JPEG 압축
                img.save(output_buffer, format='JPEG', quality=JPEG_QUALITY, optimize=True)
                format_used = 'JPEG'
            
            optimized_data = output_buffer.getvalue()
            optimized_size = len(optimized_data)
            
            compression_ratio = (1 - optimized_size / original_size) * 100
            logger.info(f"이미지 최적화 완료: {format_used}, "
                       f"{original_size:,} -> {optimized_size:,} bytes "
                       f"({compression_ratio:.1f}% 압축)")
            
            return optimized_data
            
    except Exception as e:
        logger.error(f"이미지 최적화 실패: {str(e)}")
        raise ValueError(f"이미지 처리 실패: {str(e)}")

async def get_image_info(image_data: bytes) -> dict:
    """
    이미지 정보 추출
    
    Args:
        image_data: 이미지 바이트 데이터
        
    Returns:
        dict: 이미지 정보
    """
    try:
        with Image.open(BytesIO(image_data)) as img:
            return {
                "format": img.format,
                "mode": img.mode,
                "size": img.size,
                "width": img.size[0],
                "height": img.size[1],
                "file_size": len(image_data),
                "has_transparency": img.mode in ['RGBA', 'LA'] or 'transparency' in img.info
            }
    except Exception as e:
        logger.error(f"이미지 정보 추출 실패: {str(e)}")
        return {}

# 지원되는 MIME 타입 확인
def is_supported_image_type(content_type: str) -> bool:
    """지원되는 이미지 타입인지 확인"""
    return content_type.lower() in [mime.strip().lower() for mime in ALLOWED_MIME_TYPES]

# 파일 확장자로 MIME 타입 추측
def guess_content_type(filename: str) -> Optional[str]:
    """파일 확장자로 MIME 타입 추측"""
    if not filename:
        return None
    
    extension = filename.lower().split('.')[-1]
    mime_map = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png'
    }
    
    return mime_map.get(extension)
```

---

## 🚀 2.5 API 엔드포인트 구현 (api/analyze.py)

```python
import time
import uuid
import logging
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse

from models.portfolio import (
    AnalysisResponse, AnalysisRequest, 
    ErrorResponse
)
from services.gemini_service import get_gemini_service, GeminiService
from utils.image_utils import validate_image, is_supported_image_type, get_image_info

# 로깅 설정
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter()

@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    summary="포트폴리오 이미지 분석",
    description="업로드된 포트폴리오 스크린샷을 분석하여 expected_result.md와 동일한 형식의 마크다운 텍스트 리포트를 생성합니다."
)
async def analyze_portfolio(
    file: UploadFile = File(..., description="포트폴리오 스크린샷 파일 (JPEG, PNG)"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    gemini_service: GeminiService = Depends(get_gemini_service)
):
    """
    포트폴리오 이미지 분석 엔드포인트
    
    Args:
        file: 업로드된 이미지 파일
        background_tasks: 백그라운드 작업
        gemini_service: Gemini 서비스 인스턴스
    
    Returns:
        AnalysisResponse: 마크다운 텍스트 분석 결과
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        logger.info(f"포트폴리오 분석 요청 시작 (ID: {request_id})")
        
        # 1. 파일 기본 검증
        if not file:
            raise HTTPException(
                status_code=400,
                detail="파일이 업로드되지 않았습니다."
            )
        
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="파일명이 없습니다."
            )
        
        # Content-Type 검증
        if not is_supported_image_type(file.content_type):
            raise HTTPException(
                status_code=400,
                detail=f"지원하지 않는 파일 형식입니다. (지원: JPEG, PNG)"
            )
        
        # 2. 파일 데이터 읽기
        try:
            image_data = await file.read()
        except Exception as e:
            logger.error(f"파일 읽기 실패 (ID: {request_id}): {str(e)}")
            raise HTTPException(
                status_code=400,
                detail="파일을 읽을 수 없습니다."
            )
        
        # 3. 이미지 검증
        try:
            await validate_image(image_data, file.filename)
            logger.info(f"이미지 검증 성공 (ID: {request_id})")
        except ValueError as e:
            logger.warning(f"이미지 검증 실패 (ID: {request_id}): {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
        
        # 4. 이미지 정보 로깅
        image_info = await get_image_info(image_data)
        logger.info(f"이미지 정보 (ID: {request_id}): {image_info}")
        
        # 5. Gemini API를 통한 마크다운 텍스트 분석
        try:
            logger.info(f"Gemini 마크다운 분석 시작 (ID: {request_id})")
            markdown_content = await gemini_service.analyze_portfolio_image(image_data)
            logger.info(f"Gemini 마크다운 분석 완료 (ID: {request_id})")
            
        except TimeoutError as e:
            logger.error(f"Gemini API 타임아웃 (ID: {request_id}): {str(e)}")
            raise HTTPException(
                status_code=503,
                detail="분석 요청 시간이 초과되었습니다. 잠시 후 다시 시도해 주세요."
            )
        except ValueError as e:
            logger.error(f"Gemini API 응답 오류 (ID: {request_id}): {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="분석 결과 처리 중 오류가 발생했습니다."
            )
        except Exception as e:
            logger.error(f"Gemini 분석 실패 (ID: {request_id}): {str(e)}")
            raise HTTPException(
                status_code=503,
                detail="AI 분석 서비스에 일시적인 문제가 있습니다. 잠시 후 다시 시도해 주세요."
            )
        
        # 6. 응답 생성
        processing_time = time.time() - start_time
        
        response = AnalysisResponse(
            content=markdown_content,
            processing_time=processing_time,
            request_id=request_id
        )
        
        # 7. 백그라운드 로깅
        background_tasks.add_task(
            log_analysis_success,
            request_id=request_id,
            filename=file.filename,
            file_size=len(image_data),
            processing_time=processing_time,
            content_length=len(markdown_content)
        )
        
        logger.info(f"포트폴리오 분석 완료 (ID: {request_id}, {processing_time:.2f}초)")
        return response
        
    except HTTPException:
        # HTTPException은 그대로 전달
        raise
    except Exception as e:
        # 예상치 못한 오류
        logger.error(f"예상치 못한 오류 (ID: {request_id}): {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="서버 내부 오류가 발생했습니다."
        )

@router.get(
    "/sample",
    response_model=AnalysisResponse,
    summary="샘플 분석 결과",
    description="테스트용 샘플 포트폴리오 마크다운 분석 결과를 반환합니다."
)
async def get_sample_analysis(
    gemini_service: GeminiService = Depends(get_gemini_service)
):
    """샘플 분석 결과 반환 (테스트/데모용) - 마크다운 텍스트"""
    request_id = str(uuid.uuid4())
    
    try:
        logger.info(f"샘플 마크다운 분석 요청 (ID: {request_id})")
        
        markdown_content = await gemini_service.get_sample_analysis()
        
        response = AnalysisResponse(
            content=markdown_content,
            processing_time=0.1,  # 즉시 반환
            request_id=request_id
        )
        
        logger.info(f"샘플 마크다운 분석 반환 완료 (ID: {request_id})")
        return response
        
    except Exception as e:
        logger.error(f"샘플 분석 실패 (ID: {request_id}): {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="샘플 데이터 생성 실패"
        )

# 백그라운드 작업 함수들
async def log_analysis_success(
    request_id: str,
    filename: str,
    file_size: int,
    processing_time: float,
    content_length: int
):
    """분석 성공 로깅 (백그라운드)"""
    logger.info(
        f"분석 완료 통계 - "
        f"ID: {request_id}, "
        f"파일: {filename}, "
        f"크기: {file_size:,}bytes, "
        f"처리시간: {processing_time:.2f}초, "
        f"마크다운 길이: {content_length:,}자"
    )

# 에러 핸들러
@router.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """HTTP 예외 처리"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            code=str(exc.status_code)
        ).dict()
    )
```

---

## 🧪 2.6 테스트 코드 작성

### 2.6.1 Gemini 서비스 테스트 (tests/test_gemini_service.py)
```python
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
```

### 2.6.2 API 엔드포인트 테스트 (tests/test_analyze_api.py)
```python
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
```

---

## 📋 2.7 개발 우선순위 및 체크리스트

### Phase 2 구현 순서
1. **[1일차]** 데이터 모델 및 기본 구조
   - [ ] `models/portfolio.py` 완성 (마크다운 응답 모델)
   - [ ] `main.py` 개선 (라우터, 미들웨어, 예외 처리)
   - [ ] 환경변수 설정 완료

2. **[2일차]** 이미지 처리 및 유틸리티
   - [ ] `utils/image_utils.py` 구현
   - [ ] 이미지 검증 및 최적화 기능
   - [ ] 단위 테스트 작성

3. **[3일차]** Gemini API 연동 (마크다운 출력)
   - [ ] `services/gemini_service.py` 구현
   - [ ] **마크다운 프롬프트 엔지니어링 완성**
   - [ ] API 호출 및 마크다운 텍스트 응답 처리 테스트

4. **[4일차]** API 엔드포인트 완성
   - [ ] `api/analyze.py` 구현
   - [ ] 마크다운 텍스트 응답 반환
   - [ ] 에러 핸들링 및 로깅
   - [ ] 통합 테스트 실행

### 품질 보증 체크리스트
- [ ] **코드 품질**: Black, isort, flake8 통과
- [ ] **테스트 커버리지**: 80% 이상
- [ ] **에러 처리**: 모든 예외 상황 처리
- [ ] **로깅**: 적절한 로그 레벨 및 메시지
- [ ] **보안**: API 키 보호, 입력 검증
- [ ] **성능**: 이미지 최적화, 캐싱
- [ ] **문서화**: 함수 및 클래스 독스트링
- [ ] **마크다운 출력**: expected_result.md와 동일한 형식 준수

### 검증 항목
1. **기능 검증**
   - [ ] 정상 이미지 업로드 및 분석
   - [ ] 잘못된 파일 타입 거부
   - [ ] 파일 크기 제한 동작
   - [ ] **마크다운 텍스트 출력 품질 확인**

2. **성능 검증**
   - [ ] 이미지 처리 시간 30초 이내
   - [ ] 메모리 사용량 최적화
   - [ ] 캐시 기능 동작

3. **에러 처리 검증**
   - [ ] 네트워크 오류 시 재시도
   - [ ] 타임아웃 처리
   - [ ] 사용자 친화적 에러 메시지

---

## 🔧 2.8 환경 설정 및 실행

### 개발 환경 설정
```bash
# 1. 가상환경 활성화
cd backend
source venv/bin/activate  # Linux/Mac
# 또는 venv\Scripts\activate  # Windows

# 2. 환경변수 설정
cp .env.example .env
# .env 파일에서 GEMINI_API_KEY 설정

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 코드 품질 도구 실행
black .
isort .
flake8 .

# 5. 테스트 실행
pytest tests/ -v --cov=.

# 6. 개발 서버 실행
python main.py
```

### API 테스트
```bash
# 헬스 체크
curl http://localhost:8000/health

# 샘플 마크다운 분석 결과
curl http://localhost:8000/api/analyze/sample

# 실제 이미지 분석 (마크다운 출력)
curl -X POST "http://localhost:8000/api/analyze" \
     -F "file=@portfolio_screenshot.jpg"
```

### 주요 변경사항 요약
1. **JSON → 마크다운**: 복잡한 JSON 구조 대신 expected_result.md와 동일한 마크다운 텍스트 출력
2. **프롬프트 변경**: JSON 요구 대신 마크다운 형식 요구로 변경
3. **응답 모델 단순화**: AnalysisResponse에 content(마크다운 텍스트) 필드만 포함
4. **검증 로직 변경**: JSON 파싱 대신 마크다운 형식 검증
5. **테스트 업데이트**: 마크다운 출력에 맞는 테스트 케이스로 변경

---

이 계획을 따라 단계별로 구현하면 expected_result.md와 동일한 형식의 마크다운 텍스트를 출력하는 안정적이고 간단한 MVP 백엔드 시스템을 완성할 수 있습니다. 🚀

<function_calls>
<invoke name="todo_write">
<parameter name="merge">true