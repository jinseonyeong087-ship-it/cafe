from analyzer.menu_analyzer import (
    count_menu_candidate_frequency,
    count_menu_frequency,
    extract_menu_candidates,
    extract_menu_names,
)


# 이 테스트는 리뷰 텍스트에서 메뉴명이 정상적으로 추출되는지 검증하는 테스트
def test_extract_menu_names() -> None:
    menus = extract_menu_names("아메리카노와 티라미수가 정말 맛있어요")
    assert "아메리카노" in menus
    assert "티라미수" in menus


# 이 테스트는 메뉴 별칭이 표준 메뉴명으로 정규화되는지 검증하는 테스트
def test_extract_menu_names_with_alias() -> None:
    menus = extract_menu_names("아아랑 바라 조합이 좋아요")
    assert "아메리카노" in menus
    assert "바닐라라떼" in menus


# 이 테스트는 광고 리뷰 제외 후 메뉴 빈도가 집계되는지 검증하는 테스트
def test_count_menu_frequency() -> None:
    reviews = [
        {"content": "아메리카노 최고", "is_ad": False},
        {"content": "아메리카노랑 라떼 추천", "is_ad": False},
        {"content": "협찬 라떼", "is_ad": True},
    ]
    result = count_menu_frequency(reviews)
    assert result["아메리카노"] == 2
    assert result["라떼"] == 1


# 이 테스트는 사전에 없는 메뉴 후보가 접미어 규칙으로 추출되는지 검증하는 테스트
def test_extract_menu_candidates() -> None:
    candidates = extract_menu_candidates("오늘은 흑임자라떼랑 초코타르트가 맛있었어요")
    assert "흑임자라떼" in candidates
    assert "초코타르트" in candidates


# 이 테스트는 광고 리뷰 제외 후 메뉴 후보 빈도가 집계되는지 검증하는 테스트
def test_count_menu_candidate_frequency() -> None:
    reviews = [
        {"content": "흑임자라떼 추천", "is_ad": False},
        {"content": "흑임자라떼 또 마심", "is_ad": False},
        {"content": "협찬 흑임자라떼", "is_ad": True},
    ]
    result = count_menu_candidate_frequency(reviews)
    assert result["흑임자라떼"] == 2
