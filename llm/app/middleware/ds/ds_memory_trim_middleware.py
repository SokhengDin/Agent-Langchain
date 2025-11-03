from typing import Any, Dict, Optional
from langchain_core.messages import RemoveMessage, SystemMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langchain.agents.middleware import before_model
from langgraph.runtime import Runtime

from app.states.ds_agent_state import DSAgentState
from app import logger


def estimate_tokens(messages: list) -> int:
    """Rough estimate of tokens in messages (chars / 4)"""
    total_chars = 0
    for msg in messages:
        if hasattr(msg, 'content') and isinstance(msg.content, str):
            total_chars += len(msg.content)
    return total_chars // 4


@before_model
def trim_messages_middleware(
    state       : DSAgentState
    , runtime   : Runtime
) -> Optional[Dict[str, Any]]:
    """
    Trim message history to prevent context overflow.
    Optimized for gpt-oss:20b with 131K context window.
    Keeps system message and recent conversation history.
    Preserves message pairs (HumanMessage + AIMessage) to maintain context validity.
    """
    messages = state.get("messages", [])

    if not messages:
        return None

    MAX_MESSAGES = 150
    MIN_MESSAGES = 20
    MAX_TOKENS = 100000

    if len(messages) <= MIN_MESSAGES:
        return None

    system_msgs = [m for m in messages if isinstance(m, SystemMessage)]
    non_system_msgs = [m for m in messages if not isinstance(m, SystemMessage)]

    estimated_tokens = estimate_tokens(messages)

    if len(non_system_msgs) <= MAX_MESSAGES and estimated_tokens <= MAX_TOKENS:
        return None

    logger.info(
        f"Trimming messages: {len(non_system_msgs)} messages, "
        f"~{estimated_tokens} tokens -> keeping last {MAX_MESSAGES} messages"
    )

    recent_messages = non_system_msgs[-MAX_MESSAGES:]

    if recent_messages and isinstance(recent_messages[0], (AIMessage, ToolMessage)):
        for i in range(len(non_system_msgs) - MAX_MESSAGES - 1, -1, -1):
            if isinstance(non_system_msgs[i], HumanMessage):
                recent_messages.insert(0, non_system_msgs[i])
                break

    context_warning = AIMessage(
        content="📝 *I've trimmed our conversation history to maintain performance. Recent context is preserved.*"
    )

    new_messages = system_msgs + [context_warning] + recent_messages

    return {
        "messages": [
            RemoveMessage(id=REMOVE_ALL_MESSAGES),
            *new_messages
        ]
    }


@before_model
def notify_context_limit_middleware(
    state       : DSAgentState
    , runtime   : Runtime
) -> Optional[Dict[str, Any]]:
    """
    Notify user when approaching context limit without trimming yet.
    Optimized for gpt-oss:20b with 131K context window.
    This gives users awareness before automatic trimming occurs.
    """
    messages = state.get("messages", [])

    if not messages:
        return None

    WARNING_MESSAGE_THRESHOLD = 120
    WARNING_TOKEN_THRESHOLD = 80000

    non_system_msgs = [m for m in messages if not isinstance(m, SystemMessage)]
    estimated_tokens = estimate_tokens(messages)

    context_warnings = [m for m in messages if "Context notice:" in getattr(m, 'content', '')]

    if context_warnings:
        return None

    if len(non_system_msgs) >= WARNING_MESSAGE_THRESHOLD or estimated_tokens >= WARNING_TOKEN_THRESHOLD:
        logger.info(
            f"Context warning: {len(non_system_msgs)} messages, "
            f"~{estimated_tokens} tokens"
        )

        warning_msg = AIMessage(
            content=f"ℹ️ *Context notice: Our conversation is getting long ({len(non_system_msgs)} messages, ~{estimated_tokens} tokens). I'll automatically manage the history to keep our chat flowing smoothly.*"
        )

        return {
            "messages": [warning_msg]
        }

    return None
