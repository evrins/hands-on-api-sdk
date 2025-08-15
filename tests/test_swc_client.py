import pytest
from unittest.mock import Mock, patch, MagicMock
import httpx
from datetime import datetime

from swcpy.swc_client import SWCClient
from swcpy.swc_config import SWCConfig
from swcpy.schemas import League, Team, Player, Performance, Counts


class TestSWCClient:
    """Test suite for SWCClient class."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration for testing."""
        return SWCConfig(
            base_url="https://api.test.com",
            backoff=False,
            backoff_max_time=30,
            bulk_file_format="csv"
        )

    @pytest.fixture
    def client(self, mock_config):
        """Create a SWCClient instance for testing."""
        return SWCClient(mock_config)

    @pytest.fixture
    def mock_response(self):
        """Create a mock HTTP response."""
        response = Mock(spec=httpx.Response)
        response.status_code = 200
        return response

    def test_init_with_backoff_disabled(self, mock_config):
        """Test client initialization with backoff disabled."""
        client = SWCClient(mock_config)
        
        assert client.base_url == "https://api.test.com"
        assert client.backoff is False
        assert client.backoff_max_time == 30
        assert client.bulk_file_format == "csv"
        assert isinstance(client.http_client, httpx.Client)

    def test_init_with_backoff_enabled(self):
        """Test client initialization with backoff enabled."""
        config = SWCConfig(
            base_url="https://api.test.com",
            backoff=True,
            backoff_max_time=60,
            bulk_file_format="parquet"
        )
        client = SWCClient(config)
        
        assert client.backoff is True
        assert client.backoff_max_time == 60
        assert client.bulk_file_format == "parquet"

    def test_bulk_file_names_csv_format(self, client):
        """Test bulk file names are correctly formatted for CSV."""
        expected_names = {
            'players': 'player_data.csv',
            'leagues': 'league_data.csv',
            'performances': 'performance_data.csv',
            'teams': 'team_data.csv',
            'team_players': 'team_player_data.csv',
        }
        assert client.BULK_FILE_NAMES == expected_names

    def test_bulk_file_names_parquet_format(self):
        """Test bulk file names are correctly formatted for Parquet."""
        config = SWCConfig(
            base_url="https://api.test.com",
            bulk_file_format="parquet"
        )
        client = SWCClient(config)
        
        expected_names = {
            'players': 'player_data.parquet',
            'leagues': 'league_data.parquet',
            'performances': 'performance_data.parquet',
            'teams': 'team_data.parquet',
            'team_players': 'team_player_data.parquet',
        }
        assert client.BULK_FILE_NAMES == expected_names

    @patch('swcpy.swc_client.httpx.Client.get')
    def test_call_api_success(self, mock_get, client, mock_response):
        """Test successful API call."""
        mock_response.json.return_value = {"status": "ok"}
        mock_get.return_value = mock_response
        
        result = client.call_api("/test", {"param": "value"})
        
        mock_get.assert_called_once_with("/test", params={"param": "value"})
        assert result == mock_response

    @patch('swcpy.swc_client.httpx.Client.get')
    def test_call_api_filters_none_params(self, mock_get, client, mock_response):
        """Test that None parameters are filtered out."""
        mock_response.json.return_value = {"status": "ok"}
        mock_get.return_value = mock_response
        
        client.call_api("/test", {"param1": "value", "param2": None})
        
        mock_get.assert_called_once_with("/test", params={"param1": "value"})

    @patch('swcpy.swc_client.httpx.Client.get')
    def test_call_api_http_status_error(self, mock_get, client):
        """Test API call with HTTP status error."""
        mock_get.side_effect = httpx.HTTPStatusError(
            "Bad Request", request=Mock(), response=Mock(status_code=400, text="Bad Request")
        )
        
        with pytest.raises(httpx.HTTPStatusError):
            client.call_api("/test")

    @patch('swcpy.swc_client.httpx.Client.get')
    def test_call_api_request_error(self, mock_get, client):
        """Test API call with request error."""
        mock_get.side_effect = httpx.RequestError("Connection failed")
        
        with pytest.raises(httpx.RequestError):
            client.call_api("/test")

    @patch.object(SWCClient, 'call_api')
    def test_get_health_check(self, mock_call_api, client, mock_response):
        """Test health check endpoint."""
        mock_call_api.return_value = mock_response
        
        result = client.get_health_check()
        
        mock_call_api.assert_called_once_with("/")
        assert result == mock_response

    @patch.object(SWCClient, 'call_api')
    def test_list_leagues(self, mock_call_api, client):
        """Test listing leagues."""
        mock_response_data = [
            {
                "league_id": 1,
                "league_name": "Test League",
                "scoring_type": "standard",
                "last_changed_date": "2024-01-01T00:00:00",
                "teams": []
            }
        ]
        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_call_api.return_value = mock_response
        
        result = client.list_leagues(skip=10, limit=50, league_name="Test")
        
        expected_params = {
            "skip": 10,
            "limit": 50,
            "min_last_changed_date": None,
            "league_name": "Test"
        }
        mock_call_api.assert_called_once_with("/v0/leagues/", params=expected_params)
        assert len(result) == 1
        assert isinstance(result[0], League)
        assert result[0].league_name == "Test League"

    @patch.object(SWCClient, 'call_api')
    def test_get_league_by_id(self, mock_call_api, client):
        """Test getting league by ID."""
        mock_response_data = {
            "league_id": 1,
            "league_name": "Test League",
            "scoring_type": "standard",
            "last_changed_date": "2024-01-01T00:00:00",
            "teams": []
        }
        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_call_api.return_value = mock_response
        
        result = client.get_league_by_id(1)
        
        mock_call_api.assert_called_once_with("/v0/leagues/1")
        assert isinstance(result, League)
        assert result.league_id == 1

    @patch.object(SWCClient, 'call_api')
    def test_get_counts(self, mock_call_api, client):
        """Test getting counts."""
        mock_response_data = {
            "league_count": 10,
            "team_count": 100,
            "player_count": 1000
        }
        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_call_api.return_value = mock_response
        
        result = client.get_counts()
        
        mock_call_api.assert_called_once_with("/v0/counts/")
        assert isinstance(result, Counts)
        assert result.league_count == 10

    @patch.object(SWCClient, 'call_api')
    def test_list_teams(self, mock_call_api, client):
        """Test listing teams."""
        mock_response_data = [
            {
                "league_id": 1,
                "team_id": 1,
                "team_name": "Test Team",
                "last_changed_date": "2024-01-01T00:00:00",
                "players": []
            }
        ]
        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_call_api.return_value = mock_response
        
        result = client.list_teams(league_id=1, team_name="Test")
        
        expected_params = {
            "skip": 0,
            "limit": 100,
            "min_last_changed_date": None,
            "team_name": "Test",
            "league_id": 1
        }
        mock_call_api.assert_called_once_with("/v0/teams/", expected_params)
        assert len(result) == 1
        assert isinstance(result[0], Team)

    @patch.object(SWCClient, 'call_api')
    def test_list_players(self, mock_call_api, client):
        """Test listing players."""
        mock_response_data = [
            {
                "player_id": 1,
                "gsis_id": "test123",
                "first_name": "John",
                "last_name": "Doe",
                "position": "QB",
                "last_changed_date": "2024-01-01T00:00:00",
                "performances": []
            }
        ]
        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_call_api.return_value = mock_response
        
        result = client.list_players(first_name="John", last_name="Doe")
        
        expected_params = {
            "skip": 0,
            "limit": 100,
            "min_last_changed_date": None,
            "first_name": "John",
            "last_name": "Doe"
        }
        mock_call_api.assert_called_once_with("/v0/players/", expected_params)
        assert len(result) == 1
        assert isinstance(result[0], Player)

    @patch.object(SWCClient, 'call_api')
    def test_get_player_by_id(self, mock_call_api, client):
        """Test getting player by ID."""
        mock_response_data = {
            "player_id": 1,
            "gsis_id": "test123",
            "first_name": "John",
            "last_name": "Doe",
            "position": "QB",
            "last_changed_date": "2024-01-01T00:00:00",
            "performances": []
        }
        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_call_api.return_value = mock_response
        
        result = client.get_player_by_id(1)
        
        mock_call_api.assert_called_once_with("/v0/players/1")
        assert isinstance(result, Player)
        assert result.player_id == 1

    @patch.object(SWCClient, 'call_api')
    def test_list_performances(self, mock_call_api, client):
        """Test listing performances."""
        mock_response_data = [
            {
                "performance_id": 1,
                "player_id": 1,
                "week_number": "1",
                "fantasy_points": 15.5,
                "last_changed_date": "2024-01-01T00:00:00"
            }
        ]
        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_call_api.return_value = mock_response
        
        result = client.list_performances(skip=5, limit=25)
        
        expected_params = {
            "skip": 5,
            "limit": 25,
            "min_last_changed_date": None
        }
        mock_call_api.assert_called_once_with("/v0/performances/", expected_params)
        assert len(result) == 1
        assert isinstance(result[0], Performance)

    @patch('swcpy.swc_client.httpx.get')
    def test_get_bulk_player_file(self, mock_get, client):
        """Test getting bulk player file."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"test,data"
        mock_get.return_value = mock_response
        
        result = client.get_bulk_player_file()
        
        expected_url = client.BULK_FILE_BASE_URL + "player_data.csv"
        mock_get.assert_called_once_with(expected_url, follow_redirects=True)
        assert result == b"test,data"

    @patch('swcpy.swc_client.httpx.get')
    def test_get_bulk_league_file(self, mock_get, client):
        """Test getting bulk league file."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"league,data"
        mock_get.return_value = mock_response
        
        result = client.get_bulk_league_file()
        
        expected_url = client.BULK_FILE_BASE_URL + "league_data.csv"
        mock_get.assert_called_once_with(expected_url, follow_redirects=True)
        assert result == b"league,data"

    @patch('swcpy.swc_client.httpx.get')
    def test_get_bulk_performance_file(self, mock_get, client):
        """Test getting bulk performance file."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"performance,data"
        mock_get.return_value = mock_response
        
        result = client.get_bulk_performance_file()
        
        expected_url = client.BULK_FILE_BASE_URL + "performance_data.csv"
        mock_get.assert_called_once_with(expected_url, follow_redirects=True)
        assert result == b"performance,data"

    @patch('swcpy.swc_client.httpx.get')
    def test_get_bulk_team_file(self, mock_get, client):
        """Test getting bulk team file."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"team,data"
        mock_get.return_value = mock_response
        
        result = client.get_bulk_team_file()
        
        expected_url = client.BULK_FILE_BASE_URL + "team_data.csv"
        mock_get.assert_called_once_with(expected_url, follow_redirects=True)
        assert result == b"team,data"

    @patch('swcpy.swc_client.httpx.get')
    def test_get_bulk_team_player_file(self, mock_get, client):
        """Test getting bulk team player file."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"team_player,data"
        mock_get.return_value = mock_response
        
        result = client.get_bulk_team_player_file()
        
        expected_url = client.BULK_FILE_BASE_URL + "team_player_data.csv"
        mock_get.assert_called_once_with(expected_url, follow_redirects=True)
        assert result == b"team_player,data"