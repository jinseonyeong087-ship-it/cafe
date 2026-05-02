from analyzer.trending_analyzer import calculate_popularity_score, calculate_trend_score


# 이 테스트는 비광고 누적 언급량 기반 인기도 점수가 정상 계산되는지 검증하는 테스트
def test_calculate_popularity_score() -> None:
    score = calculate_popularity_score(99)
    assert score > 0


# 이 테스트는 최근 언급량 급증 시 trend 점수가 양수로 계산되는지 검증하는 테스트
def test_calculate_trend_score() -> None:
    score = calculate_trend_score([2, 3, 2, 4, 3, 2, 3, 10])
    assert score > 0
