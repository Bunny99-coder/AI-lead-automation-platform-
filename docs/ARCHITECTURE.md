# Architecture

## Overview

```
┌─────────────┐     webhook      ┌──────────────┐     async      ┌─────────────┐
│ GoHighLevel │ ───────────────► │ FastAPI      │ ─────────────► │ AI Agent    │
└─────────────┘                  │ Backend      │                └──────┬──────┘
                                 └──────┬───────┘                       │
                                        │                               │ tools
                                        ▼                               ▼
                                 ┌──────────────┐                ┌─────────────┐
                                 │ PostgreSQL   │ ◄──────────────│ Services    │
                                 └──────────────┘                └──────┬──────┘
                                                                        │
                    ┌───────────────────────────────────────────────────┤
                    ▼                    ▼                    ▼           ▼
              ┌──────────┐        ┌────────────┐      ┌──────────┐  ┌────────┐
              │ Mock/Real│        │ ElevenLabs │      │ SMS/Email│  │ OpenAI │
              │ GHL API  │        │ Voice Agent│      │ Providers│  │ API    │
              └──────────┘        └────────────┘      └──────────┘  └────────┘
```

## Layers

| Layer | Responsibility |
|-------|----------------|
| `api/routes` | HTTP endpoints, validation, auth — no business logic |
| `services` | Business logic, orchestration, transactions |
| `agents` | AI qualification, tool dispatch, action policy |
| `integrations` | External API clients behind interfaces |
| `workers` | Async processing, retries, background jobs |
| `models` | SQLAlchemy ORM entities |
| `schemas` | Pydantic request/response validation |

## Reliability Features

- **Idempotency:** Webhook events deduplicated via `idempotency_key`
- **Retries:** Exponential backoff for GHL API and lead processing
- **Dead letter:** Failed automation events marked after max retries
- **Audit trail:** All AI actions and webhook events persisted
- **Correlation IDs:** Request tracing across async flows

## AI Guardrails

The action policy (`agents/policy.py`) restricts what the AI can do automatically vs. what requires human confirmation.

Tools are validated with Pydantic before execution. The AI never makes raw HTTP calls.

## Mock vs Real Providers

Factory functions (`get_ghl_provider`, `get_elevenlabs_provider`) return mock implementations when credentials are absent or `*_USE_MOCK=true`.
