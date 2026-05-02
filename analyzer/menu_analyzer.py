import re
from collections import Counter
from typing import List, Dict


# 이 상수는 초기 메뉴 추출에 사용할 메뉴 후보 사전(추후 DB/사전 파일로 분리 가능)
MENU_CANDIDATES = ["아메리카노", "라떼", "카페라떼", "바닐라라떼", "콜드브루", "티라미수", "치즈케이크"]


# 이 함수는 리뷰 텍스트에서 메뉴명을 추출하는 함수
def extract_menu_names(text: str) -> List[str]:
    found = []
    for menu in MENU_CANDIDATES:
        if re.search(re.escape(menu), text):
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
