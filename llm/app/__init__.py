from contextlib import asynccontextmanager
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres import AsyncPostgresStore

from app.core.logger import setup_logging
from app.core.config import settings


logger = setup_logging()


_checkpointer   = None
_store          = None


def get_db_uri() -> str:
    """Get database URI for LangGraph (checkpointer, store, and vector storage)"""
    return (
        f"postgresql://{settings.LANGGRAPH_DB_USER}:"
        f"{settings.LANGGRAPH_DB_PASS}@"
        f"{settings.LANGGRAPH_DB_HOST}:"
        f"{settings.LANGGRAPH_DB_PORT}/"
        f"{settings.LANGGRAPH_DB_NAME}"
    )


def get_vector_db_connection_string() -> str:
    """Get connection string for PGVector (same as LangGraph DB)"""
    return get_db_uri()


async def init_langgraph_db():
    global _checkpointer, _store

    db_uri = get_db_uri()

    checkpointer_cm = AsyncPostgresSaver.from_conn_string(db_uri)
    _checkpointer = await checkpointer_cm.__aenter__()
    await _checkpointer.setup()
    logger.info("LangGraph checkpointer initialized")

    store_cm = AsyncPostgresStore.from_conn_string(db_uri)
    _store = await store_cm.__aenter__()
    await _store.setup()
    logger.info("LangGraph store initialized")


async def cleanup_langgraph_db():
    global _checkpointer, _store
    
    if _checkpointer:
        try:
            await _checkpointer.aclose()
            logger.info("LangGraph checkpointer closed")
        except Exception as e:
            logger.error(f"Error closing checkpointer: {e}")
    
    if _store:
        try:
            await _store.aclose()
            logger.info("LangGraph store closed")
        except Exception as e:
            logger.error(f"Error closing store: {e}")
    
    _checkpointer = None
    _store = None


def get_checkpointer():
    """Get the async PostgreSQL checkpointer instance."""
    return _checkpointer


def get_store():
    """Get the async PostgreSQL store instance."""
    return _store