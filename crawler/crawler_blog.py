from typing import List, Dict
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup


# 이 함수는 네이버 블로그 PC URL을 모바일 URL로 정규화하는 함수
# 네이버 블로그는 모바일 페이지에서 본문 추출이 더 안정적이다.
def _normalize_naver_url(url: str) -> str:
    parsed = urlparse(url)
    if "blog.naver.com" in parsed.netloc and not parsed.netloc.startswith("m."):
        return url.replace("https://blog.naver.com/", "https://m.blog.naver.com/")
    return url


# 이 함수는 블로그/리뷰 페이지 URL에서 본문 텍스트를 수집하는 함수
# 주의: 실제 서비스에서는 robots.txt/이용약관을 반드시 준수해야 한다.
def crawl_single_page(url: str, cafe_name: str) -> List[Dict]:
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    normalized_url = _normalize_naver_url(url)
    response = requests.get(normalized_url, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # 이 셀렉터 목록은 블로그 플랫폼별 본문 우선 추출을 위한 후보 목록이다.
    selectors = [
        "div.se-main-container",
        "div#postViewArea",
        "article",
        "div.entry-content",
        "div.tt_article_useless_p_margin",
        "div.post-content",
    ]

    texts: List[str] = []
    for selector in selectors:
        node = soup.select_one(selector)
        if node:
            texts = [t.get_text(strip=True) for t in node.find_all(["p", "span", "li"]) if t.get_text(strip=True)]
            if texts:
                break

    if not texts:
        texts = [p.get_text(strip=True) for p in soup.find_all("p")]

    reviews = []
    for text in texts:
        if len(text) < 20:
            continue
        reviews.append({"cafe": cafe_name, "content": text, "ad_score": 0.0, "is_ad": False, "source_url": normalized_url})
    return reviews
