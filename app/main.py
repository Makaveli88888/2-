import uuid

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.agent import JokerAgent
from app.config import get_settings
from app.database import MemoryStore
from app.providers import HybridProvider
from app.security import authenticated_user

settings = get_settings()
if len(settings.jwt_secret) < 32:
    raise RuntimeError("JWT_SECRET must contain at least 32 characters")
store = MemoryStore(settings.database_url)
provider = HybridProvider(settings)
agent = JokerAgent(store, provider, settings.max_tool_rounds)

app = FastAPI(title="JOKER OS API", version="1.0.0",
              description="Hybrid AI assistant with owner-scoped conversation storage.")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    conversation_id: str | None = Field(default=None, min_length=1, max_length=100)


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "JOKER OS", "version": "1.0.0",
            "provider_mode": settings.ai_provider, "database": "postgresql"}


@app.get("/api/tools")
def list_tools(user_id: str = Depends(authenticated_user)):
    return {"tools": ["calculator", "current_time"], "mode": "read_only"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest, user_id: str = Depends(authenticated_user)):
    conversation_id = request.conversation_id or str(uuid.uuid4())
    try:
        answer = agent.respond(conversation_id, user_id, request.message)
        return ChatResponse(conversation_id=conversation_id, answer=answer)
    except PermissionError as exc:
        raise HTTPException(status_code=404, detail="Conversation not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail="AI provider unavailable or not configured") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Błąd dostawcy modelu AI.") from exc


@app.get("/api/conversations/{conversation_id}")
def get_conversation(conversation_id: str, user_id: str = Depends(authenticated_user)):
    try:
        return {"conversation_id": conversation_id, "messages": store.history(conversation_id, user_id, limit=100)}
    except PermissionError as exc:
        raise HTTPException(status_code=404, detail="Conversation not found") from exc


@app.delete("/api/conversations/{conversation_id}")
def clear_conversation(conversation_id: str, user_id: str = Depends(authenticated_user)):
    try:
        store.clear(conversation_id, user_id)
        return {"conversation_id": conversation_id, "deleted": True}
    except PermissionError as exc:
        raise HTTPException(status_code=404, detail="Conversation not found") from exc
