import argparse
import json
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from analyzer.ad_filter import mark_ad_review
from analyzer.menu_analyzer import count_menu_candidate_frequency, count_menu_frequency
from crawler.crawler_blog import crawl_single_page
from crawler.search_collector import collect_blog_urls_from_query
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
def run_pipeline(url: str, cafe_name: str, cafe_profile: str = "franchise") -> dict:
    from storage.mongo_client import MongoRepository

    started_at = time.perf_counter()
    reviews = run_step1(url, cafe_name)

    processed_reviews = [mark_ad_review(review, cafe_profile=cafe_profile) for review in reviews]
    ad_count = sum(1 for review in processed_reviews if review.get("is_ad"))
    non_ad_count = len(processed_reviews) - ad_count

    mongo_repo = MongoRepository()
    inserted_count = mongo_repo.insert_reviews(processed_reviews)

    menu_counts = count_menu_frequency(processed_reviews)
    candidate_counts = count_menu_candidate_frequency(processed_reviews)

    mysql_repo = MySQLRepository()
    updated_count = mysql_repo.upsert_menu_ranks(cafe_name, menu_counts)
    candidate_updated_count = mysql_repo.upsert_menu_candidates(cafe_name, candidate_counts)

    elapsed_ms = round((time.perf_counter() - started_at) * 1000, 2)

    print(f"[STEP2] 저장 리뷰 수: {inserted_count}")
    print(f"[STEP3] 광고/비광고: {ad_count}/{non_ad_count}")
    print(f"[STEP4] 메뉴 빈도: {menu_counts}")
    print(f"[STEP5] MySQL 반영 건수: {updated_count}")
    print(f"[STEP5-2] menu_candidate 반영 건수: {candidate_updated_count}")
    print(f"[PERF] 처리 소요시간(ms): {elapsed_ms}")

    return {
        "cafe": cafe_name,
        "url": url,
        "reviews": len(processed_reviews),
        "ad_count": ad_count,
        "non_ad_count": non_ad_count,
        "inserted_count": inserted_count,
        "updated_count": updated_count,
        "candidate_updated_count": candidate_updated_count,
        "elapsed_ms": elapsed_ms,
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


# 이 함수는 실행 로그 디렉터리를 준비하는 함수
def ensure_log_dir(log_dir: str) -> Path:
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    return log_path


# 이 함수는 URL별 처리 결과를 JSONL에 누적 저장하는 함수
def append_jsonl(path: Path, record: dict) -> None:
    with path.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(record, ensure_ascii=False) + "\n")


