from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from scipy import stats as sp_stats

from langchain_core.tools import tool
from langchain.tools import ToolRuntime

from app import logger
from app.states.ds_agent_state import DSAgentState

class StatsTools:

    @staticmethod
    @tool("correlation_analysis")
    async def correlation_analysis(
        file_path   : str
        , columns   : Optional[List[str]] = None
        , runtime   : ToolRuntime[None, DSAgentState] = None
    ) -> Dict:
        """
        Calculate correlation matrix for numeric columns

        Args:
            file_path   : Path to data file
            columns     : Optional list of columns (default: all numeric)

        Returns:
            Dict with correlation matrix
        """
        try:
            if runtime and runtime.stream_writer:
                runtime.stream_writer("📊 Calculating correlations...")

            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            if columns:
                df = df[columns]
            else:
                df = df.select_dtypes(include=[np.number])

            corr = df.corr()

            if runtime and runtime.stream_writer:
                runtime.stream_writer(f"✅ Analyzed {len(corr.columns)} columns")

            return {
                "status"    : 200
                , "message" : "Correlation calculated"
                , "data"    : {
                    "correlation_matrix": corr.to_dict()
                    , "columns": corr.columns.tolist()
                }
            }

        except Exception as e:
            logger.error(f"Error in correlation analysis: {str(e)}")
            if runtime and runtime.stream_writer:
                runtime.stream_writer(f"❌ Failed: {str(e)}")
            return {
                "status"    : 500
                , "message" : f"Failed correlation analysis: {str(e)}"
                , "data"    : None
            }

    @staticmethod
    @tool("hypothesis_test")
    async def hypothesis_test(
        file_path   : str
        , column    : str
        , test_type : str
        , value     : Optional[float] = None
        , runtime   : ToolRuntime[None, DSAgentState] = None
    ) -> Dict:
        """
        Perform hypothesis testing

        Args:
            file_path   : Path to data file
            column      : Column name
            test_type   : Type of test ('t-test', 'normality')
            value       : Test value for t-test

        Returns:
            Dict with test results
        """
        try:
            if runtime and runtime.stream_writer:
                runtime.stream_writer(f"🧪 Running {test_type} on '{column}'...")

            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            data = df[column].dropna()

            if test_type == 't-test' and value is not None:
                t_stat, p_value = sp_stats.ttest_1samp(data, value)
                result = {
                    "test"      : "One-sample t-test"
                    , "t_stat"  : float(t_stat)
                    , "p_value" : float(p_value)
                    , "mean"    : float(data.mean())
                    , "test_value": value
                }
            elif test_type == 'normality':
                k2, p_value = sp_stats.normaltest(data)
                result = {
                    "test"      : "Normality test"
                    , "statistic": float(k2)
                    , "p_value" : float(p_value)
                    , "normal"  : p_value > 0.05
                }
            else:
                if runtime and runtime.stream_writer:
                    runtime.stream_writer(f"❌ Invalid test type: {test_type}")
                return {
                    "status"    : 400
                    , "message" : "Invalid test type"
                    , "data"    : None
                }

            if runtime and runtime.stream_writer:
                runtime.stream_writer(f"✅ Test complete (p-value: {result.get('p_value', 'N/A'):.4f})")

            return {
                "status"    : 200
                , "message" : "Test completed"
                , "data"    : result
            }

        except Exception as e:
            logger.error(f"Error in hypothesis test: {str(e)}")
            if runtime and runtime.stream_writer:
                runtime.stream_writer(f"❌ Failed: {str(e)}")
            return {
                "status"    : 500
                , "message" : f"Failed hypothesis test: {str(e)}"
                , "data"    : None
            }

    @staticmethod
    @tool("distribution_analysis")
    async def distribution_analysis(
        file_path   : str
        , column    : str
        , runtime   : ToolRuntime[None, DSAgentState] = None
    ) -> Dict:
        """
        Analyze distribution of a column

        Args:
            file_path   : Path to data file
            column      : Column name

        Returns:
            Dict with distribution statistics
        """
        try:
            if runtime and runtime.stream_writer:
                runtime.stream_writer(f"📊 Analyzing distribution of '{column}'...")

            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            data = df[column].dropna()

            result = {
                "column"        : column
                , "count"       : int(len(data))
                , "mean"        : float(data.mean())
                , "median"      : float(data.median())
                , "std"         : float(data.std())
                , "variance"    : float(data.var())
                , "skewness"    : float(sp_stats.skew(data))
                , "kurtosis"    : float(sp_stats.kurtosis(data))
                , "min"         : float(data.min())
                , "max"         : float(data.max())
                , "range"       : float(data.max() - data.min())
            }

            if runtime and runtime.stream_writer:
                runtime.stream_writer(f"✅ Distribution analysis complete")

            return {
                "status"    : 200
                , "message" : "Distribution analyzed"
                , "data"    : result
            }

        except Exception as e:
            logger.error(f"Error in distribution analysis: {str(e)}")
            if runtime and runtime.stream_writer:
                runtime.stream_writer(f"❌ Failed: {str(e)}")
            return {
                "status"    : 500
                , "message" : f"Failed distribution analysis: {str(e)}"
                , "data"    : None
            }
