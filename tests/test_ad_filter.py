from analyzer.ad_filter import calculate_ad_score, mark_ad_review


# 이 테스트는 광고 키워드가 포함된 경우 점수가 상승하는지 검증하는 테스트
def test_calculate_ad_score() -> None:
    score = calculate_ad_score("이 글은 협찬으로 작성되었고 제품을 제공받아 작성했습니다")
    assert score > 0


# 이 테스트는 임계치 이상일 때 광고 리뷰로 판정되는지 검증하는 테스트
def test_mark_ad_review() -> None:
    review = {"content": "광고 협찬 체험단 후기"}
    result = mark_ad_review(review)
    assert result["is_ad"] is True
