import os
import json
import inspect
import base64
from typing import Optional, List, Dict, Any
import aisuite as ai
from core.rpc_handler import FreeCADRPC
from prompts.printing_guidelines import get_system_requirements
from .tool_schemas import tool_schemas

SETTINGS_PATH = os.path.join(os.path.expanduser("~"), ".FreeCAD", "freecad_ai_config.json")

SUPPORTED_MODELS = {
    "Anthropic Claude 3 Sonnet": "anthropic:claude-3-5-haiku-20241022",
    "OpenAI GPT-4o": "openai:gpt-4o"
}


def encode_image(path: str, provider: str) -> dict:
    match provider:
        case "openai":
            with open(path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
            media_type = "image/png" if path.lower().endswith(".png") else "image/jpeg"
            return {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{media_type};base64,{encoded}"
                }
            }
        
        case "anthropic":
            # Anthropic does not support image_url
            with open(path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
            media_type = "image/png" if path.lower().endswith(".png") else "image/jpeg"
            return {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": encoded,
                },
            }


def load_settings() -> Dict[str, Any]:
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "r") as f:
            return json.load(f)
    return {
        "model": list(SUPPORTED_MODELS.values())[0],
        "api_key": "",
        "max_iterations": 6
    }


class FreeCADAI:
    def __init__(self):
        config = load_settings()
        self.model = config.get("model")
        self.api_key = config.get("api_key", "")
        self.max_turns = config.get("max_iterations", 6)

        self.rpc = FreeCADRPC()
        self.tools = []
        for name, fn in inspect.getmembers(self.rpc, predicate=inspect.ismethod):
            if name.startswith("_"):
                continue
            try:
                inspect.signature(fn)
                self.tools.append(fn)
            except Exception as e:
                print(f"⚠️ Skipping invalid tool: {name} ({e})")

        self.provider = self.model.split(":")[0]
        if self.provider == "openai":
            os.environ["OPENAI_API_KEY"] = self.api_key
        elif self.provider == "anthropic":
            os.environ["ANTHROPIC_API_KEY"] = self.api_key

        self.client = ai.Client({
            self.provider: {
                "api_key": self.api_key,
            }
        })
        
        self.messages = [{"role": "system", "content": get_system_requirements()}]

    async def run_auto(self, query: str, image_paths: Optional[List[str]] = None):
        content = [{"type": "text", "text": query}]
        if image_paths:
            content = [encode_image(p, self.provider) for p in image_paths if os.path.exists(p)] + content

        messages = [
            {"role": "system", "content": get_system_requirements()},
            {"role": "user", "content": content}]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools,
            max_turns=self.max_turns
        )

        # for msg in response.choices[0].intermediate_messages:
        #     print(msg)

        #     if getattr(msg, "tool_calls", None):
        #         for tool_call in msg.tool_calls:
        #             yield {
        #                 "type": "tool_call",
        #                 "tool": tool_call.function.name,
        #                 "args": json.loads(tool_call.function.arguments),
        #             }

        final = response.choices[0].message
        if final and final.content:
            yield {"type": "_", "content": final.content}


    async def run(self, query: str, image_paths: Optional[List[str]] = None):

        # Add image + text content
        user_content = [{"type": "text", "text": query}]
        if image_paths:
            user_content = [encode_image(p, self.provider) for p in image_paths if os.path.exists(p)] + user_content

        self.messages.append({"role": "user", "content": user_content})

        turn = 0

        while turn < self.max_turns:
            turn += 1

            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=tool_schemas
            )

            message = response.choices[0].message

            if message.tool_calls:
                self.messages.append({
                    "role": "assistant",
                    "tool_calls": message.tool_calls,
                    "content": message.content
                })

                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    tool_id = tool_call.id

                    yield {
                        "type": "text",
                        "content": f"🔧 Calling tool `{tool_name}`..."
                    }

                    try:
                        tool_fn = getattr(self.rpc, tool_name)
                        result = tool_fn(**tool_args)

                        self.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_id,
                            "content": str(result)
                        })

                    except Exception as e:
                        print(f"Error calling tool `{tool_name}`: {e}")
                        self.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_id,
                            "content": f"Error: {str(e)}"
                        })
                continue

            if message.content:
                final_response = message.content.strip()
                if final_response:
                    self.messages.append({"role": "assistant", "content": final_response})
                    yield {"type": "text", "content": final_response}
                break
