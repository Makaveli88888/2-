import json
from openai import OpenAI

from app.database import MemoryStore
from app.tools import TOOL_SCHEMAS, execute_tool


SYSTEM_PROMPT = """You are JOKER GOD AI, a capable, direct Polish-speaking assistant.
Workflow roles: ORCHESTRATOR plans; TRICKSTER explores useful options; SCEPTYK challenges
assumptions and checks tool permissions; EXECUTOR performs only allow-listed tools.
Be honest about uncertainty and completed actions. Never claim to send messages, make
purchases, or modify external systems. Ask for explicit approval before any external
side effect. Protect secrets and private data. Reply in the user's language.
"""


class JokerAgent:
    def __init__(self, store: MemoryStore, api_key: str, model: str, max_tool_rounds: int = 4):
        self.store = store
        self.api_key = api_key
        self.model = model
        self.max_tool_rounds = max(1, min(max_tool_rounds, 8))
        self.client = OpenAI(api_key=api_key) if api_key else None

    def respond(self, conversation_id: str, user_message: str) -> str:
        if not self.client:
            raise RuntimeError("Brak OPENAI_API_KEY. Skonfiguruj klucz w pliku .env.")
        if not user_message.strip():
            raise ValueError("Wiadomość nie może być pusta.")
        self.store.add_message(conversation_id, "user", user_message)
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(self.store.history(conversation_id, limit=20))

        for _ in range(self.max_tool_rounds):
            completion = self.client.chat.completions.create(
                model=self.model, messages=messages, tools=TOOL_SCHEMAS, tool_choice="auto"
            )
            answer = completion.choices[0].message
            messages.append(answer)
            if not answer.tool_calls:
                result = answer.content or "Nie udało mi się wygenerować odpowiedzi."
                self.store.add_message(conversation_id, "assistant", result)
                return result
            for call in answer.tool_calls:
                try:
                    args = json.loads(call.function.arguments or "{}")
                    result = execute_tool(call.function.name, args)
                    content = json.dumps(result, ensure_ascii=False)
                except Exception as exc:
                    content = json.dumps({"error": str(exc)}, ensure_ascii=False)
                messages.append({"role": "tool", "tool_call_id": call.id, "content": content})

        fallback = "Przerwałem wykonywanie po osiągnięciu limitu kroków narzędzi. Doprecyzuj zadanie."
        self.store.add_message(conversation_id, "assistant", fallback)
        return fallback
