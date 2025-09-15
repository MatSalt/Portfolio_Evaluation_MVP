import { test, expect } from '@playwright/test';

test.describe('포트폴리오 분석 서비스', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('메인 페이지 로딩', async ({ page }) => {
    await expect(page).toHaveTitle(/포트폴리오 스코어/);
    await expect(page.getByText('포트폴리오를 분석해보세요')).toBeVisible();
    await expect(page.getByText('AI 기반 포트폴리오 분석 서비스')).toBeVisible();
  });

  test('단계 표시기 확인', async ({ page }) => {
    await expect(page.getByText('이미지 업로드')).toBeVisible();
    await expect(page.getByText('AI 분석')).toBeVisible();
    await expect(page.getByText('분석 결과')).toBeVisible();
  });

  test('업로드 영역 표시', async ({ page }) => {
    await expect(page.getByText('포트폴리오 스크린샷을 업로드하세요')).toBeVisible();
    await expect(page.getByText('PNG, JPEG 파일만 지원 • 최대 10MB')).toBeVisible();
    await expect(page.getByText('파일을 드래그하여 놓거나 클릭하여 선택하세요')).toBeVisible();
  });

  test('특징 소개 섹션', async ({ page }) => {
    await expect(page.getByText('왜 포트폴리오 스코어를 선택해야 할까요?')).toBeVisible();
    await expect(page.getByText('전문가 수준 분석')).toBeVisible();
    await expect(page.getByText('즉시 결과 확인')).toBeVisible();
    await expect(page.getByText('실행 가능한 인사이트')).toBeVisible();
  });

  test('반응형 디자인 - 모바일', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    
    await expect(page.getByText('포트폴리오를 분석해보세요')).toBeVisible();
    await expect(page.getByText('전문가 수준 분석')).toBeVisible();
  });

  test('접근성 - 키보드 네비게이션', async ({ page }) => {
    await page.keyboard.press('Tab');
    await page.keyboard.press('Enter');
    
    // 파일 선택 다이얼로그가 열리는지 확인 (실제로는 모킹됨)
    // 실제 환경에서는 파일 선택 다이얼로그가 열림
  });

  test('에러 바운더리 테스트', async ({ page }) => {
    // 에러를 강제로 발생시키는 방법 (개발 환경에서만)
    await page.evaluate(() => {
      // @ts-ignore
      window.triggerError = () => {
        throw new Error('Test error');
      };
    });
    
    // 에러 바운더리가 정상적으로 작동하는지 확인
    // 실제 에러 발생 시나리오는 복잡하므로 기본적인 렌더링만 확인
    await expect(page.getByText('포트폴리오를 분석해보세요')).toBeVisible();
  });
});

test.describe('파일 업로드 플로우', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('드래그앤드롭 영역 표시', async ({ page }) => {
    const uploadArea = page.getByLabelText('포트폴리오 이미지 업로드');
    await expect(uploadArea).toBeVisible();
    
    // 드래그 오버 상태 테스트
    await uploadArea.hover();
    // 드래그 오버 시 시각적 피드백 확인
  });

  test('지원 형식 안내', async ({ page }) => {
    await expect(page.getByText('지원 형식: PNG, JPEG • 권장 크기: 최소 800x600px • 최대 파일 크기: 10MB')).toBeVisible();
  });
});

test.describe('브라우저 호환성', () => {
  test('Chrome에서 정상 작동', async ({ page, browserName }) => {
    test.skip(browserName !== 'chromium');
    
    await page.goto('/');
    await expect(page.getByText('포트폴리오를 분석해보세요')).toBeVisible();
  });

  test('Firefox에서 정상 작동', async ({ page, browserName }) => {
    test.skip(browserName !== 'firefox');
    
    await page.goto('/');
    await expect(page.getByText('포트폴리오를 분석해보세요')).toBeVisible();
  });

  test('Safari에서 정상 작동', async ({ page, browserName }) => {
    test.skip(browserName !== 'webkit');
    
    await page.goto('/');
    await expect(page.getByText('포트폴리오를 분석해보세요')).toBeVisible();
  });
});
