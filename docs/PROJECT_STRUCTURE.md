# ☕ Cafe Menu Recommendation System - 구조 설계

## 1) 목표
광고성 리뷰를 제외하고, 실제 리뷰 기반으로 카페별 인기 메뉴 TOP N을 추천하는 API 서비스를 구축한다.

---

## 2) 아키텍처

```text
크롤링(BeautifulSoup/Selenium)
  → MongoDB(원본 리뷰 저장)
    → 광고 필터링 + 메뉴 추출 + 빈도 분석
      → MySQL(정제/집계 데이터 저장)
        → FastAPI(API 제공)
```

---

## 3) 디렉터리 구조

```text
cafe-menu-recommendation-system/
├─ app/
│  ├─ api/
│  │  └─ menu.py                # 추천 API 라우터
│  ├─ core/
│  │  └─ config.py              # .env 기반 설정
│  ├─ models/
│  │  └─ schema.py              # 요청/응답 스키마
│  ├─ services/
│  │  └─ recommendation.py      # 추천 서비스 로직
│  └─ main.py                   # FastAPI 엔트리포인트
├─ crawler/
│  └─ crawler_blog.py           # STEP1: 리뷰 크롤링
├─ analyzer/
│  ├─ ad_filter.py              # STEP3: 광고 필터링
│  └─ menu_analyzer.py          # STEP4: 메뉴 추출/빈도 분석
├─ storage/
│  ├─ mongo_client.py           # STEP2: MongoDB 저장/조회
│  └─ mysql_client.py           # MySQL 저장/조회
├─ scripts/
│  └─ run_pipeline.py           # 단계별 파이프라인 실행 스크립트
├─ tests/
│  ├─ test_ad_filter.py         # 광고 필터링 테스트
│  └─ test_menu_analyzer.py     # 메뉴 추출 테스트
├─ docs/
│  └─ PROJECT_STRUCTURE.md
├─ .env.example
├─ .gitignore
└─ requirements.txt
```

---

## 4) 개발 단계 매핑

- STEP 1: `crawler/crawler_blog.py`
- STEP 2: `storage/mongo_client.py`
- STEP 3: `analyzer/ad_filter.py`
- STEP 4: `analyzer/menu_analyzer.py` + `storage/mysql_client.py`
- STEP 5: `app/main.py`, `app/api/menu.py`, `app/services/recommendation.py`
- STEP 6: Render 배포 (`render.yaml` 또는 Render 대시보드 설정)

---

## 5) 보안 원칙

- API Key, DB 비밀번호는 `.env`만 사용
- `.gitignore`에 `.env`, `__pycache__/` 포함
- 코드에 민감정보 하드코딩 금지

---

## 6) 구현 시작 전략

1. **최소 1개 카페/페이지 크롤링 성공**
2. MongoDB에 리뷰 저장 확인
3. 광고 필터링 규칙 1차 적용
4. 메뉴 추출 + 빈도 집계 검증
5. FastAPI로 TOP N 조회 API 제공
6. Render 배포용 실행 커맨드 정리

---

## 7) 세부 진행순서 (고정 실행 절차)

아래 순서대로만 진행한다. 단계 스킵 금지.

### STEP 0. 문서 기준 확정
1. `docs/DB_SPEC.md`, `docs/API_SPEC.md`, `docs/WORKING_AGREEMENT.md` 확인
2. 구현 대상/응답 형식/스키마를 문서 기준으로 확정

### STEP 1. 크롤링 구현
1. 타겟 URL 1개 선정
2. 페이지 접근/본문 추출
3. 리뷰 최소 1건 이상 확보
4. 샘플 출력으로 수집 성공 검증

### STEP 2. MongoDB 저장
1. MongoDB 연결 확인
2. 크롤링 리뷰 insert
3. 조회 테스트로 저장 검증
4. 인덱스 설정 검토

### STEP 3. 광고 필터링
1. 광고 키워드 룰 정의
2. `ad_score`, `is_ad` 계산
3. 테스트 데이터로 precision 확인
4. 오탐/미탐 케이스 기록

### STEP 4. 메뉴 추출/빈도 분석
1. 메뉴 사전 기반 추출
2. 광고 리뷰 제외 후 빈도 집계
3. TOP N 산출
4. 이상치/중복 표현 정규화 검토

### STEP 5. MySQL 적재
1. `cafe`, `menu`, `cafe_menu_rank` upsert
2. rank 재계산
3. 적재 결과 조회 검증

### STEP 6. API 구축
1. `GET /menus/recommend` 구현
2. 파라미터 검증
3. 데이터 없음/오류 응답 처리
4. Swagger 확인

### STEP 7. 테스트 및 검증
1. 단위 테스트(pytest)
2. 샘플 E2E(수집→분석→API)
3. 문서/코드 정합성 점검

### STEP 8. 배포(Render)
1. 환경변수 등록
2. Build/Start 커맨드 설정
3. 헬스체크 및 엔드포인트 검증
4. 배포 후 회귀 테스트
