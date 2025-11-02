from langchain.agents.middleware import wrap_tool_call
from langchain_core.messages import ToolMessage

from app import logger


@wrap_tool_call
async def handle_tool_errors(request, handler):
    try:
        return await handler(request)
    except Exception as e:
        logger.error(f"Tool error: {str(e)}")
        return ToolMessage(
            content         = f"Tool error: {str(e)}. Please try again or use a different approach."
            , tool_call_id  = request.tool_call["id"]
        )
