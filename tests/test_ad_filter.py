from analyzer.ad_filter import calculate_ad_score, mark_ad_review, is_noise_heavy_review


# 이 테스트는 광고 키워드가 포함된 경우 점수가 상승하는지 검증하는 테스트
def test_calculate_ad_score() -> None:
    score = calculate_ad_score("이 글은 협찬으로 작성되었고 제품을 제공받아 작성했습니다")
    assert score > 0


# 이 테스트는 임계치 이상일 때 광고 리뷰로 판정되는지 검증하는 테스트
def test_mark_ad_review() -> None:
    review = {"content": "유료광고 협찬 체험단 후기"}
    result = mark_ad_review(review)
    assert result["is_ad"] is True


# 이 테스트는 광고 문구가 없는 일반 리뷰는 비광고로 판정되는지 검증하는 테스트
def test_non_ad_review() -> None:
    review = {"content": "아메리카노 맛이 깔끔하고 매장이 조용해서 좋았어요"}
    result = mark_ad_review(review)
    assert result["is_ad"] is False


# 이 테스트는 문장형 광고 고지 패턴이 있을 때 광고 점수가 상승하는지 검증하는 테스트
# 예: "본 포스팅은 업체로부터 ... 제공받아 작성"
def test_disclosure_pattern_score() -> None:
    content = "본 포스팅은 업체로부터 제품을 제공받아 작성한 후기입니다."
    score = calculate_ad_score(content)
    assert score >= 0.34


# 이 테스트는 제휴/파트너스 수수료 고지 문구가 광고로 판정되는지 검증하는 테스트
def test_partners_disclosure_review() -> None:
    review = {"content": "쿠팡 파트너스 활동을 통해 일정액의 수수료를 받을 수 있습니다."}
    result = mark_ad_review(review)
    assert result["is_ad"] is True


# 이 테스트는 small_cafe 프로필에서 소형카페형 광고 문구를 더 민감하게 탐지하는지 검증하는 테스트
def test_small_cafe_profile_detection() -> None:
    review = {"content": "해당 매장 방문 지원을 받아 작성한 후기입니다."}
    result = mark_ad_review(review, cafe_profile="small_cafe")
    assert result["is_ad"] is True


# 이 테스트는 주소/주차/영업시간 등 정보성 문장이 많은 경우 노이즈로 판단하는지 검증한다.
def test_noise_heavy_review() -> None:
    content = "주소: 서울시 강남구 ... 영업시간: 10:00-22:00, 주차 가능"
    assert is_noise_heavy_review(content) is True
