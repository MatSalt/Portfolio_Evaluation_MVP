// src/hooks/usePortfolioAnalysis.tsx
'use client';

import { useState, useCallback } from 'react';
import { UploadState, AnalysisState, MAX_FILES } from '@/types/portfolio';
import { analyzePortfolio, validateImageFile, fileToBase64 } from '@/utils/api';

/**
 * 포트폴리오 분석 커스텀 훅
 */
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
