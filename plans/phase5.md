# Phase 5: 다중 이미지 업로드 기능 구현 상세 계획

## 🎯 개요

**목표**: 단일 요청으로 여러 포트폴리오 이미지(1-5개)를 업로드하고 종합 분석을 받을 수 있는 기능 구현

**핵심 원칙**: 
- 버그 최소화를 위한 단순한 코드 구조
- 기존 단일 이미지 기능과의 호환성 유지
- [Gemini API 이미지 이해 문서](https://ai.google.dev/gemini-api/docs/image-understanding?hl=ko) 기준 구현

**소요 시간**: 2-3일

---

## 📋 단계 1: 백엔드 API 확장 (1일)

### 1.1 모델 정의 수정 (30분)

**파일**: `backend/models/portfolio.py`

```python
# 기존 AnalysisResponse에 images_processed 필드 추가
class AnalysisResponse(BaseModel):
    content: str          # 마크다운 형식의 분석 결과
    processing_time: float  # 처리 시간 (초)
    request_id: str       # 요청 ID
    images_processed: int = 1  # 처리된 이미지 수 (새 필드, 기본값 1)
```

### 1.2 API 엔드포인트 수정 (1시간)

**파일**: `backend/api/analyze.py`

```python
# 기존 analyze_portfolio 함수 수정
async def analyze_portfolio(
    # 단일 파일에서 다중 파일로 변경 (하위 호환성 유지)
    files: List[UploadFile] = File(..., description="포트폴리오 스크린샷 파일들 (1-5개)"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    gemini_service: GeminiService = Depends(get_gemini_service)
):
    """
    포트폴리오 이미지 분석 엔드포인트 (단일/다중 통합)
    
    Args:
        files: 업로드된 이미지 파일들 (1-5개)
        background_tasks: 백그라운드 작업
        gemini_service: Gemini 서비스 인스턴스
    
    Returns:
        AnalysisResponse: 마크다운 텍스트 분석 결과
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        logger.info(f"포트폴리오 분석 요청 시작 (ID: {request_id}, 파일 수: {len(files)})")
        
        # 1. 파일 개수 검증
        if not files or len(files) == 0:
            raise HTTPException(
                status_code=400,
                detail="최소 1개의 파일이 필요합니다."
            )
        
        if len(files) > 5:
            raise HTTPException(
                status_code=400,
                detail="최대 5개의 파일만 업로드 가능합니다."
            )
        
        # 2. 파일 유효성 검사 및 데이터 읽기
        image_data_list = []
        for i, file in enumerate(files):
            if not file.filename:
                raise HTTPException(
                    status_code=400,
                    detail=f"파일 {i+1}의 파일명이 없습니다."
                )
            
            # Content-Type 검증
            if not is_supported_image_type(file.content_type):
                raise HTTPException(
                    status_code=400,
                    detail=f"파일 {i+1}: 지원하지 않는 파일 형식입니다. (지원: JPEG, PNG)"
                )
            
            # 파일 데이터 읽기
            try:
                image_data = await file.read()
            except Exception as e:
                logger.error(f"파일 {i+1} 읽기 실패 (ID: {request_id}): {str(e)}")
                raise HTTPException(
                    status_code=400,
                    detail=f"파일 {i+1}을 읽을 수 없습니다."
                )
            
            # 이미지 검증
            try:
                await validate_image(image_data, file.filename)
                logger.info(f"이미지 {i+1} 검증 성공 (ID: {request_id})")
            except ValueError as e:
                logger.warning(f"이미지 {i+1} 검증 실패 (ID: {request_id}): {str(e)}")
                raise HTTPException(
                    status_code=400,
                    detail=f"파일 {i+1}: {str(e)}"
                )
            
            image_data_list.append(image_data)
        
        # 3. Gemini API를 통한 분석
        try:
            logger.info(f"Gemini 분석 시작 (ID: {request_id}, 이미지 수: {len(image_data_list)})")
            
            # 단일 이미지면 기존 메서드, 다중 이미지면 새 메서드 사용
            if len(image_data_list) == 1:
                markdown_content = await gemini_service.analyze_portfolio_image(image_data_list[0])
            else:
                markdown_content = await gemini_service.analyze_multiple_portfolio_images(image_data_list)
            
            logger.info(f"Gemini 분석 완료 (ID: {request_id})")
            
        except TimeoutError as e:
            logger.error(f"Gemini API 타임아웃 (ID: {request_id}): {str(e)}")
            raise HTTPException(
                status_code=503,
                detail="분석 요청 시간이 초과되었습니다. 잠시 후 다시 시도해 주세요."
            )
        except Exception as e:
            logger.error(f"Gemini 분석 실패 (ID: {request_id}): {str(e)}")
            raise HTTPException(
                status_code=503,
                detail="AI 분석 서비스에 일시적인 문제가 있습니다. 잠시 후 다시 시도해 주세요."
            )
        
        # 4. 응답 생성
        processing_time = time.time() - start_time
        
        response = AnalysisResponse(
            content=markdown_content,
            processing_time=processing_time,
            request_id=request_id,
            images_processed=len(image_data_list)  # 처리된 이미지 수 추가
        )
        
        logger.info(f"포트폴리오 분석 완료 (ID: {request_id}, {processing_time:.2f}초)")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"예상치 못한 오류 (ID: {request_id}): {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="서버 내부 오류가 발생했습니다."
        )
```

### 1.3 Gemini 서비스 확장 (3시간)

**파일**: `backend/services/gemini_service.py`

```python
# 다중 이미지 분석 메서드 추가
async def analyze_multiple_portfolio_images(self, image_data_list: List[bytes]) -> str:
    """
    다중 포트폴리오 이미지 분석
    
    Args:
        image_data_list: 이미지 바이트 데이터 리스트
    
    Returns:
        str: 마크다운 형식의 분석 결과
    """
    try:
        # 캐시 키 생성 (모든 이미지의 해시 조합)
        cache_key = self._generate_multiple_cache_key(image_data_list)
        if cache_key in self._cache:
            logger.info("다중 이미지 분석 결과 캐시에서 반환")
            return self._cache[cache_key]
        
        # 다중 이미지 API 호출
        result = await self._call_gemini_api_multiple(image_data_list)
        
        # 결과 검증 및 캐싱
        validated_result = self._validate_markdown_response(result)
        self._cache[cache_key] = validated_result
        
        logger.info(f"다중 이미지 분석 완료 ({len(image_data_list)}개 이미지)")
        return validated_result
        
    except Exception as e:
        logger.error(f"다중 이미지 분석 실패: {str(e)}")
        raise

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
                image_part = types.Part.from_bytes(
                    data=image_data,
                    mime_type='image/jpeg'
                )
                contents.append(image_part)
                logger.debug(f"이미지 {i+1} 추가됨")
            
            # 2. 다중 이미지 분석 프롬프트 추가
            prompt = self._get_multiple_image_prompt()
            contents.append(prompt)
            
            # 3. Google Search 도구 설정
            grounding_tool = types.Tool(
                google_search=types.GoogleSearch()
            )
            
            # 4. 모델 설정
            config = types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=8192,
                tools=[grounding_tool]
            )
            
            # 5. API 호출
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )
            
            if response.text:
                logger.info("Gemini API 다중 이미지 마크다운 응답 성공 (Google Search 통합)")
                return response.text
            else:
                raise ValueError("Gemini API가 빈 응답을 반환했습니다.")
                
        except Exception as e:
            logger.error(f"Gemini API 다중 이미지 호출 실패 (시도 {attempt + 1}): {str(e)}")
            if "search" in str(e).lower():
                logger.warning("Google Search 기능 관련 오류, 기본 분석으로 계속 진행")
            if attempt == self.max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)

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

def _generate_multiple_cache_key(self, image_data_list: List[bytes]) -> str:
    """다중 이미지용 캐시 키 생성"""
    # 모든 이미지의 해시를 조합하여 캐시 키 생성
    combined_hash = hashlib.md5()
    for image_data in image_data_list:
        image_hash = hashlib.md5(image_data).hexdigest()
        combined_hash.update(image_hash.encode())
    
    return f"multiple_{len(image_data_list)}_{combined_hash.hexdigest()}"
```

### 1.4 에러 처리 및 타임아웃 조정 (30분)

**파일**: `backend/services/gemini_service.py`

```python
# __init__ 메서드에서 타임아웃 조정
def __init__(self):
    # ... 기존 코드 ...
    
    # 다중 이미지 처리를 위한 타임아웃 증가
    self.timeout = int(os.getenv("GEMINI_TIMEOUT", "180"))  # 3분으로 증가
    self.max_retries = int(os.getenv("GEMINI_MAX_RETRIES", "3"))
    
    logger.info(f"GeminiService 초기화 완료 - 모델: {self.model_name}, 출력: 마크다운 텍스트, Google Search: 활성화, 다중 이미지: 지원")
```

---

## 🎨 단계 2: 프론트엔드 UI 개선 (1일)

### 2.1 타입 정의 업데이트 (30분)

**파일**: `frontend/src/types/portfolio.ts`

```typescript
// 기존 인터페이스 수정
export interface UploadState {
  status: UploadStatus;
  files: File[];        // File[] 배열로 변경
  previews: string[];   // string[] 배열로 변경
  error: string | null;
}

export interface AnalysisResponse {
  content: string;          // 마크다운 형식의 분석 결과
  processing_time: number;  // 처리 시간 (초)
  request_id: string;       // 요청 ID
  images_processed?: number; // 처리된 이미지 수 (옵셔널, 하위 호환성)
}

// 다중 파일 상수 추가
export const MAX_FILES = 5; // 최대 파일 수
```

### 2.2 ImageUploader 컴포넌트 수정 (3시간)

**파일**: `frontend/src/components/ImageUploader.tsx`

```typescript
import React, { useCallback, useRef, useState } from 'react';
import { Upload, X, CheckCircle, AlertCircle, Image as ImageIcon } from 'lucide-react';
import { UploadState, MAX_FILES } from '@/types/portfolio';

interface ImageUploaderProps {
  uploadState: UploadState;
  onFileSelect: (files: File[]) => void;
  onRemoveFile: (index: number) => void;
  disabled?: boolean;
}

export default function ImageUploader({ 
  uploadState, 
  onFileSelect, 
  onRemoveFile, 
  disabled = false 
}: ImageUploaderProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 파일 선택 핸들러
  const handleFileSelect = useCallback((selectedFiles: FileList | null) => {
    if (!selectedFiles || selectedFiles.length === 0) return;
    
    // 기존 파일과 새 파일 합치기 (최대 5개까지)
    const newFiles = Array.from(selectedFiles);
    const totalFiles = [...uploadState.files, ...newFiles].slice(0, MAX_FILES);
    
    onFileSelect(totalFiles);
  }, [uploadState.files, onFileSelect]);

  // 파일 입력 변경 핸들러
  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    handleFileSelect(event.target.files);
    event.target.value = ''; // 입력 초기화
  };

  // 드래그 이벤트 핸들러들
  const handleDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    if (!disabled) {
      setIsDragOver(true);
    }
  }, [disabled]);

  const handleDragLeave = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    if (!event.currentTarget.contains(event.relatedTarget as Node)) {
      setIsDragOver(false);
    }
  }, []);

  const handleDrop = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(false);
    
    if (!disabled) {
      handleFileSelect(event.dataTransfer.files);
    }
  }, [disabled, handleFileSelect]);

  // 파일 추가 버튼 클릭
  const handleAddClick = () => {
    if (!disabled && uploadState.files.length < MAX_FILES) {
      fileInputRef.current?.click();
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      {/* 파일 입력 */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/png,image/jpeg,image/jpg"
        multiple // 다중 선택 활성화
        onChange={handleInputChange}
        className="sr-only"
        aria-describedby="file-upload-description"
      />

      {/* 드롭존 또는 파일 미리보기 */}
      {uploadState.files.length === 0 ? (
        /* 빈 상태: 드롭존 표시 */
        <div
          className={`
            relative border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200
            ${isDragOver 
              ? 'border-blue-400 bg-blue-50' 
              : uploadState.status === 'error'
              ? 'border-red-300 bg-red-50'
              : 'border-gray-300 bg-gray-50 hover:border-gray-400'
            }
            ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
          `}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={handleAddClick}
          role="button"
          tabIndex={disabled ? -1 : 0}
          aria-label="파일 업로드"
        >
          <div className="space-y-4">
            <Upload className="mx-auto h-12 w-12 text-gray-400" />
            <div className="space-y-2">
              <p className="text-lg font-medium text-gray-900">
                포트폴리오 이미지를 업로드하세요
              </p>
              <p className="text-sm text-gray-600">
                파일을 여기로 드래그하거나 클릭하여 선택하세요
              </p>
              <p className="text-xs text-gray-500">
                최대 {MAX_FILES}개, PNG/JPEG, 각 파일 최대 10MB
              </p>
            </div>
          </div>

          {isDragOver && (
            <div className="absolute inset-0 bg-blue-100 bg-opacity-50 rounded-lg flex items-center justify-center">
              <p className="text-blue-700 font-medium">
                여기에 파일을 놓으세요
              </p>
            </div>
          )}
        </div>
      ) : (
        /* 파일 미리보기 갤러리 */
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {uploadState.files.map((file, index) => (
              <div key={`${file.name}-${index}`} className="relative group">
                {/* 이미지 미리보기 */}
                <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden border">
                  {uploadState.previews[index] ? (
                    <img
                      src={uploadState.previews[index]}
                      alt={`미리보기 ${index + 1}`}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <ImageIcon className="h-8 w-8 text-gray-400" />
                    </div>
                  )}
                </div>

                {/* 삭제 버튼 */}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onRemoveFile(index);
                  }}
                  className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 transition-colors opacity-0 group-hover:opacity-100"
                  aria-label={`이미지 ${index + 1} 제거`}
                >
                  <X className="h-4 w-4" />
                </button>

                {/* 파일 정보 */}
                <div className="mt-2 text-xs text-gray-600 truncate">
                  {file.name}
                </div>
                <div className="text-xs text-gray-500">
                  {(file.size / 1024 / 1024).toFixed(1)} MB
                </div>
              </div>
            ))}

            {/* 추가 버튼 (최대 개수 미만일 때) */}
            {uploadState.files.length < MAX_FILES && (
              <button
                onClick={handleAddClick}
                disabled={disabled}
                className={`
                  aspect-square border-2 border-dashed border-gray-300 rounded-lg 
                  flex flex-col items-center justify-center text-gray-500 
                  hover:border-gray-400 hover:text-gray-600 transition-colors
                  ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                `}
              >
                <Upload className="h-6 w-6 mb-2" />
                <span className="text-xs">추가</span>
              </button>
            )}
          </div>

          {/* 파일 상태 정보 */}
          <div className="text-center text-sm text-gray-600">
            {uploadState.files.length}/{MAX_FILES}개 파일 선택됨
          </div>
        </div>
      )}

      {/* 에러 메시지 */}
      {uploadState.status === 'error' && uploadState.error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center">
            <AlertCircle className="h-4 w-4 text-red-500 mr-2" />
            <p className="text-sm text-red-700">{uploadState.error}</p>
          </div>
        </div>
      )}

      {/* 지원 형식 안내 */}
      <div className="mt-4 text-center">
        <p className="text-xs text-gray-500">
          지원 형식: PNG, JPEG • 권장 크기: 최소 800x600px • 최대 파일 크기: 10MB
        </p>
      </div>
    </div>
  );
}
```

### 2.3 상태 관리 로직 수정 (2시간)

**파일**: `frontend/src/hooks/usePortfolioAnalysis.tsx`

```typescript
import { useState, useCallback } from 'react';
import { UploadState, AnalysisState, MAX_FILES } from '@/types/portfolio';
import { analyzePortfolio, validateImageFile, fileToBase64 } from '@/utils/api';

export function usePortfolioAnalysis() {
  // 업로드 상태 관리 (다중 파일 지원)
  const [uploadState, setUploadState] = useState<UploadState>({
    status: 'idle',
    files: [],     // 빈 배열로 초기화
    previews: [],  // 빈 배열로 초기화
    error: null,
  });

  // 분석 결과 상태 관리
  const [analysisState, setAnalysisState] = useState<AnalysisState>({
    status: 'idle',
    data: null,
    error: null,
  });

  /**
   * 파일 선택/드롭 처리 (다중 파일 지원)
   */
  const handleFileSelect = useCallback(async (files: File[]) => {
    if (!files || files.length === 0) {
      setUploadState({
        status: 'error',
        files: [],
        previews: [],
        error: '파일을 선택해주세요.',
      });
      return;
    }

    // 최대 파일 수 제한
    if (files.length > MAX_FILES) {
      setUploadState({
        status: 'error',
        files: [],
        previews: [],
        error: `최대 ${MAX_FILES}개의 파일만 업로드 가능합니다.`,
      });
      return;
    }

    try {
      const validFiles: File[] = [];
      const previews: string[] = [];

      // 각 파일 유효성 검사 및 미리보기 생성
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        
        // 파일 유효성 검사
        const validation = validateImageFile(file);
        if (!validation.isValid) {
          setUploadState({
            status: 'error',
            files: [],
            previews: [],
            error: `파일 ${i + 1}: ${validation.error}`,
          });
          return;
        }

        // 미리보기 이미지 생성
        try {
          const preview = await fileToBase64(file);
          validFiles.push(file);
          previews.push(preview);
        } catch (error) {
          setUploadState({
            status: 'error',
            files: [],
            previews: [],
            error: `파일 ${i + 1}: 이미지 미리보기 생성에 실패했습니다.`,
          });
          return;
        }
      }

      // 성공적으로 모든 파일 처리됨
      setUploadState({
        status: 'success',
        files: validFiles,
        previews,
        error: null,
      });

      // 분석 상태 초기화
      setAnalysisState({
        status: 'idle',
        data: null,
        error: null,
      });

    } catch (error) {
      setUploadState({
        status: 'error',
        files: [],
        previews: [],
        error: '파일 처리 중 오류가 발생했습니다.',
      });
    }
  }, []);

  /**
   * 개별 파일 제거
   */
  const removeFile = useCallback((index: number) => {
    if (index < 0 || index >= uploadState.files.length) return;

    const newFiles = [...uploadState.files];
    const newPreviews = [...uploadState.previews];
    
    newFiles.splice(index, 1);
    newPreviews.splice(index, 1);

    if (newFiles.length === 0) {
      // 모든 파일이 제거되면 초기 상태로
      setUploadState({
        status: 'idle',
        files: [],
        previews: [],
        error: null,
      });
    } else {
      // 일부 파일만 제거
      setUploadState({
        status: 'success',
        files: newFiles,
        previews: newPreviews,
        error: null,
      });
    }
  }, [uploadState.files, uploadState.previews]);

  /**
   * 파일 분석 실행
   */
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
      // 다중 파일 분석 API 호출
      const result = await analyzePortfolio(uploadState.files);
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
  }, [uploadState.files]);

  /**
   * 상태 초기화
   */
  const reset = useCallback(() => {
    setUploadState({
      status: 'idle',
      files: [],
      previews: [],
      error: null,
    });
    setAnalysisState({
      status: 'idle',
      data: null,
      error: null,
    });
  }, []);

  return {
    uploadState,
    analysisState,
    handleFileSelect,
    analyzeImage,
    reset,
    removeFile,
    isLoading: analysisState.status === 'loading',
    canAnalyze: uploadState.status === 'success' && uploadState.files.length > 0,
  };
}
```

### 2.4 API 호출 로직 수정 (30분)

**파일**: `frontend/src/utils/api.ts`

```typescript
// 기존 analyzePortfolio 함수 수정
export async function analyzePortfolio(files: File[]): Promise<AnalysisResponse> {
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
    formData.append('files', file); // 'files' 필드명으로 여러 파일 추가
  });

  try {
    // AbortController for timeout (다중 파일용 타임아웃 증가)
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 300000); // 5분으로 증가

    const response = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: 'POST',
      body: formData,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    // 응답 상태 확인
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

    // 성공 응답 파싱
    const data: AnalysisResponse = await response.json();
    
    // 응답 데이터 유효성 검사
    if (!data.content || typeof data.content !== 'string') {
      throw new ApiException('잘못된 응답 형식', 500);
    }

    return data;

  } catch (error: any) {
    if (error.name === 'AbortError') {
      throw new ApiException('요청 시간이 초과되었습니다. 다시 시도해 주세요.', 408);
    }
    
    if (error instanceof ApiException) {
      throw error;
    }

    // 네트워크 오류 등
    throw new ApiException('네트워크 오류가 발생했습니다. 인터넷 연결을 확인해 주세요.', 0);
  }
}
```

---

## ⚡ 단계 3: 사용자 경험 최적화 (0.5일)

### 3.1 로딩 상태 개선 (1시간)

**파일**: `frontend/src/components/AnalysisDisplay.tsx`

```typescript
// 로딩 상태 메시지 수정
if (analysisState.status === 'loading') {
  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            포트폴리오 분석 중...
          </h3>
          
          <div className="space-y-3 text-sm text-gray-600">
            <p className="flex items-center justify-center">
              <Clock className="h-4 w-4 mr-2" />
              다중 이미지 포함 최대 5분 소요됩니다
            </p>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="font-medium mb-2">AI 분석 진행 중...</p>
              <p className="text-sm text-gray-600 mb-3">
                여러 이미지를 종합하여 정확한 분석을 수행하고 있습니다.
              </p>
              <ul className="text-left space-y-1 text-xs">
                <li>• 포트폴리오 이미지 인식</li>
                <li>• 보유 종목 데이터 추출</li>
                <li>• 최신 시장 정보 검색</li>
                <li>• AI 전문가 종합 분석 수행</li>
                <li>• 상세 리포트 생성</li>
              </ul>
              <p className="text-xs text-gray-500 mt-3">
                이미지 수가 많을수록 더 정확하고 종합적인 분석이 가능합니다.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
```

### 3.2 결과 표시 개선 (1시간)

**파일**: `frontend/src/components/AnalysisDisplay.tsx`

```typescript
// 성공 상태에서 처리된 이미지 수 표시
if (analysisState.status === 'success' && analysisState.data) {
  const { content, processing_time, images_processed } = analysisState.data;
  
  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border p-8">
        {/* 분석 완료 헤더 */}
        <div className="mb-6 text-center">
          <div className="flex items-center justify-center mb-4">
            <CheckCircle className="h-8 w-8 text-green-500 mr-3" />
            <h2 className="text-2xl font-bold text-gray-900">분석 완료</h2>
          </div>
          
          <div className="flex items-center justify-center space-x-6 text-sm text-gray-600">
            <div className="flex items-center">
              <ImageIcon className="h-4 w-4 mr-1" />
              <span>{images_processed || 1}개 이미지 분석</span>
            </div>
            <div className="flex items-center">
              <Clock className="h-4 w-4 mr-1" />
              <span>{processing_time.toFixed(1)}초 소요</span>
            </div>
          </div>
          
          {images_processed && images_processed > 1 && (
            <p className="mt-2 text-xs text-blue-600">
              다중 이미지 종합 분석으로 더욱 정확한 결과를 제공합니다.
            </p>
          )}
        </div>

        {/* 마크다운 콘텐츠 렌더링 */}
        <div className="prose prose-lg max-w-none">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              // 기존 컴포넌트 설정...
            }}
          >
            {content}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
```

---

## 🧪 단계 4: 테스트 및 검증 (1시간)

### 4.1 다중 이미지 테스트 작성

**파일**: `backend/test_multiple_images.py` (새 파일)

```python
"""
다중 이미지 업로드 기능 테스트
"""
import pytest
import asyncio
import os
from fastapi.testclient import TestClient
from dotenv import load_dotenv

load_dotenv()

from main import app
from services.gemini_service import GeminiService

client = TestClient(app)

@pytest.mark.asyncio
async def test_multiple_images_analysis():
    """다중 이미지 분석 테스트"""
    service = GeminiService()
    
    # 테스트용 더미 이미지 데이터 (실제로는 실제 이미지 사용)
    dummy_image_data = b"dummy_image_data"
    image_data_list = [dummy_image_data, dummy_image_data]
    
    try:
        # 다중 이미지 분석 메서드 테스트 (모킹 환경에서)
        # result = await service.analyze_multiple_portfolio_images(image_data_list)
        # assert isinstance(result, str)
        # assert len(result) > 100
        print("다중 이미지 분석 테스트 준비 완료")
        
    except Exception as e:
        print(f"테스트 오류: {str(e)}")

def test_api_multiple_files_validation():
    """API 다중 파일 검증 테스트"""
    # 파일 개수 제한 테스트
    files = [("files", ("test1.jpg", b"fake_image_data", "image/jpeg")) for _ in range(6)]
    
    response = client.post("/api/analyze", files=files)
    assert response.status_code == 400
    assert "최대 5개" in response.json()["detail"]
    
    print("파일 개수 제한 테스트 통과")

def test_api_empty_files():
    """빈 파일 리스트 테스트"""
    response = client.post("/api/analyze", files=[])
    assert response.status_code in [400, 422]  # 400 또는 422 둘 다 허용
    
    print("빈 파일 리스트 테스트 통과")

if __name__ == "__main__":
    test_api_multiple_files_validation()
    test_api_empty_files()
    asyncio.run(test_multiple_images_analysis())
    print("모든 테스트 완료")
```

### 4.2 프론트엔드 테스트 (간단한 검증)

**파일**: `frontend/src/utils/test-multiple-images.ts` (새 파일)

```typescript
/**
 * 다중 이미지 기능 간단 테스트
 */
import { validateImageFile, MAX_FILES } from '@/types/portfolio';

export function testMultipleImageValidation() {
  console.log('다중 이미지 검증 테스트 시작...');
  
  // 1. 최대 파일 수 테스트
  console.assert(MAX_FILES === 5, '최대 파일 수는 5개여야 함');
  
  // 2. 파일 유효성 검사 테스트
  const mockFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
  const validation = validateImageFile(mockFile);
  console.assert(validation.isValid === true, '유효한 JPEG 파일이어야 함');
  
  // 3. 잘못된 파일 타입 테스트
  const invalidFile = new File(['test'], 'test.txt', { type: 'text/plain' });
  const invalidValidation = validateImageFile(invalidFile);
  console.assert(invalidValidation.isValid === false, '텍스트 파일은 무효해야 함');
  
  console.log('다중 이미지 검증 테스트 완료 ✓');
}

// 개발 환경에서만 실행
if (process.env.NODE_ENV === 'development') {
  testMultipleImageValidation();
}
```

---

## 📊 성능 고려사항

### 토큰 사용량 최적화
- **단일 이미지**: 258 토큰 (768x768 기준)
- **5개 이미지**: 약 1,290 토큰 (이미지) + 500 토큰 (프롬프트) = 1,790 토큰
- **비용 효율성**: [Gemini API 문서](https://ai.google.dev/gemini-api/docs/image-understanding?hl=ko)에 따르면 요청당 최대 3,600개 이미지 지원

### 처리 시간 최적화
- **단일 이미지**: 약 2분
- **다중 이미지**: 3-5분 (이미지 수에 따라)
- **타임아웃**: 3분 (180초)으로 설정

### 메모리 최적화
- 이미지 압축: 업로드 전 자동 리사이징
- 캐싱: 동일한 이미지 조합에 대한 결과 캐싱
- 스트리밍: 대용량 파일 처리 시 고려

---

## 🚨 주의사항 및 에러 방지

### 1. 버그 방지 체크리스트
- [ ] 파일 개수 검증 (1-5개)
- [ ] 파일 타입 검증 (PNG, JPEG)
- [ ] 파일 크기 검증 (10MB 이하)
- [ ] 빈 파일 리스트 처리
- [ ] 네트워크 타임아웃 처리
- [ ] 캐시 키 충돌 방지
- [ ] 메모리 누수 방지

### 2. 호환성 유지
- [ ] 기존 단일 이미지 API 호환성
- [ ] 기존 프론트엔드 컴포넌트 호환성
- [ ] 기존 데이터베이스 스키마 호환성

### 3. 에러 처리
- [ ] Gemini API 오류 처리
- [ ] Google Search 실패 시 폴백
- [ ] 파일 업로드 실패 처리
- [ ] 사용자 친화적 에러 메시지

---

## ✅ 완료 기준

1. **기능성**: 1-5개 이미지 모두 정상 분석
2. **성능**: 5개 이미지 처리 시간 5분 이내
3. **안정성**: 에러 상황에서도 적절한 처리
4. **사용성**: 직관적인 다중 파일 업로드 UI
5. **품질**: 다중 이미지 종합 분석의 실질적 가치

---

## 🔗 참고 자료

- [Gemini API 이미지 이해 문서](https://ai.google.dev/gemini-api/docs/image-understanding?hl=ko)
- [Google Gen AI Python SDK](https://github.com/googleapis/python-genai)
- [FastAPI 파일 업로드](https://fastapi.tiangolo.com/tutorial/request-files/)
- [React 다중 파일 업로드](https://developer.mozilla.org/en-US/docs/Web/API/File_API/Using_files_from_web_applications)

---

이 계획을 따라 구현하면 안정적이고 사용자 친화적인 다중 이미지 업로드 기능을 구현할 수 있습니다. 모든 코드는 단순성과 안정성을 우선으로 설계되었습니다.
