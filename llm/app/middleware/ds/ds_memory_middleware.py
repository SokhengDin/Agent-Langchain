from typing import Dict, Any

from langchain.agents.middleware import AgentMiddleware

from app.states.ds_agent_state import DSAgentState
from app.services.ds_memory_service import DSMemoryService
from app import logger

class DSMemoryMiddleware(AgentMiddleware):
    def __init__(self, memory_service: DSMemoryService):
        super().__init__()
        self.memory_service = memory_service

    def before_model(self, state: DSAgentState, runtime=None) -> Dict[str, Any] | None:
        try:
            thread_id = state.get("thread_id")

            if not thread_id:
                return {"recall_memories": []}

            messages        = state.get("messages", [])
            last_message    = messages[-1] if messages else None

            if last_message and hasattr(last_message, "content"):
                query = last_message.content if isinstance(last_message.content, str) else ""
            else:
                query = ""

            memories = self.memory_service.recall_memories(
                query       = query
                , thread_id = thread_id
                , limit     = 5
            )

            logger.debug(f"Loaded {len(memories)} memories for context")
            return {"recall_memories": memories}

        except Exception as e:
            logger.error(f"Error loading memories: {str(e)}")
            return {"recall_memories": []}
