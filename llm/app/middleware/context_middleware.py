import re
from typing import Dict, Any
from uuid import uuid4

from langchain.agents.middleware import AgentMiddleware

from app.states.hotel_agent_state_v2 import HotelAgentState
from app.services.memory_service_v2 import MemoryServiceV2
from app.core.utils.api_utils_sync import APIUtils

from app import logger


class ContextMiddleware(AgentMiddleware):
    def __init__(self, memory_service: MemoryServiceV2):
        super().__init__()
        self.memory_service = memory_service

    def before_model(self, state: HotelAgentState, runtime) -> Dict[str, Any] | None:
        try:
            thread_id       = runtime.context.get("thread_id", str(uuid4()))
            guest_id        = self.memory_service.get_thread_guest(thread_id)

            if state["messages"] and len(state["messages"]) > 0:
                first_message   = state["messages"][0]
                message_content = first_message.content if isinstance(first_message.content, str) else ""

                if not guest_id and message_content:
                    email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', message_content)
                    if email_match:
                        email = email_match.group(0)
                        try:
                            response = APIUtils.get(f"/api/v1/guest/email/{email}")
                            if response and isinstance(response, dict):
                                guest = response.get("data")
                                if guest and "id" in guest:
                                    guest_id = guest["id"]
                                    self.memory_service.link_guest_to_thread(
                                        guest_id    = guest_id
                                        , thread_id = thread_id
                                    )
                        except:
                            pass

            context = state.get("context", {})

            updates = {
                "thread_id" : thread_id
                , "context" : context
            }

            if guest_id:
                updates["guest_id"] = guest_id

            return updates

        except Exception as e:
            logger.error(f"Error preparing context: {str(e)}")
            return {"context": state.get("context", {})}
