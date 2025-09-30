'use client';

import React, { useState } from 'react';
import { StructuredAnalysisResponse, TabContent, isDashboardContent, isDeepDiveContent, isAllStockScoresContent, isKeyStockAnalysisContent } from '@/types/portfolio';
import { BarChart3, TrendingUp, Table, FileText } from 'lucide-react';
import DashboardTab from './tabs/DashboardTab';
import AllStockScoresTab from './tabs/AllStockScoresTab';
import DeepDiveTab from './tabs/DeepDiveTab';
import KeyStockAnalysisTab from './tabs/KeyStockAnalysisTab';

interface TabbedAnalysisDisplayProps {
  data: StructuredAnalysisResponse;
}

const TAB_ICONS = {
  dashboard: BarChart3,
  deepDive: TrendingUp,
  allStockScores: Table,
  keyStockAnalysis: FileText,
};

export default function TabbedAnalysisDisplay({ data }: TabbedAnalysisDisplayProps) {
  const [activeTabId, setActiveTabId] = useState('dashboard');
  
  const { portfolioReport } = data;
  const activeTab = portfolioReport.tabs.find(tab => tab.tabId === activeTabId);
  
  const renderTabContent = () => {
    if (!activeTab) return null;
    
    const content = activeTab.content as unknown as TabContent;
    switch (activeTab.tabId) {
      case 'dashboard':
        if (isDashboardContent(content)) return <DashboardTab content={content} />;
        break;
      case 'deepDive':
        if (isDeepDiveContent(content)) return <DeepDiveTab content={content} />;
        break;
      case 'allStockScores':
        if (isAllStockScoresContent(content)) return <AllStockScoresTab content={content} />;
        break;
      case 'keyStockAnalysis':
        if (isKeyStockAnalysisContent(content)) return <KeyStockAnalysisTab content={content} />;
        break;
      default:
        break;
    }
    // 타입 미스매치나 알 수 없는 컨텐츠는 JSON으로 안전 출력
    return (
      <div className="bg-gray-50 rounded-lg p-6">
        <pre className="text-sm overflow-auto">
          {JSON.stringify(activeTab.content, null, 2)}
        </pre>
      </div>
    );
  };
  
  return (
    <div className="w-full max-w-6xl mx-auto">
      {/* 헤더 정보 */}
      <div className="mb-6 text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          포트폴리오 분석 결과
        </h2>
        <div className="flex items-center justify-center space-x-4 text-sm text-gray-600">
          <span>{portfolioReport.reportDate}</span>
          <span>•</span>
          <span>{data.images_processed}개 이미지 분석</span>
          <span>•</span>
          <span>{data.processing_time.toFixed(1)}초 소요</span>
        </div>
      </div>
      
      {/* 탭 네비게이션 */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-2 overflow-x-auto">
          {portfolioReport.tabs.map((tab) => {
            const Icon = TAB_ICONS[tab.tabId as keyof typeof TAB_ICONS];
            const isActive = activeTabId === tab.tabId;
            
            return (
              <button
                key={tab.tabId}
                onClick={() => setActiveTabId(tab.tabId)}
                className={`
                  flex items-center px-4 py-3 border-b-2 font-medium text-sm whitespace-nowrap transition-colors
                  ${isActive
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                {Icon && <Icon className="h-4 w-4 mr-2" />}
                {tab.tabTitle}
              </button>
            );
          })}
        </nav>
      </div>
      
      {/* 탭 컨텐츠 */}
      <div className="mt-6">
        {renderTabContent()}
      </div>
    </div>
  );
}

