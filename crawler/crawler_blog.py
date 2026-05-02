from typing import List, Dict
import requests
from bs4 import BeautifulSoup


# 이 함수는 블로그/리뷰 페이지 URL에서 본문 텍스트를 수집하는 최소 크롤링 함수
# 주의: 실제 서비스에서는 robots.txt/이용약관을 반드시 준수해야 한다.
def crawl_single_page(url: str, cafe_name: str) -> List[Dict]:
    # 이 헤더는 일반 브라우저 요청으로 인식되도록 하여 차단 가능성을 낮추기 위한 요청 헤더
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]

    reviews = []
    for text in paragraphs:
        if len(text) < 20:
            continue
        reviews.append({"cafe": cafe_name, "content": text, "ad_score": 0.0, "is_ad": False})
    return reviews
