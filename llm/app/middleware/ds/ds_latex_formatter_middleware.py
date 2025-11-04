import re
from typing import Dict, Any
from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import AIMessage

from app.states.ds_agent_state import DSAgentState
from app import logger

class DSLaTeXFormatterMiddleware(AgentMiddleware):
    """
    Automatically format LaTeX math expressions in AI responses.
    Runs after the model generates content.
    """

    def after_model(self, state: DSAgentState, runtime) -> Dict[str, Any] | None:
        try:
            if state is None or "messages" not in state:
                return None

            messages = state.get("messages", [])
            if not messages:
                return None

            last_message = messages[-1]

            if isinstance(last_message, AIMessage) and last_message.content:
                original_content = last_message.content
                formatted_content = self._format_latex(original_content)

                if formatted_content != original_content:
                    last_message.content = formatted_content
                    return {"messages": messages}

            return None

        except Exception as e:
            logger.error(f"Error formatting LaTeX: {str(e)}")
            return None

    def _format_latex(self, content: str) -> str:
        """
        Format LaTeX expressions for KaTeX rendering.
        Converts [ math ] → $$math$$ (display)
        Converts \\[ math \\] → $$math$$ (display)
        Converts \\( math \\) → $math$ (inline)
        """
        lines = content.split('\n')
        formatted_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            if stripped.startswith('[') and stripped.endswith(']') and len(stripped) > 2:
                math_content = stripped[1:-1].strip()
                if self._is_likely_math(math_content):
                    if i > 0 and formatted_lines[-1].strip():
                        formatted_lines.append('')
                    formatted_lines.append('$$')
                    formatted_lines.append(math_content)
                    formatted_lines.append('$$')
                    if i < len(lines) - 1:
                        formatted_lines.append('')
                else:
                    formatted_lines.append(line)

            elif '\\[' in line and '\\]' in line:
                formatted_line = re.sub(
                    r'\\\[(.*?)\\\]',
                    lambda m: '\n$$\n' + m.group(1).strip() + '\n$$\n',
                    line,
                    flags=re.DOTALL
                )
                formatted_lines.append(formatted_line.strip())

            elif '\\(' in line and '\\)' in line:
                formatted_line = re.sub(
                    r'\\\((.*?)\\\)',
                    r'$\1$',
                    line
                )
                formatted_lines.append(formatted_line)

            else:
                formatted_lines.append(line)

            i += 1

        result = '\n'.join(formatted_lines)
        result = re.sub(r'\n{3,}', '\n\n', result)

        return result

    def _is_likely_math(self, content: str) -> bool:
        """
        Check if content is likely a math expression.
        """
        math_indicators = [
            'frac', 'int', 'sum', 'prod', 'sqrt', 'partial', 'nabla',
            'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'theta',
            'lambda', 'mu', 'sigma', 'omega', 'pi', 'mathbf',
            'times', 'cdot', 'pm', 'leq', 'geq', 'neq', 'equiv',
            'begin{', 'end{', 'displaystyle', '^', '_', '&'
        ]

        return any(indicator in content for indicator in math_indicators)
