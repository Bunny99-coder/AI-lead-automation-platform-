def test_elevenlabs_post_call_webhook(client, elevenlabs_headers, webhook_headers, sample_ghl_payload):
    ghl = client.post("/webhooks/ghl", json=sample_ghl_payload, headers=webhook_headers)
    lead_id = ghl.json()["lead_id"]

    payload = {
        "call_id": "call-001",
        "lead_id": lead_id,
        "transcript": "Agent: Hello. Lead: I want to book next week.",
        "summary": "Lead interested in booking",
        "call_outcome": "qualified",
        "qualification_result": "qualified",
    }
    response = client.post("/webhooks/elevenlabs", json=payload, headers=elevenlabs_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "processed"


def test_elevenlabs_tool_unauthorized(client):
    response = client.post("/tools/elevenlabs/get-lead", json={"lead_id": 1})
    assert response.status_code == 401


def test_elevenlabs_get_lead_tool(client, elevenlabs_headers, webhook_headers, sample_ghl_payload):
    ghl = client.post("/webhooks/ghl", json=sample_ghl_payload, headers=webhook_headers)
    lead_id = ghl.json()["lead_id"]
    response = client.post(
        "/tools/elevenlabs/get-lead",
        json={"lead_id": lead_id},
        headers=elevenlabs_headers,
    )
    assert response.status_code == 200
    assert response.json()["id"] == lead_id
