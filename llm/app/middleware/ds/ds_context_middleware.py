from typing import Dict, Any
from uuid import uuid4

from langchain.agents.middleware import AgentMiddleware

from app.states.ds_agent_state import DSAgentState
from app import logger

class DSContextMiddleware(AgentMiddleware):
    def __init__(self):
        super().__init__()

    def before_model(self, state: DSAgentState, runtime) -> Dict[str, Any] | None:
        try:
            thread_id = runtime.context.get("thread_id", str(uuid4()))
            context = state.get("context", {})

            return {
                "thread_id" : thread_id
                , "context" : context
            }

        except Exception as e:
            logger.error(f"Error preparing context: {str(e)}")
            return {"context": state.get("context", {})}
