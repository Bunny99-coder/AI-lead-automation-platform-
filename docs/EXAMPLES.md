# Examples

## GHL Webhook Payload

See `ghl_webhook.json` for a complete example.

## Example AI Conversation

```
Lead: Hi, I am interested in your services
AI: Thanks for reaching out! What service are you interested in and what timeline works for you?

Lead: I need consulting for my startup, ideally next month
AI: Great! Would you like to schedule a consultation?

Lead: Yes, book me an appointment
AI: I can help you book an appointment. Here are available times.
[System fetches real slots from calendar service — AI never invents times]
```

## Example AI Decision (Structured Output)

```json
{
  "intent": "qualified_buyer",
  "qualification_status": "qualified",
  "confidence": 0.8,
  "next_action": "offer_appointment",
  "reason": "Lead answered qualification questions positively",
  "response": "Great! Would you like to schedule a consultation?",
  "requires_human": false,
  "appointment_requested": false
}
```

## End-to-End Test

```bash
# 1. Send webhook
curl -X POST http://localhost:8000/webhooks/ghl \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: dev-webhook-secret" \
  -d @docs/examples/ghl_webhook.json

# 2. Process lead
curl -X POST http://localhost:8000/leads/1/process

# 3. Check actions
curl http://localhost:8000/leads/1/actions

# 4. Get availability and book
curl http://localhost:8000/appointments/availability
curl -X POST http://localhost:8000/leads/1/appointment \
  -H "Content-Type: application/json" \
  -d '{"slot_id": "slot-xxxxxxxx"}'
```

## Replacing Mock Integrations

### GoHighLevel
1. Set `GHL_USE_MOCK=false`
2. Add `GHL_API_KEY`, `GHL_LOCATION_ID`, `GHL_CALENDAR_ID`
3. The `GHLClient` class implements the same `GHLProvider` interface as `MockGHLProvider`

### ElevenLabs
1. Set `ELEVENLABS_USE_MOCK=false`
2. Implement real API calls in `ElevenLabsClient`
3. Point voice agent tools to `/tools/elevenlabs/*` endpoints

### Smarter Contact (SMS)
Replace `MockSmsProvider` with a class implementing `SmsProvider.send_sms()`.

### Smartlead (Email)
Replace `MockEmailProvider` with a class implementing `EmailProvider.send_email()`.

No changes needed in services — only swap the provider in dependency injection.
