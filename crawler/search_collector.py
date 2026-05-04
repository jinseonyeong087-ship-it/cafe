from typing import List
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup


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
    links = []

    # 이 셀렉터는 네이버 VIEW 검색 카드의 링크를 우선 수집하기 위한 후보 목록이다.
    selectors = [
        "a.title_link",
        "a.api_txt_lines.total_tit",
        "a.link_tit",
    ]

    for selector in selectors:
        for tag in soup.select(selector):
            href = tag.get("href", "").strip()
            if not href:
                continue
            if "blog.naver.com" not in href and "m.blog.naver.com" not in href:
                continue
            if href in links:
                continue
            links.append(href)
            if len(links) >= max_urls:
                return links

    return links
