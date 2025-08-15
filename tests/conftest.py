"""Pytest configuration and shared fixtures."""

import pytest
from unittest.mock import Mock
import httpx
from datetime import datetime

from swcpy.swc_config import SWCConfig
from swcpy.swc_client import SWCClient


@pytest.fixture
def sample_config():
    """Create a sample configuration for testing."""
    return SWCConfig(
        base_url="https://api.test.com",
        backoff=False,
        backoff_max_time=30,
        bulk_file_format="csv"
    )


@pytest.fixture
def sample_client(sample_config):
    """Create a sample client for testing."""
    return SWCClient(sample_config)


@pytest.fixture
def mock_http_response():
    """Create a mock HTTP response."""
    response = Mock(spec=httpx.Response)
    response.status_code = 200
    response.json.return_value = {"status": "ok"}
    return response


@pytest.fixture
def sample_league_data():
    """Sample league data for testing."""
    return {
        "league_id": 1,
        "league_name": "Test League",
        "scoring_type": "standard",
        "last_changed_date": "2024-01-01T00:00:00",
        "teams": []
    }


@pytest.fixture
def sample_team_data():
    """Sample team data for testing."""
    return {
        "league_id": 1,
        "team_id": 1,
        "team_name": "Test Team",
        "last_changed_date": "2024-01-01T00:00:00",
        "players": []
    }


@pytest.fixture
def sample_player_data():
    """Sample player data for testing."""
    return {
        "player_id": 1,
        "gsis_id": "test123",
        "first_name": "John",
        "last_name": "Doe",
        "position": "QB",
        "last_changed_date": "2024-01-01T00:00:00",
        "performances": []
    }


@pytest.fixture
def sample_performance_data():
    """Sample performance data for testing."""
    return {
        "performance_id": 1,
        "player_id": 1,
        "week_number": "1",
        "fantasy_points": 15.5,
        "last_changed_date": "2024-01-01T00:00:00"
    }


@pytest.fixture
def sample_counts_data():
    """Sample counts data for testing."""
    return {
        "league_count": 10,
        "team_count": 100,
        "player_count": 1000
    }