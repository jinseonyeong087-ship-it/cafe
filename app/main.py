from fastapi import FastAPI

from app.api.menu import router as menu_router


# 이 함수는 FastAPI 애플리케이션 객체를 생성하고 라우터를 등록하는 함수
def create_app() -> FastAPI:
    app = FastAPI(title="Cafe Menu Recommendation API")
    app.include_router(menu_router)
    return app


app = create_app()
