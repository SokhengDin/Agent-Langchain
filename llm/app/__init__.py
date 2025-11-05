from contextlib import asynccontextmanager
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.core.logger import setup_logging
from app.core.config import settings


logger = setup_logging()

_global_executor = None


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
    global _global_executor

    _global_executor = ThreadPoolExecutor(
        max_workers=20,
        thread_name_prefix="langgraph_executor"
    )

    loop = asyncio.get_event_loop()
    loop.set_default_executor(_global_executor)

    logger.info(f"Initialized global ThreadPoolExecutor with 20 max workers")
    logger.info("LangGraph dependencies will be initialized on-demand")


async def cleanup_langgraph_db():
    global _global_executor

    if _global_executor:
        logger.info("Shutting down global ThreadPoolExecutor")
        _global_executor.shutdown(wait=True, cancel_futures=True)
        _global_executor = None