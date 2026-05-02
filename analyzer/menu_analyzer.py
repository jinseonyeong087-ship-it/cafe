import re
from collections import Counter
from typing import List, Dict

from analyzer.menu_dictionary import DEFAULT_MENU_DICTIONARY, MENU_ALIAS_MAP


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
