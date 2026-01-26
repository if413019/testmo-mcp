"""Tests for the Testmo client."""

import pytest
from mcp_testmo.client import TestmoAPIError, TestmoClient


class TestTestmoClient:
    """Tests for TestmoClient."""

    def test_client_initialization(self):
        """Test client initializes with env vars."""
        client = TestmoClient()
        assert client.base_url == "https://test.testmo.net"
        assert client.api_key == "test-api-key"

    def test_client_initialization_with_params(self, monkeypatch):
        """Test client initializes with explicit params."""
        monkeypatch.delenv("TESTMO_URL", raising=False)
        monkeypatch.delenv("TESTMO_API_KEY", raising=False)

        client = TestmoClient(
            base_url="https://custom.testmo.net",
            api_key="custom-key",
        )
        assert client.base_url == "https://custom.testmo.net"
        assert client.api_key == "custom-key"

    def test_client_missing_url(self, monkeypatch):
        """Test client raises error when URL is missing."""
        monkeypatch.delenv("TESTMO_URL", raising=False)

        with pytest.raises(ValueError, match="TESTMO_URL not set"):
            TestmoClient(api_key="test-key")

    def test_client_missing_api_key(self, monkeypatch):
        """Test client raises error when API key is missing."""
        monkeypatch.delenv("TESTMO_API_KEY", raising=False)

        with pytest.raises(ValueError, match="TESTMO_API_KEY not set"):
            TestmoClient(base_url="https://test.testmo.net")

    def test_url_trailing_slash_stripped(self):
        """Test trailing slash is stripped from URL."""
        client = TestmoClient(
            base_url="https://test.testmo.net/",
            api_key="test-key",
        )
        assert client.base_url == "https://test.testmo.net"

    def test_web_url_generation(self):
        """Test web URL generation."""
        client = TestmoClient()

        # Basic URL
        url = client.get_web_url(project_id=2)
        assert url == "https://test.testmo.net/repository/2"

        # With folder ID
        url = client.get_web_url(project_id=2, resource_id=123)
        assert url == "https://test.testmo.net/repository/2?group_id=123"

        # With different resource type
        url = client.get_web_url(project_id=2, resource_type="runs")
        assert url == "https://test.testmo.net/runs/2"


class TestTestmoAPIError:
    """Tests for TestmoAPIError."""

    def test_error_message(self):
        """Test error message formatting."""
        error = TestmoAPIError(404, "Not found", {"detail": "Resource missing"})

        assert error.status_code == 404
        assert error.message == "Not found"
        assert error.details == {"detail": "Resource missing"}
        assert "404" in str(error)
        assert "Not found" in str(error)
