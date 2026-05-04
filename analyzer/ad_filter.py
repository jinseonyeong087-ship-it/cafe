import re
from typing import Dict, Any


# 이 상수는 광고/협찬 고지에서 자주 쓰이는 핵심 키워드 목록이다.
AD_KEYWORDS = [
    "협찬", "광고", "원고료", "제공받아", "제품제공", "체험단", "파트너스",
    "소정의", "커미션", "홍보", "지원받아", "업체로부터", "유료광고",
    "제작비 지원", "대가를 받고", "수수료", "브랜드로부터", "광고를 포함",
]

# 이 상수는 문장형 고지 패턴(예: 본 포스팅은 업체로부터...)을 탐지하기 위한 정규식 목록이다.
AD_DISCLOSURE_PATTERNS = [
    r"본\s*포스팅은\s*.*(협찬|광고|지원)",
    r"(업체|브랜드).{0,20}(제공|지원).{0,20}(작성|후기)",
    r"파트너스\s*활동.{0,20}(수수료|커미션)",
]

# 소형/로컬 카페 리뷰에서 자주 등장하는 광고성 문장 패턴
SMALL_CAFE_AD_PATTERNS = [
    r"내돈내산\s*아님",
    r"방문\s*지원",
    r"시식권\s*제공",
    r"무료\s*시음",
    r"초대\s*받아",
    r"체험권\s*제공",
]

# 메뉴 추천 신뢰도를 낮추는 정보성/노이즈 문장 패턴(광고 판정에는 직접 사용하지 않음)
NOISE_PATTERNS = [
    r"영업시간",
    r"주차",
    r"전화번호",
    r"주소",
    r"지도",
    r"위치",
]


# 이 함수는 리뷰 텍스트에 광고성 키워드/고지 패턴이 포함되어 있는지 점수화하는 함수
def calculate_ad_score(content: str, cafe_profile: str = "franchise") -> float:
    if not content:
        return 0.0

    lowered = content.lower()
    keyword_hits = sum(1 for keyword in AD_KEYWORDS if keyword in lowered)
    pattern_hits = sum(1 for pattern in AD_DISCLOSURE_PATTERNS if re.search(pattern, content))

    small_cafe_hits = 0
    if cafe_profile == "small_cafe":
        small_cafe_hits = sum(1 for pattern in SMALL_CAFE_AD_PATTERNS if re.search(pattern, content))

    # 패턴 매칭은 신뢰도가 높으므로 가중치 2를 부여한다.
    weighted_hits = keyword_hits + (pattern_hits * 2) + (small_cafe_hits * 2)
    return min(1.0, weighted_hits / 3)


# 이 함수는 리뷰 한 건을 입력받아 광고 여부 필드를 채워 반환하는 함수
def mark_ad_review(review: Dict[str, Any], threshold: float = 0.34, cafe_profile: str = "franchise") -> Dict[str, Any]:
    content = review.get("content", "")
    score = calculate_ad_score(content, cafe_profile=cafe_profile)
    review["ad_score"] = score
    review["is_ad"] = score >= threshold
    return review


# 이 함수는 리뷰가 메뉴 추천과 무관한 정보성 문장 중심인지 판단하기 위한 보조 함수
# 현재는 점검용이며, 향후 메뉴 집계 전 필터링 단계에서 활용할 수 있다.
def is_noise_heavy_review(content: str, threshold: int = 2) -> bool:
    if not content:
        return False
    hits = sum(1 for pattern in NOISE_PATTERNS if re.search(pattern, content))
    return hits >= threshold
