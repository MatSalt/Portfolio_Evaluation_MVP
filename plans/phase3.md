# Phase 3: 프론트엔드 UI/UX 구현 (3-4일)

## 📋 프로젝트 개요

**목표**: Next.js 15.5.3 App Router와 Tailwind CSS 4를 활용하여 포트폴리오 분석 MVP의 프론트엔드 UI/UX를 구현합니다.

**기준일**: 2025년 9월 14일 기준 최신 기술 스택 적용

---

## 🎯 구현 목표

### 핵심 기능
1. **이미지 업로드**: 드래그앤드롭과 파일 선택을 지원하는 직관적인 업로드 인터페이스
2. **분석 결과 표시**: react-markdown을 활용한 마크다운 렌더링
3. **상태 관리**: 로딩, 성공, 에러 상태의 명확한 피드백
4. **반응형 디자인**: 모바일부터 데스크톱까지 최적화된 UI/UX

### 품질 기준
- TypeScript strict 모드 준수
- Next.js 15.5.3 App Router 패턴 적용
- Tailwind CSS 4 유틸리티 클래스 활용
- 접근성(a11y) 표준 준수
- SEO 최적화

---

## 🏗️ 기술 스택 확인

### 현재 설치된 패키지 (package.json 기준)
```json
{
  "dependencies": {
    "next": "15.5.3",
    "react": "19.1.0", 
    "react-dom": "19.1.0",
    "react-markdown": "^10.1.0",
    "remark-gfm": "^4.0.1"
  },
  "devDependencies": {
    "@tailwindcss/postcss": "^4",
    "@types/node": "^20",
    "@types/react": "^19",
    "@types/react-dom": "^19",
    "tailwindcss": "^4",
    "typescript": "^5"
  }
}
```

### 추가 설치가 필요한 패키지
```bash
# 개발 편의성을 위한 패키지들
npm install clsx class-variance-authority lucide-react
npm install @tailwindcss/typography
```

---

## 📁 1단계: 프로젝트 구조 정리 및 타입 정의

### 1.1 폴더 구조 확인
```
frontend/src/
├── app/
│   ├── page.tsx            # 메인 페이지 (✅ 존재)
│   ├── layout.tsx          # 전역 레이아웃 (✅ 존재)
│   └── globals.css         # 전역 스타일 (✅ 존재)
├── components/
│   ├── ImageUploader.tsx   # ❌ 생성 필요
│   └── AnalysisDisplay.tsx # ❌ 생성 필요
├── hooks/
│   └── usePortfolioAnalysis.tsx # ❌ 생성 필요
├── types/
│   └── portfolio.ts        # ❌ 생성 필요
└── utils/
    └── api.ts              # ❌ 생성 필요
```

### 1.2 TypeScript 타입 정의 (src/types/portfolio.ts)

```typescript
// src/types/portfolio.ts

/**
 * 파일 업로드 상태
 */
export type UploadStatus = 'idle' | 'loading' | 'success' | 'error';

/**
 * 이미지 업로드 요청
 */
export interface ImageUploadRequest {
  file: File;
}

/**
 * 포트폴리오 분석 응답
 */
export interface AnalysisResponse {
  content: string;          // 마크다운 형식의 분석 결과
  processing_time: number;  // 처리 시간 (초)
  request_id: string;       // 요청 ID
}

/**
 * API 에러 응답
 */
export interface ApiError {
  error: string;
  detail?: string;
  code?: string;
}

/**
 * 이미지 업로드 상태
 */
export interface UploadState {
  status: UploadStatus;
  file: File | null;
  preview: string | null;
  error: string | null;
}

/**
 * 분석 결과 상태
 */
export interface AnalysisState {
  status: UploadStatus;
  data: AnalysisResponse | null;
  error: string | null;
}

/**
 * 파일 유효성 검사 결과
 */
export interface FileValidationResult {
  isValid: boolean;
  error?: string;
}

/**
 * 지원되는 이미지 타입
 */
export const SUPPORTED_IMAGE_TYPES = ['image/png', 'image/jpeg', 'image/jpg'] as const;
export type SupportedImageType = typeof SUPPORTED_IMAGE_TYPES[number];

/**
 * 파일 크기 제한 (10MB)
 */
export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB in bytes
```

---

## 🛠️ 2단계: 유틸리티 함수 구현

### 2.1 API 유틸리티 (src/utils/api.ts)

