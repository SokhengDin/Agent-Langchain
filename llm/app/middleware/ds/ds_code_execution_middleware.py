from langchain.agents.middleware import wrap_tool_call
from langchain_core.messages import ToolMessage

from app import logger


@wrap_tool_call
def handle_code_execution_feedback(request, handler):
    tool_name           = request.tool_call.get("name")

    if tool_name != "execute_python_code":
        return handler(request)

    try:
        state           = request.runtime.state
        retry_count     = state.get("code_execution_retry_count", 0)

        MAX_RETRIES     = 5
        if retry_count >= MAX_RETRIES:
            return ToolMessage(
                content         = f"Code execution failed after {MAX_RETRIES} attempts. Please simplify your code or ask for help with a different approach."
                , tool_call_id  = request.tool_call["id"]
            )

        result          = handler(request)

        if isinstance(result, ToolMessage):
            content     = result.content

            if isinstance(content, dict):
                status  = content.get("status", 200)

                if status == 500:
                    state["code_execution_retry_count"] = retry_count + 1

                    error_data  = content.get("data", {})
                    error_msg   = error_data.get("error", "Unknown error")
                    traceback   = error_data.get("traceback", "")

                    feedback_message = f"""Code execution failed with error (Attempt {retry_count + 1}/{MAX_RETRIES}):

Error Type: {error_msg}

Full Traceback:
{traceback}

You MUST now:
1. Analyze the error type and traceback carefully
2. Identify the exact issue (syntax error, runtime error, logic error, etc.)
3. Fix the code based on the error message
4. Call execute_python_code again with the corrected code
5. You have {MAX_RETRIES - retry_count - 1} attempts remaining

Common fixes:
- SyntaxError: Check for missing parentheses, brackets, quotes, colons, or indentation
- NameError: Define missing variables or fix typos
- TypeError: Convert types or use correct operations
- ValueError: Use valid values or add validation
- ImportError: Use pre-imported libraries (np, pd, plt, scipy, stats, sns, sympy, math, random)
- IndexError/KeyError: Check array bounds or dictionary keys
- AttributeError: Use correct method or attribute names
- ZeroDivisionError: Add zero checks before division

Do NOT give up. Fix the error and retry now."""

                    return ToolMessage(
                        content         = feedback_message
                        , tool_call_id  = request.tool_call["id"]
                    )
                else:
                    state["code_execution_retry_count"] = 0

        return result

    except Exception as e:
        logger.error(f"Error in code execution middleware: {str(e)}")
        return ToolMessage(
            content         = f"Middleware error: {str(e)}. Please retry the operation."
            , tool_call_id  = request.tool_call["id"]
        )
