from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain_core.prompts import ChatPromptTemplate

from app.core.utils.hotel_utils import HotelUtils

from app import logger


def create_dynamic_prompt(prompt_template: ChatPromptTemplate):

    @dynamic_prompt
    async def generate_system_prompt(request: ModelRequest) -> str:
        """Generate dynamic system prompt with hotel context"""
        try:
            # Get hotel data
            hotel_response = await HotelUtils.get_all_hotel_name()

            if not hotel_response or not isinstance(hotel_response, dict):
                logger.error("No hotel data received from API")
                hotel_data = {
                    "name"          : "Unknown Hotel"
                    , "address"     : "N/A"
                    , "city"        : "N/A"
                    , "postal_code" : "N/A"
                    , "phone_number": "N/A"
                    , "email"       : "N/A"
                    , "total_rooms" : 0
                    , "star_rating" : 0
                    , "description" : "N/A"
                }
            else:
                data = hotel_response.get("data", [])
                if not data or len(data) == 0:
                    logger.error("No hotel data in response")
                    hotel_data = {
                        "name"          : "Unknown Hotel"
                        , "address"     : "N/A"
                        , "city"        : "N/A"
                        , "postal_code" : "N/A"
                        , "phone_number": "N/A"
                        , "email"       : "N/A"
                        , "total_rooms" : 0
                        , "star_rating" : 0
                        , "description" : "N/A"
                    }
                else:
                    hotel_data = data[0]

            # Format recall memories
            recall_memories = request.state.get("recall_memories", [])
            recall_str = (
                "<recall_memory>\n"
                + "\n".join(recall_memories)
                + "\n</recall_memory>"
                if recall_memories
                else "No previous memories found."
            )

            tool_descriptions = []
            for tool in request.tools:
                tool_info = [
                    f"## {tool.name}",
                    f"Description: {tool.description}",
                ]

                if hasattr(tool, 'args_schema') and tool.args_schema:
                    try:
                        schema      = tool.args_schema.schema()
                        properties  = schema.get('properties', {})
                        required    = schema.get('required', [])

                        if properties:
                            tool_info.append("Parameters:")
                            for param_name, param_info in properties.items():
                                param_type = param_info.get('type', 'any')
                                param_desc = param_info.get('description', 'No description')
                                is_required = "(required)" if param_name in required else "(optional)"
                                tool_info.append(f"  - {param_name} ({param_type}) {is_required}: {param_desc}")
                    except Exception as e:
                        logger.warning(f"Could not extract schema for tool {tool.name}: {str(e)}")

                tool_descriptions.append("\n".join(tool_info))

            formatted_tools = "\n\n".join(tool_descriptions) if tool_descriptions else "No tools available"

            # Generate prompt using template
            prompt_messages = prompt_template.format_messages(
                tools               = formatted_tools
                , hotel_name        = hotel_data['name']
                , hotel_address     = hotel_data['address']
                , hotel_city        = hotel_data['city']
                , hotel_postal_code = hotel_data['postal_code']
                , hotel_phone_number= hotel_data['phone_number']
                , hotel_email       = hotel_data['email']
                , hotel_total_rooms = hotel_data['total_rooms']
                , hotel_star_rating = hotel_data['star_rating']
                , hotel_description = hotel_data['description']
                , context           = request.state.get("context", {})
                , recall_memories   = recall_str
            )

            # Extract system prompt from messages
            if prompt_messages and len(prompt_messages) > 0:
                return prompt_messages[0].content

            return "You are a helpful hotel booking assistant."

        except Exception as e:
            logger.error(f"Error generating system prompt: {str(e)}")
            return "You are a helpful hotel booking assistant."

    return generate_system_prompt
