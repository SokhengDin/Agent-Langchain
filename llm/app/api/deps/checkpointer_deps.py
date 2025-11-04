from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from app.core.config import settings


_checkpointer = None


def get_db_uri() -> str:
    return (
        f"postgresql://{settings.LANGGRAPH_DB_USER}:"
        f"{settings.LANGGRAPH_DB_PASS}@"
        f"{settings.LANGGRAPH_DB_HOST}:"
        f"{settings.LANGGRAPH_DB_PORT}/"
        f"{settings.LANGGRAPH_DB_NAME}"
    )


async def get_checkpointer() -> AsyncPostgresSaver:
    global _checkpointer
    if _checkpointer is None:
        _checkpointer = AsyncPostgresSaver.from_conn_string(get_db_uri())
        await _checkpointer.setup()
    return _checkpointer
