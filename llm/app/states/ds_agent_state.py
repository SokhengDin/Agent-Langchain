from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict, Annotated, NotRequired

from langgraph.graph.message import add_messages

class DSAgentState(TypedDict):

    messages                : Annotated[list, add_messages]
    current_tool            : NotRequired[str]

    thread_id               : NotRequired[str]
    dataset_id              : NotRequired[str]

    uploaded_files          : NotRequired[List[str]]
    current_dataframe       : NotRequired[str]

    context                 : NotRequired[Dict[str, Any]]
    api_base_url            : NotRequired[str]

    code_execution_count    : NotRequired[int]
    code_execution_retry_count : NotRequired[int]

    # Code persistence and reuse
    code_history            : NotRequired[List[Dict[str, Any]]]  # Track all executed code with results
    last_successful_code    : NotRequired[str]                   # Most recent working code
    loaded_datasets         : NotRequired[Dict[str, Dict]]       # {file_path: {shape, columns, dtypes}}
    computed_results        : NotRequired[Dict[str, Any]]        # Cache for analysis results
    active_variables        : NotRequired[List[str]]             # Track conceptual variables in memory
