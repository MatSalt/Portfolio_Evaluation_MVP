'use client';

import React, { useState } from 'react';
import { KeyStockAnalysisContent } from '@/types/portfolio';
import { FileText, ChevronDown, ChevronUp, BarChart } from 'lucide-react';

interface KeyStockAnalysisTabProps {
  content: KeyStockAnalysisContent;
}

export default function KeyStockAnalysisTab({ content }: KeyStockAnalysisTabProps) {
  const { analysisCards } = content;

  if (!analysisCards || analysisCards.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg p-12 text-center">
        <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600">핵심 종목 분석 데이터가 없습니다.</p>
      </div>
    );
  }

  // 각 카드별로 독립적인 아코디언 상태 관리 (카드 인덱스 → 확장된 기준 인덱스)
  const [expandedStates, setExpandedStates] = useState<Record<number, number | null>>(
    Object.fromEntries(analysisCards.map((_, idx) => [idx, 0]))
  );

  const getScoreColor = (score: number) => {
    const s = Math.max(0, Math.min(100, score));
    if (s >= 80) return 'text-green-600 bg-green-100 border-green-300';
    if (s >= 60) return 'text-yellow-600 bg-yellow-100 border-yellow-300';
    return 'text-red-600 bg-red-100 border-red-300';
  };

  const getProgressColor = (score: number) => {
    const s = Math.max(0, Math.min(100, score));
    if (s >= 80) return 'bg-green-500';
    if (s >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const clampScore = (score: number) => Math.max(0, Math.min(100, score));

  const toggleCriterion = (cardIndex: number, criterionIndex: number) => {
    setExpandedStates(prev => ({
      ...prev,
      [cardIndex]: prev[cardIndex] === criterionIndex ? null : criterionIndex
    }));
  };

  return (
    <div className="space-y-6">
      {/* 페이지 헤더 */}
      <div className="flex items-center mb-6">
        <FileText className="h-6 w-6 text-blue-600 mr-2" />
        <h3 className="text-xl font-semibold text-gray-900">핵심 종목 상세 분석</h3>
        <span className="ml-3 text-sm text-gray-500">({analysisCards.length}개 종목)</span>
      </div>

      {/* 종목 카드 그리드 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {analysisCards.map((card, cardIndex) => (
          <div
            key={cardIndex}
            className="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden"
          >
            {/* 카드 헤더: 종목명 + 종합 점수 */}
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h4 className="text-lg font-bold text-gray-900 break-words">{card.stockName}</h4>
                <div className={`px-4 py-2 rounded-full border-2 font-bold text-lg ${getScoreColor(card.overallScore)}`}>
                  {card.overallScore}점
                </div>
              </div>
              <p className="text-xs text-gray-600 mt-1">종합 평가 점수</p>
            </div>

            {/* 5개 평가 기준 아코디언 */}
            <div className="divide-y divide-gray-100">
              {card.detailedScores.map((criterion, criterionIndex) => {
                const isExpanded = expandedStates[cardIndex] === criterionIndex;

                return (
                  <div key={criterionIndex}>
                    {/* 아코디언 헤더 */}
                    <button
                      onClick={() => toggleCriterion(cardIndex, criterionIndex)}
                      className="w-full px-6 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-center flex-1">
                        <BarChart className="h-4 w-4 text-gray-400 mr-2" />
                        <span className="font-medium text-gray-900 text-sm">{criterion.category}</span>
                      </div>

                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${getScoreColor(criterion.score)}`}>
                          {criterion.score}
                        </span>
                        {isExpanded ? (
                          <ChevronUp className="h-4 w-4 text-gray-600" />
                        ) : (
                          <ChevronDown className="h-4 w-4 text-gray-600" />
                        )}
                      </div>
                    </button>

                    {/* 아코디언 본문 */}
                    {isExpanded && (
                      <div className="px-6 pb-4 bg-gray-50">
                        {/* 진행 바 */}
                        <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
                          <div
                            className={`h-2 rounded-full transition-all duration-500 ${getProgressColor(criterion.score)}`}
                            style={{ width: `${clampScore(criterion.score)}%` }}
                          ></div>
                        </div>

                        {/* 상세 분석 */}
                        <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-line break-words">
                          {criterion.analysis}
                        </p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* 안내 메시지 */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          💡 <strong>Tip:</strong> 각 평가 기준을 클릭하면 해당 항목의 상세 분석을 확인할 수 있습니다. 
          5개 기준(펀더멘탈, 기술 잠재력, 거시경제, 시장심리, CEO/리더십)을 종합하여 종합 점수가 산출됩니다.
        </p>
      </div>
    </div>
  );
}


