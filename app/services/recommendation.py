from typing import List

from app.models.schema import MenuRecommendation


# 이 함수는 모드(popular/trending)에 따라 추천 사유 문구를 생성하는 함수
def _build_reason(menu: str, mode: str) -> str:
    if mode == "trending":
        return f"'{menu}'는 최근 언급량 증가 폭이 커 급상승 메뉴로 분석되었습니다."
    return f"리뷰에서 '{menu}' 언급 빈도가 높아 인기 메뉴로 판단했습니다."


# 이 함수는 메뉴 카운트 결과를 랭킹 응답 형태로 변환하는 함수
# 추후 OpenAI/Bedrock 연동 시 reason 생성 로직을 고도화할 수 있다.
def build_recommendations(cafe: str, menu_counts: dict, top_n: int = 3, mode: str = "popular") -> List[MenuRecommendation]:
    sorted_items = sorted(menu_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    results = []
    for idx, (menu, count) in enumerate(sorted_items, start=1):
        reason = _build_reason(menu, mode)
        results.append(MenuRecommendation(cafe=cafe, menu=menu, count=count, rank=idx, reason=reason))
    return results
