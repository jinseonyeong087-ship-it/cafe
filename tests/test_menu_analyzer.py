from analyzer.menu_analyzer import extract_menu_names, count_menu_frequency


# 이 테스트는 리뷰 텍스트에서 메뉴명이 정상적으로 추출되는지 검증하는 테스트
def test_extract_menu_names() -> None:
    menus = extract_menu_names("아메리카노와 티라미수가 정말 맛있어요")
    assert "아메리카노" in menus
    assert "티라미수" in menus


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
