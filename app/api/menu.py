from fastapi import APIRouter, Query

from analyzer.menu_analyzer import count_menu_frequency, count_positive_menu_mentions
from analyzer.menu_dictionary import MENU_CATEGORY_MAP
from app.core.config import settings
from app.services.recommendation import build_recommendations
from storage.mongo_client import MongoRepository

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
    mongo_repo = MongoRepository()
    reviews = mongo_repo.get_reviews_by_cafe(cafe)
    menu_counts = count_menu_frequency(reviews)
    positive_counts = count_positive_menu_mentions(reviews)
    recommendations = build_recommendations(
        cafe,
        menu_counts,
        top_n,
        mode,
        positive_counts=positive_counts,
        positive_weight=settings.positive_taste_weight,
    )
    items = [item.model_dump() for item in recommendations]
    drinks, desserts = split_recommendations_by_category(items)
    return {
        "mode": mode,
        "items": items,
        "drinks": drinks,
        "desserts": desserts,
    }
