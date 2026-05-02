import math
from statistics import mean, pstdev
from typing import List


# 이 함수는 최근 누적 비광고 언급량 기반 안정 인기 점수를 계산하는 함수
def calculate_popularity_score(non_ad_mentions_30d: int) -> float:
    return round(math.log1p(max(0, non_ad_mentions_30d)), 4)


# 이 함수는 일별 언급량 시계열을 받아 급상승 점수를 계산하는 함수
# 입력 예시: 최근 8일 데이터 (앞 7일 기준선 + 오늘)
def calculate_trend_score(daily_mentions: List[int]) -> float:
    if len(daily_mentions) < 8:
        return 0.0

    baseline = daily_mentions[-8:-1]
    today = daily_mentions[-1]

    avg_7d = mean(baseline)
    std_7d = pstdev(baseline) if len(baseline) > 1 else 0.0
    z_score = (today - avg_7d) / (std_7d + 1)

    recent_3d = sum(daily_mentions[-3:])
    prev_3d = sum(daily_mentions[-6:-3]) if len(daily_mentions) >= 6 else 0
    growth_3d = recent_3d / (prev_3d + 1)

    trend_score = 0.7 * z_score + 0.3 * growth_3d
    return round(trend_score, 4)
