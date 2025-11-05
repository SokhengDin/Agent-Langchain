from langchain.agents.middleware import wrap_model_call
from langchain.agents.middleware import ModelRequest, ModelResponse
from langchain_core.messages import AIMessage
from ollama._types import ResponseError
import re

from app import logger


@wrap_model_call
async def handle_json_parsing_errors(request: ModelRequest, handler) -> ModelResponse:
    try:
        return await handler(request)

    except ResponseError as e:
        error_str = str(e)

        if "error parsing tool call" in error_str and "invalid character" in error_str:
            logger.warning(f"JSON parsing error detected: {error_str}")

            match = re.search(r"invalid character '(.?)' in string escape code", error_str)
            invalid_char = match.group(1) if match else "unknown"

            feedback = f"""⚠️ JSON Parsing Error in Tool Call

Your tool call had invalid JSON formatting. The error was:
- Invalid escape sequence '\\{invalid_char}' in the JSON

**Common Cause:**
You're writing Python code with strings like 'y\\'' or labels like 'Solution of y\\' = A y'
These backslashes create invalid JSON escape sequences.

**Solutions:**
1. **Use raw strings in Python code**: r'y\\'' instead of 'y\\''
2. **For matplotlib labels/titles with special chars**: Use r'...' prefix
   - ✅ CORRECT: plt.title(r"Solution of y' = A y")
   - ❌ WRONG: plt.title("Solution of y' = A y")
   - ✅ CORRECT: plt.ylabel(r'y(t)')
   - ❌ WRONG: plt.ylabel('y(t)')

3. **Simplify strings**: Remove backslashes or apostrophes if not needed
   - Instead of: "y' = A y"
   - Use: "y_prime = A*y" or "dy/dt = A*y"

**Your Next Step:**
Please retry the tool call with:
- Raw strings (r'...') for any text with quotes, backslashes, or LaTeX
- Simpler labels without special characters
- No escape sequences in JSON strings

Try again now with the corrected formatting."""

            return ModelResponse(
                messages=[AIMessage(content=feedback)]
                , state_updates={}
            )

        raise

    except Exception as e:
        error_str = str(e)

        # Handle "No generations found in stream" gracefully
        if "No generations found in stream" in error_str:
            logger.error(f"LLM generation failed in JSON parser middleware: {error_str}")
            logger.error("This usually indicates: context overflow, model timeout, or Ollama server issue")
            # Re-raise to let the service layer handle it
            raise

        logger.error(f"Unexpected error in JSON parser middleware: {error_str}")
        raise
