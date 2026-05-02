from fastapi import APIRouter, Query

from analyzer.menu_analyzer import count_menu_frequency
from app.services.recommendation import build_recommendations
from storage.mongo_client import MongoRepository

router = APIRouter(prefix="/menus", tags=["menus"])


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
    recommendations = build_recommendations(cafe, menu_counts, top_n, mode)
    return {"mode": mode, "items": [item.model_dump() for item in recommendations]}
