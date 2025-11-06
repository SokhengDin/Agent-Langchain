from typing import Dict, Optional, Any
from pathlib import Path
import sys
import io
import traceback
import ast
import multiprocessing
from multiprocessing import Process, Queue
from pydantic import BaseModel, Field

from langchain_core.tools import tool
from langchain.tools import ToolRuntime

from app import logger
from app.core.config import settings
from app.states.ds_agent_state import DSAgentState

try:
    multiprocessing.set_start_method('fork', force=False)
except RuntimeError:
    pass

MAX_EXECUTION_TIME = 30
MAX_EXECUTIONS_PER_CONVERSATION = 10


class CodeExecutionInput(BaseModel):
    code: str = Field(
        description=(
            "Python code to execute. "
            "CRITICAL: Use raw strings (r'...' or r\"...\") for ALL strings containing backslashes. "
            "Examples: "
            "plt.title(r'$\\mu$') NOT plt.title('$\\mu$'). "
            "ax.plot(x, y, label=r'$\\sigma=0.2$') NOT label='$\\sigma=0.2$'. "
            "Matplotlib labels, titles, text with LaTeX symbols MUST use raw strings. "
            "Without raw strings, the tool call will fail with JSON parsing errors."
        )
    )

    save_plot: bool = Field(
        default=True,
        description="Whether to automatically save matplotlib plots and return their URL"
    )


