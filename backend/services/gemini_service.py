"""
Gemini API 연동 서비스 - 마크다운 텍스트 출력

이 모듈은 Google Gemini 2.5 Flash API를 사용하여 포트폴리오 이미지를 분석하고
expected_result.md와 동일한 형식의 마크다운 텍스트를 생성합니다.
"""

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
        self.timeout = int(os.getenv("GEMINI_TIMEOUT", "120"))  # Google Search 포함
        self.max_retries = int(os.getenv("GEMINI_MAX_RETRIES", "3"))
        
        # 캐시 딕셔너리 (실제 환경에서는 Redis 등 사용)
        self._cache: Dict[str, str] = {}
        
        logger.info(f"GeminiService 초기화 완료 - 모델: {self.model_name}, 출력: 마크다운 텍스트, Google Search: 활성화")

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
                logger.info(f"Gemini API 호출 시도 {attempt + 1}/{self.max_retries} (Google Search 활성화)")
                
                # 이미지 파트 생성
                image_part = Part.from_bytes(
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
                
                # Google Search 도구 활성화 (올바른 방식)
                from google.genai import types
                grounding_tool = types.Tool(
                    google_search=types.GoogleSearch()
                )
                
                # config에 tools 추가
                config.tools = [grounding_tool]
                
                # API 호출 (동기 호출)
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[prompt, image_part],
                    config=config
                )
                
                if response and response.text:
                    markdown_text = response.text.strip()
                    logger.info("Gemini API 마크다운 응답 성공 (Google Search 통합)")
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
                
                # Google Search 관련 오류인 경우 특별 처리
                if "search" in str(e).lower():
                    logger.warning("Google Search 기능 관련 오류, 기본 분석으로 계속 진행")
                
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
