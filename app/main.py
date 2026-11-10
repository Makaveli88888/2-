import secrets
import uuid
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.agent import JokerAgent
from app.config import get_settings
from app.database import MemoryStore

settings = get_settings()
store = MemoryStore(settings.database_path)
agent = JokerAgent(store, settings.openai_api_key, settings.openai_model, settings.max_tool_rounds)
app = FastAPI(title="JokerGodAl API", version="0.1.0",
              description="A safe, extensible multi-agent assistant foundation.")
app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins,
                   allow_credentials=False, allow_methods=["GET", "POST", "DELETE"],
                   allow_headers=["Authorization", "Content-Type"])


def authorize(authorization: str | None = Header(default=None)):
    if not settings.joker_api_token:
        return
    expected = f"Bearer {settings.joker_api_token}"
    if not authorization or not secrets.compare_digest(authorization, expected):
        raise HTTPException(status_code=401, detail="Unauthorized")


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    conversation_id: str | None = Field(default=None, max_length=100)


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "JokerGodAl", "version": "0.1.0",
            "model_configured": bool(settings.openai_api_key),
            "telegram_configured": bool(settings.telegram_bot_token)}


@app.get("/api/tools", dependencies=[Depends(authorize)])
def list_tools():
    return {"tools": ["calculator", "current_time"], "mode": "read_only"}


@app.post("/api/chat", response_model=ChatResponse, dependencies=[Depends(authorize)])
def chat(request: ChatRequest):
    conversation_id = request.conversation_id or str(uuid.uuid4())
    try:
        return ChatResponse(conversation_id=conversation_id,
                            answer=agent.respond(conversation_id, request.message))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Błąd dostawcy modelu AI.") from exc


@app.get("/api/conversations/{conversation_id}", dependencies=[Depends(authorize)])
def get_conversation(conversation_id: str):
    return {"conversation_id": conversation_id, "messages": store.history(conversation_id, limit=100)}


@app.delete("/api/conversations/{conversation_id}", dependencies=[Depends(authorize)])
def clear_conversation(conversation_id: str):
    store.clear(conversation_id)
    return {"conversation_id": conversation_id, "deleted": True}


from app.predictive.api import router as predictive_router

app.include_router(predictive_router, dependencies=[Depends(authorize)])