class CodeExecutionTools:

    @staticmethod
    def _validate_code(code: str) -> tuple[bool, Optional[str]]:
        dangerous_patterns = [
            ('os.system', 'System command execution is not allowed'),
            ('subprocess', 'Subprocess execution is not allowed'),
            ('eval(', 'eval() is not allowed for security'),
            ('exec(', 'exec() is not allowed for security'),
            ('compile(', 'compile() is not allowed for security'),
            ('__import__', 'Dynamic imports are restricted'),
            ('open(', 'Direct file operations are restricted. Use pandas.read_csv/read_excel instead'),
            ('os.remove', 'File deletion is not allowed'),
            ('os.rmdir', 'Directory deletion is not allowed'),
            ('shutil.rmtree', 'Directory deletion is not allowed'),
            ('socket', 'Network operations are not allowed'),
            ('urllib', 'Network operations are not allowed'),
            ('requests', 'Network operations are not allowed'),
            ('http', 'Network operations are not allowed'),
            ('os.fork', 'Process forking is not allowed'),
            ('os.kill', 'Process operations are not allowed'),
            ('globals()', 'Access to globals is restricted'),
            ('locals()', 'Access to locals is restricted'),
            ('vars()', 'Access to vars is restricted'),
            ('dir()', 'Access to dir is restricted'),
        ]

        code_lower = code.lower()

        for pattern, error_msg in dangerous_patterns:
            if pattern.lower() in code_lower:
                return False, f"Security violation: {error_msg}"

        try:
            ast.parse(code)
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"

        return True, None

    @staticmethod
    def _execute_in_process(code: str, result_queue: Queue, plot_path: str):
        try:
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()

            sys.stdout = stdout_capture
            sys.stderr = stderr_capture

            try:
                import plotly.graph_objects as go
                import plotly.express as px
            except ImportError:
                go = None
                px = None

            # Import matplotlib with Agg backend for headless plotting
            import matplotlib
            matplotlib.use('Agg', force=True)
            import matplotlib.pyplot as plt_exec
            import matplotlib.animation as mpl_animation
            plt_exec.ioff()

            import scipy.stats as scipy_stats

            try:
                sklearn = __import__('sklearn')
            except (ImportError, Exception):
                sklearn = None

            try:
                xgboost = __import__('xgboost')
                xgb = xgboost
            except (ImportError, Exception):
                xgboost = None
                xgb = None

            try:
                lightgbm = __import__('lightgbm')
                lgb = lightgbm
            except (ImportError, Exception):
                lightgbm = None
                lgb = None

            try:
                statsmodels = __import__('statsmodels')
                import statsmodels.api as sm_api
            except (ImportError, Exception):
                statsmodels = None
                sm_api = None

            try:
                polars = __import__('polars')
                pl = polars
            except (ImportError, Exception):
                polars = None
                pl = None

            local_vars = {
                'np'            : __import__('numpy')
                , 'pd'          : __import__('pandas')
                , 'pl'          : pl
                , 'polars'      : polars
                , 'plt'         : plt_exec
                , 'matplotlib'  : matplotlib
                , 'animation'   : mpl_animation
                , 'FuncAnimation': mpl_animation.FuncAnimation
                , 'go'          : go
                , 'px'          : px
                , 'scipy'       : __import__('scipy')
                , 'stats'       : scipy_stats
                , 'seaborn'     : __import__('seaborn')
                , 'sns'         : __import__('seaborn')
                , 'sympy'       : __import__('sympy')
                , 'sklearn'     : sklearn
                , 'xgboost'     : xgboost
                , 'xgb'         : xgb
                , 'lightgbm'    : lightgbm
                , 'lgb'         : lgb
                , 'statsmodels' : statsmodels
                , 'sm'          : sm_api
                , 'math'        : __import__('math')
                , 'random'      : __import__('random')
                , 'itertools'   : __import__('itertools')
                , 'functools'   : __import__('functools')
                , 'collections' : __import__('collections')
                , 'datetime'    : __import__('datetime')
                , 'time'        : __import__('time')
                , 're'          : __import__('re')
            }

            exec(code, local_vars, local_vars)

            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

            stdout_text = stdout_capture.getvalue()
            stderr_text = stderr_capture.getvalue()

            has_plots = len(plt_exec.get_fignums()) > 0

            if has_plots:
                plt_exec.savefig(plot_path, dpi=150, bbox_inches='tight')
                plt_exec.close('all')

            result_queue.put({
                'success': True,
                'stdout': stdout_text,
                'stderr': stderr_text,
                'has_plots': has_plots
            })

        except Exception as e:
            error_msg = traceback.format_exc()
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

            result_queue.put({
                'success': False,
                'error': str(e),
                'traceback': error_msg
            })

    @staticmethod
    @tool("execute_python_code", args_schema=CodeExecutionInput)
    def execute_python_code(
        code        : str
        , save_plot : bool = True
        , runtime   : ToolRuntime[None, DSAgentState] = None
    ) -> Dict[str, Any]:
        """
        Execute Python code with pre-imported scientific libraries using multiprocessing for safe timeout.

        Pre-imported: np, pd, pl (polars), plt, matplotlib, scipy, stats, sns, sympy, sklearn, xgb, lgb, sm (statsmodels), math, random
        Automatically saves and returns URLs for matplotlib plots.
        Max execution: 30s, 10 calls per conversation.

        Security: No system commands, file ops, network access, or dangerous functions.
        """
        logger.info("=" * 80)
        logger.info("EXECUTE_PYTHON_CODE TOOL CALLED")
        logger.info("=" * 80)
        logger.info(f"Code to execute:\n{code}")
        logger.info(f"Save plot: {save_plot}")
        logger.info("=" * 80)

        try:
            if runtime and runtime.stream_writer:
                runtime.stream_writer("🔍 Validating code for security...")

            state = runtime.state if runtime else {}
            execution_count = state.get("code_execution_count", 0)

            if execution_count >= MAX_EXECUTIONS_PER_CONVERSATION:
                return {
                    "status"    : 429
                    , "message" : "Execution limit reached"
                    , "data"    : {
                        "error"             : f"Maximum {MAX_EXECUTIONS_PER_CONVERSATION} code executions per conversation allowed"
                        , "execution_count" : execution_count
                    }
                }

            is_safe, error_msg = CodeExecutionTools._validate_code(code)
            if not is_safe:
                if runtime and runtime.stream_writer:
                    runtime.stream_writer(f"❌ Security check failed: {error_msg}")

                return {
                    "status"    : 403
                    , "message" : "Security violation"
                    , "data"    : {
                        "error" : error_msg
                        , "code": code
                    }
                }

            if runtime and runtime.stream_writer:
                runtime.stream_writer("✅ Security check passed")
                runtime.stream_writer("⚙️ Executing code...")

            output_dir = Path("output/plots")
            output_dir.mkdir(parents=True, exist_ok=True)

            import time
            timestamp       = int(time.time() * 1000)
            plot_filename   = f"code_execution_{timestamp}.png"
            plot_path       = str(output_dir / plot_filename)

            result_queue = Queue()
            process = Process(target=CodeExecutionTools._execute_in_process, args=(code, result_queue, plot_path))
            process.start()
            process.join(timeout=MAX_EXECUTION_TIME)

            if process.is_alive():
                process.terminate()
                process.join()

                if runtime and runtime.stream_writer:
                    runtime.stream_writer(f"⏱️ Execution timed out after {MAX_EXECUTION_TIME} seconds")

                return {
                    "status"    : 408
                    , "message" : "Code execution timed out"
                    , "data"    : {
                        "error"     : f"Execution exceeded {MAX_EXECUTION_TIME} seconds"
                        , "timeout" : MAX_EXECUTION_TIME
                    }
                }

            if not result_queue.empty():
                result = result_queue.get()

                if not result['success']:
                    if runtime and runtime.stream_writer:
                        runtime.stream_writer(f"❌ Execution failed: {result['error']}")

                    logger.error("=" * 80)
                    logger.error("CODE EXECUTION FAILED")
                    logger.error("=" * 80)
                    logger.error(f"Error: {result['error']}")
                    logger.error(f"Full Traceback:\n{result.get('traceback', 'No traceback available')}")
                    logger.error("=" * 80)

                    return {
                        "status"    : 500
                        , "message" : "Code execution failed"
                        , "data"    : {
                            "error"             : result['error']
                            , "traceback"       : result['traceback']
                            , "execution_count" : execution_count + 1
                        }
                    }

                if runtime and runtime.stream_writer:
                    runtime.stream_writer("✅ Code executed successfully")

                response = {
                    "status"    : 200
                    , "message" : "Code executed successfully"
                    , "data"    : {
                        "stdout"            : result['stdout'] if result['stdout'] else None
                        , "stderr"          : result['stderr'] if result['stderr'] else None
                        , "execution_count" : execution_count + 1
                    }
                }

                if save_plot and result['has_plots']:
                    file_url = f"{settings.FRONT_API_BASE_URL}/api/v2/files/plots/{plot_filename}"

                    response["data"]["plot_path"] = plot_path
                    response["data"]["file_url"] = file_url

                    if runtime and runtime.stream_writer:
                        runtime.stream_writer(f"✅ Plot saved: {file_url}")

                    logger.info(f"Plot saved from code execution: {plot_path}")

                if runtime:
                    runtime.state["code_execution_count"] = execution_count + 1

                return response

            return {
                "status"    : 500
                , "message" : "Code execution failed"
                , "data"    : {"error": "No result from execution process"}
            }

        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.error(f"Error in code execution tool: {str(e)}")
            logger.error(f"Traceback: {error_traceback}")

            if runtime and runtime.stream_writer:
                runtime.stream_writer(f"💥 Tool error: {str(e)}")

            return {
                "status"    : 500
                , "message" : f"Tool error: {str(e)}"
                , "data"    : {
                    "error"     : str(e)
                    , "traceback": error_traceback
                }
            }
