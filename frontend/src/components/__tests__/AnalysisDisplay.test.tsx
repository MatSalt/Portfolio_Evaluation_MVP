// src/components/__tests__/AnalysisDisplay.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import AnalysisDisplay from '../AnalysisDisplay'
import { AnalysisState } from '@/types/portfolio'

// Mock react-markdown
jest.mock('react-markdown', () => {
  return function MockReactMarkdown({ children }: { children: string }) {
    return <div data-testid="markdown-content">{children}</div>
  }
})

jest.mock('remark-gfm', () => () => {})

const mockAnalysisState: AnalysisState = {
  status: 'idle',
  data: null,
  error: null,
}

const defaultProps = {
  analysisState: mockAnalysisState,
  onRetry: jest.fn(),
}

describe('AnalysisDisplay', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should render loading state', () => {
    const loadingState: AnalysisState = {
      status: 'loading',
      data: null,
      error: null,
    }

    render(<AnalysisDisplay {...defaultProps} analysisState={loadingState} />)
    
    expect(screen.getByText('포트폴리오 분석 중...')).toBeInTheDocument()
    expect(screen.getByText('일반적으로 30-60초 소요됩니다')).toBeInTheDocument()
    expect(screen.getByText('분석 진행 중...')).toBeInTheDocument()
    expect(screen.getByText('• 포트폴리오 이미지 인식')).toBeInTheDocument()
    expect(screen.getByText('• 보유 종목 데이터 추출')).toBeInTheDocument()
    expect(screen.getByText('• AI 전문가 분석 수행')).toBeInTheDocument()
    expect(screen.getByText('• 종합 리포트 생성')).toBeInTheDocument()
  })

  it('should render error state', () => {
    const errorState: AnalysisState = {
      status: 'error',
      data: null,
      error: '분석 중 오류가 발생했습니다.',
    }

    render(<AnalysisDisplay {...defaultProps} analysisState={errorState} />)
    
    expect(screen.getByText('분석 중 오류가 발생했습니다')).toBeInTheDocument()
    expect(screen.getByText('분석 중 오류가 발생했습니다.')).toBeInTheDocument()
    expect(screen.getByText('다시 분석하기')).toBeInTheDocument()
    expect(screen.getByText('문제가 지속되는 경우:')).toBeInTheDocument()
  })

  it('should render success state with analysis data', () => {
    const successState: AnalysisState = {
      status: 'success',
      data: {
        content: '# 포트폴리오 분석 결과\n\n## 종합 점수: **85/100**\n\n### 주요 특징\n- 안정적인 포트폴리오 구성\n- 적절한 분산투자',
        processing_time: 2.5,
        request_id: 'test-123',
      },
      error: null,
    }

    render(<AnalysisDisplay {...defaultProps} analysisState={successState} />)
    
    expect(screen.getByText('포트폴리오 분석 완료')).toBeInTheDocument()
    expect(screen.getByText('처리 시간: 2.5초')).toBeInTheDocument()
    expect(screen.getByText('분석 ID: test-123')).toBeInTheDocument()
    expect(screen.getByTestId('markdown-content')).toBeInTheDocument()
  })

  it('should handle retry button click', () => {
    const errorState: AnalysisState = {
      status: 'error',
      data: null,
      error: '분석 중 오류가 발생했습니다.',
    }

    render(<AnalysisDisplay {...defaultProps} analysisState={errorState} />)
    
    const retryButton = screen.getByText('다시 분석하기')
    fireEvent.click(retryButton)
    
    expect(defaultProps.onRetry).toHaveBeenCalled()
  })

  it('should not render retry button when onRetry is not provided', () => {
    const errorState: AnalysisState = {
      status: 'error',
      data: null,
      error: '분석 중 오류가 발생했습니다.',
    }

    render(<AnalysisDisplay analysisState={errorState} />)
    
    expect(screen.queryByText('다시 분석하기')).not.toBeInTheDocument()
  })

  it('should return null for idle state', () => {
    const { container } = render(<AnalysisDisplay {...defaultProps} />)
    expect(container.firstChild).toBeNull()
  })

  it('should handle empty content gracefully', () => {
    const successState: AnalysisState = {
      status: 'success',
      data: {
        content: '',
        processing_time: 0.5,
        request_id: 'test-empty',
      },
      error: null,
    }

    render(<AnalysisDisplay {...defaultProps} analysisState={successState} />)
    
    expect(screen.getByText('포트폴리오 분석 완료')).toBeInTheDocument()
    expect(screen.getByText('처리 시간: 0.5초')).toBeInTheDocument()
  })

  it('should format processing time correctly', () => {
    const successState: AnalysisState = {
      status: 'success',
      data: {
        content: 'Test content',
        processing_time: 1.234567,
        request_id: 'test-format',
      },
      error: null,
    }

    render(<AnalysisDisplay {...defaultProps} analysisState={successState} />)
    
    expect(screen.getByText('처리 시간: 1.2초')).toBeInTheDocument()
  })
})