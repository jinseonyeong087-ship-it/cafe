from pydantic import BaseModel


# 이 모델은 메뉴 추천 API의 응답 형식을 정의하는 스키마
class MenuRecommendation(BaseModel):
    cafe: str
    menu: str
    count: int
    rank: int
    reason: str
