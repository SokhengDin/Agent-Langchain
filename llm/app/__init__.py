from contextlib import asynccontextmanager

from app.core.logger import setup_logging
from app.core.config import settings


logger = setup_logging()


def get_db_uri() -> str:
    return (
        f"postgresql://{settings.LANGGRAPH_DB_USER}:"
        f"{settings.LANGGRAPH_DB_PASS}@"
        f"{settings.LANGGRAPH_DB_HOST}:"
        f"{settings.LANGGRAPH_DB_PORT}/"
        f"{settings.LANGGRAPH_DB_NAME}"
    )


def get_vector_db_connection_string() -> str:
    return get_db_uri()


async def init_langgraph_db():
    logger.info("LangGraph dependencies will be initialized on-demand")


async def cleanup_langgraph_db():
    pass