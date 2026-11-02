# JokerGodAl — architektura techniczna

## MVP v0.1.0
- FastAPI: health, chat, historia i usuwanie rozmów.
- JokerAgent: Orchestrator + persona Trickster + bramka Sceptyk + Executor.
- SQLite: trwała historia rozmów, izolowana identyfikatorem konwersacji.
- Narzędzia: bezpieczny kalkulator AST i czas UTC.
- Telegram: opcjonalny adapter polling.
- Docker: kontener API i trwały wolumen danych.

Role agentowe są na tym etapie logicznymi etapami jednego przebiegu modelu, a nie trzema niezależnymi instancjami modeli. To celowe ograniczenie kosztu i złożoności pierwszej wersji.

## Bezpieczeństwo
- Narzędzia są allow-listą; brak powłoki, dowolnego HTTP i zapisu w usługach zewnętrznych.
- Opcjonalny token Bearer chroni endpointy API.
- Sekrety przekazywane są przez zmienne środowiskowe.
- Błędy dostawcy AI nie ujawniają stack trace ani kluczy.
- Integracje wykonujące skutki zewnętrzne wymagają osobnego mechanizmu zatwierdzania.

## Następne moduły
1. Warstwa approvals z requester, action, payload hash, expiry i statusem.
2. PostgreSQL + pgvector i polityka retencji.
3. MCP client z allow-listą serwerów i timeoutami.
4. Osobne role/agent runs, ślady i ewaluacje.
5. Autoryzacja użytkowników, limity, audyt i panel web.
6. Testy integracyjne, CI i monitoring.

## API
- GET /health
- GET /api/tools
- POST /api/chat — { "message": "...", "conversation_id": "opcjonalnie" }
- GET /api/conversations/{id}
- DELETE /api/conversations/{id}
- Dokumentacja interaktywna: /docs
