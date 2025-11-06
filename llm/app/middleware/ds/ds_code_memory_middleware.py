from typing import Dict, Any
import time
import re

from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import ToolMessage

from app.states.ds_agent_state import DSAgentState
from app import logger


class DSCodeMemoryMiddleware(AgentMiddleware):

    def __init__(self, max_history_size: int = 20):
        super().__init__()
        self.max_history_size = max_history_size

    def after_tool(
        self
        , state     : DSAgentState
        , tool_call : Dict
        , result    : Any
        , runtime
    ) -> Dict[str, Any] | None:
        try:
            tool_name = tool_call.get("name")

            if tool_name == "execute_python_code":
                return self._track_code_execution(state, tool_call, result)

            elif tool_name in ["read_csv", "read_excel"]:
                return self._track_dataset_load(state, tool_call, result)

        except Exception as e:
            logger.error(f"Error in code memory middleware: {str(e)}")

        return None

    def _track_code_execution(
        self
        , state     : DSAgentState
        , tool_call : Dict
        , result    : Any
    ) -> Dict[str, Any] | None:
        if not result or not isinstance(result, dict):
            return None

        status = result.get("status", 500)

        if status == 200:
            code = tool_call.get("args", {}).get("code", "")
            if not code:
                return None

            history_entry = {
                "timestamp"             : time.time()
                , "code"                : code
                , "status"              : status
                , "had_output"          : bool(result.get("data", {}).get("stdout"))
                , "had_plot"            : bool(result.get("data", {}).get("file_url"))
                , "variables_mentioned" : self._extract_variable_names(code)
            }

            code_history = state.get("code_history", [])
            code_history.append(history_entry)

            if len(code_history) > self.max_history_size:
                code_history = code_history[-self.max_history_size:]

            active_vars = state.get("active_variables", [])
            new_vars    = history_entry["variables_mentioned"]
            active_vars = list(set(active_vars + new_vars))

            logger.info(f"Tracked code execution. History size: {len(code_history)}, Active vars: {active_vars}")

            return {
                "code_history"          : code_history
                , "last_successful_code": code
                , "active_variables"    : active_vars
            }

        return None

    def _track_dataset_load(
        self
        , state     : DSAgentState
        , tool_call : Dict
        , result    : Any
    ) -> Dict[str, Any] | None:
        if not result or not isinstance(result, dict):
            return None

        status = result.get("status", 500)
        if status != 200:
            return None

        data        = result.get("data", {})
        file_path   = tool_call.get("args", {}).get("file_path", "")

        if not file_path:
            return None

        dataset_info = {
            "shape"     : data.get("shape", "unknown")
            , "columns" : data.get("columns", [])
            , "dtypes"  : data.get("dtypes", {})
            , "loaded_at": time.time()
        }

        loaded_datasets                 = state.get("loaded_datasets", {})
        loaded_datasets[file_path]      = dataset_info

        logger.info(f"Tracked dataset load: {file_path} with shape {dataset_info['shape']}")

        return {
            "loaded_datasets"   : loaded_datasets
            , "current_dataframe": file_path
        }

    def _extract_variable_names(self, code: str) -> list[str]:
        assignments = re.findall(r'(\w+)\s*=', code)

        common_vars = ['df', 'data', 'X', 'y', 'model', 'results', 'fig', 'ax']
        found_vars  = [v for v in assignments if v in common_vars or v.startswith('df_')]

        return found_vars[:10]
