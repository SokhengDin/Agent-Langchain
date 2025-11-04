from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict, Annotated

from langgraph.graph.message import add_messages

class DSAgentState(TypedDict):

    messages                : Annotated[list, add_messages]
    current_tool            : Optional[str]

    thread_id               : Optional[str]
    dataset_id              : Optional[str]

    uploaded_files          : Optional[List[str]]
    current_dataframe       : Optional[str]

    context                 : Optional[Dict[str, Any]]
    api_base_url            : Optional[str]

    code_execution_count    : Optional[int]
