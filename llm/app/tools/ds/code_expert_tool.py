from typing import Dict, Any

from langchain_core.tools import tool
from langchain.tools import ToolRuntime

from app.agents.code_expert_agent import CodeExpertAgent
from app.states.ds_agent_state import DSAgentState
from app import logger


code_expert_agent = CodeExpertAgent()


class CodeExpertTools:

    @staticmethod
    @tool("code_expert")
    async def code_expert(
        task        : str
        , runtime   : ToolRuntime[None, DSAgentState] = None
    ) -> str:
        """
        Expert Python programmer for data science and machine learning code generation.
        Use this when you need to write complex Python code for:
        - Data analysis and manipulation
        - Statistical analysis and hypothesis testing
        - Machine learning model training and evaluation
        - Data visualization and plotting
        - Scientific computing and numerical analysis
        - Feature engineering and preprocessing
        - Time series analysis
        - Any complex Python programming task

        The expert will write clean, optimized, production-ready code with proper error handling.

        Args:
            task: Detailed description of the coding task

        Returns:
            Generated Python code ready to execute
        """
        try:
            if runtime and runtime.stream_writer:
                runtime.stream_writer("🤖 Code expert is analyzing the task...")

            logger.info(f"Code expert task: {task[:100]}...")

            code = code_expert_agent.generate_code(task)

            if runtime and runtime.stream_writer:
                runtime.stream_writer("✅ Code expert generated the solution")

            logger.info(f"Code expert generated {len(code)} chars of code")

            return code

        except Exception as e:
            logger.error(f"Error in code expert: {str(e)}")

            if runtime and runtime.stream_writer:
                runtime.stream_writer(f"❌ Code expert error: {str(e)}")

            return f"Error generating code: {str(e)}"
