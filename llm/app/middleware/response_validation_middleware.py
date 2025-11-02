from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import AIMessage, ToolMessage

from app import logger


class ResponseValidationMiddleware(AgentMiddleware):

    DATA_KEYWORDS = [
        "room", "price", "available", "booking", "reservation",
        "payment", "invoice", "review", "guest", "$", "USD"
    ]

    def after_model(self, state, runtime):
        try:
            messages = state.get("messages", [])
            if not messages:
                return None

            last_message = messages[-1]

            if not isinstance(last_message, AIMessage):
                return None

            content = last_message.content if isinstance(last_message.content, str) else ""

            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                return None

            if not content:
                return None

            has_data_keywords = any(keyword in content.lower() for keyword in self.DATA_KEYWORDS)

            if not has_data_keywords:
                return None

            recent_tool_results = False
            for msg in reversed(messages[-5:]):
                if isinstance(msg, ToolMessage):
                    recent_tool_results = True
                    break

            if not recent_tool_results:
                logger.warning(f"Potential hallucination: {content[:100]}...")

            return None

        except Exception as e:
            logger.error(f"Response validation error: {str(e)}")
            return None
