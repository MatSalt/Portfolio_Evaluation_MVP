import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import KeyStockAnalysisTab from '../tabs/KeyStockAnalysisTab';
import { KeyStockAnalysisContent, AnalysisCard, DetailedScore } from '@/types/portfolio';

function buildDetailedScores(cardIndex: number): DetailedScore[] {
  const categories = ['펀더멘탈', '기술 잠재력', '거시경제', '시장심리', 'CEO/리더십'];
  return categories.map((category, idx) => ({
    category,
    score: 60 + ((cardIndex + idx) % 41),
    analysis: `analysis-card-${cardIndex}-cat-${idx}`,
  }));
}

function buildAnalysisCards(num: number): AnalysisCard[] {
  return Array.from({ length: num }, (_, i) => ({
    stockName: `종목-${i + 1}`,
    overallScore: 70 + (i % 31),
    detailedScores: buildDetailedScores(i),
  }));
}

describe('KeyStockAnalysisTab - rendering and behavior', () => {
  test('renders 6 stock cards and header count for 5+ stocks', () => {
    const content: KeyStockAnalysisContent = {
      analysisCards: buildAnalysisCards(6),
    };

    render(<KeyStockAnalysisTab content={content} />);

    // 헤더에 6개 종목 카운트 노출
    expect(screen.getByText('(6개 종목)')).toBeInTheDocument();

    // 각 카드 헤더의 보조 텍스트 "종합 평가 점수"가 6번 표시
    const scoreBadges = screen.getAllByText('종합 평가 점수');
    expect(scoreBadges).toHaveLength(6);

    // 6개의 종목명이 렌더링
    for (let i = 1; i <= 6; i++) {
      expect(screen.getByText(`종목-${i}`)).toBeInTheDocument();
    }
  });

  test('accordion independence across multiple cards (6 stocks)', () => {
    const content: KeyStockAnalysisContent = {
      analysisCards: buildAnalysisCards(6),
    };

    render(<KeyStockAnalysisTab content={content} />);

    // 초기 상태: 각 카드의 첫 번째 기준(인덱스 0) 분석 텍스트가 모두 보임
    for (let cardIdx = 0; cardIdx < 6; cardIdx++) {
      expect(screen.getByText(`analysis-card-${cardIdx}-cat-0`)).toBeInTheDocument();
    }

    // 두 번째 카드(cardIdx=1)의 두 번째 기준(인덱스 1) 버튼 클릭 → 해당 카드에서 cat-1이 보이고 cat-0은 숨김
    const allTechButtons = screen.getAllByText('기술 잠재력');
    // 카드 순서대로 5개씩 버튼이 생기므로, 두 번째 카드의 동일 카테고리 버튼은 인덱스 1
    fireEvent.click(allTechButtons[1]);

    // 변경 확인 (cardIdx=1)
    expect(screen.queryByText('analysis-card-1-cat-0')).not.toBeInTheDocument();
    expect(screen.getByText('analysis-card-1-cat-1')).toBeInTheDocument();

    // 다른 카드(cardIdx=3)의 초기 확장(cat-0)은 영향받지 않음
    expect(screen.getByText('analysis-card-3-cat-0')).toBeInTheDocument();
  });
});


