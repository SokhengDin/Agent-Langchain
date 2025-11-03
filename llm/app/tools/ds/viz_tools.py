from typing import Dict, List, Optional, Annotated
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from app import logger
from app.core.config import settings

class VizTools:
    """Tools for data visualization"""

    @staticmethod
    @tool("create_histogram")
    async def create_histogram(
        file_path   : str
        , column    : str
        , bins      : int = 30
        , output_path: Optional[str] = None
        , state     : Annotated[Dict, InjectedState] = None
    ) -> Dict:
        """
        Create histogram for a column

        Args:
            file_path   : Path to data file
            column      : Column name
            bins        : Number of bins
            output_path : Path to save plot (auto-generated if None)

        Returns:
            Dict with plot path
        """
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            if output_path is None:
                output_dir = Path("output/plots")
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = str(output_dir / f"histogram_{column}.png")

            plt.figure(figsize=(10, 6))
            plt.hist(df[column].dropna(), bins=bins, edgecolor='black')
            plt.xlabel(column)
            plt.ylabel('Frequency')
            plt.title(f'Histogram of {column}')
            plt.grid(True, alpha=0.3)
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()

            filename = Path(output_path).name
            file_url = f"{settings.FRONT_API_BASE_URL}/api/v2/files/plots/{filename}"

            logger.info(f"Histogram saved: {output_path}")

            return {
                "status"    : 200
                , "message" : "Histogram created"
                , "data"    : {
                    "plot_path": output_path
                    , "file_url": file_url
                }
            }

        except Exception as e:
            logger.error(f"Error creating histogram: {str(e)}")
            return {
                "status"    : 500
                , "message" : f"Failed to create histogram: {str(e)}"
                , "data"    : None
            }

    @staticmethod
    @tool("create_scatter_plot")
    async def create_scatter_plot(
        file_path   : str
        , x_column  : str
        , y_column  : str
        , output_path: Optional[str] = None
        , state     : Annotated[Dict, InjectedState] = None
    ) -> Dict:
        """
        Create scatter plot

        Args:
            file_path   : Path to data file
            x_column    : X-axis column
            y_column    : Y-axis column
            output_path : Path to save plot

        Returns:
            Dict with plot path
        """
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            if output_path is None:
                output_dir = Path("output/plots")
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = str(output_dir / f"scatter_{x_column}_vs_{y_column}.png")

            plt.figure(figsize=(10, 6))
            plt.scatter(df[x_column], df[y_column], alpha=0.6)
            plt.xlabel(x_column)
            plt.ylabel(y_column)
            plt.title(f'{y_column} vs {x_column}')
            plt.grid(True, alpha=0.3)
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()

            filename = Path(output_path).name
            file_url = f"{settings.FRONT_API_BASE_URL}/api/v2/files/plots/{filename}"

            logger.info(f"Scatter plot saved: {output_path}")
            logger.debug(f"Scatter plot URL: {file_url}")

            return {
                "status"    : 200
                , "message" : "Scatter plot created"
                , "data"    : {
                    "plot_path": output_path
                    , "file_url": file_url
                }
            }

        except Exception as e:
            logger.error(f"Error creating scatter plot: {str(e)}")
            return {
                "status"    : 500
                , "message" : f"Failed to create scatter plot: {str(e)}"
                , "data"    : None
                , "file_url": file_url
            }

    @staticmethod
    @tool("create_correlation_heatmap")
    async def create_correlation_heatmap(
        file_path   : str
        , columns   : Optional[List[str]] = None
        , output_path: Optional[str] = None
        , state     : Annotated[Dict, InjectedState] = None
    ) -> Dict:
        """
        Create correlation heatmap

        Args:
            file_path   : Path to data file
            columns     : Optional column list
            output_path : Path to save plot

        Returns:
            Dict with plot path
        """
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            if columns:
                df = df[columns]
            else:
                df = df.select_dtypes(include=['number'])

            if output_path is None:
                output_dir = Path("output/plots")
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = str(output_dir / "correlation_heatmap.png")

            plt.figure(figsize=(12, 10))
            sns.heatmap(df.corr(), annot=True, fmt='.2f', cmap='coolwarm', center=0)
            plt.title('Correlation Heatmap')
            plt.tight_layout()
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()

            filename = Path(output_path).name
            file_url = f"{settings.FRONT_API_BASE_URL}/api/v2/files/plots/{filename}"

            logger.info(f"Heatmap saved: {output_path}")

            return {
                "status"    : 200
                , "message" : "Heatmap created"
                , "data"    : {
                    "plot_path": output_path
                    , "file_url": file_url
                }
            }

        except Exception as e:
            logger.error(f"Error creating heatmap: {str(e)}")
            return {
                "status"    : 500
                , "message" : f"Failed to create heatmap: {str(e)}"
                , "data"    : None
            }

    @staticmethod
    @tool("create_box_plot")
    async def create_box_plot(
        file_path   : str
        , column    : str
        , output_path: Optional[str] = None
        , state     : Annotated[Dict, InjectedState] = None
    ) -> Dict:
        """
        Create box plot for outlier detection

        Args:
            file_path   : Path to data file
            column      : Column name
            output_path : Path to save plot

        Returns:
            Dict with plot path and outlier info
        """
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            if output_path is None:
                output_dir = Path("output/plots")
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = str(output_dir / f"boxplot_{column}.png")

            data = df[column].dropna()
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            outliers = data[(data < Q1 - 1.5 * IQR) | (data > Q3 + 1.5 * IQR)]

            plt.figure(figsize=(10, 6))
            plt.boxplot(data, vert=False)
            plt.xlabel(column)
            plt.title(f'Box Plot of {column}')
            plt.grid(True, alpha=0.3)
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()

            filename = Path(output_path).name
            file_url = f"{settings.FRONT_API_BASE_URL}/api/v2/files/plots/{filename}"

            logger.info(f"Box plot saved: {output_path}")

            return {
                "status"    : 200
                , "message" : "Box plot created"
                , "data"    : {
                    "plot_path": output_path
                    , "file_url": file_url
                    , "outlier_count": len(outliers)
                    , "outlier_percentage": round(len(outliers) / len(data) * 100, 2)
                }
            }

        except Exception as e:
            logger.error(f"Error creating box plot: {str(e)}")
            return {
                "status"    : 500
                , "message" : f"Failed to create box plot: {str(e)}"
                , "data"    : None
            }
