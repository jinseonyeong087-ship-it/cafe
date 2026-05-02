from typing import Dict, Any


# 이 함수는 리뷰 텍스트에 광고성 키워드가 포함되어 있는지 점수화하는 함수
def calculate_ad_score(content: str) -> float:
    ad_keywords = [
        "협찬", "광고", "원고료", "제공받아", "제품제공", "체험단", "파트너스",
        "소정의", "커미션", "홍보", "지원받아", "업체로부터", "유료광고"
    ]
    if not content:
        return 0.0
    lowered = content.lower()
    hit_count = sum(1 for keyword in ad_keywords if keyword in lowered)
    return min(1.0, hit_count / 3)


# 이 함수는 리뷰 한 건을 입력받아 광고 여부 필드를 채워 반환하는 함수
def mark_ad_review(review: Dict[str, Any], threshold: float = 0.34) -> Dict[str, Any]:
    content = review.get("content", "")
    score = calculate_ad_score(content)
    review["ad_score"] = score
    review["is_ad"] = score >= threshold
    return review
