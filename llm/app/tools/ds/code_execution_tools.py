from typing import Dict, Optional, Any
from pathlib import Path
import sys
import io
import traceback
import signal
import resource
import ast
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from langchain_core.tools import tool
from langchain.tools import ToolRuntime

from app import logger
from app.core.config import settings
from app.states.ds_agent_state import DSAgentState


MAX_EXECUTION_TIME = 30
MAX_MEMORY_MB = 512
MAX_EXECUTIONS_PER_CONVERSATION = 10


class TimeoutException(Exception):
    pass


class CodeExecutionTools:

    @staticmethod
    def _timeout_handler(signum, frame):
        raise TimeoutException("Code execution timed out")

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
    def _set_resource_limits():
        try:
            max_memory_bytes = MAX_MEMORY_MB * 1024 * 1024
            resource.setrlimit(
                resource.RLIMIT_AS,
                (max_memory_bytes, max_memory_bytes)
            )
        except (ValueError, OSError) as e:
            logger.warning(f"Could not set memory limit: {e}")

    @staticmethod
    @tool("execute_python_code")
    async def execute_python_code(
        code        : str
        , save_plot : bool = True
        , runtime   : ToolRuntime[None, DSAgentState] = None
    ) -> Dict[str, Any]:
        """
        Execute Python code safely with timeout and resource limits.
        Supports mathematical and scientific computations with pre-imported libraries.

        ⚠️ SECURITY RESTRICTIONS:
        - Maximum execution time: 30 seconds
        - Maximum memory usage: 512 MB
        - No system commands, file operations, or network access
        - No eval(), exec(), or dynamic imports
        - Limited to 10 executions per conversation

        ✅ PRE-IMPORTED LIBRARIES (use directly):
        - np (numpy): Numerical computing
        - pd (pandas): Data manipulation (use for reading CSV/Excel files)
        - plt, matplotlib: Static plotting and visualization
        - animation, FuncAnimation: Matplotlib animations
        - go, px (plotly): Interactive plots (if installed)
        - scipy, stats: Scientific computing and statistics
        - seaborn, sns: Statistical data visualization
        - sympy: Symbolic mathematics
        - math: Basic math functions
        - random: Random number generation
        - itertools, functools, collections: Python utilities
        - datetime, time: Date and time handling
        - re: Regular expressions

        📊 PLOTTING & ANIMATIONS:
        Static (Matplotlib):
        - plt.figure(), plt.plot(), plt.scatter(), etc.
        - Animations: anim.save('filename.gif', writer='pillow', fps=30)

        Interactive (Plotly):
        - fig = px.scatter(df, x='col1', y='col2')
        - fig = go.Figure(data=[go.Bar(x=x, y=y)])
        - Save: fig.write_html('output/plots/filename.html')
        - Auto-generates shareable URL for HTML files

        Args:
            code        : Python code to execute (string)
            save_plot   : Whether to save matplotlib plots (default: True)

        Returns:
            Dict with status, message, and data containing:
            - stdout: Standard output from code execution
            - stderr: Standard error from code execution
            - plot_path: Local path to saved plot (if any)
            - file_url: Public URL to access plot (if any)
            - execution_count: Number of executions in this conversation
            - error: Error message (if execution failed)
            - traceback: Full error traceback (if execution failed)

        Example:
            ```python
            result = 2 + 2
            print(f"Result: {result}")
            ```

            ```python
            x = np.linspace(0, 2*np.pi, 100)
            y = np.sin(x)
            plt.plot(x, y)
            plt.title("Sine Wave")
            plt.xlabel("x")
            plt.ylabel("sin(x)")
            plt.grid(True)
            ```
        """
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

            CodeExecutionTools._set_resource_limits()

            old_handler = signal.signal(signal.SIGALRM, CodeExecutionTools._timeout_handler)
            signal.alarm(MAX_EXECUTION_TIME)

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

            import matplotlib.animation as mpl_animation
            import scipy.stats as scipy_stats

            local_vars = {
                'np'            : __import__('numpy')
                , 'pd'          : __import__('pandas')
                , 'plt'         : plt
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
                , 'math'        : __import__('math')
                , 'random'      : __import__('random')
                , 'itertools'   : __import__('itertools')
                , 'functools'   : __import__('functools')
                , 'collections' : __import__('collections')
                , 'datetime'    : __import__('datetime')
                , 'time'        : __import__('time')
                , 're'          : __import__('re')
            }

            try:
                exec(code, local_vars, local_vars)

                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)

            except TimeoutException:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__

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

            except MemoryError:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__

                if runtime and runtime.stream_writer:
                    runtime.stream_writer(f"💾 Memory limit exceeded ({MAX_MEMORY_MB}MB)")

                return {
                    "status"    : 507
                    , "message" : "Memory limit exceeded"
                    , "data"    : {
                        "error"             : f"Execution exceeded {MAX_MEMORY_MB}MB memory limit"
                        , "max_memory_mb"   : MAX_MEMORY_MB
                    }
                }

            except Exception as e:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
                error_msg = traceback.format_exc()
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__

                if runtime and runtime.stream_writer:
                    runtime.stream_writer(f"❌ Execution failed: {str(e)}")

                logger.error(f"Code execution error: {error_msg}")

                return {
                    "status"    : 500
                    , "message" : "Code execution failed"
                    , "data"    : {
                        "error"             : str(e)
                        , "traceback"       : error_msg
                        , "execution_count" : execution_count + 1
                    }
                }

            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

            stdout_text = stdout_capture.getvalue()
            stderr_text = stderr_capture.getvalue()

            if runtime and runtime.stream_writer:
                runtime.stream_writer("✅ Code executed successfully")

            result = {
                "status"    : 200
                , "message" : "Code executed successfully"
                , "data"    : {
                    "stdout"            : stdout_text if stdout_text else None
                    , "stderr"          : stderr_text if stderr_text else None
                    , "execution_count" : execution_count + 1
                }
            }

            if save_plot and plt.get_fignums():
                if runtime and runtime.stream_writer:
                    runtime.stream_writer("📊 Saving plot...")

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

                if runtime and runtime.stream_writer:
                    runtime.stream_writer(f"✅ Plot saved: {file_url}")

                logger.info(f"Plot saved from code execution: {output_path}")

            if runtime:
                from langgraph.types import Command
                return Command(
                    update={"code_execution_count": execution_count + 1},
                    result=result
                )

            return result

        except Exception as e:
            logger.error(f"Error in code execution tool: {str(e)}")

            if runtime and runtime.stream_writer:
                runtime.stream_writer(f"💥 Tool error: {str(e)}")

            return {
                "status"    : 500
                , "message" : f"Tool error: {str(e)}"
                , "data"    : None
            }
