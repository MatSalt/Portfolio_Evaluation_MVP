// src/components/__tests__/ImageUploader.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ImageUploader from '../ImageUploader'
import { UploadState } from '@/types/portfolio'

const mockUploadState: UploadState = {
  status: 'idle',
  file: null,
  preview: null,
  error: null,
}

const defaultProps = {
  uploadState: mockUploadState,
  onFileSelect: jest.fn(),
  onRemoveFile: jest.fn(),
  disabled: false,
}

describe('ImageUploader', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should render idle state correctly', () => {
    render(<ImageUploader {...defaultProps} />)
    
    expect(screen.getByText('포트폴리오 스크린샷을 업로드하세요')).toBeInTheDocument()
    expect(screen.getByText('PNG, JPEG 파일만 지원 • 최대 10MB')).toBeInTheDocument()
    expect(screen.getByText('파일을 드래그하여 놓거나 클릭하여 선택하세요')).toBeInTheDocument()
  })

  it('should render success state with preview', () => {
    const mockFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    const successState: UploadState = {
      status: 'success',
      file: mockFile,
      preview: 'data:image/jpeg;base64,test',
      error: null,
    }

    render(<ImageUploader {...defaultProps} uploadState={successState} />)
    
    expect(screen.getByText('업로드 완료')).toBeInTheDocument()
    expect(screen.getByText('test.jpg (0.00 MB)')).toBeInTheDocument()
    expect(screen.getByAltText('업로드된 포트폴리오 미리보기')).toBeInTheDocument()
  })

  it('should render error state', () => {
    const errorState: UploadState = {
      status: 'error',
      file: null,
      preview: null,
      error: '파일 형식이 올바르지 않습니다.',
    }

    render(<ImageUploader {...defaultProps} uploadState={errorState} />)
    
    expect(screen.getByText('업로드 오류')).toBeInTheDocument()
    expect(screen.getByText('파일 형식이 올바르지 않습니다.')).toBeInTheDocument()
    expect(screen.getByText('클릭하여 다시 시도하세요')).toBeInTheDocument()
  })

  it('should handle drag and drop', async () => {
    render(<ImageUploader {...defaultProps} />)
    
    const dropZone = screen.getByLabelText('포트폴리오 이미지 업로드')
    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    
    // Test drag over
    fireEvent.dragOver(dropZone, {
      dataTransfer: {
        files: [file],
      },
    })
    
    // Test drop
    fireEvent.drop(dropZone, {
      dataTransfer: {
        files: [file],
      },
    })
    
    expect(defaultProps.onFileSelect).toHaveBeenCalledWith(file)
  })

  it('should handle file removal', async () => {
    const user = userEvent.setup()
    const mockFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    const successState: UploadState = {
      status: 'success',
      file: mockFile,
      preview: 'data:image/jpeg;base64,test',
      error: null,
    }

    render(<ImageUploader {...defaultProps} uploadState={successState} />)
    
    const removeButton = screen.getByLabelText('이미지 제거')
    await user.click(removeButton)
    
    expect(defaultProps.onRemoveFile).toHaveBeenCalled()
  })

  it('should be disabled when disabled prop is true', () => {
    render(<ImageUploader {...defaultProps} disabled={true} />)
    
    const dropZone = screen.getByLabelText('포트폴리오 이미지 업로드')
    expect(dropZone).toHaveClass('cursor-not-allowed')
  })

  it('should show drag overlay on drag over', () => {
    render(<ImageUploader {...defaultProps} />)
    
    const dropZone = screen.getByLabelText('포트폴리오 이미지 업로드')
    
    fireEvent.dragOver(dropZone)
    
    expect(screen.getByText('여기에 파일을 놓으세요')).toBeInTheDocument()
  })

  it('should display file size correctly', () => {
    const mockFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    Object.defineProperty(mockFile, 'size', { value: 1024 * 1024 }) // 1MB
    
    const successState: UploadState = {
      status: 'success',
      file: mockFile,
      preview: 'data:image/jpeg;base64,test',
      error: null,
    }

    render(<ImageUploader {...defaultProps} uploadState={successState} />)
    
    expect(screen.getByText('test.jpg (1.00 MB)')).toBeInTheDocument()
  })
})