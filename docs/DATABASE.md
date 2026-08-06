# Database Schema

## leads

| Column | Type | Description |
|--------|------|-------------|
| id | int PK | Internal lead ID |
| ghl_contact_id | string unique | GoHighLevel contact ID |
| name, email, phone | string | Contact info |
| status | enum | Lead lifecycle status |
| qualification_status | enum | AI qualification result |
| pipeline_stage | string | CRM pipeline stage |
| appointment_id | FK | Linked appointment |
| tags, notes | text | Serialized tags and notes |
| created_at, updated_at | timestamp | Audit timestamps |

## conversations

Groups messages by channel (sms, email, voice).

## messages

All inbound/outbound communications with direction, channel, and body.

## appointments

Booked slots with GHL appointment ID, start/end times, and status.

## automation_events

Tracks automation runs: type, source, payload, status, retry_count, errors.

## ai_actions

Audit log of every AI decision and tool execution with input/output.

## webhook_events

Incoming webhook log with idempotency key for duplicate prevention.

## Relationships

- Lead → many Conversations, Messages, Appointments, AutomationEvents, AIActions
- Conversation → many Messages
- WebhookEvent → optional Lead FK
