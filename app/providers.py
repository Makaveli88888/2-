from dataclasses import dataclass

from openai import OpenAI

from app.config import Settings


@dataclass
class ModelReply:
    content: str | None
    tool_calls: list
    raw_message: object
    provider: str


class HybridProvider:
    """OpenAI-compatible provider router: OpenAI primary, xAI fallback."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.clients: list[tuple[str, OpenAI, str]] = []
        if settings.openai_api_key:
            self.clients.append(("openai", OpenAI(api_key=settings.openai_api_key), settings.openai_model))
        if settings.xai_api_key:
            self.clients.append(("xai", OpenAI(api_key=settings.xai_api_key, base_url="https://api.x.ai/v1"), settings.xai_model))
        if settings.ai_provider == "openai":
            self.clients = [item for item in self.clients if item[0] == "openai"]
        elif settings.ai_provider == "xai":
            self.clients = [item for item in self.clients if item[0] == "xai"]
        elif settings.ai_provider != "hybrid":
            raise ValueError("AI_PROVIDER must be hybrid, openai, or xai")

    def complete(self, messages: list[dict], tools: list, tool_choice: str = "auto"):
        if not self.clients:
            raise RuntimeError("Brak skonfigurowanego klucza OPENAI_API_KEY lub XAI_API_KEY.")
        failures = []
        for name, client, model in self.clients:
            try:
                response = client.chat.completions.create(
                    model=model, messages=messages, tools=tools, tool_choice=tool_choice
                )
                return response.choices[0].message, name
            except Exception as exc:
                failures.append(f"{name}: {type(exc).__name__}")
        raise RuntimeError("Wszyscy skonfigurowani dostawcy AI są niedostępni: " + "; ".join(failures))
