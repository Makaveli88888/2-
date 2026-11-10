# JokerGodAl

**Projekt:** JokerGodAl (JokerGod AI)  
**Repo:** [Makaveli88888/2-](https://github.com/Makaveli88888/2-)  
**Wersja implementacji:** 0.1.0 — fundament działającego MVP

JokerGodAl to asystent AI z architekturą przygotowaną do rozwoju wieloagentowego. Orchestrator planuje, persona Trickster eksploruje rozwiązania, Sceptyk pilnuje ograniczeń, a Executor korzysta z jawnie dozwolonych narzędzi.

## Co działa w kodzie v0.1.0

- FastAPI: chat, health check, lista narzędzi i historia konwersacji.
- Integracja z OpenAI API przez zmienną środowiskową.
- Trwała pamięć rozmów w SQLite.
- Allow-lista narzędzi: kalkulator AST i zegar UTC.
- Opcjonalny token Bearer dla API.
- Opcjonalny bot Telegram.
- Docker i Docker Compose.
- Testy jednostkowe oraz GitHub Actions workflow.

Role agentowe są na razie logicznymi etapami jednego przebiegu modelu, a nie trzema niezależnymi agentami.

## JOKER Predictive Engine v0.1

Tryb PAPER — publiczne dane rynkowe Polymarket, paginowane skanowanie Gamma, ograniczone odczyty CLOB orderbook, heurystyczny Predictive Consensus oraz symulacja zleceń bez możliwości wysyłania prawdziwych zleceń.

Szczegóły: [docs/PREDICTIVE_ENGINE.md](docs/PREDICTIVE_ENGINE.md)

## Szybki start

```bash
python -m venv .venv
# aktywuj środowisko wirtualne
pip install -r requirements.txt
cp .env.example .env
# ustaw OPENAI_API_KEY w .env
uvicorn app.main:app --reload
```

API: `http://localhost:8000`  
Dokumentacja API: `http://localhost:8000/docs`

## Testy

```bash
python -m unittest discover -s tests -v
```

## Docker

```bash
cp .env.example .env
# ustaw OPENAI_API_KEY
docker compose up --build
```

## Telegram

Ustaw `TELEGRAM_BOT_TOKEN` i `OPENAI_API_KEY`, a następnie uruchom:

```bash
python telegram_bot.py
```

## Dokumentacja

- [Architektura](docs/ARCHITECTURE.md)
- [Instrukcja uruchomienia](docs/IMPLEMENTATION.md)
- [Silnik predykcyjny](docs/PREDICTIVE_ENGINE.md)
- [Enterprise Operating System](docs/ENTERPRISE_OPERATING_SYSTEM.md)
- [Brief badawczy](docs/RESEARCH.md)
- [Roadmapa](docs/ROADMAP.md)
- [One-pager](docs/INVESTOR.md)

## Bezpieczeństwo i ograniczenia

- Nie commituj pliku `.env` ani kluczy API.
- W produkcji ustaw `JOKER_API_TOKEN`, HTTPS, ograniczone CORS i limity ruchu.
- Narzędzia v0.1.0 są tylko do odczytu/obliczeń; agent nie wysyła wiadomości ani nie wykonuje zakupów.
- Przed wdrożeniem publicznym dodaj autoryzację użytkowników, rate limiting, mechanizm zatwierdzania działań i monitoring.

## Zasady

Projekt nie buduje broni, oszustw ani treści nielegalnych. Persona Jokera to estetyka i styl rozumowania, nie instrukcje szkodzenia.
