"""Integration tests for SWCClient.

These tests verify the integration between different components
and can be run against a real API if needed.
"""

import pytest
from unittest.mock import patch, Mock
import httpx

from swcpy.swc_client import SWCClient
from swcpy.swc_config import SWCConfig
from swcpy.schemas import League, Team, Player, Performance, Counts


class TestSWCClientIntegration:
    """Integration tests for SWCClient."""

    @pytest.fixture
    def integration_config(self):
        """Configuration for integration testing."""
        return SWCConfig(
            base_url="https://api.test.com",
            backoff=True,
            backoff_max_time=10,
            bulk_file_format="csv"
        )

    @pytest.fixture
    def integration_client(self, integration_config):
        """Client for integration testing."""
        return SWCClient(integration_config)

    @patch('swcpy.swc_client.httpx.Client.get')
    def test_full_workflow_list_leagues_and_teams(self, mock_get, integration_client):
        """Test a complete workflow: list leagues, then get teams for a league."""
        # Mock league response
        league_response = Mock()
        league_response.json.return_value = [
            {
                "league_id": 1,
                "league_name": "Test League",
                "scoring_type": "standard",
                "last_changed_date": "2024-01-01T00:00:00",
                "teams": []
            }
        ]
        
        # Mock team response
        team_response = Mock()
        team_response.json.return_value = [
            {
                "league_id": 1,
                "team_id": 1,
                "team_name": "Test Team",
                "last_changed_date": "2024-01-01T00:00:00",
                "players": []
            }
        ]
        
        # Configure mock to return different responses for different calls
        mock_get.side_effect = [league_response, team_response]
        
        # Execute workflow
        leagues = integration_client.list_leagues(limit=1)
        assert len(leagues) == 1
        assert isinstance(leagues[0], League)
        
        teams = integration_client.list_teams(league_id=leagues[0].league_id)
        assert len(teams) == 1
        assert isinstance(teams[0], Team)
        assert teams[0].league_id == leagues[0].league_id

    @patch('swcpy.swc_client.httpx.Client.get')
    def test_error_handling_with_retries(self, mock_get, integration_client):
        """Test error handling and retry behavior."""
        # First call fails, second succeeds
        error_response = Mock()
        error_response.status_code = 500
        error_response.text = "Internal Server Error"
        
        success_response = Mock()
        success_response.json.return_value = {"status": "ok"}
        
        mock_get.side_effect = [
            httpx.HTTPStatusError("Server Error", request=Mock(), response=error_response),
            success_response
        ]
        
        # This should raise the error since we disabled backoff in the config
        with pytest.raises(httpx.HTTPStatusError):
            integration_client.get_health_check()

    @patch('swcpy.swc_client.httpx.get')
    def test_bulk_file_download_workflow(self, mock_bulk_get, integration_client):
        """Test downloading multiple bulk files."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"test,data\n1,value"
        mock_bulk_get.return_value = mock_response
        
        # Test downloading different bulk files
        player_data = integration_client.get_bulk_player_file()
        league_data = integration_client.get_bulk_league_file()
        performance_data = integration_client.get_bulk_performance_file()
        
        assert player_data == b"test,data\n1,value"
        assert league_data == b"test,data\n1,value"
        assert performance_data == b"test,data\n1,value"
        
        # Verify correct URLs were called
        expected_calls = [
            f"{integration_client.BULK_FILE_BASE_URL}player_data.csv",
            f"{integration_client.BULK_FILE_BASE_URL}league_data.csv",
            f"{integration_client.BULK_FILE_BASE_URL}performance_data.csv"
        ]
        
        actual_calls = [call[0][0] for call in mock_bulk_get.call_args_list]
        assert actual_calls == expected_calls

    def test_client_with_different_configurations(self):
        """Test client behavior with different configuration options."""
        # Test with backoff enabled
        config_with_backoff = SWCConfig(
            base_url="https://api.test.com",
            backoff=True,
            backoff_max_time=5
        )
        client_with_backoff = SWCClient(config_with_backoff)
        assert client_with_backoff.backoff is True
        
        # Test with parquet format
        config_parquet = SWCConfig(
            base_url="https://api.test.com",
            bulk_file_format="parquet"
        )
        client_parquet = SWCClient(config_parquet)
        assert "parquet" in client_parquet.BULK_FILE_NAMES['players']

    @patch('swcpy.swc_client.httpx.Client.get')
    def test_parameter_filtering_integration(self, mock_get, integration_client):
        """Test that None parameters are properly filtered in real scenarios."""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        # Call with mix of None and valid parameters
        integration_client.list_leagues(
            skip=0,
            limit=100,
            min_last_changed_date=None,
            league_name="Test League"
        )
        
        # Verify that None parameters were filtered out
        call_args = mock_get.call_args
        params = call_args[1]['params']
        assert 'min_last_changed_date' not in params
        assert params['league_name'] == "Test League"
        assert params['skip'] == 0
        assert params['limit'] == 100