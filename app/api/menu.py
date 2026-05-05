from fastapi import APIRouter, HTTPException, Query

from analyzer.menu_dictionary import MENU_CATEGORY_MAP
from app.services.recommendation import build_recommendations
from storage.mysql_client import MySQLRepository


# 이 상수는 메뉴 추천에서 제외할 일반 카테고리 명칭 목록이다.
GENERIC_MENU_NAMES = {"디저트", "음료", "커피", "메뉴"}
FALLBACK_DRINKS = ["아메리카노", "카페라떼", "콜드브루", "디카페인", "말차라떼"]
FALLBACK_DESSERTS = ["티라미수", "치즈케이크", "쿠키", "케이크", "크루아상"]

router = APIRouter(prefix="/menus", tags=["menus"])


# 이 함수는 추천 결과를 음료/디저트로 분리하는 함수
# 카테고리 미분류 항목은 기본값으로 음료에 포함한다.
def split_recommendations_by_category(recommendations: list[dict]) -> tuple[list[dict], list[dict]]:
    drinks = []
    desserts = []
    for item in recommendations:
        category = MENU_CATEGORY_MAP.get(item["menu"], "drink")
        if category == "dessert":
            desserts.append(item)
        else:
            drinks.append(item)
    return drinks, desserts


# 이 엔드포인트는 카페명을 기준으로 인기 메뉴 TOP N 추천 결과를 반환하는 API
@router.get("/recommend")
def recommend_menu(
    cafe: str = Query(..., description="카페 이름"),
    top_n: int = Query(3, ge=1, le=10),
    mode: str = Query("popular", pattern="^(popular|trending)$"),
):
    try:
        mysql_repo = MySQLRepository()
        ranked_rows = mysql_repo.get_menu_ranks(cafe)

        if not ranked_rows:
            raise HTTPException(status_code=404, detail="해당 카페의 집계 데이터가 없습니다.")

        # 이 로직은 MySQL 집계 결과를 추천 서비스 입력 형태로 변환하는 로직
        # 일반 카테고리 명칭(예: 디저트)은 추천에서 제외한다.
        filtered_rows = [row for row in ranked_rows if row["menu"] not in GENERIC_MENU_NAMES]
        menu_counts = {row["menu"]: int(row["count"]) for row in filtered_rows}

        if not menu_counts:
            raise HTTPException(status_code=404, detail="추천 가능한 구체 메뉴 데이터가 없습니다.")

        # 이 로직은 mode별 정렬 정책을 분리하는 로직이다.
        # popular: 기존 count 중심
        # trending: 현재는 count + rank 보정으로 가벼운 최신성 반영(추후 trend_score 컬럼 연동 예정)
        if mode == "trending":
            menu_counts = {
                row["menu"]: int(row["count"] + max(0, 10 - int(row["menu_rank"]))) for row in filtered_rows
            }

        # 이 로직은 카테고리 분리를 위해 후보를 넉넉히 뽑은 뒤 음료/디저트를 각각 top_n으로 자른다.
        fetch_n = min(max(top_n * 3, top_n), len(menu_counts))
        recommendations = build_recommendations(cafe, menu_counts, top_n=fetch_n, mode=mode, positive_counts={})
        all_items = [item.model_dump() for item in recommendations]
        drinks, desserts = split_recommendations_by_category(all_items)
        items = all_items[:top_n]
        # 이 로직은 카테고리별 최소 top_n개를 보장하기 위해 fallback 메뉴를 채운다.
        drink_names = {d['menu'] for d in drinks}
        dessert_names = {d['menu'] for d in desserts}

        for name in FALLBACK_DRINKS:
            if len(drinks) >= top_n:
                break
            if name in drink_names:
                continue
            drinks.append({"cafe": cafe, "menu": name, "count": 0, "rank": len(drinks) + 1, "reason": "데이터 보강 전 기본 추천 메뉴입니다."})
            drink_names.add(name)

        for name in FALLBACK_DESSERTS:
            if len(desserts) >= top_n:
                break
            if name in dessert_names:
                continue
            desserts.append({"cafe": cafe, "menu": name, "count": 0, "rank": len(desserts) + 1, "reason": "데이터 보강 전 기본 추천 메뉴입니다."})
            dessert_names.add(name)

        return {
            "mode": mode,
            "items": items,
            "drinks": drinks[:top_n],
            "desserts": desserts[:top_n],
        }
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"잘못된 요청입니다: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"내부 서버 오류: {exc}") from exc
