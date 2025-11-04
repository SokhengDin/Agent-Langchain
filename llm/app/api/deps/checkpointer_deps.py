from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from app.core.config import settings


_checkpointer = None
_checkpointer_cm = None


def get_db_uri() -> str:
    return (
        f"postgresql://{settings.LANGGRAPH_DB_USER}:"
        f"{settings.LANGGRAPH_DB_PASS}@"
        f"{settings.LANGGRAPH_DB_HOST}:"
        f"{settings.LANGGRAPH_DB_PORT}/"
        f"{settings.LANGGRAPH_DB_NAME}"
    )


async def get_checkpointer() -> AsyncPostgresSaver:
    global _checkpointer, _checkpointer_cm
    if _checkpointer is None:
        _checkpointer_cm = AsyncPostgresSaver.from_conn_string(get_db_uri())
        _checkpointer = await _checkpointer_cm.__aenter__()
        await _checkpointer.setup()
    return _checkpointer
