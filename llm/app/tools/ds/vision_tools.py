from typing import Dict, Optional, Annotated
import base64
from pathlib import Path

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langgraph.prebuilt import InjectedState

from app.core.config import settings
from app import logger

class DSVisionTools:
    """Tools for analyzing images with math problems and exercises"""

    vision_model = ChatOllama(
        base_url    = settings.OLLAMA_BASE_URL
        , model     = "qwen3-vl:8b"
        , temperature= 0.0
    )

    @staticmethod
    @tool("analyze_exercise_image")
    async def analyze_exercise_image(
        image_path  : str
        , question  : Optional[str] = None
        , state     : Annotated[Dict, InjectedState] = None
    ) -> Dict:
        """
        Analyze image containing math problems or exercises

        Args:
            image_path  : Path to image file
            question    : Optional specific question about the image

        Returns:
            Dict with analysis result
        """
        try:
            if not Path(image_path).exists():
                return {
                    "status"    : 404
                    , "message" : "Image file not found"
                    , "data"    : None
                }

            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')

            prompt = question or "Analyze this image. If it contains math problems, equations, or exercises, extract and explain them in detail."

            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_data}"}
                ]
            )

            response = await DSVisionTools.vision_model.ainvoke([message])

            logger.info(f"Analyzed exercise image: {image_path}")

            return {
                "status"    : 200
                , "message" : "Image analyzed"
                , "data"    : {
                    "image"     : image_path
                    , "analysis": response.content
                }
            }

        except Exception as e:
            logger.error(f"Error analyzing exercise image: {str(e)}")
            return {
                "status"    : 500
                , "message" : f"Failed to analyze image: {str(e)}"
                , "data"    : None
            }

    @staticmethod
    @tool("extract_math_equations")
    async def extract_math_equations(
        image_path  : str
        , state     : Annotated[Dict, InjectedState] = None
    ) -> Dict:
        """
        Extract mathematical equations from image

        Args:
            image_path: Path to image

        Returns:
            Dict with extracted equations
        """
        try:
            if not Path(image_path).exists():
                return {
                    "status"    : 404
                    , "message" : "Image file not found"
                    , "data"    : None
                }

            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')

            prompt = """Extract all mathematical equations, formulas, and expressions from this image.
Format them clearly and explain what each equation represents.
If there are step-by-step solutions shown, preserve the order and steps."""

            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_data}"}
                ]
            )

            response = await DSVisionTools.vision_model.ainvoke([message])

            logger.info(f"Extracted equations from: {image_path}")

            return {
                "status"    : 200
                , "message" : "Equations extracted"
                , "data"    : {
                    "image"     : image_path
                    , "equations": response.content
                }
            }

        except Exception as e:
            logger.error(f"Error extracting equations: {str(e)}")
            return {
                "status"    : 500
                , "message" : f"Failed to extract equations: {str(e)}"
                , "data"    : None
            }

    @staticmethod
    @tool("analyze_graph_chart")
    async def analyze_graph_chart(
        image_path  : str
        , state     : Annotated[Dict, InjectedState] = None
    ) -> Dict:
        """
        Analyze graphs, charts, or statistical plots in image

        Args:
            image_path: Path to image

        Returns:
            Dict with graph analysis
        """
        try:
            if not Path(image_path).exists():
                return {
                    "status"    : 404
                    , "message" : "Image file not found"
                    , "data"    : None
                }

            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')

            prompt = """Analyze this graph or chart image:
1. Identify the type of visualization (histogram, scatter plot, bar chart, etc.)
2. Describe the axes, labels, and units
3. Identify key patterns, trends, or insights
4. Extract numerical data if visible
5. Provide statistical interpretation"""

            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_data}"}
                ]
            )

            response = await DSVisionTools.vision_model.ainvoke([message])

            logger.info(f"Analyzed graph/chart: {image_path}")

            return {
                "status"    : 200
                , "message" : "Graph analyzed"
                , "data"    : {
                    "image"     : image_path
                    , "analysis": response.content
                }
            }

        except Exception as e:
            logger.error(f"Error analyzing graph: {str(e)}")
            return {
                "status"    : 500
                , "message" : f"Failed to analyze graph: {str(e)}"
                , "data"    : None
            }