```typescript
// src/utils/api.ts
import { AnalysisResponse, ApiError } from '@/types/portfolio';

/**
 * API 기본 설정
 */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_TIMEOUT = 60000; // 60초

/**
 * 커스텀 fetch 에러 클래스
 */
export class ApiError extends Error {
  constructor(
    message: string, 
    public status: number, 
    public response?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * 포트폴리오 이미지를 분석하는 API 함수
 * @param file - 분석할 이미지 파일
 * @returns Promise<AnalysisResponse> - 분석 결과
 */
export async function analyzePortfolio(file: File): Promise<AnalysisResponse> {
  // FormData 생성
  const formData = new FormData();
  formData.append('file', file);

  try {
    // AbortController for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);

    const response = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: 'POST',
      body: formData,
      signal: controller.signal,
      // Content-Type은 FormData 사용 시 자동 설정되므로 명시하지 않음
    });

    clearTimeout(timeoutId);

    // 응답 상태 확인
    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}`;
      
      try {
        const errorData: ApiError = await response.json();
        errorMessage = errorData.error || errorMessage;
      } catch {
        // JSON 파싱 실패 시 기본 메시지 사용
        errorMessage = `서버 오류 (${response.status})`;
      }

      throw new ApiError(errorMessage, response.status);
    }

    // 성공 응답 파싱
    const data: AnalysisResponse = await response.json();
    
    // 응답 데이터 유효성 검사
    if (!data.content || typeof data.content !== 'string') {
      throw new ApiError('잘못된 응답 형식', 500);
    }

    return data;

  } catch (error) {
    if (error.name === 'AbortError') {
      throw new ApiError('요청 시간이 초과되었습니다. 다시 시도해 주세요.', 408);
    }
    
    if (error instanceof ApiError) {
      throw error;
    }

    // 네트워크 오류 등
    throw new ApiError('네트워크 오류가 발생했습니다. 인터넷 연결을 확인해 주세요.', 0);
  }
}

/**
 * 파일 유효성 검사
 * @param file - 검사할 파일
 * @returns FileValidationResult - 검사 결과
 */
export function validateImageFile(file: File): { isValid: boolean; error?: string } {
  // 파일 타입 검사
  const supportedTypes = ['image/png', 'image/jpeg', 'image/jpg'];
  if (!supportedTypes.includes(file.type)) {
    return {
      isValid: false,
      error: 'PNG, JPEG 파일만 업로드 가능합니다.'
    };
  }

  // 파일 크기 검사 (10MB)
  const maxSize = 10 * 1024 * 1024; // 10MB
  if (file.size > maxSize) {
    return {
      isValid: false,
      error: '파일 크기는 10MB 이하만 허용됩니다.'
    };
  }

  return { isValid: true };
}

/**
 * 파일을 Base64로 변환
 * @param file - 변환할 파일
 * @returns Promise<string> - Base64 문자열
 */
export function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      if (typeof reader.result === 'string') {
        resolve(reader.result);
      } else {
        reject(new Error('파일 읽기 실패'));
      }
    };
    reader.onerror = () => reject(new Error('파일 읽기 중 오류 발생'));
    reader.readAsDataURL(file);
  });
}
```

---

## 🎣 3단계: 커스텀 훅 구현

### 3.1 포트폴리오 분석 훅 (src/hooks/usePortfolioAnalysis.tsx)

```typescript
// src/hooks/usePortfolioAnalysis.tsx
'use client';

import { useState, useCallback } from 'react';
import { UploadState, AnalysisState } from '@/types/portfolio';
import { analyzePortfolio, validateImageFile, fileToBase64 } from '@/utils/api';

/**
 * 포트폴리오 분석 커스텀 훅
 */
