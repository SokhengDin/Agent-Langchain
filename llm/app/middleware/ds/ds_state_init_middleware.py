from typing import Dict, Any
from langchain.agents.middleware import AgentMiddleware

from app.states.ds_agent_state import DSAgentState
from app.core.config import settings
from app import logger

class DSStateInitMiddleware(AgentMiddleware):

    def before_model(self, state: DSAgentState, runtime) -> Dict[str, Any] | None:
        try:
            updates = {}

            if "dataset_id" not in state:
                updates["dataset_id"] = None

            if "current_tool" not in state:
                updates["current_tool"] = None

            if "uploaded_files" not in state:
                updates["uploaded_files"] = []

            if "current_dataframe" not in state:
                updates["current_dataframe"] = None

            if "context" not in state:
                updates["context"] = {}

            if "api_base_url" not in state:
                updates["api_base_url"] = settings.FRONT_API_BASE_URL

            if "code_execution_count" not in state:
                updates["code_execution_count"] = 0

            if "thread_id" not in state:
                thread_id = runtime.context.get("thread_id") if runtime and runtime.context else None
                if thread_id:
                    updates["thread_id"] = thread_id

            return updates if updates else None

        except Exception as e:
            logger.error(f"Error initializing state: {str(e)}")
            return None
