from fastapi import APIRouter, HTTPException, Query

from analyzer.menu_dictionary import MENU_CATEGORY_MAP
from app.services.recommendation import build_recommendations
from storage.mysql_client import MySQLRepository

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
        menu_counts = {row["menu"]: int(row["count"]) for row in ranked_rows}

        # 이 로직은 mode별 정렬 정책을 분리하는 로직이다.
        # popular: 기존 count 중심
        # trending: 현재는 count + rank 보정으로 가벼운 최신성 반영(추후 trend_score 컬럼 연동 예정)
        if mode == "trending":
            menu_counts = {
                row["menu"]: int(row["count"] + max(0, 10 - int(row["menu_rank"]))) for row in ranked_rows
            }

        recommendations = build_recommendations(cafe, menu_counts, top_n=top_n, mode=mode, positive_counts={})
        items = [item.model_dump() for item in recommendations]
        drinks, desserts = split_recommendations_by_category(items)
        return {
            "mode": mode,
            "items": items,
            "drinks": drinks,
            "desserts": desserts,
        }
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"잘못된 요청입니다: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"내부 서버 오류: {exc}") from exc
