import argparse

from analyzer.ad_filter import mark_ad_review
from analyzer.menu_analyzer import count_menu_frequency
from crawler.crawler_blog import crawl_single_page


# 이 함수는 STEP1(크롤링)만 단독으로 검증하는 함수
# 실행 예시: python scripts/run_pipeline.py --step step1 --url "https://example.com" --cafe "샘플카페"
def run_step1(url: str, cafe_name: str) -> list[dict]:
    reviews = crawl_single_page(url, cafe_name)
    print(f"[STEP1] 수집 리뷰 수: {len(reviews)}")
    if reviews:
        print(f"[STEP1] 샘플 리뷰: {reviews[0]['content'][:120]}")
    return reviews


# 이 함수는 STEP1~STEP4의 최소 파이프라인을 순차 실행하는 함수
# 실행 예시: python scripts/run_pipeline.py --step all --url "https://example.com" --cafe "샘플카페"
def run_pipeline(url: str, cafe_name: str) -> None:
    from storage.mongo_client import MongoRepository

    # STEP1: 크롤링
    reviews = run_step1(url, cafe_name)

    # STEP2, STEP3: MongoDB 저장 전 광고 점수 반영
    processed_reviews = [mark_ad_review(review) for review in reviews]
    mongo_repo = MongoRepository()
    inserted_count = mongo_repo.insert_reviews(processed_reviews)

    # STEP4: 빈도 분석
    menu_counts = count_menu_frequency(processed_reviews)

    print(f"[STEP2] 저장 리뷰 수: {inserted_count}")
    print(f"[STEP4] 메뉴 빈도: {menu_counts}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--step", choices=["step1", "all"], default="step1")
    parser.add_argument("--url", required=True)
    parser.add_argument("--cafe", default="샘플카페")
    args = parser.parse_args()

    if args.step == "step1":
        run_step1(args.url, args.cafe)
    else:
        run_pipeline(args.url, args.cafe)
