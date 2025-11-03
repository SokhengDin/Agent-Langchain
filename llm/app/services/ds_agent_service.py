from typing import Dict, Any, Optional
from uuid import uuid4
from pathlib import Path

from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_chroma import Chroma

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from app.tools.ds.data_tools import DataTools
from app.tools.ds.stats_tools import StatsTools
from app.tools.ds.viz_tools import VizTools
from app.tools.ds.ml_tools import MLTools
from app.tools.ds.rag_tools import DSRAGTools
from app.tools.ds.vision_tools import DSVisionTools

from app.states.ds_agent_state import DSAgentState
from app.services.ds_memory_service import DSMemoryService
from app.prompts.ds_prompt import DSPrompt

from app.middleware.ds.ds_memory_middleware import DSMemoryMiddleware
from app.middleware.ds.ds_context_middleware import DSContextMiddleware
from app.middleware.ds.ds_tool_context_middleware import DSToolContextMiddleware
from app.middleware.ds.ds_prompt_middleware import create_ds_dynamic_prompt
from app.middleware.tool_error_middleware import handle_tool_errors

from app.core.config import settings
from app import logger

class DSAgentService:
    """Data Science Agent Service for educational assistance"""

    def __init__(self):
        output_dir = Path("output")
        output_dir.mkdir(parents=True, exist_ok=True)

        self.embeddings = OllamaEmbeddings(
            base_url    = settings.OLLAMA_BASE_URL
            , model     = "llama3.1"
        )

        self.memory_store = Chroma(
            collection_name         = "ds_memories"
            , embedding_function    = self.embeddings
            , persist_directory     = str(output_dir / "ds_chromadb")
        )

        self.memory_service = DSMemoryService(self.memory_store)

        self.tools = [
            # Data tools
            DataTools.read_csv
            , DataTools.read_excel
            , DataTools.get_column_info

            # Statistics tools
            , StatsTools.correlation_analysis
            , StatsTools.hypothesis_test
            , StatsTools.distribution_analysis

            # Visualization tools
            , VizTools.create_histogram
            , VizTools.create_scatter_plot
            , VizTools.create_correlation_heatmap
            , VizTools.create_box_plot

            # ML tools
            , MLTools.train_linear_regression
            , MLTools.train_random_forest
            , MLTools.make_prediction

            # RAG tools
            , DSRAGTools.process_pdf_document
            , DSRAGTools.search_document_content
            , DSRAGTools.extract_pdf_text

            # Vision tools
            , DSVisionTools.analyze_exercise_image
            , DSVisionTools.extract_math_equations
            , DSVisionTools.analyze_graph_chart
        ]

        self.llm = ChatOllama(
            base_url    = settings.OLLAMA_BASE_URL
            , model     = "gpt-oss:20b"
            , temperature= 0.0
            , num_ctx   = 16384
            , reasoning = True
            , streaming = True
        )

        self.prompt = DSPrompt.prompt_agent()

        self.memory_middleware          = DSMemoryMiddleware(self.memory_service)
        self.context_middleware         = DSContextMiddleware()
        self.tool_context_middleware    = DSToolContextMiddleware()
        self.prompt_middleware          = create_ds_dynamic_prompt(self.prompt)

        self.agent = create_agent(
            model           = self.llm
            , tools         = self.tools
            , middleware    = [
                self.context_middleware
                , self.memory_middleware
                , self.tool_context_middleware
                , handle_tool_errors
                , self.prompt_middleware
            ]
            , state_schema  = DSAgentState
            , checkpointer  = InMemorySaver()
        )

    async def handle_conversation(
        self
        , message   : str
        , thread_id : str = None
    ) -> Dict[str, Any]:
        """Handle conversation with DS agent"""
        try:
            logger.debug(f"Handling conversation: {message}")

            thread_id = thread_id if thread_id else str(uuid4())

            state = {
                "messages"          : [HumanMessage(content=message)]
                , "dataset_id"      : None
                , "thread_id"       : thread_id
                , "recall_memories" : []
                , "current_tool"    : None
                , "uploaded_files"  : []
                , "current_dataframe": None
                , "context"         : {}
            }

            result = await self.agent.ainvoke(
                state
                , config    = {"configurable": {"thread_id": thread_id}}
                , context   = {"thread_id": thread_id}
            )

            response = result["messages"][-1].content if result["messages"] else "No response generated"

            return {
                "response"  : response
                , "thread_id": thread_id
            }

        except Exception as e:
            logger.error(f"Error handling conversation: {str(e)}")
            raise

    async def handle_conversation_stream(
        self
        , message   : str
        , thread_id : str = None
    ):
        try:
            thread_id = thread_id if thread_id else str(uuid4())

            state = {
                "messages"          : [HumanMessage(content=message)]
                , "dataset_id"      : None
                , "thread_id"       : thread_id
                , "recall_memories" : []
                , "current_tool"    : None
                , "uploaded_files"  : []
                , "current_dataframe": None
                , "context"         : {}
            }

            yield {
                "type"      : "start"
                , "thread_id": thread_id
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
                        if hasattr(token_data, 'additional_kwargs'):
                            additional = token_data.additional_kwargs
                            reasoning_content = additional.get('reasoning_content', '')

                            if reasoning_content:
                                yield {
                                    "type"      : "thinking"
                                    , "content" : reasoning_content
                                }

                        if hasattr(token_data, 'content'):
                            content = token_data.content

                            if content:
                                yield {
                                    "type"      : "token"
                                    , "content" : content
                                }

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
                                    "type"      : "tool_call"
                                    , "step"    : step
                                    , "tool_calls": [
                                        {
                                            "name"  : tc.get("name") if isinstance(tc, dict) else (tc.name if hasattr(tc, "name") else tc["name"])
                                            , "args": tc.get("args", {}) if isinstance(tc, dict) else (tc.args if hasattr(tc, "args") else (tc.get("args") or {}))
                                        }
                                        for tc in last_message.tool_calls
                                    ]
                                }

            yield {
                "type"      : "done"
                , "thread_id": thread_id
            }

        except Exception as e:
            logger.error(f"Error in conversation stream: {str(e)}")
            yield {
                "type"  : "error"
                , "error": str(e)
            }
