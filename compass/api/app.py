from fastapi import FastAPI

from compass.api.routes import router


def create_app() -> FastAPI:
    application = FastAPI(title="Compass RAG Platform")
    application.include_router(router)
    return application


app = create_app()
