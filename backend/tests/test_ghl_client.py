import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.integrations.ghl.client import GHLClient


@pytest.mark.asyncio
async def test_ghl_api_failure_retries():
    client = GHLClient()
    client.max_retries = 2
    client.settings.retry_base_delay_seconds = 0.01

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.content = b"error"
    mock_response.raise_for_status.side_effect = Exception("API failure")

    mock_http = AsyncMock()
    mock_http.request.return_value = mock_response

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client_cls.return_value.__aenter__.return_value = mock_http
        mock_client_cls.return_value.__aexit__.return_value = None

        with pytest.raises(RuntimeError):
            await client.get_contact("contact-123")
