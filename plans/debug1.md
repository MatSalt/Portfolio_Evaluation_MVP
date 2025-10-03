# JSON 파싱 에러 디버깅

## 에러 분석
- **에러 타입**: JSON 파싱 에러 (EOF while parsing a string)
- **발생 위치**: Gemini 서비스의 Step 2 JSON 생성 단계
- **에러 메시지**: `Invalid JSON: EOF while parsing a string at line 6 column 16` 및 `line 49 column 989`
- **재시도 횟수**: 3번 모두 실패

## 에러 패턴 분석
1. Step 1은 성공적으로 완료됨 (8337자 구조화된 데이터 생성)
2. Step 2에서 JSON 스키마 생성 시 파싱 에러 발생
3. JSON이 중간에 잘리는 현상 (EOF 에러)
4. 3번의 재시도 모두 동일한 패턴의 에러

## 가능한 원인들
1. Gemini API 응답이 토큰 제한으로 인해 잘림
2. JSON 문자열 내에 이스케이프되지 않은 특수문자
3. Pydantic 모델과 실제 JSON 구조 불일치
4. API 응답 크기 제한 초과

## 코드 분석 결과

### 1. Gemini 서비스 구조 확인
- **Two-step 전략 사용**: Step 1 (검색·그라운딩) → Step 2 (JSON 생성)
- **Step 1 성공**: 8337자 구조화된 데이터 생성 완료
- **Step 2 실패**: JSON 파싱 에러 발생

### 2. 에러 발생 지점
```python
# gemini_service.py:884
portfolio_report = PortfolioReport.model_validate_json(response_text)
```

### 3. 에러 메시지 분석
- `EOF while parsing a string at line 6 column 16`
- `EOF while parsing a string at line 49 column 989`
- JSON이 중간에 잘리는 현상 확인

### 4. 가능한 원인들
1. **토큰 제한**: `max_output_tokens=8192` 설정이 부족할 수 있음
2. **JSON 응답 잘림**: Gemini API가 긴 JSON을 완전히 생성하지 못함
3. **특수문자 이스케이프**: 한국어 텍스트 내 특수문자 처리 문제

## 해결 방안

### 1. 토큰 제한 증가
- 현재: `max_output_tokens=8192`
- 제안: `max_output_tokens=16384` 또는 `max_output_tokens=32768`

### 2. JSON 응답 검증 강화
- JSON 완성도 검사 추가
- 잘린 JSON 감지 및 재시도 로직 개선

### 3. 프롬프트 최적화
- JSON 구조 단순화
- 필수 필드만 포함하도록 프롬프트 수정

### 4. 에러 처리 개선
- JSON 파싱 실패 시 더 자세한 로깅
- 부분 JSON 복구 시도

## 제안된 수정사항 (사용자 검토 대기)

### 1. 토큰 제한 증가 🔄
**파일**: `backend/services/gemini_service.py`
**위치**: 라인 865
**변경사항**: `max_output_tokens=8192` → `max_output_tokens=16384`
**이유**: JSON 응답이 토큰 제한으로 인해 잘리는 문제 해결

### 2. JSON 완성도 검사 추가 🔄
**파일**: `backend/services/gemini_service.py`
**위치**: 라인 725-764 (새 메서드 추가)
**변경사항**: `_is_valid_json_structure()` 메서드 추가
**기능**: 
- JSON 파싱 검증
- 중괄호/대괄호 균형 검사
- 필수 키워드 존재 확인
- 잘린 JSON 조기 감지

### 3. JSON 검증 로직 강화 🔄
**파일**: `backend/services/gemini_service.py`
**위치**: 라인 883-891 (기존 로직 수정)
**변경사항**: JSON 완성도 검사 후 Pydantic 검증 진행
**기능**: 불완전한 JSON 감지 시 재시도 로직

### 4. 프롬프트 최적화 🔄
**파일**: `backend/services/gemini_service.py`
**위치**: 라인 815-830 (프롬프트 수정)
**변경사항**: 
- 텍스트 길이 요구사항 완화 (50자 → 20-30자)
- JSON 크기 제한 명시 (8000자 이내)
- 간결한 JSON 생성 유도