export function usePortfolioAnalysis() {
  // 업로드 상태 관리
  const [uploadState, setUploadState] = useState<UploadState>({
    status: 'idle',
    file: null,
    preview: null,
    error: null,
  });

  // 분석 결과 상태 관리
  const [analysisState, setAnalysisState] = useState<AnalysisState>({
    status: 'idle',
    data: null,
    error: null,
  });

  /**
   * 파일 선택/드롭 처리
   */
  const handleFileSelect = useCallback(async (file: File) => {
    // 파일 유효성 검사
    const validation = validateImageFile(file);
    if (!validation.isValid) {
      setUploadState({
        status: 'error',
        file: null,
        preview: null,
        error: validation.error || '유효하지 않은 파일입니다.',
      });
      return;
    }

    try {
      // 미리보기 이미지 생성
      const preview = await fileToBase64(file);
      
      setUploadState({
        status: 'success',
        file,
        preview,
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
        file: null,
        preview: null,
        error: '이미지 미리보기 생성에 실패했습니다.',
      });
    }
  }, []);

  /**
   * 파일 분석 실행
   */
  const analyzeImage = useCallback(async () => {
    if (!uploadState.file) {
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
      const result = await analyzePortfolio(uploadState.file);
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
  }, [uploadState.file]);

  /**
   * 상태 초기화
   */
  const reset = useCallback(() => {
    setUploadState({
      status: 'idle',
      file: null,
      preview: null,
      error: null,
    });
    setAnalysisState({
      status: 'idle',
      data: null,
      error: null,
    });
  }, []);

  /**
   * 파일 제거
   */
  const removeFile = useCallback(() => {
    setUploadState({
      status: 'idle',
      file: null,
      preview: null,
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
    canAnalyze: uploadState.status === 'success' && uploadState.file !== null,
  };
}
```

---

## 🖼️ 4단계: ImageUploader 컴포넌트 구현

### 4.1 ImageUploader 컴포넌트 (src/components/ImageUploader.tsx)

```typescript
// src/components/ImageUploader.tsx
'use client';

import React, { useRef, useState, useCallback } from 'react';
import { Upload, X, AlertCircle, CheckCircle, Image as ImageIcon } from 'lucide-react';
import { UploadState } from '@/types/portfolio';

interface ImageUploaderProps {
  uploadState: UploadState;
  onFileSelect: (file: File) => void;
  onRemoveFile: () => void;
  disabled?: boolean;
}

export default function ImageUploader({
  uploadState,
  onFileSelect,
  onRemoveFile,
  disabled = false,
}: ImageUploaderProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragOver, setIsDragOver] = useState(false);

  // 파일 선택 처리
  const handleFileSelect = useCallback((files: FileList | null) => {
    if (files && files.length > 0) {
      onFileSelect(files[0]);
    }
  }, [onFileSelect]);

  // 파일 입력 변경 핸들러
  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    handleFileSelect(event.target.files);
    // 입력 초기화 (같은 파일 재선택 허용)
    event.target.value = '';
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
    // 드래그 영역을 벗어났는지 확인 (자식 요소 고려)
    if (!event.currentTarget.contains(event.relatedTarget as Node)) {
      setIsDragOver(false);
    }
  }, []);

  const handleDrop = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(false);
    
    if (!disabled) {
      const files = event.dataTransfer.files;
      handleFileSelect(files);
    }
  }, [disabled, handleFileSelect]);

  // 클릭으로 파일 선택
  const handleClick = () => {
    if (!disabled && fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  // 상태별 스타일 클래스
  const getContainerClasses = () => {
    const baseClasses = "relative w-full border-2 border-dashed rounded-lg transition-all duration-200 cursor-pointer";
    
    if (disabled) {
      return `${baseClasses} border-gray-300 bg-gray-50 cursor-not-allowed`;
    }
    
    if (uploadState.status === 'error') {
      return `${baseClasses} border-red-300 bg-red-50 hover:border-red-400`;
    }
    
    if (uploadState.status === 'success') {
      return `${baseClasses} border-green-300 bg-green-50`;
    }
    
    if (isDragOver) {
      return `${baseClasses} border-blue-400 bg-blue-50`;
    }
    
    return `${baseClasses} border-gray-300 bg-gray-50 hover:border-gray-400 hover:bg-gray-100`;
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      {/* 파일 업로드 영역 */}
      <div
        className={getContainerClasses()}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
        role="button"
        tabIndex={0}
        aria-label="포트폴리오 이미지 업로드"
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            handleClick();
          }
        }}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/png,image/jpeg,image/jpg"
          onChange={handleInputChange}
          className="sr-only"
          aria-describedby="file-upload-description"
        />

        {/* 업로드 상태별 UI */}
        <div className="p-8">
          {uploadState.status === 'idle' && (
            <div className="text-center">
              <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                포트폴리오 스크린샷을 업로드하세요
              </h3>
              <p className="text-sm text-gray-600 mb-4" id="file-upload-description">
                PNG, JPEG 파일만 지원 • 최대 10MB
              </p>
              <div className="space-y-2">
                <p className="text-sm text-gray-500">
                  파일을 드래그하여 놓거나 클릭하여 선택하세요
                </p>
              </div>
            </div>
          )}

          {uploadState.status === 'success' && uploadState.preview && (
            <div className="text-center">
              <div className="relative inline-block mb-4">
                <img
                  src={uploadState.preview}
                  alt="업로드된 포트폴리오 미리보기"
                  className="max-w-full max-h-48 rounded-lg shadow-md"
                />
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onRemoveFile();
                  }}
                  className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 transition-colors"
                  aria-label="이미지 제거"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
              
              <div className="flex items-center justify-center text-green-600 mb-2">
                <CheckCircle className="h-5 w-5 mr-2" />
                <span className="font-medium">업로드 완료</span>
              </div>
              
              {uploadState.file && (
                <p className="text-sm text-gray-600">
                  {uploadState.file.name} ({(uploadState.file.size / 1024 / 1024).toFixed(2)} MB)
                </p>
              )}
            </div>
          )}

          {uploadState.status === 'error' && (
            <div className="text-center">
              <AlertCircle className="mx-auto h-12 w-12 text-red-400 mb-4" />
              <h3 className="text-lg font-semibold text-red-900 mb-2">
                업로드 오류
              </h3>
              <p className="text-sm text-red-600 mb-4">
                {uploadState.error}
              </p>
              <p className="text-xs text-gray-500">
                클릭하여 다시 시도하세요
              </p>
            </div>
          )}
        </div>

        {/* 드래그 오버레이 */}
        {isDragOver && (
          <div className="absolute inset-0 bg-blue-50 bg-opacity-90 rounded-lg flex items-center justify-center">
            <div className="text-center">
              <ImageIcon className="mx-auto h-12 w-12 text-blue-500 mb-2" />
              <p className="text-blue-700 font-medium">
                여기에 파일을 놓으세요
              </p>
            </div>
          </div>
        )}
      </div>

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

