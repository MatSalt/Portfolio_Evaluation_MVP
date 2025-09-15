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
  images_processed?: number; // 처리된 이미지 수 (옵셔널, 하위 호환성)
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
  files: File[];        // File[] 배열로 변경
  previews: string[];   // string[] 배열로 변경
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

/**
 * 다중 파일 상수
 */
export const MAX_FILES = 5; // 최대 파일 수
