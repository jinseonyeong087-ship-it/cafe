from typing import List
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup


# 이 함수는 블로그 글 URL 여부를 판별하는 함수
# 규칙: blog.naver.com 도메인 + /{blog_id}/{post_id} 형태를 우선 허용한다.
def _is_blog_post_url(url: str) -> bool:
    if "blog.naver.com" not in url and "m.blog.naver.com" not in url:
        return False
    if "/" not in url:
        return False

    parts = [p for p in url.split("/") if p]
    # 예: https:, blog.naver.com, sangyun1106, 223666614285
    if len(parts) < 4:
        return False
    last = parts[-1]
    if not last.isdigit():
        return False
    return True


# 이 함수는 검색어로 네이버 검색 결과 페이지를 조회해 블로그 URL 후보를 수집하는 함수
# 주의: 검색 페이지 구조 변경 시 셀렉터 수정이 필요할 수 있다.
def collect_blog_urls_from_query(query: str, max_urls: int = 10) -> List[str]:
    encoded_query = quote(query)
    search_url = f"https://search.naver.com/search.naver?where=view&sm=tab_jum&query={encoded_query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    response = requests.get(search_url, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    links: List[str] = []
    seen = set()

    # 네이버 검색 HTML 구조가 수시로 변경되므로, a[href] 전수 탐색으로 안정성을 높인다.
    for tag in soup.select("a[href]"):
        href = tag.get("href", "").strip()
        if not href or href in seen:
            continue
        seen.add(href)

        if not _is_blog_post_url(href):
            continue

        links.append(href)
        if len(links) >= max_urls:
            break

    return links
