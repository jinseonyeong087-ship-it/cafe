# DB 명세서 (고정 기준)

이 문서는 본 프로젝트의 데이터 구조 기준 문서입니다.
코드 변경 시 본 문서와 반드시 정합성을 맞춥니다.

---

## 1. MongoDB (원본 리뷰 저장)

- DB: `cafe_reviews`
- Collection: `reviews`

### 1-1. Document 스키마

| 필드명 | 타입 | 설명 |
|---|---|---|
| cafe | string | 카페명 |
| content | string | 리뷰 본문 |
| ad_score | float | 광고성 점수 (0.0 ~ 1.0) |
| is_ad | bool | 광고 여부 |
| source_url | string | 수집 URL |
| collected_at | datetime | 수집 시각 |

### 1-2. 인덱스
- `cafe` 단일 인덱스
- `is_ad` 단일 인덱스
- `(cafe, collected_at)` 복합 인덱스

---

## 2. MySQL (정제/집계 데이터 저장)

### 2-0. ERD (확장)

```text
cafe (1) ---- (N) cafe_menu_rank (N) ---- (1) menu
menu (1) ---- (N) menu_alias
cafe (1) ---- (N) menu_daily_stats (N) ---- (1) menu
menu (1) ---- (N) menu_candidate
```

### 2-1. ERD (텍스트)

```text
cafe (1) ---- (N) cafe_menu_rank (N) ---- (1) menu
```

### 2-2. 테이블 정의

#### cafe
| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | 카페 식별자 |
| name | VARCHAR(255) | UNIQUE, NOT NULL | 카페명 |
| created_at | DATETIME | NOT NULL | 생성일시 |

#### menu
| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | 메뉴 식별자 |
| name | VARCHAR(255) | UNIQUE, NOT NULL | 메뉴명 |
| created_at | DATETIME | NOT NULL | 생성일시 |

#### cafe_menu_rank
| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| cafe_id | BIGINT | PK(FK), NOT NULL | 카페 ID |
| menu_id | BIGINT | PK(FK), NOT NULL | 메뉴 ID |
| count | INT | NOT NULL | 리뷰 언급 수 |
| rank | INT | NOT NULL | 카페 내 순위 |
| updated_at | DATETIME | NOT NULL | 갱신일시 |

PK: `(cafe_id, menu_id)`

#### menu_daily_stats
| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| stat_date | DATE | PK, NOT NULL | 기준 일자 |
| cafe_id | BIGINT | PK(FK), NOT NULL | 카페 ID |
| menu_id | BIGINT | PK(FK), NOT NULL | 메뉴 ID |
| mention_count | INT | NOT NULL | 일별 총 언급 수 |
| non_ad_count | INT | NOT NULL | 비광고 언급 수 |
| ad_ratio | DECIMAL(5,4) | NOT NULL | 광고 비율 |
| trend_score | DECIMAL(10,4) | NOT NULL | 급상승 점수 |
| popularity_score | DECIMAL(10,4) | NOT NULL | 안정 인기 점수 |
| created_at | DATETIME | NOT NULL | 생성일시 |

PK: `(stat_date, cafe_id, menu_id)`

#### menu_alias
| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | 식별자 |
| menu_id | BIGINT | FK, NOT NULL | 메뉴 ID |
| alias_name | VARCHAR(255) | UNIQUE, NOT NULL | 메뉴 별칭/오타/줄임말 |
| created_at | DATETIME | NOT NULL | 생성일시 |

#### menu_candidate
| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | 식별자 |
| cafe_id | BIGINT | FK, NOT NULL | 카페 ID |
| candidate_name | VARCHAR(255) | NOT NULL | 신규 후보 메뉴명 |
| mention_count | INT | NOT NULL | 누적 언급량 |
| first_seen_at | DATETIME | NOT NULL | 최초 탐지 시각 |
| last_seen_at | DATETIME | NOT NULL | 마지막 탐지 시각 |
| status | VARCHAR(50) | NOT NULL | `new`/`reviewing`/`approved`/`rejected` |

---

## 3. 신뢰성 규칙
1. `is_ad = true` 데이터는 집계에서 제외
2. 메뉴 count는 광고 제거 후 데이터만 사용
3. rank는 count 내림차순 기준
4. 동률 시 메뉴명 오름차순으로 deterministic 정렬