### 5. Pydantic 모델 조정 🔄
**파일**: `backend/models/portfolio.py`
**위치**: 라인 144, 150, 208
**변경사항**: 
- `InDepthAnalysisItem.description`: min_length 50 → 20
- `OpportunityItem.details`: min_length 30 → 20  
- `DetailedScore.analysis`: min_length 30 → 20
**이유**: 과도한 텍스트 길이 요구사항으로 인한 JSON 생성 실패 방지

## 예상 효과
1. **토큰 제한 해결**: 더 긴 JSON 응답 처리 가능
2. **JSON 잘림 감지**: 불완전한 JSON 조기 발견 및 재시도
3. **검증 완화**: 더 유연한 텍스트 길이 요구사항
4. **안정성 향상**: JSON 생성 성공률 증가

## 테스트 권장사항
1. 동일한 이미지로 재테스트
2. 다양한 크기의 포트폴리오 이미지 테스트
3. 에러 로그 모니터링
4. JSON 응답 크기 확인

## 추가 디버깅 계획 (JSON 잘림 현상 분석)

### 6. 상세 로깅 추가 ✅
**파일**: `backend/services/gemini_service.py`
**목적**: Step 1과 Step 2의 전체 결과를 확인하여 JSON 잘림 현상 정확히 파악
**상태**: 완료됨

#### 6.1 Step 1 결과 전체 로깅 ✅
**위치**: 라인 712-714 (기존 미리보기 로깅 수정)
**변경사항**: 
```python
# 기존: 300자 미리보기만
preview = result_text[:300] + "..." if len(result_text) > 300 else result_text
logger.info(f"Step 1 성공 - 응답 미리보기: {preview}")

# 변경: 전체 결과 로깅
logger.info(f"Step 1 성공 - 전체 응답 길이: {len(result_text)}자")
logger.info(f"Step 1 전체 응답:\n{result_text}")
```
**상태**: 완료됨

#### 6.2 Step 2 JSON 응답 전체 로깅 ✅
**위치**: 라인 880-881 (JSON 응답 수신 후)
**변경사항**:
```python
# 기존: 간단한 로깅
logger.info("Step 2: JSON 응답 수신, 수동 파싱 시작")
response_text = response.text.strip()

# 변경: 상세 로깅 추가
logger.info("Step 2: JSON 응답 수신, 수동 파싱 시작")
response_text = response.text.strip()
logger.info(f"Step 2 JSON 응답 길이: {len(response_text)}자")
logger.info(f"Step 2 전체 JSON 응답:\n{response_text}")
```
**상태**: 완료됨

#### 6.3 JSON 잘림 감지 로깅 ✅
**위치**: 라인 903-904 (검증 실패 시)
**변경사항**:
```python
# 기존: 500자 미리보기
preview = response_text[:500] if len(response_text) > 500 else response_text
logger.debug(f"Step 2: 검증 실패 JSON 미리보기: {preview}...")

# 변경: 전체 응답과 잘림 지점 분석
logger.error(f"Step 2: 검증 실패 - JSON 전체 길이: {len(response_text)}자")
logger.error(f"Step 2: 전체 JSON 응답:\n{response_text}")
# JSON 끝부분 확인
if len(response_text) > 100:
    logger.error(f"Step 2: JSON 끝부분 (마지막 100자): {response_text[-100:]}")
```
**상태**: 완료됨

### 7. JSON 완성도 검사 강화 🔄
**파일**: `backend/services/gemini_service.py`
**위치**: 라인 725-764 (새 메서드 추가)
**기능**: JSON이 완전한지 더 정확히 판단

