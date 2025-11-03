from typing import Dict, Optional, Annotated
from pathlib import Path
import sys
import io
import traceback
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from app import logger
from app.core.config import settings


class CodeExecutionTools:
    """Tools for executing Python code"""

    @staticmethod
    @tool("execute_python_code")
    async def execute_python_code(
        code        : str
        , save_plot : bool = True
        , state     : Annotated[Dict, InjectedState] = None
    ) -> Dict:
        """
        Execute Python code and return the output. Supports all mathematical and scientific computations.

        Pre-imported libraries available:
        - np (numpy): Numerical computing
        - pd (pandas): Data manipulation
        - plt, matplotlib: Plotting and visualization
        - scipy, stats: Scientific computing and statistics
        - seaborn, sns: Statistical data visualization
        - sympy: Symbolic mathematics
        - math: Basic math functions
        - random: Random number generation
        - itertools, functools, collections: Python utilities
        - datetime, time: Date and time handling
        - re: Regular expressions

        Args:
            code        : Python code to execute
            save_plot   : Whether to save matplotlib plots (default: True)

        Returns:
            Dict with execution results, stdout, stderr, and plot URL if generated
        """
        try:
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()

            sys.stdout = stdout_capture
            sys.stderr = stderr_capture

            local_vars = {
                'np'            : __import__('numpy'),
                'pd'            : __import__('pandas'),
                'plt'           : plt,
                'matplotlib'    : matplotlib,
                'scipy'         : __import__('scipy'),
                'stats'         : __import__('scipy.stats'),
                'seaborn'       : __import__('seaborn'),
                'sns'           : __import__('seaborn'),
                'sympy'         : __import__('sympy'),
                'math'          : __import__('math'),
                'random'        : __import__('random'),
                'itertools'     : __import__('itertools'),
                'functools'     : __import__('functools'),
                'collections'   : __import__('collections'),
                'datetime'      : __import__('datetime'),
                'time'          : __import__('time'),
                're'            : __import__('re'),
            }

            try:
                exec(code, local_vars, local_vars)
            except Exception as e:
                error_msg = traceback.format_exc()
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__

                logger.error(f"Code execution error: {error_msg}")

                return {
                    "status"    : 500
                    , "message" : "Code execution failed"
                    , "data"    : {
                        "error"     : str(e)
                        , "traceback": error_msg
                    }
                }

            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

            stdout_text = stdout_capture.getvalue()
            stderr_text = stderr_capture.getvalue()

            result = {
                "status"    : 200
                , "message" : "Code executed successfully"
                , "data"    : {
                    "stdout": stdout_text if stdout_text else None
                    , "stderr": stderr_text if stderr_text else None
                }
            }

            if save_plot and plt.get_fignums():
                output_dir = Path("output/plots")
                output_dir.mkdir(parents=True, exist_ok=True)

                import time
                timestamp       = int(time.time() * 1000)
                plot_filename   = f"code_execution_{timestamp}.png"
                output_path     = str(output_dir / plot_filename)

                plt.savefig(output_path, dpi=150, bbox_inches='tight')
                plt.close('all')

                file_url = f"{settings.FRONT_API_BASE_URL}/api/v2/files/plots/{plot_filename}"

                result["data"]["plot_path"] = output_path
                result["data"]["file_url"] = file_url

                logger.info(f"Plot saved from code execution: {output_path}")

            return result

        except Exception as e:
            logger.error(f"Error in code execution tool: {str(e)}")
            return {
                "status"    : 500
                , "message" : f"Tool error: {str(e)}"
                , "data"    : None
            }
