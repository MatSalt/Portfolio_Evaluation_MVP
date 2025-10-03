// src/app/page.tsx
'use client';

import { useState, Suspense } from 'react';
import dynamic from 'next/dynamic';
import { usePortfolioAnalysis } from '@/hooks/usePortfolioAnalysis';
import { BarChart3, Sparkles, ArrowRight, Loader2 } from 'lucide-react';
import TabbedAnalysisDisplay from '@/components/TabbedAnalysisDisplay';
import { isStructuredResponse } from '@/types/portfolio';

// Dynamic imports for code splitting
const ImageUploader = dynamic(() => import('@/components/ImageUploader'), {
  loading: () => (
    <div className="flex justify-center items-center p-8">
      <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
    </div>
  ),
});

const AnalysisDisplay = dynamic(() => import('@/components/AnalysisDisplay'), {
  loading: () => (
    <div className="flex justify-center items-center p-8">
      <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
    </div>
  ),
});

const ErrorBoundary = dynamic(() => import('@/components/ErrorBoundary'));

export default function Home() {
  const {
    uploadState,
    analysisState,
    analysisResult,
    format,
    setFormat,
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
    <ErrorBoundary>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-100">
      {/* 헤더 */}
      <header className="bg-white border-b border-gray-200 shadow-sm" role="banner">
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
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8" role="main">
        {/* 단계 표시기 */}
        <div className="mb-8" role="progressbar" aria-label="분석 진행 단계">
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
          {!analysisResult && (
            <section>
              <div className="text-center mb-6">
                <h2 className="text-3xl font-bold text-gray-900 mb-4">
                  포트폴리오를 분석해보세요
                </h2>
                <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                  증권사 앱의 포트폴리오 화면을 캡처하여 업로드하면, 
                  AI가 최신 시장 정보를 검색하여 전문가 수준의 투자 분석을 제공합니다.
                </p>
              </div>

              <Suspense fallback={
                <div className="flex justify-center items-center p-8">
                  <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
                </div>
              }>
                <ImageUploader
                  uploadState={uploadState}
                  onFileSelect={handleFileSelect}
                  onRemoveFile={removeFile}
                  disabled={isLoading}
                />
              </Suspense>

              {/* 포맷 선택 및 분석 버튼 */}
              {canAnalyze && (
                <div className="text-center mt-6 space-y-4">
                  {/* Format 선택 토글 */}
                  <div className="flex justify-center">
                    <div className="bg-gray-100 p-1 rounded-lg inline-flex">
                      <button
                        onClick={() => setFormat('json')}
                        className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                          format === 'json'
                            ? 'bg-white text-gray-900 shadow'
                            : 'text-gray-600 hover:text-gray-900'
                        }`}
                      >
                        탭 뷰
                      </button>
                      <button
                        onClick={() => setFormat('markdown')}
                        className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                          format === 'markdown'
                            ? 'bg-white text-gray-900 shadow'
                            : 'text-gray-600 hover:text-gray-900'
                        }`}
                      >
                        마크다운 뷰
                      </button>
                    </div>
                  </div>

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

          {/* 분석 결과/로딩 영역 */}
          {(analysisState.status === 'loading' || analysisResult) && (
            <section>
              {analysisState.status === 'loading' && (
                <Suspense fallback={
                  <div className="flex justify-center items-center p-8">
                    <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
                  </div>
                }>
                  <AnalysisDisplay 
                    analysisState={analysisState}
                    onRetry={handleAnalyzeClick}
                  />
                </Suspense>
              )}

              {analysisState.status !== 'loading' && analysisResult && (
                isStructuredResponse(analysisResult) ? (
                  <TabbedAnalysisDisplay data={analysisResult} />
                ) : (
                  <Suspense fallback={
                    <div className="flex justify-center items-center p-8">
                      <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
                    </div>
                  }>
                    <AnalysisDisplay 
                      analysisState={{
                        status: 'success',
                        data: analysisResult,
                        error: null,
                      }}
                      onRetry={handleAnalyzeClick}
                    />
                  </Suspense>
                )
              )}

              {/* 다시 분석하기 버튼 */}
              {analysisResult && (
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
        {!analysisResult && (
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
                  이미지 업로드 후 10분 이내에 
                  최신 시장 정보 기반 상세한 분석 리포트를 받아보세요.
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
      <footer className="bg-white border-t border-gray-200 mt-16" role="contentinfo">
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
    </ErrorBoundary>
  );
}