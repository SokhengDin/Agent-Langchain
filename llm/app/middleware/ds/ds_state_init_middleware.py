from typing import Dict, Any
from langchain.agents.middleware import AgentMiddleware

from app.states.ds_agent_state import DSAgentState
from app.core.config import settings
from app import logger

class DSStateInitMiddleware(AgentMiddleware):

    def before_model(self, state: DSAgentState, runtime) -> Dict[str, Any] | None:
        try:
            if state is None:
                return None

            updates = {}

            if state.get("dataset_id") is None:
                updates["dataset_id"] = None

            if state.get("current_tool") is None:
                updates["current_tool"] = None

            if state.get("uploaded_files") is None:
                updates["uploaded_files"] = []

            if state.get("current_dataframe") is None:
                updates["current_dataframe"] = None

            if state.get("context") is None:
                updates["context"] = {}

            if state.get("api_base_url") is None:
                updates["api_base_url"] = settings.FRONT_API_BASE_URL

            if state.get("code_execution_count") is None:
                updates["code_execution_count"] = 0

            if state.get("thread_id") is None:
                thread_id = runtime.context.get("thread_id") if runtime and runtime.context else None
                if thread_id:
                    updates["thread_id"] = thread_id

            return updates if updates else None

        except Exception as e:
            logger.error(f"Error initializing state: {str(e)}")
            return None
