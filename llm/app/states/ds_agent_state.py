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
