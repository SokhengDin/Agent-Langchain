import base64
from typing import Dict, Optional
from pathlib import Path

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama

from app.core.config import settings
from app import logger


class VisionTools:
    """Tools for analyzing images using vision-capable LLM"""

    @staticmethod
    def _encode_image(image_path: str) -> str:
        """Encode image to base64 string"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except Exception as e:
            logger.error(f"Failed to encode image: {str(e)}")
            raise

    @staticmethod
    @tool("analyze_image_tool")
    def analyze_image(
        image_path  : str
        , question  : Optional[str] = None
    ) -> Dict:
        """
        Analyze an image using vision-capable LLM.
        Use this tool when a user uploads an image or asks about visual content.

        Args:
            image_path: Path to the image file (supports jpg, jpeg, png, webp)
            question: Optional specific question about the image.
                     If not provided, returns a general description.

        Returns:
            Dict containing the analysis result

        Examples:
            - "What's in this image?"
            - "Can you read the text in this receipt?"
            - "Describe the room in this photo"
            - "What amenities can you see in this hotel room photo?"
        """
        try:
            image_file = Path(image_path)

            if not image_file.exists():
                return {
                    "status"    : "error"
                    , "message" : f"Image file not found: {image_path}"
                    , "data"    : None
                }

            valid_extensions = {".jpg", ".jpeg", ".png", ".webp"}
            if image_file.suffix.lower() not in valid_extensions:
                return {
                    "status"    : "error"
                    , "message" : f"Unsupported image format. Supported: {', '.join(valid_extensions)}"
                    , "data"    : None
                }

            vision_model = ChatOllama(
                base_url    = settings.OLLAMA_BASE_URL
                , model     = "llama3.2-vision:11b"
                , temperature = 0.0
            )

            prompt = question if question else "Describe this image in detail."

            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt}
                    , {
                        "type"      : "image_url"
                        , "image_url" : f"data:image/jpeg;base64,{VisionTools._encode_image(image_path)}"
                    }
                ]
            )

            response = vision_model.invoke([message])

            logger.info("Image analyzed", extra={"image_path": image_path})

            return {
                "status"    : "success"
                , "message" : "Image analyzed successfully"
                , "data"    : {
                    "analysis"  : response.content
                    , "image_path" : image_path
                    , "question": prompt
                }
            }

        except Exception as e:
            logger.error(f"Failed to analyze image: {str(e)}")
            return {
                "status"    : "error"
                , "message" : f"Failed to analyze image: {str(e)}"
                , "data"    : None
            }

    @staticmethod
    @tool("extract_receipt_info_tool")
    def extract_receipt_info(image_path: str) -> Dict:
        """
        Extract structured information from a receipt image.
        Use this when a user uploads a receipt or payment proof.

        Args:
            image_path: Path to the receipt image

        Returns:
            Dict containing extracted receipt information (total, date, items, etc.)
        """
        try:
            image_file = Path(image_path)

            if not image_file.exists():
                return {
                    "status"    : "error"
                    , "message" : f"Receipt image not found: {image_path}"
                    , "data"    : None
                }

            vision_model = ChatOllama(
                base_url    = settings.OLLAMA_BASE_URL
                , model     = "llama3.2-vision:11b"
                , temperature = 0.0
            )

            prompt = """Analyze this receipt image and extract the following information in a structured format:
1. Total amount
2. Date and time
3. Payment method (if visible)
4. Merchant/vendor name
5. List of items/services (if visible)
6. Currency
7. Receipt number/transaction ID (if visible)

Format the response as a clear, structured list."""

            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt}
                    , {
                        "type"      : "image_url"
                        , "image_url" : f"data:image/jpeg;base64,{VisionTools._encode_image(image_path)}"
                    }
                ]
            )

            response = vision_model.invoke([message])

            logger.info("Receipt info extracted", extra={"image_path": image_path})

            return {
                "status"    : "success"
                , "message" : "Receipt information extracted successfully"
                , "data"    : {
                    "extracted_info": response.content
                    , "image_path"  : image_path
                }
            }

        except Exception as e:
            logger.error(f"Failed to extract receipt info: {str(e)}")
            return {
                "status"    : "error"
                , "message" : f"Failed to extract receipt info: {str(e)}"
                , "data"    : None
            }

    @staticmethod
    @tool("verify_room_condition_tool")
    def verify_room_condition(image_path: str) -> Dict:
        """
        Verify and assess room condition from an image.
        Use this when checking room cleanliness, damage, or overall condition.

        Args:
            image_path: Path to the room image

        Returns:
            Dict containing room condition assessment
        """
        try:
            image_file = Path(image_path)

            if not image_file.exists():
                return {
                    "status"    : "error"
                    , "message" : f"Room image not found: {image_path}"
                    , "data"    : None
                }

            vision_model = ChatOllama(
                base_url    = settings.OLLAMA_BASE_URL
                , model     = "llama3.2-vision:11b"
                , temperature = 0.0
            )

            prompt = """Analyze this hotel room image and provide an assessment including:
1. Overall cleanliness (rate 1-10)
2. Visible amenities
3. Room type (single, double, suite, etc.)
4. Any visible damage or issues
5. Condition of furniture and fixtures
6. Overall impression and rating

Provide a detailed but concise assessment."""

            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt}
                    , {
                        "type"      : "image_url"
                        , "image_url" : f"data:image/jpeg;base64,{VisionTools._encode_image(image_path)}"
                    }
                ]
            )

            response = vision_model.invoke([message])

            logger.info("Room condition verified", extra={"image_path": image_path})

            return {
                "status"    : "success"
                , "message" : "Room condition verified successfully"
                , "data"    : {
                    "assessment": response.content
                    , "image_path" : image_path
                }
            }

        except Exception as e:
            logger.error(f"Failed to verify room condition: {str(e)}")
            return {
                "status"    : "error"
                , "message" : f"Failed to verify room condition: {str(e)}"
                , "data"    : None
            }