```python
def _is_valid_json_structure(self, json_text: str) -> bool:
    """JSON 구조의 완성도 검사 (강화된 버전)"""
    try:
        # 기본 JSON 파싱 시도
        import json
        json.loads(json_text)
        
        # JSON 길이 검사
        if len(json_text) < 1000:
            logger.warning(f"JSON이 너무 짧습니다: {len(json_text)}자")
            return False
        
        # 필수 키워드 확인
        required_keywords = [
            '"version"', '"reportDate"', '"tabs"',
            '"tabId"', '"tabTitle"', '"content"'
        ]
        
        for keyword in required_keywords:
            if keyword not in json_text:
                logger.warning(f"JSON에서 필수 키워드 누락: {keyword}")
                return False
        
        # 중괄호 균형 검사
        open_braces = json_text.count('{')
        close_braces = json_text.count('}')
        if open_braces != close_braces:
            logger.warning(f"JSON 중괄호 불균형: 열림 {open_braces}, 닫힘 {close_braces}")
            return False
        
        # 대괄호 균형 검사
        open_brackets = json_text.count('[')
        close_brackets = json_text.count(']')
        if open_brackets != close_brackets:
            logger.warning(f"JSON 대괄호 불균형: 열림 {open_brackets}, 닫힘 {close_brackets}")
            return False
        
        # JSON 끝부분 검사 (잘림 감지)
        if not json_text.strip().endswith('}'):
            logger.warning("JSON이 올바르게 끝나지 않습니다 (마지막 문자가 '}'가 아님)")
            return False
        
        return True
        
    except json.JSONDecodeError as e:
        logger.warning(f"JSON 파싱 실패: {str(e)}")
        return False
    except Exception as e:
        logger.warning(f"JSON 구조 검사 실패: {str(e)}")
        return False
```

## 수정 진행 상태
- ✅ 디버깅 분석 완료
- ✅ 수정 계획 수립 완료
- ✅ **상세 로깅 추가 완료**
- 🔄 **JSON 완성도 검사 강화 대기**
- ⏳ 나머지 수정사항 대기

### 완료된 작업
1. ✅ **Step 1 결과 전체 로깅**: 300자 미리보기 → 전체 응답 로깅
2. ✅ **Step 2 JSON 응답 전체 로깅**: JSON 길이와 전체 내용 로깅  
3. ✅ **JSON 잘림 감지 로깅**: 검증 실패 시 전체 응답과 끝부분 분석

### 다음 단계
이제 동일한 이미지로 재테스트하면 Step 1과 Step 2의 전체 결과를 로그에서 확인할 수 있습니다. 이를 통해 JSON이 정확히 어디서 잘리는지 파악할 수 있을 것입니다.

## 🔍 JSON 호출 실패 원인 분석 방법

### 현재 상황 분석
터미널 로그에서 확인된 문제:
- **Step 1**: 성공 (7579자 응답 완료)
- **Step 2**: 3번 모두 실패 - "Gemini API에서 응답을 받지 못했습니다"
- **HTTP 상태**: 200 OK (API 호출은 성공)
- **문제**: `response.text`가 None이거나 빈 값

### 원인 분석 방법들

#### 1. 응답 객체 상세 로깅 추가 ✅
**위치**: `gemini_service.py` 라인 879-896
**목적**: response 객체의 전체 구조 확인
**상태**: 완료됨
```python
# 기존 코드 수정
if response and getattr(response, "text", None):
    logger.info("Step 2: JSON 응답 수신, 수동 파싱 시작")
    response_text = response.text.strip()
    logger.info(f"Step 2 JSON 응답 길이: {len(response_text)}자")
    logger.info(f"Step 2 전체 JSON 응답:\n{response_text}")
else:
    # 응답 객체 상세 분석
    logger.error(f"Step 2: 응답 객체 분석")
    logger.error(f"response 존재: {response is not None}")
    if response:
        logger.error(f"response 타입: {type(response)}")
        logger.error(f"response 속성들: {dir(response)}")
        logger.error(f"response.text 존재: {hasattr(response, 'text')}")
        if hasattr(response, 'text'):
            logger.error(f"response.text 값: {response.text}")
        logger.error(f"response 전체: {response}")
```

#### 2. API 응답 헤더 및 메타데이터 로깅 🔄
**위치**: `gemini_service.py` 라인 872-876 (API 호출 후)
**목적**: API 응답의 메타데이터 확인
```python
# API 호출 후 추가
response = self.client.models.generate_content(
    model=self.model_name,
    contents=[prompt],
    config=config
)

# 응답 메타데이터 로깅
logger.info(f"Step 2: API 응답 메타데이터")
logger.info(f"response 타입: {type(response)}")
if hasattr(response, '__dict__'):
    logger.info(f"response 속성들: {response.__dict__}")
```

