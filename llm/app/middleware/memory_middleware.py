from typing import Dict, Any

from langchain.agents.middleware import AgentMiddleware

from app.states.hotel_agent_state_v2 import HotelAgentState
from app.services.memory_service_v2 import MemoryServiceV2

from app import logger


class HotelMemoryMiddleware(AgentMiddleware):
    def __init__(self, memory_service: MemoryServiceV2):
        super().__init__()
        self.memory_service = memory_service

    def before_model(self, state: HotelAgentState, runtime=None) -> Dict[str, Any] | None:
        try:
            guest_id    = state.get("guest_id")
            thread_id   = state.get("thread_id")

            if not guest_id and not thread_id:
                return {"recall_memories": []}

            messages        = state.get("messages", [])
            last_message    = messages[-1] if messages else None

            if last_message and hasattr(last_message, "content"):
                query = last_message.content if isinstance(last_message.content, str) else ""
            else:
                query = ""

            # Load memories
            memories = self.memory_service.recall_memories(
                query       = query
                , guest_id  = guest_id
                , thread_id = thread_id
                , limit     = 5
            )

            # Add preferences and bookings if guest_id exists
            if guest_id:
                try:
                    preferences     = self.memory_service.get_guest_preferences(guest_id)
                    if preferences:
                        pref_memory = "Guest preferences: " + ", ".join([
                            f"{k}: {v}" for k, v in preferences.items()
                        ])
                        memories.append(pref_memory)

                    bookings = self.memory_service.get_guest_bookings(guest_id)
                    if bookings and len(bookings) > 0:
                        recent_booking  = bookings[0]
                        booking_memory  = "Most recent booking: " + ", ".join([
                            f"{k}: {v}" for k, v in recent_booking.items()
                            if k not in ["cross_thread", "memory_type"]
                        ])
                        memories.append(booking_memory)
                except:
                    pass

            logger.debug(f"Loaded {len(memories)} memories for context")
            return {"recall_memories": memories}

        except Exception as e:
            logger.error(f"Error loading memories: {str(e)}")
            return {"recall_memories": []}
