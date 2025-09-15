// src/utils/api.ts
import { AnalysisResponse, ApiError } from '@/types/portfolio';

/**
 * API 기본 설정
 */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_TIMEOUT = 120000; // 120초 (Google Search 포함)

/**
 * 커스텀 fetch 에러 클래스
 */
export class ApiException extends Error {
  constructor(
    message: string, 
    public status: number, 
    public response?: any
  ) {
    super(message);
    this.name = 'ApiException';
  }
}

/**
 * 포트폴리오 이미지를 분석하는 API 함수 (다중 파일 지원)
 * @param files - 분석할 이미지 파일들
 * @returns Promise<AnalysisResponse> - 분석 결과
 */
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