# 이 함수는 다중 타겟 파이프라인을 실행하고 요약 통계를 출력하는 함수
def run_pipeline_batch(
    targets: list[tuple[str, str]],
    cafe_profile: str = "franchise",
    source_type: str = "manual",
    source_name: str = "direct",
    log_dir: str = "storage/logs",
) -> None:
    started_at_iso = datetime.now().isoformat(timespec="seconds")
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = ensure_log_dir(log_dir)
    event_log_file = log_path / f"pipeline_events_{run_id}.jsonl"
    summary_log_file = log_path / f"pipeline_summary_{run_id}.json"

    success = 0
    failed = 0
    cafe_stats = defaultdict(
        lambda: {
            "targets": 0,
            "success": 0,
            "failed": 0,
            "reviews": 0,
            "ad": 0,
            "non_ad": 0,
            "elapsed_ms_total": 0.0,
        }
    )

    for idx, (cafe_name, url) in enumerate(targets, start=1):
        cafe_stats[cafe_name]["targets"] += 1
        print(f"\n[BATCH] ({idx}/{len(targets)}) cafe={cafe_name} url={url}")

        event_record = {
            "run_id": run_id,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "source_type": source_type,
            "source_name": source_name,
            "cafe": cafe_name,
            "url": url,
            "cafe_profile": cafe_profile,
            "status": "success",
        }

        try:
            result = run_pipeline(url, cafe_name, cafe_profile=cafe_profile)
            success += 1
            cafe_stats[cafe_name]["success"] += 1
            cafe_stats[cafe_name]["reviews"] += result["reviews"]
            cafe_stats[cafe_name]["ad"] += result["ad_count"]
            cafe_stats[cafe_name]["non_ad"] += result["non_ad_count"]
            cafe_stats[cafe_name]["elapsed_ms_total"] += result["elapsed_ms"]

            event_record.update(result)
        except Exception as exc:
            failed += 1
            cafe_stats[cafe_name]["failed"] += 1
            event_record["status"] = "failed"
            event_record["error"] = str(exc)
            print(f"[ERROR] cafe={cafe_name} url={url} 실패: {exc}")

        append_jsonl(event_log_file, event_record)

    print("\n===== BATCH SUMMARY =====")
    print(f"총 대상 URL: {len(targets)}")
    print(f"성공: {success} / 실패: {failed}")

    summary_by_cafe: dict[str, dict] = {}
    for cafe_name, stat in sorted(cafe_stats.items()):
        ad_ratio = round((stat["ad"] / stat["reviews"]), 4) if stat["reviews"] else 0.0
        avg_elapsed_ms = round((stat["elapsed_ms_total"] / stat["success"]), 2) if stat["success"] else 0.0
        summary_by_cafe[cafe_name] = {
            **stat,
            "ad_ratio": ad_ratio,
            "avg_elapsed_ms": avg_elapsed_ms,
        }
        print(
            f"- {cafe_name}: targets={stat['targets']} success={stat['success']} failed={stat['failed']} "
            f"reviews={stat['reviews']} ad={stat['ad']} non_ad={stat['non_ad']} "
            f"ad_ratio={ad_ratio} avg_elapsed_ms={avg_elapsed_ms}"
        )

    summary_record = {
        "run_id": run_id,
        "started_at": started_at_iso,
        "finished_at": datetime.now().isoformat(timespec="seconds"),
        "source_type": source_type,
        "source_name": source_name,
        "total_targets": len(targets),
        "success": success,
        "failed": failed,
        "by_cafe": summary_by_cafe,
        "event_log": str(event_log_file),
    }
    summary_log_file.write_text(json.dumps(summary_record, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[LOG] 이벤트 로그 저장: {event_log_file}")
    print(f"[LOG] 요약 로그 저장: {summary_log_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--step", choices=["step1", "all"], default="step1")
    parser.add_argument("--url")
    parser.add_argument("--urls-file")
    parser.add_argument("--query")
    parser.add_argument("--max-urls", type=int, default=10)
    parser.add_argument("--cafe", default="샘플카페")
    parser.add_argument("--cafe-profile", choices=["franchise", "small_cafe"], default="franchise")
    parser.add_argument("--log-dir", default="storage/logs")
    args = parser.parse_args()

    if not args.url and not args.urls_file and not args.query:
        parser.error("--url 또는 --urls-file 또는 --query 중 하나는 필수입니다.")

    if args.step == "step1":
        if args.urls_file:
            targets = load_targets_from_file(args.urls_file, args.cafe)
            for cafe_name, url in targets:
                run_step1(url, cafe_name)
        elif args.query:
            urls = collect_blog_urls_from_query(args.query, max_urls=args.max_urls)
            print(f"[SEARCH] query='{args.query}' 수집 URL 수: {len(urls)}")
            for url in urls:
                run_step1(url, args.cafe)
        else:
            run_step1(args.url, args.cafe)
    else:
        if args.urls_file:
            targets = load_targets_from_file(args.urls_file, args.cafe)
            run_pipeline_batch(
                targets,
                cafe_profile=args.cafe_profile,
                source_type="urls_file",
                source_name=args.urls_file,
                log_dir=args.log_dir,
            )
        elif args.query:
            urls = collect_blog_urls_from_query(args.query, max_urls=args.max_urls)
            print(f"[SEARCH] query='{args.query}' 수집 URL 수: {len(urls)}")
            targets = [(args.cafe, url) for url in urls]
            run_pipeline_batch(
                targets,
                cafe_profile=args.cafe_profile,
                source_type="query",
                source_name=args.query,
                log_dir=args.log_dir,
            )
        else:
            run_pipeline_batch(
                [(args.cafe, args.url)],
                cafe_profile=args.cafe_profile,
                source_type="single_url",
                source_name=args.url,
                log_dir=args.log_dir,
            )
