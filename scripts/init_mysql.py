from pathlib import Path
import mysql.connector

from app.core.config import settings


# 이 함수는 docs/sql/schema.sql 파일을 읽어 MySQL에 테이블을 생성하는 함수
def init_mysql_schema() -> None:
    schema_path = Path(__file__).resolve().parent.parent / "docs" / "sql" / "schema.sql"
    sql_text = schema_path.read_text(encoding="utf-8")

    conn = mysql.connector.connect(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password,
        database=settings.mysql_database,
    )
    cur = conn.cursor()

    # 이 구문은 세미콜론 기준으로 SQL 문장을 분리하여 순차 실행하는 로직
    statements = [stmt.strip() for stmt in sql_text.split(";") if stmt.strip()]
    for stmt in statements:
        cur.execute(stmt)

    conn.commit()
    cur.close()
    conn.close()
    print("MySQL 스키마 초기화 완료")


if __name__ == "__main__":
    init_mysql_schema()
