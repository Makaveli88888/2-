# JOKERAl Mini App Skeleton — Stars Flow

## Setup

1. Skopiuj `.env.example` do `.env` i ustaw `JOKERAL_BOT_TOKEN`.
2. Backend:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```
3. Frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
4. Dla prawdziwego Stars: wystaw frontend na HTTPS i ustaw URL w BotFather.

## Pierwszy płatny flow

- Paczki: starter (50 Stars), standard (150), high (500)
- Backend tworzy invoice link (XTR)
- Frontend otwiera przez Telegram.WebApp.openInvoice
- Bot potwierdza successful_payment i księguje w ledgerze

## Compliance

- Tylko Stars. Brak prawdziwych pieniędzy bez licencji.
- Prywatne stoły = invite code.
- Age gate 18+.
