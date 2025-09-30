'use client';

import React, { useState } from 'react';
import { DeepDiveContent } from '@/types/portfolio';
import { TrendingUp, Lightbulb, ChevronDown, ChevronUp } from 'lucide-react';

interface DeepDiveTabProps {
  content: DeepDiveContent;
}

export default function DeepDiveTab({ content }: DeepDiveTabProps) {
  const { inDepthAnalysis, opportunities } = content;
  const [expandedIndex, setExpandedIndex] = useState<number | null>(0);

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

  const toggleOpportunity = (index: number) => {
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  return (
    <div className="space-y-8">
      <div>
        <div className="flex items-center mb-6">
          <TrendingUp className="h-6 w-6 text-blue-600 mr-2" />
          <h3 className="text-xl font-semibold text-gray-900">3대 기준 심층 분석</h3>
        </div>

        <div className="grid grid-cols-1 gap-6">
          {inDepthAnalysis.map((item, index) => (
            <div
              key={index}
              className="bg-white rounded-lg shadow-md border border-gray-200 p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-start justify-between mb-4">
                <h4 className="text-lg font-semibold text-gray-900 flex-1">
                  {item.title}
                </h4>
                <div className={`ml-4 px-4 py-2 rounded-full border-2 font-bold text-lg ${getScoreColor(item.score)}`}>
                  {item.score}점
                </div>
              </div>

              <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
                <div
                  className={`h-2 rounded-full transition-all duration-500 ${getProgressColor(item.score)}`}
                  style={{ width: `${clampScore(item.score)}%` }}
                ></div>
              </div>

              <p className="text-gray-700 leading-relaxed text-sm">
                {item.description}
              </p>
            </div>
          ))}
        </div>
      </div>

      <div>
        <div className="flex items-center mb-6">
          <Lightbulb className="h-6 w-6 text-yellow-600 mr-2" />
          <h3 className="text-xl font-semibold text-gray-900">{opportunities.title}</h3>
        </div>

        <div className="space-y-3">
          {opportunities.items.map((opportunity, index) => (
            <div
              key={index}
              className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg border border-yellow-200 overflow-hidden"
            >
              <button
                onClick={() => toggleOpportunity(index)}
                className="w-full px-6 py-4 flex items-center justify-between hover:bg-yellow-100 transition-colors"
              >
                <div className="flex items-start flex-1 text-left">
                  <span className="flex-shrink-0 w-6 h-6 bg-yellow-400 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3 mt-0.5">
                    {index + 1}
                  </span>
                  <h4 className="font-semibold text-gray-900 flex-1">
                    {opportunity.summary}
                  </h4>
                </div>
                {expandedIndex === index ? (
                  <ChevronUp className="h-5 w-5 text-gray-600 ml-2 flex-shrink-0" />
                ) : (
                  <ChevronDown className="h-5 w-5 text-gray-600 ml-2 flex-shrink-0" />
                )}
              </button>

              {expandedIndex === index && (
                <div className="px-6 pb-4 pt-2 bg-white border-t border-yellow-200">
                  <div className="pl-9">
                    <p className="text-gray-700 leading-relaxed text-sm whitespace-pre-line">
                      {opportunity.details}
                    </p>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          💡 <strong>Tip:</strong> 기회 항목을 클릭하면 상세한 What-if 시나리오를 확인할 수 있습니다.
        </p>
      </div>
    </div>
  );
}


