"""Pytest configuration and fixtures."""

import os

import pytest


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Set mock environment variables for testing."""
    monkeypatch.setenv("TESTMO_URL", "https://test.testmo.net")
    monkeypatch.setenv("TESTMO_API_KEY", "test-api-key")


@pytest.fixture
def sample_case_data():
    """Sample test case data for testing."""
    return {
        "name": "Test Login Flow",
        "folder_id": 123,
        "custom_priority": 1,
        "custom_type": 59,
        "custom_creator": 51,
        "custom_milestone_id": "release/5.2.0",
        "custom_references": "TEST-123",
        "custom_issues_tags_and_configurations_added": 66,
        "custom_confluence_url": "https://example.atlassian.net/wiki/test",
        "custom_feature": "<pre><code>Feature: Login</code></pre>",
        "configurations": [5],
        "tags": ["services-usergrowth", "e2e"],
    }
