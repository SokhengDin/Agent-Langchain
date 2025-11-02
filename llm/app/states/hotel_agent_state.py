from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict, Annotated
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.managed import IsLastStep

class HotelAgentState(TypedDict):
    """State management for hotel agent"""
    
    messages            : Annotated[list, add_messages]
    current_tool        : Optional[str]   
    recall_memories     : List[str]       
    
    context             : Dict[str, Optional[UUID]]  
    thread_id           : Optional[str]             

    class Config:
        """Configuration for state management"""
        
        arbitrary_types_allowed = True


class KnowledgeTriple(TypedDict):
    """Knowledge representation for hotel domain"""
    
    subject         : str
    predicate       : str
    object_         : str
    timestamp       : datetime