#### 3. 프롬프트 크기 및 토큰 수 확인 🔄
**위치**: `gemini_service.py` 라인 860 (프롬프트 생성 후)
**목적**: 입력 프롬프트가 너무 큰지 확인
```python
# 프롬프트 생성 후 추가
prompt = self._get_json_generation_prompt(grounded_facts)
logger.info(f"Step 2: 프롬프트 크기 분석")
logger.info(f"grounded_facts 길이: {len(grounded_facts)}자")
logger.info(f"전체 프롬프트 길이: {len(prompt)}자")
logger.info(f"프롬프트 미리보기 (처음 500자): {prompt[:500]}")
```

#### 4. API 설정 및 제한사항 확인 🔄
**위치**: `gemini_service.py` 라인 863-869 (config 설정)
**목적**: API 설정이 올바른지 확인
```python
# config 설정 후 추가
config = GenerateContentConfig(
    temperature=0.0,
    max_output_tokens=8192,
    response_mime_type="application/json",
)
logger.info(f"Step 2: API 설정 확인")
logger.info(f"temperature: {config.temperature}")
logger.info(f"max_output_tokens: {config.max_output_tokens}")
logger.info(f"response_mime_type: {config.response_mime_type}")
```

#### 5. 에러 상세 정보 캐치 🔄
**위치**: `gemini_service.py` 라인 911-915 (예외 처리)
**목적**: 구체적인 에러 원인 파악
```python
# 예외 처리 강화
except Exception as e:
    logger.error(f"Step 2 호출 실패 (시도 {attempt + 1}): {str(e)}")
    logger.error(f"에러 타입: {type(e)}")
    logger.error(f"에러 상세: {e.__dict__ if hasattr(e, '__dict__') else 'N/A'}")
    import traceback
    logger.error(f"스택 트레이스: {traceback.format_exc()}")
```

### 예상 원인들
1. **응답 크기 제한**: JSON 응답이 너무 커서 빈 응답 반환
2. **프롬프트 크기 제한**: 입력 프롬프트가 너무 커서 처리 실패
3. **API 설정 문제**: `response_mime_type="application/json"` 설정 문제
4. **토큰 제한**: `max_output_tokens=8192` 부족
5. **API 버그**: Gemini API의 일시적 문제

### 권장 디버깅 순서
1. ✅ **응답 객체 상세 로깅** (가장 중요) - **완료**
2. **프롬프트 크기 확인**
3. **API 설정 검증**
4. **에러 상세 정보 캐치**

### 완료된 디버깅 작업
- ✅ **응답 객체 상세 로깅**: response 객체의 전체 구조와 속성 분석 로직 추가
- ✅ **빈 응답 감지**: response가 None이거나 text 속성이 없는 경우 상세 로깅

### 다음 단계
이제 동일한 이미지로 재테스트하면 Step 2에서 response 객체의 상세 정보를 확인할 수 있습니다. 이를 통해 JSON 호출 실패의 정확한 원인을 파악할 수 있을 것입니다.

## 🎯 **최종 원인 분석 결과**

### 로그 분석을 통한 핵심 발견사항
```
finish_reason=<FinishReason.MAX_TOKENS: 'MAX_TOKENS'>
response.text 값: None
Step 2 JSON 응답 길이: 11689자 (부분적으로 생성됨)
```

### **확정된 원인: MAX_TOKENS 제한 도달**
1. **첫 번째 시도**: `finish_reason=MAX_TOKENS`로 인해 `response.text=None`
2. **두 번째/세 번째 시도**: 11,689자의 JSON 생성되지만 토큰 제한으로 중간에 잘림
3. **일관된 패턴**: 동일한 지점에서 JSON이 잘리는 현상

## 🛠️ **구체적인 해결 방안**

### **1단계: 토큰 제한 즉시 증가** (최우선)

#### 1.1 토큰 제한 증가
**파일**: `backend/services/gemini_service.py`
**위치**: 라인 865
**현재 코드**:
```python
config = GenerateContentConfig(
    temperature=0.0,
    max_output_tokens=8192,  # ← 문제 지점
    response_mime_type="application/json",
)
```

