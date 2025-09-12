# Git 전략 및 브랜치 전략

## 📋 개요
Portfolio Evaluation MVP 프로젝트에서 사용할 간단하고 대중적인 Git 전략과 브랜치 전략을 정의합니다.

## 🌿 브랜치 전략: Git Flow

### 기본 원칙
- **main**: 프로덕션 배포 가능한 안정적인 코드
- **develop**: 다음 릴리스를 위한 개발 브랜치
- **feature/**: 새로운 기능 개발 브랜치
- **release/**: 릴리스 준비 브랜치
- **hotfix/**: 긴급 버그 수정 브랜치

### 브랜치 구조
```
main (프로덕션)
├── develop (개발)
│   ├── feature/image-upload
│   ├── feature/gemini-integration
│   └── feature/analysis-display
├── release/v1.0.0
└── hotfix/critical-bug-fix
```

## 🔄 워크플로우

### 1. 기능 개발 (Feature Development)
```bash
# 1. develop 브랜치에서 최신 코드 가져오기
git checkout develop
git pull origin develop

# 2. 기능 브랜치 생성 및 전환
git checkout -b feature/기능명

# 3. 개발 작업 수행
# ... 코드 작성 ...

# 4. 변경사항 커밋
git add .
git commit -m "feat: 이미지 업로드 기능 추가"

# 5. 원격 저장소에 푸시
git push origin feature/기능명

# 6. Pull Request 생성 (develop 브랜치로)
# 7. 코드 리뷰 후 develop 브랜치로 병합
```

### 2. 릴리스 준비 (Release)
```bash
# 1. develop 브랜치에서 release 브랜치 생성
git checkout develop
git checkout -b release/v1.0.0

# 2. 릴리스 준비 작업
# - 버전 번호 업데이트
# - 최종 테스트
# - 문서 업데이트

# 3. 커밋 및 푸시
git add .
git commit -m "chore: v1.0.0 릴리스 준비"
git push origin release/v1.0.0

# 4. Pull Request 생성하여 main과 develop으로 병합
```

### 3. 긴급 버그 수정 (Hotfix)
```bash
# 1. main 브랜치에서 hotfix 브랜치 생성
git checkout main
git checkout -b hotfix/버그설명

# 2. 버그 수정
# ... 수정 작업 ...

# 3. 커밋 및 푸시
git add .
git commit -m "hotfix: 이미지 업로드 오류 수정"
git push origin hotfix/버그설명

# 4. Pull Request 생성하여 main과 develop으로 병합
```

## 📝 커밋 메시지 규칙

### 형식
```
타입(범위): 간단한 설명

상세 설명 (선택사항)

- 변경사항 1
- 변경사항 2
```

### 타입 (Type)
- **feat**: 새로운 기능 추가
- **fix**: 버그 수정
- **docs**: 문서 수정
- **style**: 코드 포맷팅, 세미콜론 누락 등
- **refactor**: 코드 리팩토링
- **test**: 테스트 코드 추가/수정
- **chore**: 빌드 과정, 보조 도구 변경

### 예시
```bash
# 기능 추가
git commit -m "feat(upload): 드래그 앤 드롭 이미지 업로드 기능 추가"

# 버그 수정
git commit -m "fix(api): Gemini API 응답 파싱 오류 수정"

# 문서 수정
git commit -m "docs(readme): 설치 가이드 업데이트"

# 리팩토링
git commit -m "refactor(components): ImageUploader 컴포넌트 구조 개선"
```

## 🚀 배포 전략

### 환경별 브랜치
- **main**: 프로덕션 환경 (Vercel, Render)
- **develop**: 개발 환경 (스테이징)

### 배포 프로세스
1. feature 브랜치 → develop 브랜치 병합 (개발 환경 배포)
2. develop 브랜치 → release 브랜치 생성
3. release 브랜치 → main 브랜치 병합 (프로덕션 환경 배포)
4. 자동 배포 트리거 (GitHub Actions)

## 🔧 Git 설정

### 기본 설정
```bash
# 사용자 정보 설정
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 기본 브랜치명 설정
git config --global init.defaultBranch main

# 자동 줄바꿈 설정
git config --global core.autocrlf input
```

### 유용한 Git 명령어
```bash
# 브랜치 목록 확인
git branch -a

# 브랜치 삭제
git branch -d feature/기능명

# 원격 브랜치 삭제
git push origin --delete feature/기능명

# 커밋 히스토리 확인
git log --oneline

# 변경사항 되돌리기
git reset --hard HEAD~1

# 특정 파일만 되돌리기
git checkout HEAD -- 파일명
```

## 📋 체크리스트

### Pull Request 생성 전
- [ ] 코드가 정상적으로 작동하는지 확인
- [ ] 테스트 코드 작성 및 통과
- [ ] 코드 리뷰 요청
- [ ] 문서 업데이트 (필요시)

### 병합 전
- [ ] 충돌 해결
- [ ] 최신 main 브랜치와 동기화
- [ ] 최종 테스트 수행

## 🚨 주의사항

### 절대 하지 말아야 할 것
- main 브랜치에 직접 커밋하지 않기
- develop 브랜치에 직접 커밋하지 않기
- 커밋 메시지를 "수정", "업데이트" 등으로 작성하지 않기
- 큰 변경사항을 한 번에 커밋하지 않기

### 권장사항
- 작은 단위로 자주 커밋하기
- 의미 있는 커밋 메시지 작성하기
- 정기적으로 develop 브랜치와 동기화하기
- Pull Request를 통한 코드 리뷰 진행하기
- 릴리스 전 충분한 테스트 수행하기

## 🔗 참고 자료
- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Best Practices](https://git-scm.com/book/en/v2/Git-Branching-Branching-Workflows)
