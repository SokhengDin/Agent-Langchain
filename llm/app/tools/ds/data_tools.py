from typing import Dict, List, Optional, Annotated
from pathlib import Path
import pandas as pd
import json

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from app import logger

class DataTools:
    """Tools for data loading and basic analysis"""

    @staticmethod
    @tool("read_csv")
    async def read_csv(
        file_path       : str
        , state         : Annotated[Dict, InjectedState]
    ) -> Dict:
        """
        Read CSV file and provide summary statistics

        Args:
            file_path: Path to CSV file

        Returns:
            Dict with data summary and preview
        """
        try:
            df = pd.read_csv(file_path)

            summary = {
                "rows"          : len(df)
                , "columns"     : len(df.columns)
                , "column_names": df.columns.tolist()
                , "dtypes"      : df.dtypes.astype(str).to_dict()
                , "missing"     : df.isnull().sum().to_dict()
                , "preview"     : df.head(5).to_dict(orient='records')
            }

            logger.info(f"Read CSV: {file_path} - {len(df)} rows, {len(df.columns)} columns")

            return {
                "status"    : 200
                , "message" : "CSV loaded successfully"
                , "data"    : summary
            }

        except Exception as e:
            logger.error(f"Error reading CSV: {str(e)}")
            return {
                "status"    : 500
                , "message" : f"Failed to read CSV: {str(e)}"
                , "data"    : None
            }

    @staticmethod
    @tool("read_excel")
    async def read_excel(
        file_path       : str
        , sheet_name    : Optional[str] = None
        , state         : Annotated[Dict, InjectedState] = None
    ) -> Dict:
        """
        Read Excel file and provide summary

        Args:
            file_path   : Path to Excel file
            sheet_name  : Optional sheet name (default: first sheet)

        Returns:
            Dict with data summary and preview
        """
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name or 0)

            summary = {
                "rows"          : len(df)
                , "columns"     : len(df.columns)
                , "column_names": df.columns.tolist()
                , "dtypes"      : df.dtypes.astype(str).to_dict()
                , "missing"     : df.isnull().sum().to_dict()
                , "preview"     : df.head(5).to_dict(orient='records')
            }

            logger.info(f"Read Excel: {file_path} - {len(df)} rows, {len(df.columns)} columns")

            return {
                "status"    : 200
                , "message" : "Excel loaded successfully"
                , "data"    : summary
            }

        except Exception as e:
            logger.error(f"Error reading Excel: {str(e)}")
            return {
                "status"    : 500
                , "message" : f"Failed to read Excel: {str(e)}"
                , "data"    : None
            }

    @staticmethod
    @tool("get_column_info")
    async def get_column_info(
        file_path   : str
        , column    : str
        , state     : Annotated[Dict, InjectedState] = None
    ) -> Dict:
        """
        Get detailed statistics for a specific column

        Args:
            file_path   : Path to data file
            column      : Column name

        Returns:
            Dict with column statistics
        """
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            if column not in df.columns:
                return {
                    "status"    : 404
                    , "message" : f"Column '{column}' not found"
                    , "data"    : None
                }

            col_data = df[column]

            stats = {
                "column"        : column
                , "dtype"       : str(col_data.dtype)
                , "count"       : int(col_data.count())
                , "missing"     : int(col_data.isnull().sum())
                , "unique"      : int(col_data.nunique())
            }

            if pd.api.types.is_numeric_dtype(col_data):
                stats.update({
                    "mean"      : float(col_data.mean())
                    , "std"     : float(col_data.std())
                    , "min"     : float(col_data.min())
                    , "max"     : float(col_data.max())
                    , "q25"     : float(col_data.quantile(0.25))
                    , "q50"     : float(col_data.quantile(0.50))
                    , "q75"     : float(col_data.quantile(0.75))
                })
            else:
                top_values = col_data.value_counts().head(5).to_dict()
                stats["top_values"] = top_values

            return {
                "status"    : 200
                , "message" : "Column info retrieved"
                , "data"    : stats
            }

        except Exception as e:
            logger.error(f"Error getting column info: {str(e)}")
            return {
                "status"    : 500
                , "message" : f"Failed to get column info: {str(e)}"
                , "data"    : None
            }
