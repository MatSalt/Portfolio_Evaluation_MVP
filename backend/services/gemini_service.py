"""
Gemini API 연동 서비스 - 마크다운 텍스트 출력

이 모듈은 Google Gemini 2.5 Flash API를 사용하여 포트폴리오 이미지를 분석하고
expected_result.md와 동일한 형식의 마크다운 텍스트를 생성합니다.
"""

import os
import asyncio
import base64
import hashlib
from typing import Optional, Dict, List
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
        self.timeout = int(os.getenv("GEMINI_TIMEOUT", "180"))  # 다중 이미지 처리를 위한 타임아웃 증가 (3분)
        self.max_retries = int(os.getenv("GEMINI_MAX_RETRIES", "3"))
        
        # 캐시 딕셔너리 (실제 환경에서는 Redis 등 사용)
        self._cache: Dict[str, str] = {}
        
        logger.info(f"GeminiService 초기화 완료 - 모델: {self.model_name}, 출력: 마크다운 텍스트, Google Search: 활성화, 다중 이미지: 지원")

    def _generate_image_hash(self, image_data: bytes) -> str:
        """이미지 데이터의 해시값 생성"""
        return hashlib.md5(image_data).hexdigest()

    def _generate_multiple_cache_key(self, image_data_list: List[bytes]) -> str:
        """다중 이미지용 캐시 키 생성"""
        # 모든 이미지의 해시를 조합하여 캐시 키 생성
        combined_hash = hashlib.md5()
        for image_data in image_data_list:
            image_hash = hashlib.md5(image_data).hexdigest()
            combined_hash.update(image_hash.encode())
        
        return f"multiple_{len(image_data_list)}_{combined_hash.hexdigest()}"

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

    def _get_multiple_image_prompt(self) -> str:
        """다중 이미지 분석용 프롬프트"""
        return """
        당신은 포트폴리오 분석 전문가입니다. 위에 제공된 여러 포트폴리오 이미지들을 종합적으로 분석해주세요.

        각 이미지를 개별적으로 분석한 후, 전체적인 포트폴리오 상황을 종합하여 
        다음 마크다운 형식으로 정확히 출력하세요 (추가 텍스트 없이):

        **AI 총평:** [포트폴리오 전략과 주요 리스크를 2-3문장으로 요약]

        **포트폴리오 종합 리니아 스코어: [0-100] / 100**

        **3대 핵심 기준 스코어:**

        - **성장 잠재력:** [0-100] / 100
        - **안정성 및 방어력:** [0-100] / 100
        - **전략적 일관성:** [0-100] / 100

        **[1] 포트폴리오 리니아 스코어 심층 분석**

        **1.1 성장 잠재력 분석 ([점수] / 100): [제목]**

        [3-4문장의 구체적 분석]

        **1.2 안정성 및 방어력 분석 ([점수] / 100): [제목]**

        [3-4문장의 구체적 분석]

        **1.3 전략적 일관성 분석 ([점수] / 100): [제목]**

        [3-4문장의 구체적 분석]

        **[2] 포트폴리오 강점 및 약점, 그리고 기회**

        **💪 강점**

        - [강점 1: 1-2문장, 실행 가능한 인사이트]
        - [강점 2: 1-2문장, 실행 가능한 인사이트]

        **📉 약점**

        - [약점 1: 1-2문장, 구체적 개선방안]
        - [약점 2: 1-2문장, 구체적 개선방안]

        **💡 기회 및 개선 방안**

        - [기회 1: What-if 시나리오 포함]
        - [기회 2: 구체적 실행 방안]

        **[3] 개별 종목 리니아 스코어 상세 분석**

        **3.1 스코어 요약 테이블**

        | 주식 | Overall (100점 만점) | 펀더멘탈 | 기술 잠재력 | 거시경제 | 시장심리 | CEO/리더십 |
        | --- | --- | --- | --- | --- | --- | --- |
        | [종목명] | [점수] | [점수] | [점수] | [점수] | [점수] | [점수] |

        **3.2 개별 종목 분석 카드**

        **[번호]. [종목명] - Overall: [점수] / 100**

        - **펀더멘탈 ([점수]/100):** [상세 분석]
        - **기술 잠재력 ([점수]/100):** [상세 분석]
        - **거시경제 ([점수]/100):** [상세 분석]
        - **시장심리 ([점수]/100):** [상세 분석]
        - **CEO/리더십 ([점수]/100):** [상세 분석]

        다중 이미지 분석 시 고려사항:
        1. 각 이미지의 포트폴리오 구성을 개별적으로 분석
        2. 시간에 따른 변화가 있다면 시계열 분석 포함
        3. 전체적인 투자 전략의 일관성 평가
        4. 리스크 분산 정도 종합 평가
        5. 수익률 추이 분석 (여러 시점이 있는 경우)

        분석 규칙:
        - 모든 점수는 0-100 사이의 정수로 평가
        - 각 분석은 구체적이고 전문적인 내용으로 작성
        - 강점/약점/기회는 실행 가능한 인사이트 제공
        - 기회에는 간단한 "What-if" 시나리오 포함
        - 모든 텍스트는 한국어로 작성
        - 전문적인 투자 분석 언어 사용
        - 구체적인 예시와 데이터 포인트 포함
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

    async def _call_gemini_api_multiple(self, image_data_list: List[bytes]) -> str:
        """
        Gemini API 다중 이미지 호출
        
        참고: https://ai.google.dev/gemini-api/docs/image-understanding?hl=ko
        - 요청당 최대 3,600개 이미지 지원 (우리는 5개로 제한)
        - 각 이미지는 768x768 타일로 처리되며 타일당 258 토큰
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Gemini API 다중 이미지 호출 시도 {attempt + 1}/{self.max_retries} (Google Search 활성화)")
                
                # contents 배열 구성 - 이미지들 먼저, 프롬프트는 마지막
                contents = []
                
                # 1. 이미지들을 contents에 추가
                for i, image_data in enumerate(image_data_list):
                    try:
                        image_part = Part.from_bytes(
                            data=image_data,
                            mime_type='image/jpeg'
                        )
                        contents.append(image_part)
                        logger.debug(f"이미지 {i+1} 추가됨 (크기: {len(image_data)} bytes)")
                    except Exception as e:
                        logger.error(f"이미지 {i+1} 처리 실패: {str(e)}")
                        raise ValueError(f"이미지 {i+1} 처리 중 오류가 발생했습니다.")
                
                # 2. 다중 이미지 분석 프롬프트 추가
                prompt = self._get_multiple_image_prompt()
                contents.append(prompt)
                
                # 3. Google Search 도구 설정
                from google.genai import types
                grounding_tool = types.Tool(
                    google_search=types.GoogleSearch()
                )
                
                # 4. 모델 설정
                config = GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=8192,
                    tools=[grounding_tool]
                )
                
                # 5. API 호출 (타임아웃 설정)
                try:
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=contents,
                        config=config
                    )
                except asyncio.TimeoutError:
                    logger.error(f"Gemini API 다중 이미지 호출 타임아웃 (시도 {attempt + 1})")
                    if attempt == self.max_retries - 1:
                        raise TimeoutError(f"{self.timeout}초 내에 Gemini API 응답 없음 (다중 이미지)")
                    await asyncio.sleep(2 ** attempt)
                    continue
                
                if response and response.text:
                    logger.info("Gemini API 다중 이미지 마크다운 응답 성공 (Google Search 통합)")
                    return response.text
                else:
                    raise ValueError("Gemini API가 빈 응답을 반환했습니다.")
                    
            except TimeoutError:
                # TimeoutError는 이미 처리됨
                raise
            except ValueError as e:
                # ValueError는 재시도하지 않고 즉시 전파
                logger.error(f"Gemini API 다중 이미지 호출 값 오류: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"Gemini API 다중 이미지 호출 실패 (시도 {attempt + 1}): {str(e)}")
                
                # 특정 에러 타입별 처리
                error_str = str(e).lower()
                if "search" in error_str:
                    logger.warning("Google Search 기능 관련 오류, 기본 분석으로 계속 진행")
                elif "quota" in error_str or "limit" in error_str:
                    logger.error("API 할당량 초과 또는 제한 도달")
                    raise ValueError("API 사용량이 한도를 초과했습니다. 잠시 후 다시 시도해 주세요.")
                elif "invalid" in error_str or "malformed" in error_str:
                    logger.error("잘못된 요청 형식")
                    raise ValueError("요청 형식이 올바르지 않습니다.")
                
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

    async def analyze_multiple_portfolio_images(self, image_data_list: List[bytes]) -> str:
        """
        다중 포트폴리오 이미지 분석
        
        Args:
            image_data_list: 이미지 바이트 데이터 리스트
        
        Returns:
            str: 마크다운 형식의 분석 결과
            
        Raises:
            ValueError: 이미지 검증 실패 또는 API 응답 검증 실패
            TimeoutError: API 호출 타임아웃
            Exception: 기타 예외
        """
        try:
            # 입력 검증
            if not image_data_list or len(image_data_list) == 0:
                raise ValueError("분석할 이미지가 없습니다.")
            
            if len(image_data_list) > 5:
                raise ValueError("최대 5개의 이미지만 분석 가능합니다.")
            
            # 각 이미지 검증
            for i, image_data in enumerate(image_data_list):
                try:
                    await validate_image(image_data)
                except ValueError as e:
                    logger.error(f"이미지 {i+1} 검증 실패: {str(e)}")
                    raise ValueError(f"이미지 {i+1} 검증 실패: {str(e)}")
            
            # 캐시 키 생성 (모든 이미지의 해시 조합)
            cache_key = self._generate_multiple_cache_key(image_data_list)
            if cache_key in self._cache:
                logger.info("다중 이미지 분석 결과 캐시에서 반환")
                return self._cache[cache_key]
            
            # 다중 이미지 API 호출
            try:
                result = await self._call_gemini_api_multiple(image_data_list)
            except TimeoutError as e:
                logger.error(f"다중 이미지 분석 타임아웃: {str(e)}")
                raise TimeoutError(f"다중 이미지 분석 시간이 초과되었습니다. 이미지 수를 줄이거나 잠시 후 다시 시도해 주세요.")
            except ValueError as e:
                logger.error(f"다중 이미지 분석 값 오류: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"다중 이미지 API 호출 실패: {str(e)}")
                raise ValueError(f"AI 분석 서비스에 일시적인 문제가 있습니다. 잠시 후 다시 시도해 주세요.")
            
            # 결과 검증 및 캐싱
            try:
                validated_result = self._validate_markdown_response(result)
            except ValueError as e:
                logger.error(f"다중 이미지 분석 결과 검증 실패: {str(e)}")
                raise ValueError(f"분석 결과 형식이 올바르지 않습니다. 다시 시도해 주세요.")
            
            self._cache[cache_key] = validated_result
            
            logger.info(f"다중 이미지 분석 완료 ({len(image_data_list)}개 이미지)")
            return validated_result
            
        except (ValueError, TimeoutError):
            # 이미 처리된 예외는 그대로 전파
            raise
        except Exception as e:
            logger.error(f"다중 이미지 분석 예상치 못한 오류: {str(e)}", exc_info=True)
            raise ValueError(f"분석 중 예상치 못한 오류가 발생했습니다. 다시 시도해 주세요.")

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
