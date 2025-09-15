// src/hooks/__tests__/usePortfolioAnalysis.test.tsx
import { renderHook, act } from '@testing-library/react'
import { usePortfolioAnalysis } from '../usePortfolioAnalysis'

// Mock API functions
jest.mock('@/utils/api', () => ({
  validateImageFile: jest.fn(),
  fileToBase64: jest.fn(),
  analyzePortfolio: jest.fn(),
}))

import * as api from '@/utils/api'
const mockApi = api as jest.Mocked<typeof api>

describe('usePortfolioAnalysis', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should initialize with idle state', () => {
    const { result } = renderHook(() => usePortfolioAnalysis())
    
    expect(result.current.uploadState.status).toBe('idle')
    expect(result.current.analysisState.status).toBe('idle')
    expect(result.current.isLoading).toBe(false)
    expect(result.current.canAnalyze).toBe(false)
  })

  it('should handle file selection successfully', async () => {
    const mockFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    const mockPreview = 'data:image/jpeg;base64,test'
    
    mockApi.validateImageFile.mockReturnValue({ isValid: true })
    mockApi.fileToBase64.mockResolvedValue(mockPreview)

    const { result } = renderHook(() => usePortfolioAnalysis())

    await act(async () => {
      result.current.handleFileSelect(mockFile)
    })

    expect(mockApi.validateImageFile).toHaveBeenCalledWith(mockFile)
    expect(mockApi.fileToBase64).toHaveBeenCalledWith(mockFile)
    expect(result.current.uploadState.status).toBe('success')
    expect(result.current.uploadState.file).toBe(mockFile)
    expect(result.current.uploadState.preview).toBe(mockPreview)
    expect(result.current.canAnalyze).toBe(true)
  })

  it('should handle file validation error', async () => {
    const mockFile = new File(['test'], 'test.gif', { type: 'image/gif' })
    
    mockApi.validateImageFile.mockReturnValue({ 
      isValid: false, 
      error: 'PNG, JPEG 파일만 업로드 가능합니다.' 
    })

    const { result } = renderHook(() => usePortfolioAnalysis())

    await act(async () => {
      result.current.handleFileSelect(mockFile)
    })

    expect(result.current.uploadState.status).toBe('error')
    expect(result.current.uploadState.error).toBe('PNG, JPEG 파일만 업로드 가능합니다.')
    expect(result.current.canAnalyze).toBe(false)
  })

  it('should handle file preview generation error', async () => {
    const mockFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    
    mockApi.validateImageFile.mockReturnValue({ isValid: true })
    mockApi.fileToBase64.mockRejectedValue(new Error('Preview error'))

    const { result } = renderHook(() => usePortfolioAnalysis())

    await act(async () => {
      result.current.handleFileSelect(mockFile)
    })

    expect(result.current.uploadState.status).toBe('error')
    expect(result.current.uploadState.error).toBe('이미지 미리보기 생성에 실패했습니다.')
  })

  it('should analyze image successfully', async () => {
    const mockFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    const mockAnalysisResult = {
      content: '# 분석 결과\n포트폴리오 점수: 85/100',
      processing_time: 2.5,
      request_id: 'test-123'
    }
    
    mockApi.validateImageFile.mockReturnValue({ isValid: true })
    mockApi.fileToBase64.mockResolvedValue('data:image/jpeg;base64,test')
    mockApi.analyzePortfolio.mockResolvedValue(mockAnalysisResult)

    const { result } = renderHook(() => usePortfolioAnalysis())

    // First, select a file
    await act(async () => {
      result.current.handleFileSelect(mockFile)
    })

    // Then analyze
    await act(async () => {
      result.current.analyzeImage()
    })

    expect(mockApi.analyzePortfolio).toHaveBeenCalledWith(mockFile)
    expect(result.current.analysisState.status).toBe('success')
    expect(result.current.analysisState.data).toEqual(mockAnalysisResult)
    expect(result.current.isLoading).toBe(false)
  })

  it('should handle analysis error', async () => {
    const mockFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    
    mockApi.validateImageFile.mockReturnValue({ isValid: true })
    mockApi.fileToBase64.mockResolvedValue('data:image/jpeg;base64,test')
    mockApi.analyzePortfolio.mockRejectedValue(new Error('Analysis failed'))

    const { result } = renderHook(() => usePortfolioAnalysis())

    // First, select a file
    await act(async () => {
      result.current.handleFileSelect(mockFile)
    })

    // Then analyze
    await act(async () => {
      result.current.analyzeImage()
    })

    expect(result.current.analysisState.status).toBe('error')
    expect(result.current.analysisState.error).toBe('Analysis failed')
    expect(result.current.isLoading).toBe(false)
  })

  it('should handle analysis without file', async () => {
    const { result } = renderHook(() => usePortfolioAnalysis())

    await act(async () => {
      result.current.analyzeImage()
    })

    expect(result.current.analysisState.status).toBe('error')
    expect(result.current.analysisState.error).toBe('분석할 파일이 없습니다.')
  })

  it('should reset state', async () => {
    const mockFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    
    mockApi.validateImageFile.mockReturnValue({ isValid: true })
    mockApi.fileToBase64.mockResolvedValue('data:image/jpeg;base64,test')

    const { result } = renderHook(() => usePortfolioAnalysis())

    // First, select a file
    await act(async () => {
      result.current.handleFileSelect(mockFile)
    })

    // Then reset
    act(() => {
      result.current.reset()
    })

    expect(result.current.uploadState.status).toBe('idle')
    expect(result.current.analysisState.status).toBe('idle')
    expect(result.current.uploadState.file).toBe(null)
    expect(result.current.analysisState.data).toBe(null)
  })

  it('should remove file', async () => {
    const mockFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    
    mockApi.validateImageFile.mockReturnValue({ isValid: true })
    mockApi.fileToBase64.mockResolvedValue('data:image/jpeg;base64,test')

    const { result } = renderHook(() => usePortfolioAnalysis())

    // First, select a file
    await act(async () => {
      result.current.handleFileSelect(mockFile)
    })

    // Then remove file
    act(() => {
      result.current.removeFile()
    })

    expect(result.current.uploadState.status).toBe('idle')
    expect(result.current.uploadState.file).toBe(null)
    expect(result.current.uploadState.preview).toBe(null)
  })
})