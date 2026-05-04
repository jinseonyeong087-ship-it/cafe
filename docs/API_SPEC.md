# API 명세서 (고정 기준)

이 문서는 FastAPI 인터페이스 기준 문서입니다.
엔드포인트/응답 구조 변경 시 이 문서를 먼저 수정합니다.

---

## 1. GET /menus/recommend

카페명을 기준으로 인기 메뉴 TOP N을 반환합니다.

### Query Parameters
- `cafe` (string, required): 카페명
- `top_n` (int, optional, default=3, min=1, max=10): 상위 추천 개수
- `mode` (string, optional, default=`popular`): `popular` | `trending`

### Response 200

```json
{
  "items": [
    {
      "cafe": "샘플카페",
      "menu": "아메리카노",
      "count": 12,
      "rank": 1,
      "reason": "리뷰에서 '아메리카노' 언급 빈도가 높아 인기 메뉴로 판단했습니다."
    }
  ]
}
```

### 오류 정책
- 400: 잘못된 요청 파라미터
- 404: 카페 리뷰/집계 데이터 없음
- 500: 내부 서버 오류

---

## 2. 향후 확장 예정 API
- `POST /pipeline/run` : 수집~분석 파이프라인 실행
- `GET /cafes` : 카페 목록 조회
- `GET /menus/trending` : 전체 인기 메뉴 조회

---

## 3. 파이프라인 입력 포맷(스크립트 기준)

`python scripts/run_pipeline.py --step all --urls-file <경로>` 사용 시 아래 형식을 지원합니다.

### urls 파일 형식
- 한 줄에 1건
- 기본 형식: `카페명|URL`
- 호환 형식: `URL` (카페명은 `--cafe` 기본값 사용)
- 빈 줄/`#` 주석 줄은 무시

예시:
```text
이디야|https://blog.naver.com/sample1
이디야|https://blog.naver.com/sample2
스타벅스|https://blog.naver.com/sample3
# 주석 라인
https://blog.naver.com/sample4
```

확장 시에도 기존 `GET /menus/recommend`의 응답 계약은 하위호환을 유지합니다.
