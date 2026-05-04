# 구현 체크리스트 (운영용 단일 기준)

이 문서는 `README.md`와 `docs/*.md`에 흩어진 실행/검증 항목을 하나로 모은 운영 체크리스트입니다.  
원칙: 상태 변경 시 **문서 먼저 업데이트** 후 코드/테스트를 반영합니다.

---

## 0) 문서 기준 고정

- [x] `docs/WORKING_AGREEMENT.md` 확인
- [x] `docs/PROJECT_STRUCTURE.md` 확인
- [x] `docs/API_SPEC.md` 확인
- [x] `docs/DB_SPEC.md` 확인
- [x] `docs/TRENDING_SPEC.md` 확인
- [x] `docs/SOCIAL_DATA_POLICY.md` 확인

검증:
- `docs/` 기준 명세가 최신인지 확인
- 변경 필요 시 코드 수정 전에 문서 선반영

---

## 1) 현재 구현 완료 항목 (as-is)

### STEP1~STEP5 기본 골격
- [x] 프로젝트 구조 생성
- [x] 크롤링/분석/저장/API 기본 코드 구성

### 수집/저장
- [x] 네이버 블로그 모바일 URL 정규화 및 본문 추출 고도화
- [x] MongoDB 저장 검증
- [x] MySQL 스키마 초기화 및 upsert 적재 구현

### 분석
- [x] 광고 필터 키워드 확장
- [x] 메뉴 사전/별칭 정규화 도입

### 품질
- [x] 테스트 통과 (`8 passed`)

검증 명령:
```bash
cd /home/xkak9/projects/cafe-menu-recommendation-system
source .venv/bin/activate
pytest -q
```

---

## 2) 진행 필요 항목 (to-be)

### A. 파이프라인 고도화
- [x] `scripts/run_pipeline.py` 다중 URL 입력 지원 (`--urls-file`)
- [x] 검색어 기반 URL 자동 수집(`--query`, `--max-urls`) 추가
- [ ] 카페명/소스별 수집 성능 로그 저장
- [ ] 광고/비광고 건수 로그 출력 및 저장

완료 기준:
- 파일 입력으로 URL N건 일괄 처리
- 처리 결과(성공/실패/광고비율/소요시간) 로그 파일 생성

---

### B. 메뉴 사전 운영 자동화
- [ ] 사전 미매칭 용어 `menu_candidate` 자동 적재
- [ ] 후보 검수 상태 전이(`new`→`reviewing`→`approved/rejected`) 운영 규칙 반영

완료 기준:
- 일정 임계치 이상 반복 등장 용어가 자동 누적
- 검수 후 `menu`/`menu_alias` 반영 경로 문서화

---

### C. 추천 API 정합성 강화
- [ ] `GET /menus/recommend`를 MySQL 집계 조회 중심으로 정리
- [x] 광고 리뷰 100% 제외 + 긍정 맛평가 가중치 반영 로직 적용
- [x] 긍정 맛평가 가중치 `.env(POSITIVE_TASTE_WEIGHT)` 외부 설정화
- [ ] `mode=popular|trending` 기준에 맞는 점수/정렬 로직 명확화
- [ ] 데이터 없음(404), 파라미터 오류(400), 내부 오류(500) 응답 일관화

완료 기준:
- `docs/API_SPEC.md` 응답 계약 준수
- `docs/TRENDING_SPEC.md` 수치 근거(reason) 반영

---

### D. 배포
- [ ] Render 배포 설정 (`render.yaml` 또는 대시보드 설정) 반영
- [ ] 환경변수 등록 체크리스트 작성
- [ ] 배포 후 헬스체크/회귀 테스트

완료 기준:
- 배포 URL에서 API 정상 응답
- 최소 샘플 시나리오 E2E 재검증

---

## 3) 품질 게이트 (매 변경 공통)

- [ ] 테스트 통과
- [ ] 광고 필터링 검증
- [ ] 메뉴 추출 검증
- [ ] 문서/코드 정합성 확인
- [ ] 민감정보 하드코딩 여부 점검

검증 명령(기본):
```bash
cd /home/xkak9/projects/cafe-menu-recommendation-system
source .venv/bin/activate
pytest -q
```

---

## 4) 작업 순서 규칙 (고정)

1. 문서 수정(필요 시)
2. 코드 구현
3. 테스트/검증
4. README + 본 체크리스트 상태 동기화

---

## 5) 업데이트 로그

- 2026-05-04: 단일 운영 체크리스트 문서 최초 생성
