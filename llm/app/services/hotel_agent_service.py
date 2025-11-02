import os
import re
import tiktoken
import json

from typing import List, Dict, Any
from typing_extensions import Literal
from uuid import UUID, uuid4

from pathlib import Path
from IPython.display import Image, display

from dotenv import load_dotenv

from datetime import datetime


from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.messages import BaseMessage, HumanMessage, get_buffer_string, AIMessage
from langchain_core.tools import render_text_description
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_chroma import Chroma

from langgraph.prebuilt.tool_node import ToolNode
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from app.tools.booking_tools import BookingTools
from app.tools.guest_tools import GuestTools
from app.tools.hotel_tools import HotelTools
from app.tools.room_tools import RoomTools
from app.tools.payment_tools import PaymentTools
from app.tools.invoice_tools import InvoiceTools
from app.states.hotel_agent_state import HotelAgentState

from app.services.memory_service import MemoryService

# from app.prompts.prompt_v1 import Prompt
from app.prompts.prompt_v2 import Prompt

from app.core.utils.hotel_utils import HotelUtils
from app.core.utils.api_utils import APIUtils
from app.core.config import settings

from app import logger

load_dotenv()

os.environ["OPENAI_API_KEY"]        = os.getenv("OPENAI_API_KEY")
os.environ["NVIDIA_NIM_API_KEY"]    = os.getenv("NVIDIA_NIM_API_KEY")

