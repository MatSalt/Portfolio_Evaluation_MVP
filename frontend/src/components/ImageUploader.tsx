// src/components/ImageUploader.tsx
'use client';

import React, { useCallback, useRef, useState } from 'react';
import { Upload, X, CheckCircle, AlertCircle, Image as ImageIcon } from 'lucide-react';
import { UploadState, MAX_FILES } from '@/types/portfolio';

interface ImageUploaderProps {
  uploadState: UploadState;
  onFileSelect: (files: File[]) => void;
  onRemoveFile: (index: number) => void;
  disabled?: boolean;
}

export default function ImageUploader({ 
  uploadState, 
  onFileSelect, 
  onRemoveFile, 
  disabled = false 
}: ImageUploaderProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 파일 선택 핸들러
  const handleFileSelect = useCallback((selectedFiles: FileList | null) => {
    if (!selectedFiles || selectedFiles.length === 0) return;
    
    // 기존 파일과 새 파일 합치기 (최대 5개까지)
    const newFiles = Array.from(selectedFiles);
    const totalFiles = [...uploadState.files, ...newFiles].slice(0, MAX_FILES);
    
    onFileSelect(totalFiles);
  }, [uploadState.files, onFileSelect]);

  // 파일 입력 변경 핸들러
  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    handleFileSelect(event.target.files);
    event.target.value = ''; // 입력 초기화
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
    if (!event.currentTarget.contains(event.relatedTarget as Node)) {
      setIsDragOver(false);
    }
  }, []);

  const handleDrop = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(false);
    
    if (!disabled) {
      handleFileSelect(event.dataTransfer.files);
    }
  }, [disabled, handleFileSelect]);

  // 파일 추가 버튼 클릭
  const handleAddClick = () => {
    if (!disabled && uploadState.files.length < MAX_FILES) {
      fileInputRef.current?.click();
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      {/* 파일 입력 */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/png,image/jpeg,image/jpg"
        multiple // 다중 선택 활성화
        onChange={handleInputChange}
        className="sr-only"
        aria-describedby="file-upload-description"
      />

      {/* 드롭존 또는 파일 미리보기 */}
      {uploadState.files.length === 0 ? (
        /* 빈 상태: 드롭존 표시 */
        <div
          className={`
            relative border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200
            ${isDragOver 
              ? 'border-blue-400 bg-blue-50' 
              : uploadState.status === 'error'
              ? 'border-red-300 bg-red-50'
              : 'border-gray-300 bg-gray-50 hover:border-gray-400'
            }
            ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
          `}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={handleAddClick}
          role="button"
          tabIndex={disabled ? -1 : 0}
          aria-label="파일 업로드"
        >
          <div className="space-y-4">
            <Upload className="mx-auto h-12 w-12 text-gray-400" />
            <div className="space-y-2">
              <p className="text-lg font-medium text-gray-900">
                포트폴리오 이미지를 업로드하세요
              </p>
              <p className="text-sm text-gray-600">
                파일을 여기로 드래그하거나 클릭하여 선택하세요
              </p>
              <p className="text-xs text-gray-500">
                최대 {MAX_FILES}개, PNG/JPEG, 각 파일 최대 10MB
              </p>
            </div>
          </div>

          {isDragOver && (
            <div className="absolute inset-0 bg-blue-100 bg-opacity-50 rounded-lg flex items-center justify-center">
              <p className="text-blue-700 font-medium">
                여기에 파일을 놓으세요
              </p>
            </div>
          )}
        </div>
      ) : (
        /* 파일 미리보기 갤러리 */
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {uploadState.files.map((file, index) => (
              <div key={`${file.name}-${index}`} className="relative group">
                {/* 이미지 미리보기 */}
                <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden border">
                  {uploadState.previews[index] ? (
                    <img
                      src={uploadState.previews[index]}
                      alt={`미리보기 ${index + 1}`}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <ImageIcon className="h-8 w-8 text-gray-400" />
                    </div>
                  )}
                </div>

                {/* 삭제 버튼 */}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onRemoveFile(index);
                  }}
                  className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 transition-colors opacity-0 group-hover:opacity-100"
                  aria-label={`이미지 ${index + 1} 제거`}
                >
                  <X className="h-4 w-4" />
                </button>

                {/* 파일 정보 */}
                <div className="mt-2 text-xs text-gray-600 truncate">
                  {file.name}
                </div>
                <div className="text-xs text-gray-500">
                  {(file.size / 1024 / 1024).toFixed(1)} MB
                </div>
              </div>
            ))}

            {/* 추가 버튼 (최대 개수 미만일 때) */}
            {uploadState.files.length < MAX_FILES && (
              <button
                onClick={handleAddClick}
                disabled={disabled}
                className={`
                  aspect-square border-2 border-dashed border-gray-300 rounded-lg 
                  flex flex-col items-center justify-center text-gray-500 
                  hover:border-gray-400 hover:text-gray-600 transition-colors
                  ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                `}
              >
                <Upload className="h-6 w-6 mb-2" />
                <span className="text-xs">추가</span>
              </button>
            )}
          </div>

          {/* 파일 상태 정보 */}
          <div className="text-center text-sm text-gray-600">
            {uploadState.files.length}/{MAX_FILES}개 파일 선택됨
          </div>
        </div>
      )}

      {/* 에러 메시지 */}
      {uploadState.status === 'error' && uploadState.error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center">
            <AlertCircle className="h-4 w-4 text-red-500 mr-2" />
            <p className="text-sm text-red-700">{uploadState.error}</p>
          </div>
        </div>
      )}

      {/* 지원 형식 안내 */}
      <div className="mt-4 text-center">
        <p className="text-xs text-gray-500">
          지원 형식: PNG, JPEG • 권장 크기: 최소 800x600px • 최대 파일 크기: 10MB
        </p>
      </div>
    </div>
  );
}
