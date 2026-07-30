import pytest


@pytest.mark.asyncio
async def test_end_to_end_lead_flow(client, webhook_headers, sample_ghl_payload):
    """Full flow: webhook -> lead stored -> process -> actions logged."""
    webhook = client.post("/webhooks/ghl", json=sample_ghl_payload, headers=webhook_headers)
    assert webhook.status_code == 200
    lead_id = webhook.json()["lead_id"]

    process = client.post(f"/leads/{lead_id}/process")
    assert process.status_code == 200

    actions = client.get(f"/leads/{lead_id}/actions")
    assert actions.status_code == 200
    assert len(actions.json()["actions"]) >= 1

    events = client.get(f"/leads/{lead_id}/events")
    assert events.status_code == 200
    assert len(events.json()["events"]) >= 1

    stats = client.get("/admin/stats")
    assert stats.status_code == 200
    assert stats.json()["total_leads"] >= 1
