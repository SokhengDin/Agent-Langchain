from typing import List, Dict, Optional
from typing_extensions import TypedDict
from datetime import datetime

from langchain_core.tools import tool
from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig
from langchain_community.vectorstores import Chroma

from app import logger


class HotelMemory(TypedDict):
    """Structure for hotel-related memories"""

    guest_id        : Optional[str]
    hotel_id        : Optional[str]
    room_id         : Optional[str]
    memory_type     : str
    content         : str


class MemoryTools:
    """Tools for managing memories in the hotel system"""
    
    def __init__(self, memory_store: Chroma):
        self.memory_store = memory_store
        
    @tool("save_memory")
    def save_memory(
        self
        , memory    : HotelMemory
        , config    : RunnableConfig
    ) -> str:
        """
        Save a memory with metadata.
        
        Args:
            memory : The memory text to save (e.g., "Guest John prefers quiet rooms")
            config : Must include thread_id and can include:
                    - guest_id, hotel_id, room_id
                    - memory_type: Type of memory (booking/preference/complaint)
                    - timestamp: Automatically added
        Returns:
            The memory content saved
        """
        try:
            
            thread_id   = config["configurable"].get("thread_id")

            if not thread_id:
                raise ValueError("thread_id required in config")
            
            document    = Document(
                page_content = memory["content"]
                , metadata   = {
                    "thread_id"     : thread_id
                    , "guest_id"    : memory.get("guest_id")
                    , "hotel_id"    : memory.get("hotel_id")
                    , "room_id"     : memory.get("room_id")
                    , "memory_type" : memory["memory_type"]
                    , "timestamp"   : datetime.now().isoformat()
                }
            )
            
            self.memory_store.add_documents([document])

            logger.info(
                "Memory saved successfully"
            )
            
            return memory["content"]
        
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
            raise
            
    @tool("load_memories")
    def load_memories(
        self
        , query             : str
        , config            : RunnableConfig
        , memory_type       : Optional[str] = None
        , limit             : int = 5
    ) -> List[str]:
        """
        Load relevant memories based on query and filters.
        
        Args:
            query        : Text to search for
            config       : Must include thread_id
            memory_type  : Optional filter by memory type
            limit        : Max number of memories to return
            
        Returns:
            List of memory contents
        """
        try:
            
            thread_id   = config["configurable"].get("thread_id")

            if not thread_id:
                raise ValueError("thread_id required in config")
            
            filter_dict = {"thread_id": thread_id}
            if memory_type:
                filter_dict["memory_type"] = memory_type

            docs        = self.memory_store.similarity_search(
                query   = query
                , k     = limit
                , filter= filter_dict
            )

            memories    = [doc.page_content for doc in docs]
            
            logger.info(
                f"Loaded {len(memories)} memories"
            )

            return memories

        except Exception as e:
            logger.error(f"Error loading memories: {e}")
            raise
