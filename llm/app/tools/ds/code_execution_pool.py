import multiprocessing as mp
from multiprocessing import Queue
import time
from typing import Dict, Any
import atexit

from app import logger


class CodeExecutionPool:

    _instance = None
    _pool = None
    _pool_size = 2

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._pool is None:
            self._initialize_pool()

    def _initialize_pool(self):
        try:
            self._pool = mp.Pool(
                processes       = self._pool_size
                , initializer   = self._worker_init
                , maxtasksperchild= 50
            )

            atexit.register(self._cleanup_pool)
            logger.info(f"Initialized code execution pool with {self._pool_size} workers")

        except Exception as e:
            logger.error(f"Failed to initialize pool: {str(e)}")
            self._pool = None

    @staticmethod
    def _worker_init():
        import sys
        import io

        try:
            import matplotlib
            matplotlib.use('Agg', force=True)
            import matplotlib.pyplot as plt
            plt.ioff()

            import numpy as np
            import pandas as pd
            import scipy.stats
            import seaborn as sns

            logger.info(f"Worker {mp.current_process().pid} initialized with pre-loaded libraries")

        except Exception as e:
            logger.error(f"Worker initialization failed: {str(e)}")

    def execute_with_pool(
        self
        , execute_func
        , code          : str
        , result_queue  : Queue
        , plot_path     : str
        , timeout       : int = 30
    ) -> Dict[str, Any]:
        if self._pool is None:
            logger.warning("Pool not available, falling back to direct execution")
            return None

        try:
            async_result = self._pool.apply_async(
                execute_func
                , args=(code, result_queue, plot_path)
            )

            async_result.wait(timeout=timeout)

            if async_result.ready():
                return {"success": True}
            else:
                logger.warning("Pool execution timed out")
                return {"success": False, "timeout": True}

        except mp.TimeoutError:
            logger.error("Pool execution timeout")
            return {"success": False, "timeout": True}

        except Exception as e:
            logger.error(f"Pool execution error: {str(e)}")
            return {"success": False, "error": str(e)}

    def _cleanup_pool(self):
        if self._pool is not None:
            try:
                self._pool.close()
                self._pool.join(timeout=5)
                self._pool.terminate()
                logger.info("Code execution pool cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up pool: {str(e)}")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
