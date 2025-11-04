from pydantic_settings import BaseSettings
from decouple import config


class Settings(BaseSettings):

    API_V1_STR      : str = "/api/v1"

    API_BASE_URL    : str = config('API_BASE_URL'       , cast=str)
    FRONT_API_BASE_URL  : str = config('FRONT_API_BASE_URL', cast=str)

    PORT            : int = config('PORT'               , cast=int)
    OPENAI_API_KEY  : str = config('OPENAI_API_KEY'     , cast=str)
    OLLAMA_BASE_URL : str = config('OLLAMA_BASE_URL'    , cast=str)

    NVIDIA_NIM_API_KEY  : str = config('NVIDIA_NIM_API_KEY' , cast=str)

    # LangGraph Database (PostgreSQL with pgvector for checkpointing, store, and vector embeddings)
    LANGGRAPH_DB_USER   : str = config('LANGGRAPH_DB_USER', cast=str)
    LANGGRAPH_DB_PASS   : str = config('LANGGRAPH_DB_PASS', cast=str)
    LANGGRAPH_DB_NAME   : str = config('LANGGRAPH_DB_NAME', cast=str)
    LANGGRAPH_DB_HOST   : str = config('LANGGRAPH_DB_HOST', cast=str)
    LANGGRAPH_DB_PORT   : str = config('LANGGRAPH_DB_PORT', cast=str)

    # LANGSMITH_TRACING       : str = config('LANGSMITH_TRACING', cast=str)
    # LANGSMITH_ENDPOINT      : str = config('LANGSMITH_ENDPOINT', cast=str)
    # LANGSMITH_API_KEY       : str = config('LANGSMITH_API_KEY', cast=str)
    # LANGSMITH_PROJECT       : str = config('LANGSMITH_PROJECT', cast=str)

    class Config:
        env_file    = ".env"
        env_file_encoding = "utf-8"
        extra       = "ignore"


settings = Settings()