# AI Lead Automation Platform

Production-style practice project for AI-driven lead qualification, CRM automation, and appointment scheduling.

**Flow:** GoHighLevel → Webhook → Backend → AI Agent → Actions → GoHighLevel

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

| Service  | URL                        |
|----------|----------------------------|
| API      | http://localhost:8000      |
| API Docs | http://localhost:8000/docs |
| Dashboard| http://localhost:5173      |

## Test the Flow

Send a mock GHL webhook:

```bash
curl -X POST http://localhost:8000/webhooks/ghl \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: dev-webhook-secret" \
  -d @docs/examples/ghl_webhook.json
```

Process the lead:

```bash
curl -X POST http://localhost:8000/leads/1/process
```

View results at http://localhost:5173

## Run Tests

```bash
cd backend
pip install -r requirements.txt
pytest -v
```

Tests use SQLite and mock GHL/ElevenLabs providers — no real credentials required.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Database Schema](docs/DATABASE.md)
- [API Reference](docs/API.md)
- [Examples](docs/EXAMPLES.md)

## Environment Variables

See `.env.example`. All secrets are loaded from environment variables.

## Replacing Mock Integrations

Set `GHL_USE_MOCK=false` and provide `GHL_API_KEY`, `GHL_LOCATION_ID`, `GHL_CALENDAR_ID` for real GoHighLevel.

Set `ELEVENLABS_USE_MOCK=false` and provide ElevenLabs credentials for real voice agent integration.

SMS/Email mock providers in `app/integrations/messaging/` can be swapped for Smarter Contact or Smartlead by implementing the same `SmsProvider` / `EmailProvider` interfaces.
