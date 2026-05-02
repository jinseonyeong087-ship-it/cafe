from typing import List, Dict, Any
from pymongo import MongoClient

from app.core.config import settings


# 이 클래스는 MongoDB 연결과 리뷰 데이터 저장/조회 기능을 담당하는 저장소 클래스
class MongoRepository:
    # 이 함수는 MongoDB 클라이언트와 컬렉션을 초기화하는 생성자
    def __init__(self) -> None:
        self.client = MongoClient(settings.mongodb_uri)
        self.db = self.client[settings.mongodb_db]
        self.collection = self.db[settings.mongodb_collection]

    # 이 함수는 크롤링한 리뷰 목록을 MongoDB에 일괄 저장하는 함수
    def insert_reviews(self, reviews: List[Dict[str, Any]]) -> int:
        if not reviews:
            return 0
        result = self.collection.insert_many(reviews)
        return len(result.inserted_ids)

    # 이 함수는 특정 카페의 리뷰를 조회하는 함수
    def get_reviews_by_cafe(self, cafe_name: str) -> List[Dict[str, Any]]:
        return list(self.collection.find({"cafe": cafe_name}, {"_id": 0}))
