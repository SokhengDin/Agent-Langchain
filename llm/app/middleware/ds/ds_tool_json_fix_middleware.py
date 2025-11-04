import re
from langchain_core.messages import AIMessage
from ollama._types import ResponseError


def create_json_error_feedback(error: ResponseError) -> AIMessage:
    """
    Create feedback message for JSON parsing errors in tool calls.

    Parses the Ollama ResponseError and creates a helpful message to guide
    the model to retry with proper JSON escaping.
    """
    error_str = str(error)

    match = re.search(r"invalid character '(.?)' in string escape code", error_str)
    invalid_char = match.group(1) if match else "unknown"

    feedback = f"""⚠️ Tool call failed: JSON parsing error - invalid escape sequence '\\{invalid_char}'

The tool call JSON was malformed. Common causes:

❌ WRONG: Backslash before letters that aren't valid escape codes
   Example: "mu = 0" after \\n becomes "\\nmu" which is invalid

✅ CORRECT: Use raw strings in Python code or double-escape in JSON
   - In Python: r'$\\mu$' (raw string)
   - In JSON: "r'$\\\\mu$'" (escaped backslash)

For code with LaTeX/math symbols:
1. Use Python raw strings: r'...'
2. Avoid comments immediately after \\n
3. Add blank line: \\n\\n# Comment

Please retry with:
- Python raw strings for LaTeX: r'$\\mu$', r'$\\sigma$'
- Spacing around comments
- Simpler variable names if needed

Try again with corrected escaping."""

    return AIMessage(content=feedback)