class HotelAgentService:
    """Service for handling hotel management operations using LangChain agent"""
    
    def __init__(self):

        output_dir = Path("output")
        output_dir.mkdir(parents=True, exist_ok=True)
        # Initialize embeddings
        # self.embeddings     = HuggingFaceEmbeddings(
        #     model_name      = "sentence-transformers/all-MiniLM-L6-v2"
        # )

        # OPENAI EMBEDDING

        self.embeddings     = OpenAIEmbeddings()
        # self.embeddings     = OllamaEmbeddings(model="llama3.1")

        self.memory_store   = Chroma(
            collection_name         = "hotel_memories"
            , embedding_function    = self.embeddings
            , persist_directory     = str(output_dir / "chromadb")
        )

        self.memory_service = MemoryService(self.memory_store)

        self.memory         = MemorySaver()
        
        # Collect all tools
        self.tools          = [
            # Guest
            GuestTools.search_guest
            , GuestTools.create_guest
            , GuestTools.update_guest

            # Rooms
            # , RoomTools.check_room_availability
            # , RoomTools.get_room
            , RoomTools.get_all_rooms
            
            # Bookings
            , BookingTools.check_booking_status
            , BookingTools.create_booking
            , BookingTools.get_guest_bookings
            , BookingTools.list_bookings

            # Invoice tools
            , InvoiceTools.generate_invoice
        ]

        self.tool_node  = ToolNode(tools=self.tools, )
        
        # memory
        self.memory     = MemorySaver()

        # Create agent prompt
        self.prompt     = Prompt.prompt_agent()
        
        # OLLAMA
        self.llm    = ChatOllama(
            model       = "gemma3:12b"
            , temperature = 0.0
        ).bind_tools(tools=self.tools)

        self.llm        = ChatOpenAI(
            api_key = settings.OPENAI_API_KEY
            , model = "gpt-4o-2024-08-06"
            , temperature   = 0.4
        )

        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # inti graph
        self.graph  = self.init_workflow()

    def init_workflow(self):
        """Initialize the LangGraph workflow with enhanced memory management"""
        workflow = StateGraph(HotelAgentState)
        

        workflow.add_node("prepare_context", self._prepare_context)
        workflow.add_node("load_memories", self._load_memories)
        workflow.add_node("agent", self._call_model)
        workflow.add_node("tools", ToolNode(self.tools))
        workflow.add_node("process_response", self._process_tool_results)
        

        workflow.add_edge(START, "prepare_context")
        workflow.add_edge("prepare_context", "load_memories")
        workflow.add_edge("load_memories", "agent")
        
        workflow.add_conditional_edges(
            "agent",
            self._route_next_step,
            {
                "tools" : "tools"
                , END     : END
            }
        )
        
        workflow.add_edge("tools", "process_response")
        workflow.add_edge("process_response", "agent")
        
        try:
            graph = workflow.compile(checkpointer=self.memory)
            # png_data = graph.get_graph().draw_mermaid_png()
            
            # output_file = "output/agent_graph.png"  
            
            # with open(output_file, "wb") as f:
            #     f.write(png_data)
                
        except Exception as e:
            raise
        
        return graph

    async def handle_conversation(
        self
        , message   : str
        , thread_id : str = None
        , context   : Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Handle a conversation thread with memory management"""
        try:
            logger.debug(f"Handling conversation: {message}")
            
            thread_id = thread_id if thread_id else str(uuid4())
            

            state = {
                "messages"          : []
                , "context"         : context or {
                    "guest_id"  : None
                    , "hotel_id"  : None
                    , "room_id"   : None
                    , "thread_id" : thread_id
                }
                , "recall_memories" : []
            }

            state["messages"].append(HumanMessage(content=message))
            

            config = {
                "configurable": {
                    "thread_id" : thread_id
                }
            }
            

            result = await self.graph.ainvoke(state, config)

            output = result["messages"][-1].content if result["messages"] else "No response generated"
            
            return {
                "output"      : output
                , "context"   : result["context"]
                , "thread_id" : thread_id
            }
            
        except Exception as e:
            logger.error(f"Error handling conversation: {str(e)}")
            raise


    async def _call_model(self, state: HotelAgentState, config: RunnableConfig):
        """Process the current state with the LLM"""
        try:
            # Format tool descriptions
            tool_descriptions = "\n".join(
                f"- {tool.name}: {tool.description}" 
                for tool in self.tools
            )

            hotel_response = await HotelUtils.get_all_hotel_name()

            if not hotel_response or not isinstance(hotel_response, dict):
                logger.error("No hotel data received from API")
                raise ValueError("No hotel data available - API returned empty response")

            data = hotel_response.get("data", [])
            if not data or len(data) == 0:
                logger.error("No hotel data in response")
                raise ValueError("No hotel data available - API returned empty data")

            hotel_data = data[0] 
            
            # Format recall memories
            recall_str = (
                "<recall_memory>\n" 
                + "\n".join(state["recall_memories"]) 
                + "\n</recall_memory>"
                if state["recall_memories"]
                else "No previous memories found."
            )
            

            prompt_messages = self.prompt.format_messages(
                tools               = tool_descriptions
                , hotel_name        = hotel_data['name']
                , hotel_address     = hotel_data['address']
                , hotel_city        = hotel_data['city']
                , hotel_postal_code = hotel_data['postal_code']
                , hotel_phone_number= hotel_data['phone_number']
                , hotel_email       = hotel_data['email']
                , hotel_total_rooms = hotel_data['total_rooms']
                , hotel_star_rating = hotel_data['star_rating']
                , hotel_description = hotel_data['description']
                , context           = state["context"]
                , recall_memories   = recall_str
            )

            # Get LLM response
            messages = prompt_messages + state["messages"]
            response = await self.llm_with_tools.ainvoke(messages, config)
            
            return {
                "messages": state["messages"] + [response]
            }

        except Exception as e:
            logger.error(f"Error in _call_model: {str(e)}")
            raise


    async def _load_memories(
        self
        , state  : HotelAgentState
        , config : RunnableConfig
    ) -> HotelAgentState:
        """Load relevant memories for conversation"""
        try:
            guest_id = state["context"].get("guest_id")
            if not guest_id:
                return {"recall_memories": []}
                
            messages = get_buffer_string(state["messages"])
            
            tokenizer   = tiktoken.encoding_for_model("gpt-4")
            messages    = tokenizer.decode(
                tokenizer.encode(messages)[:2048]
            )
            
            # Get relevant memories
            memories = await self.memory_service.recall_memories(
                guest_id = guest_id
                , query  = messages
            )
            
            logger.debug(f"Loaded memories: {memories}")
            
            return {
                "recall_memories": memories
            }
            
        except Exception as e:
            logger.error(f"Failed to load memories: {str(e)}")
            raise

    async def _process_response(
        self
        , state  : HotelAgentState
        , config : RunnableConfig
    ) -> HotelAgentState:
        """Process tool response and update memories if needed"""
        try:
            last_message = state["messages"][-1]
            guest_id = state["context"].get("guest_id")
            
            if not guest_id:
                return {"messages": state["messages"]}
                

            if isinstance(last_message.content, dict):
                if "preferences" in last_message.content:
                    for pref_type, value in last_message.content["preferences"].items():
                        await self.memory_service.save_guest_preference(
                            guest_id            = guest_id
                            , preference_type   = pref_type
                            , value             = value
                        )
                        
                if "booking" in last_message.content:
                    booking     = last_message.content["booking"]
                    await self.memory_service.save_booking_memory(
                        guest_id    = guest_id
                        , hotel_id  = booking["hotel_id"]
                        , room_id   = booking["room_id"]
                        , check_in  = booking["check_in"]
                        , check_out = booking["check_out"]
                        , details   = booking.get("details")
                    )
            
            return {
                "messages": state["messages"]
            }
            
        except Exception as e:
            logger.error(f"Failed to process response: {str(e)}")
            raise

    def _route_next_step(
        self
        , state: HotelAgentState
    ) -> Literal["tools", END]:
        """Determine next step in conversation"""
        try:
            last_message = state["messages"][-1]
            
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                logger.debug(f"Found tool calls: {last_message.tool_calls}")
                return "tools"
                
            logger.debug("No tool calls found, ending")
            return END
            
        except Exception as e:
            logger.error(f"Error in route_next_step: {str(e)}")
            raise


    def _format_chat_history(self, message: str, previous_messages: List[BaseMessage] = None) -> List[BaseMessage]:

        chat_history    = previous_messages or []

        current_msg     = HumanMessage(content=message)
        chat_history.append(current_msg)
        
        return chat_history
    
    async def _prepare_context(
        self
        , state  : HotelAgentState
        , config : RunnableConfig
    ) -> HotelAgentState:
        """Prepare the conversation context, identifying the guest if possible"""
        try:
            
            thread_id   = config.get("configurable", {}).get("thread_id", str(uuid4()))
            
            #
            guest_id    = await self.memory_service.get_thread_guest(thread_id)
            
 
            if state["messages"] and len(state["messages"]) > 0:
                first_message   = state["messages"][0]
                message_content = first_message.content if isinstance(first_message.content, str) else ""
                
                if not guest_id and message_content:
                    
                    email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', message_content)
                    if email_match:
                        email   = email_match.group(0)
                    
                        try:
                            guest           = await APIUtils.get(f"/api/v1/guest/email/{email}")
                            if guest and "id" in guest:
                                guest_id    = guest["id"]
                                
                                await self.memory_service.link_guest_to_thread(
                                    guest_id    = guest_id
                                    , thread_id = thread_id
                                )
                        except:
                           
                            pass
            
            context = state.get("context", {})
            context["thread_id"] = thread_id
            
            if guest_id:
                context["guest_id"] = guest_id
            
            return {
                "context": context
            }
        
        except Exception as e:
            logger.error(f"Error preparing context: {str(e)}")
            return {
                "context": state.get("context", {})
            }

    async def _load_memories(
        self
        , state  : HotelAgentState
        , config : RunnableConfig
    ) -> HotelAgentState:
        """Load relevant memories based on conversation context"""
        try:
            guest_id        = state.get("context", {}).get("guest_id")
            thread_id       = state.get("context", {}).get("thread_id")
            
            if not guest_id and not thread_id:
                return {"recall_memories": []}
            

            messages        = state.get("messages", [])
            last_message    = messages[-1] if messages else None
            
            if last_message and hasattr(last_message, "content"):
                query       = last_message.content if isinstance(last_message.content, str) else ""
            else:
                query = ""
            

            memories = await self.memory_service.recall_memories(
                query     = query
                , guest_id  = guest_id
                , thread_id = thread_id
                , limit     = 5
            )
            

            if guest_id:
                try:
                    preferences = await self.memory_service.get_guest_preferences(guest_id)
                    if preferences:
                        pref_memory = "Guest preferences: " + ", ".join([
                            f"{k}: {v}" for k, v in preferences.items()
                        ])
                        memories.append(pref_memory)
                    
                    bookings            = await self.memory_service.get_guest_bookings(guest_id)
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

    async def _process_tool_results(
        self
        , state  : HotelAgentState
        , config : RunnableConfig
    ) -> HotelAgentState:
        """Process tool results and extract relevant context information"""
        try:
    
            messages            = state.get("messages", [])
            if not messages or len(messages) < 2:
                return state
                
            last_message        = messages[-1]
            tool_call_message   = messages[-2] 
            
            context             = state.get("context", {})
            guest_id            = context.get("guest_id")
            thread_id           = context.get("thread_id")
            

            if hasattr(tool_call_message, "tool_calls") and tool_call_message.tool_calls:
                for tool_call in tool_call_message.tool_calls:
                    tool_name   = tool_call.name if hasattr(tool_call, "name") else ""
                    

                    if tool_name == "search_guest" and hasattr(last_message, "content"):
                        content = last_message.content
                        if isinstance(content, str) and "id" in content:
                            try:

                                guest_data = json.loads(content)
                                if "id" in guest_data:
                                    
                                    context["guest_id"] = guest_data["id"]
                                    
                                    if thread_id and guest_data["id"] != guest_id:
                                        await self.memory_service.link_guest_to_thread(
                                            guest_id  = guest_data["id"]
                                            , thread_id = thread_id
                                        )
                            except:

                                match           = re.search(r'"id"\s*:\s*"([^"]+)"', content)
                                if match:
                                    guest_id    = match.group(1)
                                    context["guest_id"] = guest_id
                                    
                                    if thread_id:
                                        await self.memory_service.link_guest_to_thread(
                                            guest_id  = guest_id
                                            , thread_id = thread_id
                                        )
                    
                    elif tool_name == "create_guest" and hasattr(last_message, "content"):
                        content = last_message.content
                        if isinstance(content, str) and "id" in content:
                            try:
                                # Try to parse as JSON
                                guest_data = json.loads(content)
                                if "id" in guest_data:
                                    # Update guest_id in context
                                    context["guest_id"] = guest_data["id"]
                                    
                                    # Link guest to thread
                                    if thread_id:
                                        await self.memory_service.link_guest_to_thread(
                                            guest_id  = guest_data["id"]
                                            , thread_id = thread_id
                                        )
                            except:
                                # Not valid JSON, try to extract ID from string
                                match = re.search(r'"id"\s*:\s*"([^"]+)"', content)
                                if match:
                                    guest_id = match.group(1)
                                    context["guest_id"] = guest_id
                                    
                                    # Link guest to thread
                                    if thread_id:
                                        await self.memory_service.link_guest_to_thread(
                                            guest_id  = guest_id
                                            , thread_id = thread_id
                                        )
                    
                    elif tool_name == "create_booking_tool" and hasattr(last_message, "content"):
                        content = last_message.content
                        if isinstance(content, str) and "id" in content:
                            try:
                                
                                booking_data = json.loads(content)
                                if "id" in booking_data and guest_id:
                                    await self.memory_service.save_booking_memory(
                                        guest_id    = guest_id
                                        , booking_id = booking_data["id"]
                                        , hotel_id   = booking_data.get("hotel_id")
                                        , room_id    = booking_data.get("room_id")
                                        , check_in   = booking_data.get("check_in_date")
                                        , check_out  = booking_data.get("check_out_date")
                                        , num_guests = booking_data.get("num_guests")
                                        , thread_id  = thread_id
                                    )
                                    
                            
                                    context["booking_id"] = booking_data["id"]
                                    if "hotel_id" in booking_data:
                                        context["hotel_id"] = booking_data["hotel_id"]
                                    if "room_id" in booking_data:
                                        context["room_id"] = booking_data["room_id"]
                            except:
                            
                                pass
                    
                    
                    if tool_name in ["get_all_rooms", "check_room_availability"] and guest_id:
                    
                        for i in range(len(messages)-1):
                            if isinstance(messages[i], HumanMessage) and isinstance(messages[i].content, str):
                    
                                content     = messages[i].content.lower()
                                
                                room_types  = ["suite", "standard", "deluxe", "premium", "single", "double", "twin"]
                                for room_type in room_types:
                                    if f"prefer {room_type}" in content or f"want {room_type}" in content:
                                        await self.memory_service.save_guest_preference(
                                            guest_id        = guest_id
                                            , preference_type = "room_type"
                                            , value           = room_type
                                            , thread_id       = thread_id
                                        )
  
                                views = ["ocean", "sea", "mountain", "garden", "city", "pool"]
                                for view in views:
                                    if f"{view} view" in content:
                                        await self.memory_service.save_guest_preference(
                                            guest_id        = guest_id
                                            , preference_type = "view"
                                            , value           = view
                                            , thread_id       = thread_id
                                        )
            

            if guest_id and thread_id and len(messages) >= 2:
                
                last_user_msg       = None
                last_assistant_msg  = None

                for msg in reversed(messages):
                    if isinstance(msg, HumanMessage) and last_user_msg is None:
                        last_user_msg       = msg.content
                    elif isinstance(msg, AIMessage) and last_assistant_msg is None:
                        last_assistant_msg  = msg.content
                    
                    if last_user_msg and last_assistant_msg:
                        break
                
                if last_user_msg and last_assistant_msg:
                    exchange        = f"User: {last_user_msg}\nAssistant: {last_assistant_msg}"
                    await self.memory_service.save_interaction_memory(
                        thread_id   = thread_id
                        , content   = exchange
                        , guest_id = guest_id
                    )   
            
            return {"context": context}
            
        except Exception as e:
            logger.error(f"Error processing tool results: {str(e)}")
            return state

    