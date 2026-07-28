def test_ghl_webhook_creates_lead(client, webhook_headers, sample_ghl_payload):
    response = client.post("/webhooks/ghl", json=sample_ghl_payload, headers=webhook_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"
    assert data["lead_id"] is not None
    assert data["duplicate"] is False


def test_ghl_webhook_validation_failure(client, webhook_headers):
    response = client.post("/webhooks/ghl", json={"type": "ContactCreate"}, headers=webhook_headers)
    assert response.status_code == 422


def test_duplicate_webhook_prevention(client, webhook_headers, sample_ghl_payload):
    first = client.post("/webhooks/ghl", json=sample_ghl_payload, headers=webhook_headers)
    assert first.status_code == 200
    second = client.post("/webhooks/ghl", json=sample_ghl_payload, headers=webhook_headers)
    assert second.status_code == 200
    assert second.json()["duplicate"] is True


def test_webhook_unauthorized(client, sample_ghl_payload):
    response = client.post("/webhooks/ghl", json=sample_ghl_payload)
    assert response.status_code == 401


def test_lead_list_after_webhook(client, webhook_headers, sample_ghl_payload):
    client.post("/webhooks/ghl", json=sample_ghl_payload, headers=webhook_headers)
    response = client.get("/leads")
    assert response.status_code == 200
    assert response.json()["total"] >= 1
