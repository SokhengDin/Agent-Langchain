from typing import Dict, Any
from pydantic import BaseModel, Field

from langchain_core.tools import tool
from langchain.tools import ToolRuntime
from langchain_ollama import ChatOllama

from app import logger
from app.core.config import settings
from app.states.ds_agent_state import DSAgentState


class CodeGenerationInput(BaseModel):
    task_description: str = Field(
        description="Clear description of what the code should do. Include requirements, constraints, and expected behavior."
    )
    language: str = Field(
        default="python"
        , description="Programming language (python, javascript, etc.)"
    )
    context: str = Field(
        default=""
        , description="Additional context like existing variables, data structures, or code that needs to integrate with this"
    )


class CodeGenerationTools:

    @staticmethod
    @tool("generate_code", args_schema=CodeGenerationInput)
    def generate_code(
        task_description    : str
        , language          : str = "python"
        , context           : str = ""
        , runtime           : ToolRuntime[None, DSAgentState] = None
    ) -> Dict[str, Any]:
        """
        Generate code using a specialized coding model (qwen3-coder:30b).

        Use this tool when you need to write code but are not confident in generating it yourself.
        The coding model excels at: data processing, algorithms, API integrations, complex logic.

        Returns generated code with explanation.
        """
        try:
            if runtime and runtime.stream_writer:
                runtime.stream_writer("🤖 Generating code with specialized coding model...")

            code_history        = runtime.state.get("code_history", []) if runtime else []
            loaded_datasets     = runtime.state.get("loaded_datasets", {}) if runtime else {}

            recent_codes = [h["code"] for h in code_history[-3:]] if code_history else []

            dataset_context = ""
            if loaded_datasets:
                dataset_info = []
                for filepath, info in loaded_datasets.items():
                    cols = info.get("columns", [])
                    dataset_info.append(f"- {filepath}: {info.get('shape', 'unknown')} with columns: {', '.join(cols[:5])}")
                dataset_context = f"\n\n🔄 LOADED DATASETS:\n" + "\n".join(dataset_info)

            recent_code_context = ""
            if recent_codes:
                recent_code_context = f"\n\n🔄 RECENT CODE EXECUTIONS (reuse patterns):\n" + "\n".join(
                    f"```python\n{code}\n```" for code in recent_codes
                )

            coder_llm = ChatOllama(
                base_url    = settings.OLLAMA_BASE_URL
                , model     = "qwen3-coder:30b"
                , temperature= 0.0
                , num_ctx   = 32768
            )

            prompt = f"""You are an expert programmer. Generate clean, efficient, well-commented code.

Task: {task_description}

Language: {language}

{f"Context: {context}" if context else ""}{dataset_context}{recent_code_context}

Requirements:
1. REUSE patterns from recent code if applicable (build incrementally, don't reinvent)
2. If dataset is already loaded (see LOADED DATASETS above), use the same file path
3. Generate ONLY executable code, no explanations before or after
4. Use best practices and proper error handling
5. For Python: use type hints
6. Make code production-ready

🚨 CRITICAL - For matplotlib/plotting code:
- NEVER use plt.show() - raises NotImplementedError in headless environment
- NEVER use fig.show() - same error
- NEVER use plt.savefig() - the execution environment handles this automatically
- Just create plots with plt.plot(), plt.bar(), etc. and leave them

Example CORRECT matplotlib code:
```python
import matplotlib.pyplot as plt
plt.plot([1,2,3], [1,4,9])
plt.title('My Plot')
# NO plt.show() or plt.savefig()!
```

Generate the code now:"""

            if runtime and runtime.stream_writer:
                runtime.stream_writer("💭 Coding model is thinking...")

            response        = coder_llm.invoke(prompt)
            generated_code  = response.content.strip()

            code_lines      = generated_code.split('\n')
            if code_lines and code_lines[0].startswith('```'):
                code_lines = code_lines[1:]
            if code_lines and code_lines[-1].startswith('```'):
                code_lines = code_lines[:-1]
            generated_code = '\n'.join(code_lines).strip()

            if runtime and runtime.stream_writer:
                runtime.stream_writer(f"✅ Generated {len(generated_code.split())} lines of code")

            logger.info(f"Generated code for task: {task_description[:100]}")

            return {
                "status"    : 200
                , "message" : "Code generated successfully"
                , "data"    : {
                    "code"              : generated_code
                    , "language"        : language
                    , "task_description": task_description
                    , "lines_of_code"   : len(generated_code.split('\n'))
                }
            }

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error generating code: {error_msg}")

            if runtime and runtime.stream_writer:
                runtime.stream_writer(f"❌ Code generation failed: {error_msg}")

            return {
                "status"    : 500
                , "message" : f"Code generation failed: {error_msg}"
                , "data"    : {
                    "error" : error_msg
                }
            }
