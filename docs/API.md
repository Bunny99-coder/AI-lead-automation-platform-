# API Reference

Base URL: `http://localhost:8000`

Interactive docs: `/docs`

## Webhooks

| Method | Path | Auth Header |
|--------|------|-------------|
| POST | `/webhooks/ghl` | `X-Webhook-Secret` |
| POST | `/webhooks/elevenlabs` | `X-ElevenLabs-Secret` |

## Leads

| Method | Path | Description |
|--------|------|-------------|
| GET | `/leads` | List leads |
| GET | `/leads/{id}` | Get lead |
| GET | `/leads/{id}/conversation` | Conversation history |
| GET | `/leads/{id}/events` | Automation events |
| GET | `/leads/{id}/actions` | AI actions |
| POST | `/leads/{id}/process` | Trigger AI processing |
| POST | `/leads/{id}/qualify` | Run qualification |
| POST | `/leads/{id}/appointment` | Book appointment |

## Appointments

| Method | Path | Description |
|--------|------|-------------|
| GET | `/appointments/availability` | Available slots |

## ElevenLabs Tools

| Method | Path | Description |
|--------|------|-------------|
| POST | `/tools/elevenlabs/get-lead` | Get lead data |
| POST | `/tools/elevenlabs/update-lead` | Update lead |
| POST | `/tools/elevenlabs/book-appointment` | Book slot |
| POST | `/tools/elevenlabs/add-note` | Add CRM note |

## Admin

| Method | Path | Description |
|--------|------|-------------|
| GET | `/admin/stats` | Dashboard statistics |
| GET | `/admin/actions` | Recent AI actions |
| GET | `/admin/webhooks` | Recent webhook events |

## Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Service health check |
