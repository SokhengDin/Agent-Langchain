from typing import Dict, Any
import time
import re
import hashlib
import json
import os
from pathlib import Path

from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import ToolMessage

from app.states.ds_agent_state import DSAgentState
from app import logger


class DSCodeMemoryMiddleware(AgentMiddleware):

    def __init__(self, max_history_size: int = 20):
        super().__init__()
        self.max_history_size = max_history_size

    def before_tool(
        self
        , state     : DSAgentState
        , tool_call : Dict
        , runtime
    ) -> Dict[str, Any] | None:
        try:
            tool_name = tool_call.get("name")

            if tool_name in ["correlation_analysis", "hypothesis_test", "distribution_analysis"]:
                return self._check_cached_result(state, tool_call)

        except Exception as e:
            logger.error(f"Error checking cache in code memory middleware: {str(e)}")

        return None

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

            elif tool_name in ["correlation_analysis", "hypothesis_test", "distribution_analysis"]:
                return self._cache_analysis_result(state, tool_call, result)

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

        file_hash       = self._get_file_hash(file_path)
        loaded_datasets = state.get("loaded_datasets", {})

        existing_info   = loaded_datasets.get(file_path, {})
        existing_hash   = existing_info.get("file_hash", "")

        if existing_hash and existing_hash != file_hash:
            logger.warning(f"Dataset changed: {file_path} (invalidating cache)")
            computed_results = state.get("computed_results", {})
            computed_results = {
                k: v for k, v in computed_results.items()
                if file_path not in json.dumps(k)
            }

        dataset_info = {
            "shape"     : data.get("shape", "unknown")
            , "columns" : data.get("columns", [])
            , "dtypes"  : data.get("dtypes", {})
            , "loaded_at": time.time()
            , "file_hash": file_hash
        }

        loaded_datasets[file_path] = dataset_info

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

    def _generate_cache_key(self, tool_call: Dict) -> str:
        tool_name   = tool_call.get("name", "")
        args        = tool_call.get("args", {})

        cache_data  = {
            "tool": tool_name
            , "args": {k: v for k, v in sorted(args.items())}
        }

        cache_str   = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()

    def _check_cached_result(
        self
        , state     : DSAgentState
        , tool_call : Dict
    ) -> Dict[str, Any] | None:
        cache_key       = self._generate_cache_key(tool_call)
        computed_results= state.get("computed_results", {})

        if cache_key in computed_results:
            cached = computed_results[cache_key]
            logger.info(f"Cache hit for {tool_call.get('name')}")

            return {
                "skip_tool": True
                , "result": cached["result"]
            }

        return None

    def _cache_analysis_result(
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

        cache_key           = self._generate_cache_key(tool_call)
        computed_results    = state.get("computed_results", {})

        computed_results[cache_key] = {
            "result"    : result
            , "timestamp": time.time()
        }

        logger.info(f"Cached result for {tool_call.get('name')}")

        return {"computed_results": computed_results}

    def _get_file_hash(self, file_path: str) -> str:
        try:
            path = Path(file_path)
            if not path.exists():
                return ""

            stat_info   = path.stat()
            hash_data   = f"{stat_info.st_size}_{stat_info.st_mtime}"

            return hashlib.md5(hash_data.encode()).hexdigest()

        except Exception as e:
            logger.error(f"Error getting file hash for {file_path}: {str(e)}")
            return ""
