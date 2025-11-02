import os

from typing import Dict, Any, Optional
from uuid import uuid4

from pathlib import Path
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_chroma import Chroma

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from app.tools.v2.booking_tools import BookingTools
from app.tools.v2.guest_tools import GuestTools
from app.tools.v2.hotel_tools import HotelTools
from app.tools.v2.room_tools import RoomTools
from app.tools.v2.payment_tools import PaymentTools
from app.tools.v2.invoice_tools import InvoiceTools
from app.tools.v2.review_tools import ReviewTools
from app.tools.v2.vision_tools import VisionTools
from app.tools.v2.rag_tools import RAGTools

from app.states.hotel_agent_state_v2 import HotelAgentState
from app.services.memory_service_v2 import MemoryServiceV2
from app.prompts.prompt_v2 import Prompt

from app.middleware import (
    HotelMemoryMiddleware
    , ContextMiddleware
    , handle_tool_errors
    , create_dynamic_prompt
    , ToolContextMiddleware
)

from app.core.config import settings
from app import logger


os.environ["LANGCHAIN_TRACING_V2"]  = settings.LANGSMITH_TRACING
os.environ["LANGCHAIN_ENDPOINT"]    = settings.LANGSMITH_ENDPOINT
os.environ["LANGCHAIN_API_KEY"]     = settings.LANGSMITH_API_KEY
os.environ["LANGCHAIN_PROJECT"]     = settings.LANGSMITH_PROJECT

