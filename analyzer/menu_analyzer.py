import re
from collections import Counter
from typing import List, Dict

from analyzer.menu_dictionary import DEFAULT_MENU_DICTIONARY, MENU_ALIAS_MAP


# 이 상수는 긍정적인 맛/추천 문맥을 판별하기 위한 키워드 목록이다.
POSITIVE_TASTE_KEYWORDS = [
    "맛있", "존맛", "추천", "고소", "진하", "풍미", "재구매", "또 먹", "또 마",
]

# 이 상수는 메뉴 후보 추출 시 메뉴성 단어로 볼 접미 키워드 목록이다.
MENU_SUFFIX_KEYWORDS = ["라떼", "에이드", "티", "케이크", "쿠키", "브레드", "샌드", "스콘", "푸딩", "타르트"]


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


# 이 함수는 사전에 없는 메뉴 후보를 추출하는 함수
# 메뉴성 접미어를 가진 토큰 중 기존 메뉴 사전에 없는 항목을 후보로 본다.
def extract_menu_candidates(text: str) -> List[str]:
    normalized = _normalize_text(text)
    tokens = re.findall(r"[가-힣A-Za-z0-9]{2,20}", normalized)
    candidates = []
    known = set(DEFAULT_MENU_DICTIONARY)
    particles = ("은", "는", "이", "가", "을", "를", "랑", "과", "와", "도")
    for token in tokens:
        normalized_token = token
        for particle in particles:
            if normalized_token.endswith(particle) and len(normalized_token) > len(particle) + 1:
                normalized_token = normalized_token[: -len(particle)]
                break

        if normalized_token in known:
            continue
        if any(normalized_token.endswith(suffix) for suffix in MENU_SUFFIX_KEYWORDS):
            candidates.append(normalized_token)
    return list(dict.fromkeys(candidates))


# 이 함수는 비광고 리뷰 기준으로 메뉴 후보 빈도를 집계하는 함수
def count_menu_candidate_frequency(reviews: List[Dict]) -> Dict[str, int]:
    counter = Counter()
    for review in reviews:
        if review.get("is_ad"):
            continue
        candidates = extract_menu_candidates(review.get("content", ""))
        counter.update(candidates)
    return dict(counter)
