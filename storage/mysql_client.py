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
