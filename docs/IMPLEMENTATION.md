# Uruchomienie JokerGodAl

## Lokalnie
1. Python 3.12+
2. python -m venv .venv
3. Aktywuj środowisko i wykonaj pip install -r requirements.txt
4. Skopiuj .env.example do .env i ustaw OPENAI_API_KEY.
5. uvicorn app.main:app --reload
6. Otwórz http://localhost:8000/docs.

## Testy
python -m unittest discover -s tests -v

## Docker
Skopiuj .env.example do .env, uzupełnij klucz API, następnie docker compose up --build.

## Telegram
Utwórz bota przez BotFather, ustaw TELEGRAM_BOT_TOKEN i OPENAI_API_KEY, a następnie uruchom python telegram_bot.py.

## Ważne
- Nie commituj .env.
- W produkcji ustaw JOKER_API_TOKEN, HTTPS, ograniczone CORS i trwały wolumen.
- Pierwsza wersja udostępnia wyłącznie narzędzia read-only.
- Nie uruchamiaj publicznego endpointu bez autoryzacji i limitowania ruchu.
