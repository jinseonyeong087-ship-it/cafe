from typing import List

from app.models.schema import MenuRecommendation


# 이 함수는 모드(popular/trending)에 따라 추천 사유 문구를 생성하는 함수
def _build_reason(menu: str, mode: str, mention_count: int, positive_count: int) -> str:
    if mode == "trending":
        return f"'{menu}'는 비광고 리뷰에서 언급 {mention_count}회, 긍정 맛평가 {positive_count}회로 최근 주목도가 높았습니다."
    return f"비광고 리뷰에서 '{menu}' 언급 {mention_count}회, 긍정 맛평가 {positive_count}회로 인기 메뉴로 판단했습니다."


# 이 함수는 메뉴 카운트 결과를 랭킹 응답 형태로 변환하는 함수
# 추후 OpenAI/Bedrock 연동 시 reason 생성 로직을 고도화할 수 있다.
def build_recommendations(
    cafe: str,
    menu_counts: dict,
    top_n: int = 3,
    mode: str = "popular",
    positive_counts: dict | None = None,
    positive_weight: float = 1.5,
) -> List[MenuRecommendation]:
    positive_counts = positive_counts or {}

    scored_items = []
    for menu, mention_count in menu_counts.items():
        positive_count = positive_counts.get(menu, 0)
        score = mention_count + (positive_count * positive_weight)
        scored_items.append((menu, mention_count, positive_count, score))

    sorted_items = sorted(scored_items, key=lambda x: (x[3], x[1], x[0]), reverse=True)[:top_n]
    results = []
    for idx, (menu, mention_count, positive_count, _score) in enumerate(sorted_items, start=1):
        reason = _build_reason(menu, mode, mention_count, positive_count)
        results.append(MenuRecommendation(cafe=cafe, menu=menu, count=mention_count, rank=idx, reason=reason))
    return results