class HotelAgentServiceV2:
    """Hotel Agent Service using LangChain 1.0 create_agent with Ollama"""

    def __init__(self):
        # Initialize output directory
        output_dir = Path("output")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize embeddings with Ollama
        self.embeddings = OllamaEmbeddings(
            base_url    = settings.OLLAMA_BASE_URL
            , model     = "llama3.1"
        )

        # Initialize memory store
        self.memory_store = Chroma(
            collection_name         = "hotel_memories"
            , embedding_function    = self.embeddings
            , persist_directory     = str(output_dir / "chromadb")
        )

        self.memory_service = MemoryServiceV2(self.memory_store)

        # Collect all tools
        self.tools          = [
            # Guest tools
            GuestTools.get_guest
            , GuestTools.update_guest

            # Hotel tools
            , HotelTools.search_hotels
            , HotelTools.get_hotel
            , HotelTools.list_hotels
            , HotelTools.get_hotel_rooms

            # Room tools
            , RoomTools.create_room
            , RoomTools.get_room
            , RoomTools.get_hotel_rooms
            , RoomTools.get_all_rooms
            , RoomTools.check_room_availability
            , RoomTools.update_room_status

            # Booking tools
            , BookingTools.create_booking
            , BookingTools.check_booking_status
            , BookingTools.update_booking_status
            , BookingTools.cancel_booking
            , BookingTools.cancel_guest_booking
            , BookingTools.get_guest_bookings
            , BookingTools.list_bookings

            # Payment tools
            , PaymentTools.create_payment
            , PaymentTools.get_payment
            , PaymentTools.get_booking_payments
            , PaymentTools.list_payments

            # Invoice tools
            , InvoiceTools.generate_invoice

            # Review tools
            , ReviewTools.create_review
            , ReviewTools.get_review
            , ReviewTools.get_hotel_reviews
            , ReviewTools.update_review
            , ReviewTools.delete_review

            # Vision tools
            , VisionTools.analyze_image
            , VisionTools.extract_receipt_info
            , VisionTools.verify_room_condition

            # RAG tools
            , RAGTools.process_pdf_receipt
            , RAGTools.search_pdf_content
            , RAGTools.extract_pdf_text
        ]

        self.llm = ChatOllama(
            base_url    = settings.OLLAMA_BASE_URL
            ,model          = "gpt-oss:20b"
            , temperature   = 0.0
            , num_ctx       = 16384  # Context window
            , reasoning     = True
            , streaming     = True
        )

        # Create prompt
        self.prompt             = Prompt.prompt_agent()

        # Initialize middleware
        self.memory_middleware          = HotelMemoryMiddleware(self.memory_service)
        self.context_middleware         = ContextMiddleware(self.memory_service)
        self.tool_context_middleware    = ToolContextMiddleware()
        self.prompt_middleware          = create_dynamic_prompt(self.prompt)

        # Create agent using LangChain 1.0
        self.agent = create_agent(
            model               = self.llm
            , tools             = self.tools
            , middleware        = [
                self.context_middleware
                , self.memory_middleware
                , self.tool_context_middleware
                , handle_tool_errors
                , self.prompt_middleware
            ]
            , state_schema      = HotelAgentState
            , checkpointer      = InMemorySaver()
        )

    async def handle_conversation(
        self
        , message       : str
        , thread_id     : str = None
        , token         : Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle a conversation with the agent"""
        try:
            logger.debug(f"Handling conversation: {message}")

            thread_id = thread_id if thread_id else str(uuid4())

            # Prepare initial state
            state = {
                "messages"          : [HumanMessage(content=message)]
                , "guest_id"        : None
                , "hotel_id"        : None
                , "room_id"         : None
                , "thread_id"       : thread_id
                , "recall_memories" : []
                , "current_tool"    : None
                , "thread_id"       : thread_id
                , "token"           : token
            }

            result      = await self.agent.ainvoke(
                state
                , config    = {"configurable": {"thread_id": thread_id}}
                , context   = {"thread_id": thread_id}
            )

            # Extract output
            response    = result["messages"][-1].content if result["messages"] else "No response generated"

            return {
                "response"      : response
                , "thread_id"   : thread_id
            }

        except Exception as e:
            logger.error(f"Error handling conversation: {str(e)}")
            raise

    async def handle_conversation_stream(
        self
        , message       : str
        , thread_id     : str = None
        , token         : Optional[str] = None
    ):
        try:
            from uuid import uuid4

            thread_id = thread_id if thread_id else str(uuid4())

            state = {
                "messages"          : [HumanMessage(content=message)]
                , "guest_id"        : None
                , "hotel_id"        : None
                , "room_id"         : None
                , "thread_id"       : thread_id
                , "recall_memories" : []
                , "current_tool"    : None
                , "token"           : token
            }

            yield {
                "type"      : "start"
                , "thread_id" : thread_id
            }

            async for stream_mode, chunk in self.agent.astream(
                state
                , config        = {"configurable": {"thread_id": thread_id}}
                , context       = {"thread_id": thread_id}
                , stream_mode   = ["messages", "updates"]
            ):
                if stream_mode == "messages":
                    token_data, metadata = chunk
                    node = metadata.get("langgraph_node")

                    if node == "model":
                        # Check for reasoning content in additional_kwargs
                        if hasattr(token_data, 'additional_kwargs'):
                            additional = token_data.additional_kwargs
                            reasoning_content = additional.get('reasoning_content', '')

                            if reasoning_content:
                                yield {
                                    "type"      : "thinking"
                                    , "content" : reasoning_content
                                }

                        # Stream regular content
                        if hasattr(token_data, 'content'):
                            content = token_data.content

                            if content:
                                yield {
                                    "type"      : "token"
                                    , "content" : content
                                }

                        # Check for token usage metadata
                        if hasattr(token_data, 'response_metadata'):
                            response_meta = token_data.response_metadata

                            if 'token_usage' in response_meta:
                                token_usage         = response_meta['token_usage']
                                completion_details  = token_usage.get('completion_tokens_details', {})
                                reasoning_tokens    = completion_details.get('reasoning_tokens', 0)

                                if reasoning_tokens > 0:
                                    yield {
                                        "type"              : "thinking_stats"
                                        , "reasoning_tokens": reasoning_tokens
                                    }

                elif stream_mode == "updates":
                    for step, data in chunk.items():
                        if 'messages' in data and len(data['messages']) > 0:
                            last_message = data['messages'][-1]

                            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                                yield {
                                    "type"          : "tool_call"
                                    , "step"        : step
                                    , "tool_calls"  : [
                                        {
                                            "name"  : tc.get("name") if isinstance(tc, dict) else (tc.name if hasattr(tc, "name") else tc["name"])
                                            , "args": tc.get("args", {}) if isinstance(tc, dict) else (tc.args if hasattr(tc, "args") else (tc.get("args") or {}))
                                        }
                                        for tc in last_message.tool_calls
                                    ]
                                }

            yield {
                "type"      : "done"
                , "thread_id" : thread_id
            }

        except Exception as e:
            logger.error(f"Error in conversation stream: {str(e)}")
            yield {
                "type"  : "error"
                , "error": str(e)
            }