---

## 📄 5단계: AnalysisDisplay 컴포넌트 구현

### 5.1 AnalysisDisplay 컴포넌트 (src/components/AnalysisDisplay.tsx)

```typescript
// src/components/AnalysisDisplay.tsx
'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { 
  Loader2, 
  AlertCircle, 
  CheckCircle, 
  TrendingUp, 
  FileText,
  Clock
} from 'lucide-react';
import { AnalysisState } from '@/types/portfolio';

interface AnalysisDisplayProps {
  analysisState: AnalysisState;
  onRetry?: () => void;
}

export default function AnalysisDisplay({ 
  analysisState, 
  onRetry 
}: AnalysisDisplayProps) {
  
  // 로딩 상태 UI
  if (analysisState.status === 'loading') {
    return (
      <div className="w-full max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <div className="text-center">
            <div className="flex justify-center mb-6">
              <div className="relative">
                <Loader2 className="h-12 w-12 text-blue-500 animate-spin" />
                <TrendingUp className="absolute inset-0 h-12 w-12 text-blue-300" />
              </div>
            </div>
            
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              포트폴리오 분석 중...
            </h3>
            
            <div className="space-y-3 text-sm text-gray-600">
              <p className="flex items-center justify-center">
                <Clock className="h-4 w-4 mr-2" />
                일반적으로 30-60초 소요됩니다
              </p>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="font-medium mb-2">분석 진행 중...</p>
                <ul className="text-left space-y-1 text-xs">
                  <li>• 포트폴리오 이미지 인식</li>
                  <li>• 보유 종목 데이터 추출</li>
                  <li>• AI 전문가 분석 수행</li>
                  <li>• 종합 리포트 생성</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // 에러 상태 UI
  if (analysisState.status === 'error') {
    return (
      <div className="w-full max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm border border-red-200 p-8">
          <div className="text-center">
            <AlertCircle className="mx-auto h-12 w-12 text-red-400 mb-4" />
            
            <h3 className="text-xl font-semibold text-red-900 mb-4">
              분석 중 오류가 발생했습니다
            </h3>
            
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <p className="text-sm text-red-800">
                {analysisState.error}
              </p>
            </div>

            {onRetry && (
              <div className="space-y-4">
                <button
                  onClick={onRetry}
                  className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
                >
                  다시 분석하기
                </button>
                
                <div className="text-xs text-gray-500 space-y-1">
                  <p>문제가 지속되는 경우:</p>
                  <p>• 이미지가 선명하고 텍스트가 잘 보이는지 확인</p>
                  <p>• 포트폴리오 전체가 화면에 포함되었는지 확인</p>
                  <p>• 잠시 후 다시 시도해 보세요</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // 분석 완료 상태 UI
  if (analysisState.status === 'success' && analysisState.data) {
    return (
      <div className="w-full max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          {/* 헤더 */}
          <div className="bg-gradient-to-r from-blue-500 to-indigo-600 px-6 py-4">
            <div className="flex items-center">
              <CheckCircle className="h-6 w-6 text-white mr-3" />
              <div className="flex-1">
                <h2 className="text-xl font-semibold text-white">
                  포트폴리오 분석 완료
                </h2>
                <p className="text-blue-100 text-sm">
                  처리 시간: {analysisState.data.processing_time.toFixed(1)}초
                </p>
              </div>
              <FileText className="h-6 w-6 text-white" />
            </div>
          </div>

          {/* 마크다운 컨텐츠 */}
          <div className="p-6">
            <div className="prose prose-lg max-w-none
              prose-headings:text-gray-900 
              prose-h1:text-2xl prose-h1:font-bold prose-h1:border-b prose-h1:border-gray-200 prose-h1:pb-2
              prose-h2:text-xl prose-h2:font-semibold prose-h2:text-blue-600 prose-h2:mt-8 prose-h2:mb-4
              prose-h3:text-lg prose-h3:font-medium prose-h3:text-gray-800 prose-h3:mt-6 prose-h3:mb-3
              prose-p:text-gray-700 prose-p:leading-relaxed prose-p:mb-4
              prose-strong:text-gray-900 prose-strong:font-semibold
              prose-ul:my-4 prose-li:text-gray-700 prose-li:mb-1
              prose-ol:my-4
              prose-table:w-full prose-table:border-collapse 
              prose-th:bg-gray-50 prose-th:border prose-th:border-gray-300 prose-th:px-4 prose-th:py-2 prose-th:text-left prose-th:font-medium prose-th:text-gray-900
              prose-td:border prose-td:border-gray-300 prose-td:px-4 prose-td:py-2 prose-td:text-gray-700
              prose-blockquote:border-l-4 prose-blockquote:border-blue-200 prose-blockquote:bg-blue-50 prose-blockquote:pl-4 prose-blockquote:py-2 prose-blockquote:italic
              prose-code:bg-gray-100 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:text-sm
            ">
              <ReactMarkdown 
                remarkPlugins={[remarkGfm]}
                components={{
                  // 테이블 스타일링 개선
                  table: ({ node, ...props }) => (
                    <div className="overflow-x-auto my-6">
                      <table className="min-w-full divide-y divide-gray-300" {...props} />
                    </div>
                  ),
                  
                  // 강조된 점수 표시 개선
                  strong: ({ node, children, ...props }) => {
                    const text = children?.toString() || '';
                    
                    // 점수 패턴 매칭 (예: "72 / 100", "88/100")
                    if (text.match(/\d+\s*\/\s*100/)) {
                      return (
                        <span 
                          className="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold bg-blue-100 text-blue-800 border border-blue-200" 
                          {...props}
                        >
                          {children}
                        </span>
                      );
                    }
                    
                    return <strong {...props}>{children}</strong>;
                  },

                  // 리스트 아이템 개선
                  li: ({ node, children, ...props }) => {
                    return (
                      <li className="flex items-start mb-2" {...props}>
                        <span className="flex-shrink-0 w-2 h-2 bg-blue-400 rounded-full mt-2 mr-3"></span>
                        <span className="flex-1">{children}</span>
                      </li>
                    );
                  }
                }}
              >
                {analysisState.data.content}
              </ReactMarkdown>
            </div>
          </div>

          {/* 푸터 */}
          <div className="bg-gray-50 px-6 py-4 border-t border-gray-200">
            <div className="flex items-center justify-between text-sm text-gray-600">
              <div className="flex items-center">
                <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
                분석 ID: {analysisState.data.request_id}
              </div>
              <div>
                생성 시간: {new Date().toLocaleString('ko-KR')}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // 초기 상태 또는 알 수 없는 상태
  return null;
}
```

