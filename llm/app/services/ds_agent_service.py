from typing import Dict, Any, Optional
from uuid import uuid4
from pathlib import Path

from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama

from langchain.agents import create_agent

from app.tools.ds.data_tools import DataTools
from app.tools.ds.stats_tools import StatsTools
from app.tools.ds.viz_tools import VizTools
from app.tools.ds.ml_tools import MLTools
from app.tools.ds.rag_tools import DSRAGTools
from app.tools.ds.vision_tools import DSVisionTools
from app.tools.ds.theoretical_tools import TheoreticalTools
from app.tools.ds.code_execution_tools import CodeExecutionTools
from app.tools.ds.code_expert_tool import CodeExpertTools

from app.states.ds_agent_state import DSAgentState
from app.prompts.ds_prompt import DSPrompt

from app.middleware.ds.ds_state_init_middleware import DSStateInitMiddleware
from app.middleware.ds.ds_context_middleware import DSContextMiddleware
from app.middleware.ds.ds_tool_context_middleware import DSToolContextMiddleware
from app.middleware.ds.ds_prompt_middleware import create_ds_dynamic_prompt
from app.middleware.ds.ds_memory_trim_middleware import trim_messages_middleware, notify_context_limit_middleware
from app.middleware.ds.ds_code_execution_middleware import handle_code_execution_feedback
from app.middleware.tool_error_middleware import handle_tool_errors

from app.core.config import settings
from app import logger, get_checkpointer

class DSAgentService:
    """Data Science Agent Service for educational assistance"""

    def __init__(self):
        output_dir = Path("output")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Note: Conversation memory is handled by PostgreSQL checkpointer
        # No need for separate ChromaDB memory store

        self.tools = [
            CodeExpertTools.code_expert

            , DataTools.read_csv
            , DataTools.read_excel
            , DataTools.get_column_info

            , StatsTools.correlation_analysis
            , StatsTools.hypothesis_test
            , StatsTools.distribution_analysis

            , VizTools.create_histogram
            , VizTools.create_scatter_plot
            , VizTools.create_correlation_heatmap
            , VizTools.create_box_plot

            , MLTools.train_linear_regression
            , MLTools.train_random_forest
            , MLTools.make_prediction

            , DSRAGTools.process_pdf_document
            , DSRAGTools.search_document_content
            , DSRAGTools.extract_pdf_text

            , DSVisionTools.analyze_exercise_image
            , DSVisionTools.extract_math_equations
            , DSVisionTools.analyze_graph_chart

            , TheoreticalTools.plot_normal_distribution
            , TheoreticalTools.plot_distribution

            , CodeExecutionTools.execute_python_code
        ]

        self.llm = ChatOllama(
            base_url    = settings.OLLAMA_BASE_URL
            , model     = "gpt-oss:20b"
            , temperature= 0.3
            , num_ctx   = 16384
            , reasoning = True
            , streaming = True
        )

        self.prompt = DSPrompt.prompt_agent()

        self.state_init_middleware      = DSStateInitMiddleware()
        self.context_middleware         = DSContextMiddleware()
        self.tool_context_middleware    = DSToolContextMiddleware()
        self.prompt_middleware          = create_ds_dynamic_prompt(self.prompt)

        self.agent = create_agent(
            model           = self.llm
            , tools         = self.tools
            , middleware    = [
                self.state_init_middleware
                , self.context_middleware
                , self.tool_context_middleware
                # , notify_context_limit_middleware
                # , trim_messages_middleware
                , handle_code_execution_feedback
                , handle_tool_errors
                , self.prompt_middleware
            ]
            , state_schema  = DSAgentState
            , checkpointer  = get_checkpointer()
        )

    async def handle_conversation(
        self
        , message           : str
        , thread_id         : str = None
        , uploaded_files    : list[str] = None
    ) -> Dict[str, Any]:
        """Handle conversation with DS agent"""
        try:
            logger.debug(f"Handling conversation: {message}")

            thread_id = thread_id if thread_id else str(uuid4())

            message_content = message
            if uploaded_files:
                file_list = "\n".join([f"- {f}" for f in uploaded_files])
                message_content = f"{message}\n\n📎 Uploaded files:\n{file_list}"

            config = {"configurable": {"thread_id": thread_id}}

            state = {"messages": [HumanMessage(content=message_content)]}

            if uploaded_files:
                state["uploaded_files"] = uploaded_files

            result = await self.agent.ainvoke(
                state
                , config    = config
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
        , message           : str
        , thread_id         : str = None
        , uploaded_files    : list[str] = None
    ):
        try:
            thread_id = thread_id if thread_id else str(uuid4())

            message_content = message
            if uploaded_files:
                file_list   = "\n".join([f"- {f}" for f in uploaded_files])
                message_content = f"{message}\n\n📎 Uploaded files:\n{file_list}"

            config  = {"configurable": {"thread_id": thread_id}}

            state   = {"messages": [HumanMessage(content=message_content)]}

            if uploaded_files:
                state["uploaded_files"] = uploaded_files

            yield {
                "type"      : "start"
                , "thread_id": thread_id
            }

            async for stream_mode, chunk in self.agent.astream(
                state
                , config        = config
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
            import traceback
            logger.error(f"Error in conversation stream: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            yield {
                "type"  : "error"
                , "error": str(e)
            }
