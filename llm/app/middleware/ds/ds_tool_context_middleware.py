from typing import Dict, Any
from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import ToolMessage

from app.states.ds_agent_state import DSAgentState
from app import logger

class DSToolContextMiddleware(AgentMiddleware):

    def after_tools(self, state: DSAgentState, runtime=None) -> Dict[str, Any] | None:
        try:
            context = state.get("context", {})

            messages = state.get("messages", [])
            if not messages:
                return None

            for message in reversed(messages):
                if isinstance(message, ToolMessage):
                    tool_name = message.name if hasattr(message, 'name') else "unknown"

                    if tool_name not in context:
                        context[tool_name] = []

                    try:
                        import json
                        content_data = json.loads(message.content) if isinstance(message.content, str) else message.content

                        if isinstance(content_data, dict) and "data" in content_data:
                            context[tool_name].append(content_data["data"])
                        else:
                            context[tool_name].append(content_data)
                    except:
                        context[tool_name].append(message.content)

                    if len(context[tool_name]) > 3:
                        context[tool_name] = context[tool_name][-3:]

            return {"context": context}

        except Exception as e:
            logger.error(f"Error capturing tool context: {str(e)}")
            return None
