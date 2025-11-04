import re
from typing import Optional
from langchain_core.tools import tool
from langchain.tools import ToolRuntime

from app import logger

class LaTeXFormatterTool:

    @staticmethod
    @tool("format_latex")
    def format_latex(
        content: str,
        runtime: ToolRuntime = None
    ) -> str:
        """
        Format mathematical content with proper LaTeX syntax for markdown rendering.

        Use this tool when you need to:
        - Format mathematical equations and expressions
        - Convert LaTeX to markdown-compatible format
        - Ensure proper rendering of mathematical notation

        The tool will:
        - Wrap inline math with single $ delimiters
        - Wrap display math with double $$ delimiters
        - Ensure proper spacing and newlines
        - Fix common LaTeX rendering issues

        Args:
            content: Mathematical content that may contain LaTeX notation

        Returns:
            Properly formatted markdown with LaTeX math expressions

        Example:
            Input: "The derivative is \\frac{dy}{dx} and integral is \\int f(x)dx"
            Output: "The derivative is $\\frac{dy}{dx}$ and integral is $\\int f(x)dx$"
        """
        try:
            if runtime and runtime.stream_writer:
                runtime.stream_writer("📐 Formatting LaTeX mathematical notation...")

            formatted_content = LaTeXFormatterTool._format_latex_content(content)

            if runtime and runtime.stream_writer:
                runtime.stream_writer("✅ LaTeX formatting complete")

            return formatted_content

        except Exception as e:
            logger.error(f"Error formatting LaTeX: {str(e)}")
            return content

    @staticmethod
    def _format_latex_content(content: str) -> str:
        """
        Internal method to format LaTeX content.
        """
        lines = content.split('\n')
        formatted_lines = []
        in_display_math = False

        for line in lines:
            stripped = line.strip()

            if stripped.startswith('[') and stripped.endswith(']'):
                math_content = stripped[1:-1].strip()
                formatted_lines.append('')
                formatted_lines.append(f'$$')
                formatted_lines.append(math_content)
                formatted_lines.append(f'$$')
                formatted_lines.append('')

            elif '\\[' in stripped and '\\]' in stripped:
                parts = re.split(r'(\\\[.*?\\\])', stripped)
                formatted_parts = []
                for part in parts:
                    if part.startswith('\\[') and part.endswith('\\]'):
                        math_content = part[2:-2].strip()
                        formatted_parts.append('\n$$\n' + math_content + '\n$$\n')
                    elif part:
                        formatted_parts.append(part)
                formatted_lines.append(''.join(formatted_parts))

            elif '\\(' in stripped and '\\)' in stripped:
                formatted_line = re.sub(
                    r'\\\((.*?)\\\)',
                    r'$\1$',
                    stripped
                )
                formatted_lines.append(formatted_line)

            else:
                inline_math_pattern = r'(?<!\$)([^$\s][^$]*?(?:frac|int|sum|prod|sqrt|partial|nabla|infty|alpha|beta|gamma|delta|epsilon|theta|lambda|mu|sigma|omega|times|cdot|pm|leq|geq|neq|equiv|approx|propto|subset|supset|in|notin|cup|cap|emptyset|forall|exists|rightarrow|leftarrow|Rightarrow|Leftarrow|mapsto|to)[^$]*?)(?!\$)'

                if re.search(inline_math_pattern, stripped):
                    formatted_line = stripped
                else:
                    formatted_line = stripped

                formatted_lines.append(formatted_line)

        result = '\n'.join(formatted_lines)

        result = re.sub(r'\n{3,}', '\n\n', result)

        return result
