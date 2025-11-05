from typing import Dict, Any, Optional
from uuid import uuid4
from pathlib import Path

from langchain_core.messages import HumanMessage, ToolMessage
from langchain_ollama import ChatOllama
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware, ToolCallLimitMiddleware, ToolRetryMiddleware

from app.tools.ds.data_tools import DataTools
from app.tools.ds.stats_tools import StatsTools
from app.tools.ds.viz_tools import VizTools
from app.tools.ds.ml_tools import MLTools
from app.tools.ds.rag_tools import DSRAGTools
from app.tools.ds.vision_tools import DSVisionTools
from app.tools.ds.theoretical_tools import TheoreticalTools
from app.tools.ds.code_execution_tools import CodeExecutionTools
from app.tools.ds.notebook_tools import NotebookTools

from app.states.ds_agent_state import DSAgentState
from app.prompts.ds_prompt import DSPrompt

from app.middleware.ds.ds_state_init_middleware import DSStateInitMiddleware
from app.middleware.ds.ds_context_middleware import DSContextMiddleware
from app.middleware.ds.ds_tool_context_middleware import DSToolContextMiddleware
from app.middleware.ds.ds_prompt_middleware import create_ds_dynamic_prompt
from app.middleware.ds.ds_code_execution_middleware import handle_code_execution_feedback
from app.middleware.ds.ds_json_parser_middleware import handle_json_parsing_errors
from app.middleware.tool_error_middleware import handle_tool_errors

from app.core.config import settings
from app import logger

class DSAgentService:

    def __init__(self, checkpointer: AsyncPostgresSaver):
        output_dir = Path("output")
        output_dir.mkdir(parents=True, exist_ok=True)

        self.tools = [
            DataTools.read_csv
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

            , NotebookTools.generate_notebook
            , NotebookTools.create_analysis_notebook
        ]

        self.llm = ChatOllama(
            base_url    = settings.OLLAMA_BASE_URL
            , model     = "qwen3:30b"
            , temperature= 0.0
            , num_ctx   = 131072
            , reasoning = True
            , streaming = True
        )

        # Separate LLM for summarization (smaller, faster model)
        self.summary_llm = ChatOllama(
            base_url    = settings.OLLAMA_BASE_URL
            , model     = "gemma3:4b"
            , temperature= 0.0
            , num_ctx   = 8192
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
                , handle_json_parsing_errors
                , SummarizationMiddleware(
                    model                       = self.summary_llm
                    , max_tokens_before_summary = 80000
                    , messages_to_keep          = 15
                    , summary_prefix            = "## Context from earlier:\n"
                )
                , ToolCallLimitMiddleware(
                    thread_limit=50
                    , run_limit=15
                )
                , ToolCallLimitMiddleware(
                    tool_name="execute_python_code"
                    , thread_limit=30
                    , run_limit=5
                )
                , ToolCallLimitMiddleware(
                    tool_name="analyze_exercise_image"
                    , thread_limit=10
                )
                , ToolCallLimitMiddleware(
                    tool_name="extract_math_equations"
                    , thread_limit=10
                )
                , ToolCallLimitMiddleware(
                    tool_name="analyze_graph_chart"
                    , thread_limit=10
                )
                , ToolRetryMiddleware(
                    max_retries=2
                    , backoff_factor=2.0
                    , initial_delay=1.0
                )
                , handle_code_execution_feedback
                , handle_tool_errors
                , self.prompt_middleware
            ]
            , state_schema  = DSAgentState
            , checkpointer  = checkpointer
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

            config = {
                "configurable": {"thread_id": thread_id},
                "recursion_limit": 50,  # Increase from default 25 to handle complex tasks
                "max_concurrency": 5  # Limit concurrent operations to reduce thread pressure
            }

            state = {"messages": [HumanMessage(content=message_content)]}

            if uploaded_files:
                state["uploaded_files"] = uploaded_files

            result = await self.agent.ainvoke(
                state
                , config    = config
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

            config  = {
                "configurable"          : {"thread_id": thread_id}
                , "recursion_limit"     : 50
                , "max_concurrency"     : 5  # Limit concurrent operations to reduce thread pressure
            }

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
                        if data and isinstance(data, dict) and 'messages' in data and len(data['messages']) > 0:
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

                            if isinstance(last_message, ToolMessage):
                                try:
                                    import json
                                    content = last_message.content
                                    if isinstance(content, str):
                                        content_data = json.loads(content)
                                    else:
                                        content_data = content

                                    yield {
                                        "type"      : "tool_result"
                                        , "tool_name": last_message.name if hasattr(last_message, 'name') else "unknown"
                                        , "status"  : content_data.get("status") if isinstance(content_data, dict) else None
                                        , "message" : content_data.get("message") if isinstance(content_data, dict) else str(content)
                                    }
                                except:
                                    yield {
                                        "type"      : "tool_result"
                                        , "tool_name": last_message.name if hasattr(last_message, 'name') else "unknown"
                                        , "message" : str(last_message.content)
                                    }

            yield {
                "type"      : "done"
                , "thread_id": thread_id
            }

        except Exception as e:
            import traceback
            from ollama._types import ResponseError
            from app.middleware.ds.ds_tool_json_fix_middleware import create_json_error_feedback

            logger.error(f"Error in conversation stream: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")

            if isinstance(e, ResponseError) and "error parsing tool call" in str(e):
                logger.warning("Detected Ollama tool JSON parsing error - providing feedback for retry")

                feedback_msg = create_json_error_feedback(e)
                state["messages"].append(feedback_msg)

                try:
                    async for stream_mode, chunk in self.agent.astream(
                        state
                        , config        = config
                        , stream_mode   = ["messages", "updates"]
                    ):
                        if stream_mode == "messages":
                            token_data, metadata = chunk
                            node = metadata.get("langgraph_node")

                            if node == "model" and hasattr(token_data, 'content'):
                                content = token_data.content
                                if content:
                                    yield {
                                        "type"      : "token"
                                        , "content" : content
                                    }

                    yield {
                        "type"      : "done"
                        , "thread_id": thread_id
                    }
                    return

                except Exception as retry_error:
                    logger.error(f"Retry after feedback also failed: {str(retry_error)}")
                    yield {
                        "type"  : "error"
                        , "error": f"Tool call failed even after retry: {str(retry_error)}"
                    }
                    return

            yield {
                "type"  : "error"
                , "error": str(e)
            }

