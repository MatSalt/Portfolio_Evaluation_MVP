'use client';

import React from 'react';
import { DashboardContent } from '@/types/portfolio';
import { TrendingUp, TrendingDown, CheckCircle, AlertCircle } from 'lucide-react';

interface DashboardTabProps {
  content: DashboardContent;
}

export default function DashboardTab({ content }: DashboardTabProps) {
  const { overallScore, coreCriteriaScores, strengths, weaknesses } = content;
  
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };
  
  return (
    <div className="space-y-8">
      {/* 종합 스코어 */}
      <div className="text-center bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-8 border border-blue-100">
        <h3 className="text-lg font-medium text-gray-700 mb-2">{overallScore.title}</h3>
        <div className="text-6xl font-bold text-blue-600 mb-2">
          {overallScore.score}
        </div>
        <div className="text-sm text-gray-600">/ {overallScore.maxScore}점</div>
      </div>
      
      {/* 핵심 기준 스코어 */}
      <div>
        <h3 className="text-xl font-semibold text-gray-900 mb-4">3대 핵심 기준</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {coreCriteriaScores.map((criteria, index) => (
            <div key={index} className="bg-white rounded-lg shadow-sm border p-5">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-900">{criteria.criterion}</h4>
                <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getScoreColor(criteria.score)}`}>
                  {criteria.score}점
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3 mt-3">
                <div 
                  className={`h-3 rounded-full transition-all duration-500 ${
                    criteria.score >= 80 ? 'bg-green-500' :
                    criteria.score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${(criteria.score / criteria.maxScore) * 100}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* 강점/약점 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* 강점 */}
        <div className="bg-green-50 rounded-lg p-6 border border-green-200">
          <div className="flex items-center mb-4">
            <CheckCircle className="h-6 w-6 text-green-600 mr-2" />
            <h3 className="text-lg font-semibold text-green-900">강점</h3>
          </div>
          <ul className="space-y-3">
            {strengths.map((strength, index) => (
              <li key={index} className="flex items-start">
                <TrendingUp className="h-5 w-5 text-green-600 mr-2 flex-shrink-0 mt-0.5" />
                <span className="text-gray-800">{strength}</span>
              </li>
            ))}
          </ul>
        </div>
        
        {/* 약점 */}
        <div className="bg-red-50 rounded-lg p-6 border border-red-200">
          <div className="flex items-center mb-4">
            <AlertCircle className="h-6 w-6 text-red-600 mr-2" />
            <h3 className="text-lg font-semibold text-red-900">약점</h3>
          </div>
          <ul className="space-y-3">
            {weaknesses.map((weakness, index) => (
              <li key={index} className="flex items-start">
                <TrendingDown className="h-5 w-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" />
                <span className="text-gray-800">{weakness}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