**수정 코드**:
```python
config = GenerateContentConfig(
    temperature=0.0,
    max_output_tokens=16384,  # 8192 → 16384로 증가
    response_mime_type="application/json",
)
```

#### 1.2 추가 안전장치: 더 높은 토큰 제한
**대안 코드** (16384로도 부족한 경우):
```python
config = GenerateContentConfig(
    temperature=0.0,
    max_output_tokens=32768,  # 최대 토큰 제한
    response_mime_type="application/json",
)
```

### **2단계: JSON 완성도 검사 강화**

#### 2.1 JSON 완성도 검사 메서드 추가
**파일**: `backend/services/gemini_service.py`
**위치**: 라인 725 이후 (새 메서드)
**추가할 코드**:
```python
def _is_valid_json_structure(self, json_text: str) -> bool:
    """JSON 구조의 완성도 검사 (MAX_TOKENS 대응)"""
    try:
        # 기본 JSON 파싱 시도
        import json
        json.loads(json_text)
        
        # JSON 길이 검사 (최소 1000자)
        if len(json_text) < 1000:
            logger.warning(f"JSON이 너무 짧습니다: {len(json_text)}자")
            return False
        
        # 필수 키워드 확인
        required_keywords = [
            '"version"', '"reportDate"', '"tabs"',
            '"tabId"', '"tabTitle"', '"content"'
        ]
        
        for keyword in required_keywords:
            if keyword not in json_text:
                logger.warning(f"JSON에서 필수 키워드 누락: {keyword}")
                return False
        
        # 중괄호 균형 검사
        open_braces = json_text.count('{')
        close_braces = json_text.count('}')
        if open_braces != close_braces:
            logger.warning(f"JSON 중괄호 불균형: 열림 {open_braces}, 닫힘 {close_braces}")
            return False
        
        # 대괄호 균형 검사
        open_brackets = json_text.count('[')
        close_brackets = json_text.count(']')
        if open_brackets != close_brackets:
            logger.warning(f"JSON 대괄호 불균형: 열림 {open_brackets}, 닫힘 {close_brackets}")
            return False
        
        # JSON 끝부분 검사 (잘림 감지)
        if not json_text.strip().endswith('}'):
            logger.warning("JSON이 올바르게 끝나지 않습니다 (마지막 문자가 '}'가 아님)")
            return False
        
        return True
        
    except json.JSONDecodeError as e:
        logger.warning(f"JSON 파싱 실패: {str(e)}")
        return False
    except Exception as e:
        logger.warning(f"JSON 구조 검사 실패: {str(e)}")
        return False
```

#### 2.2 JSON 검증 로직에 완성도 검사 추가
**파일**: `backend/services/gemini_service.py`
**위치**: 라인 884 이후 (기존 로직 수정)
**현재 코드**:
```python
if response and getattr(response, "text", None):
    logger.info("Step 2: JSON 응답 수신, 수동 파싱 시작")
    response_text = response.text.strip()
    logger.info(f"Step 2 JSON 응답 길이: {len(response_text)}자")
    logger.info(f"Step 2 전체 JSON 응답:\n{response_text}")
```

**수정 코드**:
```python
if response and getattr(response, "text", None):
    logger.info("Step 2: JSON 응답 수신, 수동 파싱 시작")
    response_text = response.text.strip()
    logger.info(f"Step 2 JSON 응답 길이: {len(response_text)}자")
    logger.info(f"Step 2 전체 JSON 응답:\n{response_text}")
    
    # JSON 완성도 검사 추가
    if not self._is_valid_json_structure(response_text):
        logger.error("Step 2: JSON이 잘렸거나 불완전합니다")
        if attempt == 0:
            logger.info("Step 2: JSON 잘림 감지, 재시도")
            await asyncio.sleep(1)
            continue
        else:
            raise ValueError("JSON 응답이 불완전합니다. 토큰 제한으로 인해 잘렸을 가능성이 있습니다.")
```

### **3단계: 프롬프트 최적화** (토큰 사용량 감소)

#### 3.1 프롬프트 텍스트 길이 제한 추가
**파일**: `backend/services/gemini_service.py`
**위치**: 라인 815-830 (프롬프트 수정)
**현재 코드**:
```python
## 변환 규칙:
1. **null 값 절대 금지**: 모든 점수는 0-100 사이의 정수로 채워야 함 (null, None 사용 금지)
2. **최소 문자 수 필수**: 
   - description (심층 분석): 최소 50자 이상
   - analysis (개별 종목): 최소 30자 이상
   - details (기회): 최소 30자 이상
```

