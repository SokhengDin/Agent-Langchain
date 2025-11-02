from typing import Dict, Any, List, Optional
from datetime import datetime
from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig
from langchain_community.vectorstores import Chroma

from app.states.hotel_agent_state import HotelAgentState, HotelMemory
from app import logger


class LLMMemoryNode:
    """Node handling long-term memory operations for hotel agent system"""
    
    def __init__(
        self
        , memory_store    : Chroma
        , memory_tools    : Any  
    ):
        self.memory_store = memory_store
        self.memory_tools = memory_tools

    async def retrieve_memories_node(
        self
        , state           : HotelAgentState
        , config          : RunnableConfig
    ) -> Dict[str, List[str]]:
        """
        Node: Retrieve context-aware memories from vector store
        
        Args:
            state: Current agent state containing context
            config: Runnable configuration with thread metadata
            
        Returns:
            State update with relevant memories
        """
        try:
            context_filter  = self._build_context_filter(state)
            query           = self._build_memory_query(state) 
            
            if not state["messages"]:
                return {"recall_memories": []}
            
            logger.debug(f"Debugging from LLM MEMory node {context_filter}")

            docs            = await self.memory_store.asearch(
                query       = query
                , search_type="similarity"
                , k         = 3
                , filter    = context_filter
                
            )

            weighted_memories   = sorted(
                docs
                , key       = lambda x: x.metadata.get("timestamp", 0)
                , reverse   = True
            )[:3]

            logger.debug(f"Debugging from docs {docs}")
            
            return {"recall_memories": [f"{doc.metadata['type']}: {doc.page_content}" 
                                      for doc in weighted_memories]}
            
        except Exception as e:
            logger.error(
                f"Memory retrieval error: {str(e)}"
                , extra={"thread_id": config["configurable"].get("thread_id")}
            )
            return {"recall_memories": []}

    async def save_memories_node(
        self
        , state           : HotelAgentState
        , config          : RunnableConfig
    ) -> Dict[str, Any]:
        """
        Node: Persist relevant memories to vector store
        
        Args:
            state: Current agent state containing tool outputs
            config: Runnable configuration with thread metadata
            
        Returns:
            Cleaned state with reset tool output
        """
        try:
            updates = {}
            
            # Save explicit tool outputs
            if state.get("last_tool_output"):
                await self._save_tool_memory(state, config)
                updates["last_tool_output"] = None
                
            # Auto-save conversation summaries
            if len(state["messages"]) % 3 == 0:
                await self._save_conversation_summary(state, config)
                
            return updates
            
        except Exception as e:
            logger.error(
                f"Memory save error: {str(e)}"
                , extra={"thread_id": config["configurable"].get("thread_id")}
            )
            return state

    def _build_context_filter(
        self
        , state           : HotelAgentState
    ) -> Dict[str, str]:
        """Build filter dictionary from current context"""

        filter_dict         = {"memory_type"    : "preference"}

        if state["context"].get("guest_id"):
            filter_dict["guest_id"] = state["context"]["guest_id"]
        if state["context"].get("hotel_id"):
            filter_dict["hotel_id"] = state["context"]["hotel_id"]

        return filter_dict
    
    def _build_memory_query(
            self
            , state     : HotelAgentState
    ) -> str:
        """Build contextual query from conversation history"""

        last_3_messages = "\n".join([msg.content for msg in state["messages"][-3:]])
        context         = state["context"]

        return (
            f"Guest Context: {context.get('guest_id', 'new guest')}\n"
            f"Hotel Context: {context.get('hotel_id', 'unknown hotel')}\n"
            f"Recent Conversation:\n{last_3_messages}"
        )

    async def _save_tool_memory(
        self
        , state           : HotelAgentState
        , config          : RunnableConfig
    ) -> None:
        """Persist tool-generated memory"""
        memory_data = HotelMemory(
            guest_id      = state["context"].get("guest_id")
            , hotel_id    = state["context"].get("hotel_id")
            , room_id     = state["context"].get("room_id")
            , memory_type = "operation"
            , content     = state["last_tool_output"]
        )
        
        await self.memory_tools.save_memory.ainvoke(
            memory_data,
            {"configurable": config["configurable"]}
        )

    async def _save_conversation_summary(
        self
        , state           : HotelAgentState
        , config          : RunnableConfig
    ) -> None:
        """Auto-save summarized conversation highlights"""
        convo_summary   = await self._summarize_conversation(state["messages"])
        summary_memory  = HotelMemory(
            guest_id      = state["context"].get("guest_id")
            , memory_type = "summary"
            , content     = convo_summary
        )
        
        await self.memory_tools.save_memory.ainvoke(
            summary_memory
            , {"configurable": config["configurable"]}
        )

    async def _summarize_conversation(
        self
        , messages       : List[Any]
    ) -> str:
        """Generate conversation summary (implementation placeholder)"""
        # TODO: Implement summary
        return "Conversation summary placeholder",