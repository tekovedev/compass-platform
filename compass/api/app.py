import logging

from fastapi import FastAPI

from compass.api.routes import router

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


def create_app() -> FastAPI:
    application = FastAPI(title="Compass RAG Platform")
    application.include_router(router, prefix="/api/v1")
    return application


app = create_app()
