from typing import Dict
import mysql.connector

from app.core.config import settings


# 이 클래스는 MySQL 연결 및 메뉴 집계 데이터 적재/조회 기능을 담당하는 저장소 클래스
class MySQLRepository:
    # 이 함수는 MySQL 커넥션을 생성하는 함수
    def _get_connection(self):
        return mysql.connector.connect(
            host=settings.mysql_host,
            port=settings.mysql_port,
            user=settings.mysql_user,
            password=settings.mysql_password,
            database=settings.mysql_database,
        )

    # 이 함수는 카페명을 기준으로 cafe 테이블에 upsert하고 cafe_id를 반환하는 함수
    def upsert_cafe(self, cafe_name: str) -> int:
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO cafe (name) VALUES (%s)
            ON DUPLICATE KEY UPDATE name = VALUES(name)
            """,
            (cafe_name,),
        )
        conn.commit()
        cur.execute("SELECT id FROM cafe WHERE name = %s", (cafe_name,))
        cafe_id = cur.fetchone()[0]
        cur.close()
        conn.close()
        return cafe_id

    # 이 함수는 메뉴명을 기준으로 menu 테이블에 upsert하고 menu_id를 반환하는 함수
    def upsert_menu(self, menu_name: str) -> int:
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO menu (name) VALUES (%s)
            ON DUPLICATE KEY UPDATE name = VALUES(name)
            """,
            (menu_name,),
        )
        conn.commit()
        cur.execute("SELECT id FROM menu WHERE name = %s", (menu_name,))
        menu_id = cur.fetchone()[0]
        cur.close()
        conn.close()
        return menu_id

    # 이 함수는 카페별 메뉴 집계 결과를 cafe_menu_rank 테이블에 upsert하는 함수
    def upsert_menu_ranks(self, cafe_name: str, menu_counts: Dict[str, int]) -> int:
        if not menu_counts:
            return 0

        cafe_id = self.upsert_cafe(cafe_name)
        sorted_items = sorted(menu_counts.items(), key=lambda x: (-x[1], x[0]))

        conn = self._get_connection()
        cur = conn.cursor()

        updated = 0
        for rank, (menu_name, count) in enumerate(sorted_items, start=1):
            menu_id = self.upsert_menu(menu_name)
            cur.execute(
                """
                INSERT INTO cafe_menu_rank (cafe_id, menu_id, count, menu_rank)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                  count = VALUES(count),
                  menu_rank = VALUES(menu_rank),
                  updated_at = CURRENT_TIMESTAMP
                """,
                (cafe_id, menu_id, count, rank),
            )
            updated += 1

        conn.commit()
        cur.close()
        conn.close()
        return updated

    # 이 함수는 카페별 후보 메뉴 누적치를 menu_candidate 테이블에 upsert하는 함수
    def upsert_menu_candidates(self, cafe_name: str, candidate_counts: Dict[str, int], review_threshold: int = 3) -> int:
        if not candidate_counts:
            return 0

        cafe_id = self.upsert_cafe(cafe_name)
        conn = self._get_connection()
        cur = conn.cursor()

        updated = 0
        for candidate_name, mention_count in candidate_counts.items():
            cur.execute(
                """
                INSERT INTO menu_candidate (cafe_id, candidate_name, mention_count, first_seen_at, last_seen_at, status)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'new')
                ON DUPLICATE KEY UPDATE
                  mention_count = mention_count + VALUES(mention_count),
                  last_seen_at = CURRENT_TIMESTAMP,
                  status = CASE
                    WHEN status = 'new' AND (mention_count + VALUES(mention_count)) >= %s THEN 'reviewing'
                    ELSE status
                  END
                """,
                (cafe_id, candidate_name, mention_count, review_threshold),
            )
            updated += 1

        conn.commit()
        cur.close()
        conn.close()
        return updated

    # 이 함수는 카페별 메뉴 랭크를 조회해 API 응답 계산에 사용하는 함수
    def get_menu_ranks(self, cafe_name: str) -> list[dict]:
        conn = self._get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT c.name AS cafe, m.name AS menu, cmr.count AS count, cmr.menu_rank AS rank
            FROM cafe_menu_rank cmr
            JOIN cafe c ON c.id = cmr.cafe_id
            JOIN menu m ON m.id = cmr.menu_id
            WHERE c.name = %s
            ORDER BY cmr.menu_rank ASC
            """,
            (cafe_name,),
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
