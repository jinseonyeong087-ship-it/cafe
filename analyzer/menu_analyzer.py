import re
from collections import Counter
from typing import List, Dict

from analyzer.menu_dictionary import DEFAULT_MENU_DICTIONARY, MENU_ALIAS_MAP


# 이 상수는 긍정적인 맛/추천 문맥을 판별하기 위한 키워드 목록이다.
POSITIVE_TASTE_KEYWORDS = [
    "맛있", "존맛", "추천", "고소", "진하", "풍미", "재구매", "또 먹", "또 마",
]


# 이 함수는 리뷰 텍스트를 정규화(소문자/공백정리/별칭치환)하는 함수
def _normalize_text(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text.strip())
    for alias, canonical in MENU_ALIAS_MAP.items():
        normalized = normalized.replace(alias, canonical)
    return normalized


# 이 함수는 리뷰 텍스트에서 메뉴명을 추출하는 함수
def extract_menu_names(text: str) -> List[str]:
    normalized = _normalize_text(text)
    found = []
    for menu in DEFAULT_MENU_DICTIONARY:
        if re.search(re.escape(menu), normalized):
            found.append(menu)
    return found


# 이 함수는 광고가 아닌 리뷰 목록에서 메뉴 빈도를 집계하는 함수
def count_menu_frequency(reviews: List[Dict]) -> Dict[str, int]:
    counter = Counter()
    for review in reviews:
        if review.get("is_ad"):
            continue
        menus = extract_menu_names(review.get("content", ""))
        counter.update(menus)
    return dict(counter)


# 이 함수는 비광고 리뷰에서 메뉴별 긍정 맛평가 횟수를 집계하는 함수
# 메뉴가 언급되고 동시에 긍정 키워드가 포함된 경우만 카운트한다.
def count_positive_menu_mentions(reviews: List[Dict]) -> Dict[str, int]:
    counter = Counter()
    for review in reviews:
        if review.get("is_ad"):
            continue
        content = _normalize_text(review.get("content", ""))
        if not any(keyword in content for keyword in POSITIVE_TASTE_KEYWORDS):
            continue
        menus = extract_menu_names(content)
        counter.update(menus)
    return dict(counter)
