from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain_core.prompts import ChatPromptTemplate

from app import logger

def create_ds_dynamic_prompt(prompt_template: ChatPromptTemplate):

    @dynamic_prompt
    async def generate_system_prompt(request: ModelRequest) -> str:
        """Generate dynamic system prompt for DS agent"""
        try:
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

            prompt_messages = prompt_template.format_messages(
                tools           = formatted_tools
                , context       = request.state.get("context", {})
                , recall_memories= recall_str
                , api_base_url  = request.state.get("api_base_url", "http://localhost:8000")
            )

            if prompt_messages and len(prompt_messages) > 0:
                return prompt_messages[0].content

            return "You are a helpful data science assistant."

        except Exception as e:
            logger.error(f"Error generating system prompt: {str(e)}")
            return "You are a helpful data science assistant."

    return generate_system_prompt