**수정 코드**:
```python
## 변환 규칙:
1. **null 값 절대 금지**: 모든 점수는 0-100 사이의 정수로 채워야 함 (null, None 사용 금지)
2. **간결한 텍스트 (토큰 절약)**: 
   - description (심층 분석): 30-50자 (너무 길지 않게)
   - analysis (개별 종목): 20-30자 (간결하게)
   - details (기회): 20-30자 (간결하게)
3. **JSON 크기 제한**: 전체 JSON이 12000자 이내로 유지
4. **토큰 효율성**: 불필요한 설명이나 반복 표현 피하기
```

#### 3.2 프롬프트에 토큰 제한 명시
**추가할 코드**:
```python
**중요**: 토큰 제한을 고려하여 간결하고 정확한 JSON을 생성하세요. 
불필요하게 긴 텍스트는 피하고 핵심 정보만 포함하세요.
전체 JSON 크기는 12000자 이내로 유지해야 합니다.
```

### **4단계: Pydantic 모델 조정** (검증 완화)

#### 4.1 텍스트 길이 요구사항 완화
**파일**: `backend/models/portfolio.py`
**위치**: 라인 144, 150, 208
**현재 코드**:
```python
class InDepthAnalysisItem(BaseModel):
    description: str = Field(..., min_length=50, description="상세 분석 내용")

class OpportunityItem(BaseModel):
    details: str = Field(..., min_length=30, description="상세 설명")

class DetailedScore(BaseModel):
    analysis: str = Field(..., min_length=30, description="상세 분석")
```

**수정 코드**:
```python
class InDepthAnalysisItem(BaseModel):
    description: str = Field(..., min_length=20, description="상세 분석 내용")

class OpportunityItem(BaseModel):
    details: str = Field(..., min_length=20, description="상세 설명")

class DetailedScore(BaseModel):
    analysis: str = Field(..., min_length=20, description="상세 분석")
```

### **5단계: 에러 처리 개선**

#### 5.1 MAX_TOKENS 에러 특별 처리
**파일**: `backend/services/gemini_service.py`
**위치**: 라인 884-896 (응답 처리 로직)
**추가할 코드**:
```python
# MAX_TOKENS 에러 특별 처리
if response and hasattr(response, 'candidates') and response.candidates:
    candidate = response.candidates[0]
    if hasattr(candidate, 'finish_reason') and candidate.finish_reason == 'MAX_TOKENS':
        logger.error("Step 2: MAX_TOKENS 제한 도달 - 토큰 제한 증가 필요")
        if attempt == 0:
            logger.info("Step 2: 토큰 제한으로 인한 실패, 재시도")
            await asyncio.sleep(1)
            continue
        else:
            raise ValueError("토큰 제한으로 인해 JSON이 완성되지 않았습니다. max_output_tokens를 증가시켜야 합니다.")
```

## 📋 **구현 우선순위**

### **즉시 구현 (1단계)**
1. ✅ **토큰 제한 증가**: `max_output_tokens=8192` → `max_output_tokens=16384`
2. ✅ **JSON 완성도 검사**: `_is_valid_json_structure()` 메서드 추가

### **2차 구현 (2-3단계)**
3. ✅ **프롬프트 최적화**: 텍스트 길이 제한 및 토큰 효율성 개선
4. ✅ **Pydantic 모델 조정**: min_length 요구사항 완화

### **3차 구현 (4-5단계)**
5. ✅ **에러 처리 개선**: MAX_TOKENS 에러 특별 처리

## 🎯 **예상 효과**

### **1단계 구현 후**
- JSON 생성 성공률: 0% → 80%+ (토큰 제한 해결)
- 응답 완성도: 불완전 → 완전한 JSON 생성

### **전체 구현 후**
- JSON 생성 성공률: 95%+
- 에러 처리: 구체적인 원인 파악 및 자동 재시도
- 토큰 효율성: 20-30% 토큰 사용량 감소
