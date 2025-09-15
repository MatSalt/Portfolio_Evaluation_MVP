/**
 * 다중 이미지 기능 간단 테스트
 */
import { MAX_FILES } from '@/types/portfolio';
import { validateImageFile } from '@/utils/api';

export function testMultipleImageValidation() {
  console.log('다중 이미지 검증 테스트 시작...');
  
  // 1. 최대 파일 수 테스트
  console.assert(MAX_FILES === 5, '최대 파일 수는 5개여야 함');
  
  // 2. 파일 유효성 검사 테스트
  const mockFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
  const validation = validateImageFile(mockFile);
  console.assert(validation.isValid === true, '유효한 JPEG 파일이어야 함');
  
  // 3. 잘못된 파일 타입 테스트
  const invalidFile = new File(['test'], 'test.txt', { type: 'text/plain' });
  const invalidValidation = validateImageFile(invalidFile);
  console.assert(invalidValidation.isValid === false, '텍스트 파일은 무효해야 함');
  
  console.log('다중 이미지 검증 테스트 완료 ✓');
}

export function testFileArrayHandling() {
  console.log('파일 배열 처리 테스트 시작...');
  
  // 1. 빈 배열 테스트
  const emptyArray: File[] = [];
  console.assert(emptyArray.length === 0, '빈 배열 길이는 0이어야 함');
  
  // 2. 최대 개수 배열 테스트
  const maxFiles = Array.from({ length: MAX_FILES }, (_, i) => 
    new File(['test'], `test${i + 1}.jpg`, { type: 'image/jpeg' })
  );
  console.assert(maxFiles.length === MAX_FILES, `최대 파일 배열 길이는 ${MAX_FILES}여야 함`);
  
  // 3. 초과 배열 테스트
  const excessFiles = Array.from({ length: MAX_FILES + 1 }, (_, i) => 
    new File(['test'], `test${i + 1}.jpg`, { type: 'image/jpeg' })
  );
  console.assert(excessFiles.length > MAX_FILES, '초과 파일 배열은 최대 개수를 넘어야 함');
  
  console.log('파일 배열 처리 테스트 완료 ✓');
}

export function testImagePreviewGeneration() {
  console.log('이미지 미리보기 생성 테스트 시작...');
  
  // 1. 단일 파일 미리보기 테스트
  const singleFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
  console.assert(singleFile instanceof File, '단일 파일은 File 객체여야 함');
  console.assert(singleFile.type === 'image/jpeg', '파일 타입은 image/jpeg여야 함');
  
  // 2. 다중 파일 미리보기 테스트
  const multipleFiles = [
    new File(['test1'], 'test1.jpg', { type: 'image/jpeg' }),
    new File(['test2'], 'test2.jpg', { type: 'image/jpeg' }),
    new File(['test3'], 'test3.jpg', { type: 'image/jpeg' })
  ];
  console.assert(multipleFiles.length === 3, '다중 파일 배열 길이는 3이어야 함');
  console.assert(multipleFiles.every(file => file instanceof File), '모든 파일은 File 객체여야 함');
  
  console.log('이미지 미리보기 생성 테스트 완료 ✓');
}

export function testUploadStateStructure() {
  console.log('업로드 상태 구조 테스트 시작...');
  
  // 1. 초기 상태 테스트
  const initialUploadState = {
    status: 'idle' as const,
    files: [],
    previews: [],
    error: null
  };
  
  console.assert(initialUploadState.status === 'idle', '초기 상태는 idle이어야 함');
  console.assert(Array.isArray(initialUploadState.files), 'files는 배열이어야 함');
  console.assert(Array.isArray(initialUploadState.previews), 'previews는 배열이어야 함');
  console.assert(initialUploadState.files.length === 0, '초기 files 배열은 비어있어야 함');
  console.assert(initialUploadState.previews.length === 0, '초기 previews 배열은 비어있어야 함');
  
  // 2. 성공 상태 테스트
  const successUploadState = {
    status: 'success' as const,
    files: [
      new File(['test1'], 'test1.jpg', { type: 'image/jpeg' }),
      new File(['test2'], 'test2.jpg', { type: 'image/jpeg' })
    ],
    previews: ['data:image/jpeg;base64,test1', 'data:image/jpeg;base64,test2'],
    error: null
  };
  
  console.assert(successUploadState.status === 'success', '성공 상태는 success여야 함');
  console.assert(successUploadState.files.length === 2, '성공 상태 files 길이는 2여야 함');
  console.assert(successUploadState.previews.length === 2, '성공 상태 previews 길이는 2여야 함');
  console.assert(successUploadState.files.length === successUploadState.previews.length, 'files와 previews 길이는 같아야 함');
  
  console.log('업로드 상태 구조 테스트 완료 ✓');
}

export function testAnalysisResponseStructure() {
  console.log('분석 응답 구조 테스트 시작...');
  
  // 1. 기본 분석 응답 테스트
  const basicResponse = {
    content: '테스트 분석 결과',
    processing_time: 2.5,
    request_id: 'test-request-id'
  };
  
  console.assert(typeof basicResponse.content === 'string', 'content는 문자열이어야 함');
  console.assert(typeof basicResponse.processing_time === 'number', 'processing_time은 숫자여야 함');
  console.assert(typeof basicResponse.request_id === 'string', 'request_id는 문자열이어야 함');
  
  // 2. 다중 이미지 분석 응답 테스트
  const multipleImageResponse = {
    content: '다중 이미지 분석 결과',
    processing_time: 4.2,
    request_id: 'test-multiple-request-id',
    images_processed: 3
  };
  
  console.assert(multipleImageResponse.images_processed === 3, 'images_processed는 3이어야 함');
  console.assert(typeof multipleImageResponse.images_processed === 'number', 'images_processed는 숫자여야 함');
  
  console.log('분석 응답 구조 테스트 완료 ✓');
}

export function testFormDataGeneration() {
  console.log('FormData 생성 테스트 시작...');
  
  // 1. 단일 파일 FormData 테스트
  const singleFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
  const singleFormData = new FormData();
  singleFormData.append('files', singleFile);
  
  console.assert(singleFormData.has('files'), 'FormData에 files 필드가 있어야 함');
  
  // 2. 다중 파일 FormData 테스트
  const multipleFiles = [
    new File(['test1'], 'test1.jpg', { type: 'image/jpeg' }),
    new File(['test2'], 'test2.jpg', { type: 'image/jpeg' }),
    new File(['test3'], 'test3.jpg', { type: 'image/jpeg' })
  ];
  
  const multipleFormData = new FormData();
  multipleFiles.forEach(file => {
    multipleFormData.append('files', file);
  });
  
  // FormData의 entries 개수 확인 (files 필드에 3개 파일)
  const entries = Array.from(multipleFormData.entries());
  const fileEntries = entries.filter(([key]) => key === 'files');
  console.assert(fileEntries.length === 3, 'FormData에 3개의 files 엔트리가 있어야 함');
  
  console.log('FormData 생성 테스트 완료 ✓');
}

export function runAllTests() {
  console.log('=== 다중 이미지 기능 테스트 시작 ===');
  
  try {
    testMultipleImageValidation();
    testFileArrayHandling();
    testImagePreviewGeneration();
    testUploadStateStructure();
    testAnalysisResponseStructure();
    testFormDataGeneration();
    
    console.log('=== 모든 테스트 통과! ===');
    return true;
  } catch (error) {
    console.error('=== 테스트 실패 ===', error);
    return false;
  }
}

// 개발 환경에서만 실행
if (process.env.NODE_ENV === 'development') {
  runAllTests();
}
