// src/components/ImageUploader.tsx
'use client';

import React, { useRef, useState, useCallback } from 'react';
import { Upload, X, AlertCircle, CheckCircle, Image as ImageIcon } from 'lucide-react';
import { UploadState } from '@/types/portfolio';

interface ImageUploaderProps {
  uploadState: UploadState;
  onFileSelect: (file: File) => void;
  onRemoveFile: () => void;
  disabled?: boolean;
}

export default function ImageUploader({
  uploadState,
  onFileSelect,
  onRemoveFile,
  disabled = false,
}: ImageUploaderProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragOver, setIsDragOver] = useState(false);

  // 파일 선택 처리
  const handleFileSelect = useCallback((files: FileList | null) => {
    if (files && files.length > 0) {
      onFileSelect(files[0]);
    }
  }, [onFileSelect]);

  // 파일 입력 변경 핸들러
  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    handleFileSelect(event.target.files);
    // 입력 초기화 (같은 파일 재선택 허용)
    event.target.value = '';
  };

  // 드래그 이벤트 핸들러들
  const handleDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    if (!disabled) {
      setIsDragOver(true);
    }
  }, [disabled]);

  const handleDragLeave = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    // 드래그 영역을 벗어났는지 확인 (자식 요소 고려)
    if (!event.currentTarget.contains(event.relatedTarget as Node)) {
      setIsDragOver(false);
    }
  }, []);

  const handleDrop = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(false);
    
    if (!disabled) {
      const files = event.dataTransfer.files;
      handleFileSelect(files);
    }
  }, [disabled, handleFileSelect]);

  // 클릭으로 파일 선택
  const handleClick = () => {
    if (!disabled && fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  // 상태별 스타일 클래스
  const getContainerClasses = () => {
    const baseClasses = "relative w-full border-2 border-dashed rounded-lg transition-all duration-200 cursor-pointer";
    
    if (disabled) {
      return `${baseClasses} border-gray-300 bg-gray-50 cursor-not-allowed`;
    }
    
    if (uploadState.status === 'error') {
      return `${baseClasses} border-red-300 bg-red-50 hover:border-red-400`;
    }
    
    if (uploadState.status === 'success') {
      return `${baseClasses} border-green-300 bg-green-50`;
    }
    
    if (isDragOver) {
      return `${baseClasses} border-blue-400 bg-blue-50`;
    }
    
    return `${baseClasses} border-gray-300 bg-gray-50 hover:border-gray-400 hover:bg-gray-100`;
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      {/* 파일 업로드 영역 */}
      <div
        className={getContainerClasses()}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
        role="button"
        tabIndex={0}
        aria-label="포트폴리오 이미지 업로드"
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            handleClick();
          }
        }}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/png,image/jpeg,image/jpg"
          onChange={handleInputChange}
          className="sr-only"
          aria-describedby="file-upload-description"
        />

        {/* 업로드 상태별 UI */}
        <div className="p-8">
          {uploadState.status === 'idle' && (
            <div className="text-center">
              <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                포트폴리오 스크린샷을 업로드하세요
              </h3>
              <p className="text-sm text-gray-600 mb-4" id="file-upload-description">
                PNG, JPEG 파일만 지원 • 최대 10MB
              </p>
              <div className="space-y-2">
                <p className="text-sm text-gray-500">
                  파일을 드래그하여 놓거나 클릭하여 선택하세요
                </p>
              </div>
            </div>
          )}

          {uploadState.status === 'success' && uploadState.preview && (
            <div className="text-center">
              <div className="relative inline-block mb-4">
                <img
                  src={uploadState.preview}
                  alt="업로드된 포트폴리오 미리보기"
                  className="max-w-full max-h-48 rounded-lg shadow-md"
                />
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onRemoveFile();
                  }}
                  className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 transition-colors"
                  aria-label="이미지 제거"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
              
              <div className="flex items-center justify-center text-green-600 mb-2">
                <CheckCircle className="h-5 w-5 mr-2" />
                <span className="font-medium">업로드 완료</span>
              </div>
              
              {uploadState.file && (
                <p className="text-sm text-gray-600">
                  {uploadState.file.name} ({(uploadState.file.size / 1024 / 1024).toFixed(2)} MB)
                </p>
              )}
            </div>
          )}

          {uploadState.status === 'error' && (
            <div className="text-center">
              <AlertCircle className="mx-auto h-12 w-12 text-red-400 mb-4" />
              <h3 className="text-lg font-semibold text-red-900 mb-2">
                업로드 오류
              </h3>
              <p className="text-sm text-red-600 mb-4">
                {uploadState.error}
              </p>
              <p className="text-xs text-gray-500">
                클릭하여 다시 시도하세요
              </p>
            </div>
          )}
        </div>

        {/* 드래그 오버레이 */}
        {isDragOver && (
          <div className="absolute inset-0 bg-blue-50 bg-opacity-90 rounded-lg flex items-center justify-center">
            <div className="text-center">
              <ImageIcon className="mx-auto h-12 w-12 text-blue-500 mb-2" />
              <p className="text-blue-700 font-medium">
                여기에 파일을 놓으세요
              </p>
            </div>
          </div>
        )}
      </div>

      {/* 지원 형식 안내 */}
      <div className="mt-4 text-center">
        <p className="text-xs text-gray-500">
          지원 형식: PNG, JPEG • 권장 크기: 최소 800x600px • 최대 파일 크기: 10MB
        </p>
      </div>
    </div>
  );
}
