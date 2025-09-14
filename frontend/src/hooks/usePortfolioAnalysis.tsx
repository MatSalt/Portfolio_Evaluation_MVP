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
