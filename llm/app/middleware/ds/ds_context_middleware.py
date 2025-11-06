from typing import Dict, Any
from uuid import uuid4

from langchain.agents.middleware import AgentMiddleware

from app.states.ds_agent_state import DSAgentState
from app import logger

class DSContextMiddleware(AgentMiddleware):
    def __init__(self):
        super().__init__()

    def before_model(self, state: DSAgentState, runtime) -> Dict[str, Any] | None:
        try:
            thread_id = None
            if runtime and runtime.context:
                thread_id = runtime.context.get("thread_id", str(uuid4()))
            else:
                thread_id = str(uuid4())

            context = state.get("context", {}) if state else {}

            loaded_datasets         = state.get("loaded_datasets", {})
            code_history            = state.get("code_history", [])
            active_variables        = state.get("active_variables", [])
            last_successful_code    = state.get("last_successful_code", "")

            dataset_summary = []
            for filepath, info in loaded_datasets.items():
                shape   = info.get("shape", "unknown")
                cols    = len(info.get("columns", []))
                dataset_summary.append(f"📊 {filepath} - Shape: {shape}, Columns: {cols}")

            datasets_context = "\n".join(dataset_summary) if dataset_summary else "No datasets loaded in this session"

            code_history_summary = ""
            if code_history:
                recent_count = min(len(code_history), 3)
                code_history_summary = f"{len(code_history)} code executions in history (showing last {recent_count})"

            variables_context = ""
            if active_variables:
                variables_context = f"Active variables: {', '.join(active_variables)}"

            enhanced_context = {
                **context
                , "loaded_datasets_summary" : datasets_context
                , "code_history_summary"    : code_history_summary
                , "active_variables_summary": variables_context
                , "has_code_history"        : len(code_history) > 0
            }

            return {
                "thread_id" : thread_id
                , "context" : enhanced_context
            }

        except Exception as e:
            logger.error(f"Error preparing context: {str(e)}")
            return {"context": state.get("context", {}) if state else {}}
