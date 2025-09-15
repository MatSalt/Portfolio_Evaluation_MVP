# Phase 4: Google Search 기능 통합 구현 계획

## 🎯 목표
Gemini API에 Google Search 도구를 통합하여 백그라운드에서 자동으로 최신 시장 정보를 검색하도록 구현합니다.
**핵심 원칙: 기존 코드 최소 변경, 복잡한 메타데이터 없이 단순한 구조 유지**

## 📋 구현 범위
- ✅ Google Search 도구 활성화 (단순한 tools 파라미터 추가)
- ✅ 기존 API 응답 형식 유지 (AnalysisResponse 변경 없음)
- ✅ 기존 프롬프트 유지 (복잡한 검색 지침 없음)
- ❌ 복잡한 메타데이터 추출 (버그 위험 최소화)
- ❌ 검색 쿼리 추적 (불필요한 복잡성 제거)

## 🔧 구현 단계

### 단계 1: Gemini Service 수정 (15분)

**파일**: `backend/services/gemini_service.py`
**수정 위치**: `_call_gemini_api` 메서드

#### 변경 전 코드 (라인 163-167):
```python
# API 호출 (동기 호출)
response = self.client.models.generate_content(
    model=self.model_name,
    contents=[prompt, image_part],
    config=config
)
```

#### 변경 후 코드:
```python
# Google Search 도구 활성화
tools = [{"google_search": {}}]

# API 호출 (동기 호출)
response = self.client.models.generate_content(
    model=self.model_name,
    contents=[prompt, image_part],
    config=config,
    tools=tools  # Google Search 도구 추가
)
```

### 단계 2: 에러 처리 강화 (10분)

**파일**: `backend/services/gemini_service.py`
**수정 위치**: `_call_gemini_api` 메서드의 예외 처리 부분

#### 추가할 예외 처리:
```python
except Exception as e:
    logger.error(f"Gemini API 호출 실패 (시도 {attempt + 1}): {str(e)}")
    
    # Google Search 관련 오류인 경우 특별 처리
    if "search" in str(e).lower():
        logger.warning("Google Search 기능 관련 오류, 기본 분석으로 계속 진행")
    
    if attempt == self.max_retries - 1:
        raise
    await asyncio.sleep(2 ** attempt)
```

### 단계 3: 테스트 및 검증 (30분)

#### 3.1 기본 동작 테스트
```python
# 테스트 파일: test_google_search_integration.py
import pytest
import asyncio
from services.gemini_service import GeminiService

@pytest.mark.asyncio
async def test_google_search_integration():
    """Google Search 통합 기본 테스트"""
    service = GeminiService()
    
    # 테스트용 더미 이미지 데이터
    with open("test_portfolio.jpg", "rb") as f:
        image_data = f.read()
    
    # 분석 실행
    result = await service.analyze_portfolio_image(image_data)
    
    # 기본 검증
    assert isinstance(result, str)
    assert len(result) > 100
    assert "**AI 총평:**" in result
    assert "**포트폴리오 종합 리니아 스코어:" in result
```

#### 3.2 API 응답 검증
```python
@pytest.mark.asyncio 
async def test_api_response_format():
    """API 응답 형식이 기존과 동일한지 확인"""
    # 기존 AnalysisResponse 모델과 호환성 확인
    from models.portfolio import AnalysisResponse
    
    # 샘플 응답 데이터로 검증
    sample_data = {
        "content": "**AI 총평:** 테스트...",
        "processing_time": 15.2,
        "request_id": "test-123"
    }
    
    response = AnalysisResponse(**sample_data)
    assert response.content is not None
```

## 🚨 버그 방지 체크리스트

### ✅ 필수 검증 항목

1. **Import 문 확인**
   ```python
   # gemini_service.py 상단에 필요한 import가 있는지 확인
   from google import genai
   from google.genai.types import GenerateContentConfig, Part
   ```

2. **기존 기능 동작 확인**
   - Google Search 없이도 기본 분석이 동작하는지 확인
   - 기존 API 응답 형식이 변경되지 않았는지 확인

3. **에러 처리 확인**
   - Google Search 실패 시에도 기본 분석이 진행되는지 확인
   - 타임아웃 처리가 올바르게 동작하는지 확인

4. **환경변수 확인**
   ```bash
   # .env 파일에서 Gemini API 키 확인
   GEMINI_API_KEY=your_api_key_here
   ```

### ❌ 하지 말아야 할 것들

1. **기존 AnalysisResponse 모델 변경 금지**
   - 새로운 필드 추가 금지
   - 기존 필드 타입 변경 금지

2. **복잡한 검색 메타데이터 추출 금지**
   - 검색 쿼리 추적 코드 작성 금지
   - 출처 정보 파싱 코드 작성 금지

3. **프롬프트 대폭 수정 금지**
   - 기존 프롬프트에 복잡한 검색 지침 추가 금지
   - 출력 형식 변경 금지

## 🧪 검증 시나리오

### 시나리오 1: 정상 동작 테스트
```bash
# 1. 서버 시작
cd backend
python main.py

# 2. API 테스트
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_portfolio.jpg"

# 3. 응답 확인
# - content 필드에 마크다운 텍스트 존재
# - processing_time, request_id 필드 존재
# - 기존과 동일한 JSON 구조
```

### 시나리오 2: Google Search 실패 테스트
```python
# 네트워크 연결 없는 환경에서 테스트
# 또는 잘못된 API 키로 테스트
# 기본 분석이 정상 동작하는지 확인
```

### 시나리오 3: 성능 테스트
```python
import time

start_time = time.time()
# API 호출
end_time = time.time()

# 30초 이내 응답 확인
assert (end_time - start_time) < 30
```

## 📝 구현 후 확인사항

### 1. 로그 확인
```bash
# 로그에서 Google Search 관련 메시지 확인
tail -f backend.log | grep -i search
```

### 2. API 문서 확인
```bash
# FastAPI 자동 문서에서 스키마 변경 없음 확인
http://localhost:8000/docs
```

### 3. 프론트엔드 호환성 확인
```bash
# 프론트엔드에서 API 호출 시 기존과 동일하게 동작하는지 확인
cd frontend
npm run dev
```

## 🔄 롤백 계획

만약 문제가 발생할 경우 즉시 롤백할 수 있도록 준비:

### 롤백용 코드 (원본 유지):
```python
# 원본 코드 (tools 파라미터 없음)
response = self.client.models.generate_content(
    model=self.model_name,
    contents=[prompt, image_part],
    config=config
)
```

### 롤백 절차:
1. `gemini_service.py`에서 `tools` 파라미터 제거
2. 관련 에러 처리 코드 제거
3. 서비스 재시작 및 테스트

## ⏱️ 예상 소요 시간

- **코드 수정**: 15분
- **에러 처리 추가**: 10분  
- **기본 테스트**: 30분
- **통합 테스트**: 30분
- **문서 업데이트**: 15분

**총 소요 시간: 약 1.5시간**

## 🎯 성공 기준

1. ✅ Google Search 도구가 활성화되어 백그라운드에서 동작
2. ✅ 기존 API 응답 형식 100% 유지
3. ✅ 기존 기능에 영향 없음
4. ✅ 에러 발생 시 기본 분석으로 fallback
5. ✅ 성능 저하 없음 (30초 이내 응답)

이 계획을 따라 구현하면 버그 없이 안전하게 Google Search 기능을 통합할 수 있습니다.