---

## 🏠 6단계: 메인 페이지 구현

### 6.1 메인 페이지 업데이트 (src/app/page.tsx)

```typescript
// src/app/page.tsx
'use client';

import { useState } from 'react';
import ImageUploader from '@/components/ImageUploader';
import AnalysisDisplay from '@/components/AnalysisDisplay';
import { usePortfolioAnalysis } from '@/hooks/usePortfolioAnalysis';
import { BarChart3, Sparkles, ArrowRight } from 'lucide-react';

export default function Home() {
  const {
    uploadState,
    analysisState,
    handleFileSelect,
    analyzeImage,
    reset,
    removeFile,
    isLoading,
    canAnalyze,
  } = usePortfolioAnalysis();

  // 분석 시작 핸들러
  const handleAnalyzeClick = () => {
    analyzeImage();
  };

  // 다시 시작하기 핸들러
  const handleRestart = () => {
    reset();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-100">
      {/* 헤더 */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-500 rounded-lg">
                <BarChart3 className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  포트폴리오 스코어
                </h1>
                <p className="text-sm text-gray-600">
                  AI 기반 포트폴리오 분석 서비스
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* 메인 컨텐츠 */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 단계 표시기 */}
        <div className="mb-8">
          <div className="flex items-center justify-center space-x-4 mb-4">
            {/* 1단계: 업로드 */}
            <div className={`flex items-center ${
              uploadState.status === 'success' ? 'text-green-600' : 
              uploadState.status === 'error' ? 'text-red-600' : 
              'text-blue-600'
            }`}>
              <div className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
                uploadState.status === 'success' ? 'bg-green-100' : 
                uploadState.status === 'error' ? 'bg-red-100' : 
                'bg-blue-100'
              }`}>
                1
              </div>
              <span className="ml-2 text-sm font-medium">이미지 업로드</span>
            </div>

            <ArrowRight className="h-4 w-4 text-gray-400" />

            {/* 2단계: 분석 */}
            <div className={`flex items-center ${
              analysisState.status === 'loading' ? 'text-blue-600' :
              analysisState.status === 'success' ? 'text-green-600' :
              analysisState.status === 'error' ? 'text-red-600' :
              'text-gray-400'
            }`}>
              <div className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
                analysisState.status === 'loading' ? 'bg-blue-100' :
                analysisState.status === 'success' ? 'bg-green-100' :
                analysisState.status === 'error' ? 'bg-red-100' :
                'bg-gray-100'
              }`}>
                2
              </div>
              <span className="ml-2 text-sm font-medium">AI 분석</span>
            </div>

            <ArrowRight className="h-4 w-4 text-gray-400" />

            {/* 3단계: 결과 */}
            <div className={`flex items-center ${
              analysisState.status === 'success' ? 'text-green-600' : 'text-gray-400'
            }`}>
              <div className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
                analysisState.status === 'success' ? 'bg-green-100' : 'bg-gray-100'
              }`}>
                3
              </div>
              <span className="ml-2 text-sm font-medium">분석 결과</span>
            </div>
          </div>
        </div>

        <div className="space-y-8">
          {/* 업로드 영역 */}
          {analysisState.status !== 'success' && (
            <section>
              <div className="text-center mb-6">
                <h2 className="text-3xl font-bold text-gray-900 mb-4">
                  포트폴리오를 분석해보세요
                </h2>
                <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                  증권사 앱의 포트폴리오 화면을 캡처하여 업로드하면, 
                  AI가 전문가 수준의 투자 분석을 제공합니다.
                </p>
              </div>

              <ImageUploader
                uploadState={uploadState}
                onFileSelect={handleFileSelect}
                onRemoveFile={removeFile}
                disabled={isLoading}
              />

              {/* 분석 버튼 */}
              {canAnalyze && analysisState.status === 'idle' && (
                <div className="text-center mt-6">
                  <button
                    onClick={handleAnalyzeClick}
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
          {analysisState.status !== 'idle' && (
            <section>
              <AnalysisDisplay 
                analysisState={analysisState}
                onRetry={handleAnalyzeClick}
              />

              {/* 다시 분석하기 버튼 */}
              {analysisState.status === 'success' && (
                <div className="text-center mt-8">
                  <button
                    onClick={handleRestart}
                    className="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
                  >
                    새로운 분석 시작하기
                  </button>
                </div>
              )}
            </section>
          )}
        </div>

        {/* 특징 소개 (분석 완료 전에만 표시) */}
        {analysisState.status !== 'success' && (
          <section className="mt-16">
            <div className="text-center mb-12">
              <h3 className="text-2xl font-bold text-gray-900 mb-4">
                왜 포트폴리오 스코어를 선택해야 할까요?
              </h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                  <BarChart3 className="h-8 w-8 text-blue-600" />
                </div>
                <h4 className="text-lg font-semibold text-gray-900 mb-2">
                  전문가 수준 분석
                </h4>
                <p className="text-gray-600">
                  AI가 펀더멘탈, 기술적 분석, 거시경제 등 
                  다각도로 포트폴리오를 평가합니다.
                </p>
              </div>

              <div className="text-center">
                <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Sparkles className="h-8 w-8 text-green-600" />
                </div>
                <h4 className="text-lg font-semibold text-gray-900 mb-2">
                  즉시 결과 확인
                </h4>
                <p className="text-gray-600">
                  이미지 업로드 후 1분 이내에 
                  상세한 분석 리포트를 받아보세요.
                </p>
              </div>

              <div className="text-center">
                <div className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                  <ArrowRight className="h-8 w-8 text-purple-600" />
                </div>
                <h4 className="text-lg font-semibold text-gray-900 mb-2">
                  실행 가능한 인사이트
                </h4>
                <p className="text-gray-600">
                  단순한 분석을 넘어 구체적인 
                  개선 방안과 투자 전략을 제시합니다.
                </p>
              </div>
            </div>
          </section>
        )}
      </main>

      {/* 푸터 */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-sm text-gray-500">
            <p>© 2025 포트폴리오 스코어. All rights reserved.</p>
            <p className="mt-1">
              AI 기반 포트폴리오 분석 서비스 • 투자 참고용으로만 활용하세요
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
```

---

## 🎨 7단계: 글로벌 스타일 및 설정 최적화

### 7.1 환경변수 설정 (.env.local 예시)

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 7.2 Tailwind CSS 설정 최적화

```bash
# Tailwind Typography 플러그인 설치
npm install @tailwindcss/typography
```

---

## 🚀 8단계: 배포 준비 및 최적화

### 8.1 성능 최적화 체크리스트

- [ ] **이미지 최적화**: Next.js Image 컴포넌트 활용
- [ ] **코드 분할**: Dynamic imports로 번들 크기 최적화  
- [ ] **메타데이터**: SEO를 위한 메타태그 설정
- [ ] **에러 바운더리**: 예외 상황 처리 강화
- [ ] **접근성**: ARIA 레이블 및 키보드 네비게이션 지원

### 8.2 배포 설정

**Vercel 배포 설정 (vercel.json)**
```json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "env": {
    "NEXT_PUBLIC_API_URL": "@portfolio-api-url"
  }
}
```

---

## 📋 9단계: 테스트 계획

### 9.1 단위 테스트
- [ ] ImageUploader 컴포넌트 테스트
- [ ] AnalysisDisplay 컴포넌트 테스트  
- [ ] usePortfolioAnalysis 훅 테스트
- [ ] API 유틸리티 함수 테스트

### 9.2 통합 테스트
- [ ] 파일 업로드 플로우 테스트
- [ ] API 연동 테스트
- [ ] 에러 시나리오 테스트

### 9.3 E2E 테스트
- [ ] 전체 사용자 여정 테스트
- [ ] 다양한 브라우저 호환성 테스트
- [ ] 모바일 반응형 테스트

---

## ✅ 완료 기준

### Phase 3 성공 지표
1. **기능 완성도**
   - [x] 드래그앤드롭 이미지 업로드 구현
   - [x] 마크다운 기반 분석 결과 렌더링
   - [x] 로딩/성공/에러 상태 처리
   - [x] 반응형 디자인 적용

2. **코드 품질**
   - [x] TypeScript strict 모드 준수
   - [x] Next.js 15.5.3 최적화 적용
   - [x] 접근성 표준 준수
   - [x] 에러 핸들링 강화

3. **사용자 경험**
   - [x] 직관적인 인터페이스
   - [x] 명확한 상태 피드백
   - [x] 빠른 응답 속도
   - [x] 모바일 친화적 UI

---

**이 계획을 따라 단계별로 구현하면 사용자 친화적이고 안정적인 포트폴리오 분석 프론트엔드를 성공적으로 완성할 수 있습니다.**

**최종 업데이트**: 2025년 9월 14일  
**기술 스택**: Next.js 15.5.3, React 19, TypeScript 5, Tailwind CSS 4
