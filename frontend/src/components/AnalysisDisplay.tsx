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
