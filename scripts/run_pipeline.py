import argparse
from collections import defaultdict
from pathlib import Path

from analyzer.ad_filter import mark_ad_review
from analyzer.menu_analyzer import count_menu_frequency
from crawler.crawler_blog import crawl_single_page
from storage.mysql_client import MySQLRepository


# 이 함수는 STEP1(크롤링)만 단독으로 검증하는 함수
# 실행 예시: python scripts/run_pipeline.py --step step1 --url "https://example.com" --cafe "샘플카페"
def run_step1(url: str, cafe_name: str) -> list[dict]:
    reviews = crawl_single_page(url, cafe_name)
    print(f"[STEP1] cafe={cafe_name} url={url} 수집 리뷰 수: {len(reviews)}")
    if reviews:
        print(f"[STEP1] 샘플 리뷰: {reviews[0]['content'][:120]}")
    return reviews


# 이 함수는 STEP1~STEP5의 최소 파이프라인을 순차 실행하는 함수
# 실행 예시: python scripts/run_pipeline.py --step all --url "https://example.com" --cafe "샘플카페"
def run_pipeline(url: str, cafe_name: str) -> dict:
    from storage.mongo_client import MongoRepository

    reviews = run_step1(url, cafe_name)

    processed_reviews = [mark_ad_review(review) for review in reviews]
    ad_count = sum(1 for review in processed_reviews if review.get("is_ad"))
    non_ad_count = len(processed_reviews) - ad_count

    mongo_repo = MongoRepository()
    inserted_count = mongo_repo.insert_reviews(processed_reviews)

    menu_counts = count_menu_frequency(processed_reviews)

    mysql_repo = MySQLRepository()
    updated_count = mysql_repo.upsert_menu_ranks(cafe_name, menu_counts)

    print(f"[STEP2] 저장 리뷰 수: {inserted_count}")
    print(f"[STEP3] 광고/비광고: {ad_count}/{non_ad_count}")
    print(f"[STEP4] 메뉴 빈도: {menu_counts}")
    print(f"[STEP5] MySQL 반영 건수: {updated_count}")

    return {
        "cafe": cafe_name,
        "url": url,
        "reviews": len(processed_reviews),
        "ad_count": ad_count,
        "non_ad_count": non_ad_count,
        "inserted_count": inserted_count,
        "updated_count": updated_count,
    }


# 이 함수는 urls 파일에서 (카페명, URL) 목록을 파싱하는 함수
# 형식: cafe|url 또는 url 단독(이 경우 default_cafe 사용)
def load_targets_from_file(urls_file: str, default_cafe: str) -> list[tuple[str, str]]:
    targets: list[tuple[str, str]] = []
    for raw_line in Path(urls_file).read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if "|" in line:
            cafe_name, url = [part.strip() for part in line.split("|", 1)]
            if not cafe_name or not url:
                continue
            targets.append((cafe_name, url))
        else:
            targets.append((default_cafe, line))

    return targets


# 이 함수는 다중 타겟 파이프라인을 실행하고 요약 통계를 출력하는 함수
def run_pipeline_batch(targets: list[tuple[str, str]]) -> None:
    success = 0
    failed = 0
    cafe_stats = defaultdict(lambda: {"targets": 0, "success": 0, "failed": 0, "reviews": 0, "ad": 0, "non_ad": 0})

    for idx, (cafe_name, url) in enumerate(targets, start=1):
        cafe_stats[cafe_name]["targets"] += 1
        print(f"\n[BATCH] ({idx}/{len(targets)}) cafe={cafe_name} url={url}")
        try:
            result = run_pipeline(url, cafe_name)
            success += 1
            cafe_stats[cafe_name]["success"] += 1
            cafe_stats[cafe_name]["reviews"] += result["reviews"]
            cafe_stats[cafe_name]["ad"] += result["ad_count"]
            cafe_stats[cafe_name]["non_ad"] += result["non_ad_count"]
        except Exception as exc:
            failed += 1
            cafe_stats[cafe_name]["failed"] += 1
            print(f"[ERROR] cafe={cafe_name} url={url} 실패: {exc}")

    print("\n===== BATCH SUMMARY =====")
    print(f"총 대상 URL: {len(targets)}")
    print(f"성공: {success} / 실패: {failed}")
    for cafe_name, stat in sorted(cafe_stats.items()):
        print(
            f"- {cafe_name}: targets={stat['targets']} success={stat['success']} failed={stat['failed']} "
            f"reviews={stat['reviews']} ad={stat['ad']} non_ad={stat['non_ad']}"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--step", choices=["step1", "all"], default="step1")
    parser.add_argument("--url")
    parser.add_argument("--urls-file")
    parser.add_argument("--cafe", default="샘플카페")
    args = parser.parse_args()

    if not args.url and not args.urls_file:
        parser.error("--url 또는 --urls-file 중 하나는 필수입니다.")

    if args.step == "step1":
        if args.urls_file:
            targets = load_targets_from_file(args.urls_file, args.cafe)
            for cafe_name, url in targets:
                run_step1(url, cafe_name)
        else:
            run_step1(args.url, args.cafe)
    else:
        if args.urls_file:
            targets = load_targets_from_file(args.urls_file, args.cafe)
            run_pipeline_batch(targets)
        else:
            run_pipeline(args.url, args.cafe)
