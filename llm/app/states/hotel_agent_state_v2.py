from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict, Annotated
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from langgraph.graph.message import add_messages

class HotelAgentState(TypedDict):
    """State management for hotel agent"""

    messages            : Annotated[list, add_messages]
    current_tool        : Optional[str]
    recall_memories     : List[str]

    thread_id           : Optional[str]
    guest_id            : Optional[str]
    room_id             : Optional[str]
    booking_id          : Optional[str]
    payment_id          : Optional[str]

    token               : Optional[str]
    context             : Optional[Dict[str, Any]]  # Added for middleware context