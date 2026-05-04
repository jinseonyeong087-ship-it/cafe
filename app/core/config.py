from pydantic_settings import BaseSettings, SettingsConfigDict


# 이 클래스는 .env 파일의 설정값을 애플리케이션 전역에서 사용하기 위한 설정 클래스
class Settings(BaseSettings):
    openai_api_key: str = ""

    mongodb_uri: str
    mongodb_db: str = "cafe_reviews"
    mongodb_collection: str = "reviews"

    mysql_host: str
    mysql_port: int = 3306
    mysql_user: str
    mysql_password: str
    mysql_database: str = "cafe_menu"

    crawl_max_pages: int = 3

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    positive_taste_weight: float = 1.5

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


# 이 객체는 다른 모듈에서 공통 설정값을 가져다 쓰기 위한 싱글톤 설정 인스턴스
settings = Settings()
