from typing import Dict, Any, List
from pathlib import Path
import json
import time

from langchain_core.tools import tool
from langchain.tools import ToolRuntime

from app import logger
from app.core.config import settings
from app.states.ds_agent_state import DSAgentState


class NotebookTools:

    @staticmethod
    @tool("generate_notebook")
    async def generate_notebook(
        title: str
        , cells: List[Dict[str, Any]]
        , runtime: ToolRuntime[None, DSAgentState] = None
    ) -> Dict[str, Any]:
        """
        Generate a Jupyter notebook (.ipynb) file containing code, markdown explanations, and outputs.

        Use this tool when the user explicitly requests a notebook file for their data analysis.
        The notebook will contain all code, explanations, and can include data analysis results.

        Args:
            title: Title for the notebook (will be used as filename)
            cells: List of cell dictionaries with structure:
                [
                    {
                        "cell_type": "markdown",
                        "content": "# Analysis Overview\nThis notebook contains..."
                    },
                    {
                        "cell_type": "code",
                        "content": "import pandas as pd\ndf = pd.read_csv('data.csv')",
                        "outputs": []  # Optional: can include execution results
                    }
                ]

        Returns:
            Dict with status, message, and data containing:
            - notebook_path: Local path to saved notebook
            - file_url: Public URL to download the notebook
            - filename: Name of the generated file

        Example:
            cells = [
                {"cell_type": "markdown", "content": "# Data Analysis\nAnalyzing sales data"},
                {"cell_type": "code", "content": "import pandas as pd\ndf = pd.read_csv('sales.csv')\ndf.head()"}
            ]
            result = generate_notebook("Sales Analysis", cells)
        """
        try:
            if runtime and runtime.stream_writer:
                runtime.stream_writer("📓 Generating Jupyter notebook...")

            output_dir = Path("output/notebooks")
            output_dir.mkdir(parents=True, exist_ok=True)

            timestamp = int(time.time() * 1000)
            safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in title)
            safe_title = safe_title.replace(' ', '_')
            filename = f"{safe_title}_{timestamp}.ipynb"
            output_path = output_dir / filename

            notebook_cells = []
            for cell_data in cells:
                cell_type = cell_data.get("cell_type", "code")
                content = cell_data.get("content", "")

                cell = {
                    "cell_type": cell_type,
                    "metadata": {},
                    "source": content.split('\n') if '\n' in content else [content]
                }

                if cell_type == "code":
                    outputs = cell_data.get("outputs", [])
                    cell["execution_count"] = None
                    cell["outputs"] = outputs

                notebook_cells.append(cell)

            notebook = {
                "cells": notebook_cells,
                "metadata": {
                    "kernelspec": {
                        "display_name": "Python 3",
                        "language": "python",
                        "name": "python3"
                    },
                    "language_info": {
                        "codemirror_mode": {
                            "name": "ipython",
                            "version": 3
                        },
                        "file_extension": ".py",
                        "mimetype": "text/x-python",
                        "name": "python",
                        "nbconvert_exporter": "python",
                        "pygments_lexer": "ipython3",
                        "version": "3.12.0"
                    }
                },
                "nbformat": 4,
                "nbformat_minor": 4
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(notebook, f, indent=2, ensure_ascii=False)

            file_url = f"{settings.FRONT_API_BASE_URL}/api/v2/files/notebooks/{filename}"

            if runtime and runtime.stream_writer:
                runtime.stream_writer(f"✅ Notebook generated: {file_url}")

            logger.info(f"Notebook generated: {output_path}")

            return {
                "status": 200,
                "message": "Notebook generated successfully",
                "data": {
                    "notebook_path": str(output_path),
                    "file_url": file_url,
                    "filename": filename
                }
            }

        except Exception as e:
            logger.error(f"Error generating notebook: {str(e)}")

            if runtime and runtime.stream_writer:
                runtime.stream_writer(f"❌ Failed to generate notebook: {str(e)}")

            return {
                "status": 500,
                "message": f"Notebook generation failed: {str(e)}",
                "data": None
            }

    @staticmethod
    @tool("create_analysis_notebook")
    async def create_analysis_notebook(
        analysis_title: str
        , overview: str
        , code_blocks: List[str]
        , explanations: List[str]
        , runtime: ToolRuntime[None, DSAgentState] = None
    ) -> Dict[str, Any]:
        """
        Create a complete data analysis notebook with alternating explanations and code blocks.

        This is a convenience tool that automatically formats analysis into a proper notebook structure
        with markdown explanations followed by code blocks.

        Args:
            analysis_title: Title of the analysis (e.g., "Sales Data Analysis")
            overview: Introduction/overview text for the analysis
            code_blocks: List of code snippets to include
            explanations: List of explanations (one for each code block)

        Returns:
            Dict with notebook file URL and path

        Example:
            create_analysis_notebook(
                "Customer Segmentation",
                "This analysis explores customer segments based on purchase behavior",
                ["import pandas as pd\ndf = pd.read_csv('customers.csv')", "df.groupby('segment').mean()"],
                ["Load the customer data", "Calculate average metrics by segment"]
            )
        """
        try:
            if len(code_blocks) != len(explanations):
                return {
                    "status": 400,
                    "message": "Number of code blocks must match number of explanations",
                    "data": None
                }

            cells = [
                {
                    "cell_type": "markdown",
                    "content": f"# {analysis_title}\n\n{overview}"
                }
            ]

            for explanation, code in zip(explanations, code_blocks):
                cells.append({
                    "cell_type": "markdown",
                    "content": f"## {explanation}"
                })
                cells.append({
                    "cell_type": "code",
                    "content": code
                })

            cells.append({
                "cell_type": "markdown",
                "content": "## Conclusion\n\nThis notebook was generated to document the analysis process."
            })

            return await NotebookTools.generate_notebook(
                title=analysis_title,
                cells=cells,
                runtime=runtime
            )

        except Exception as e:
            logger.error(f"Error creating analysis notebook: {str(e)}")
            return {
                "status": 500,
                "message": f"Failed to create analysis notebook: {str(e)}",
                "data": None
            }
