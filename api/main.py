from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import engine

from app.middleware.http_traffic_logger import HTTPTrafficLoggerMiddleware
from app.middleware.response_formatter import ResponseFormatterMiddleware

from app.api.router import router

from app.core.config import settings
from app.database import engine
from app.database.models.base_model import Base
from app import logger

def create_tables():
    Base.metadata.create_all(bind=engine)
    logger.info("Database connection connected successfully...")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up application...")
    create_tables()
    yield
    logger.info("Shutting down application...")


app         = FastAPI(lifespan=lifespan)

app.include_router(router, prefix=settings.API_V1_STR)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

app.add_middleware(
    HTTPTrafficLoggerMiddleware
    , save_to_database  = True
    , log_response_body = True
)

app.add_middleware(ResponseFormatterMiddleware)


if __name__ == "__main__":
    import uvicorn
    from uvicorn.config import LOGGING_CONFIG


    LOGGING_CONFIG["handlers"] = {}
    LOGGING_CONFIG["loggers"] = {}

    logger.info("Starting application")
    uvicorn.run("main:app"
                , host  = "0.0.0.0"
                , port  = 8000
                , reload= True
                , reload_dirs   = ["app"]
                , log_config    = None)