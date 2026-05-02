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

확장 시에도 기존 `GET /menus/recommend`의 응답 계약은 하위호환을 유지합니다.
