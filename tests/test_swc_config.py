import pytest
import os
from unittest.mock import patch

from swcpy.swc_config import SWCConfig


class TestSWCConfig:
    """Test suite for SWCConfig class."""

    def test_init_with_all_parameters(self):
        """Test configuration initialization with all parameters provided."""
        config = SWCConfig(
            base_url="https://api.example.com",
            backoff=False,
            backoff_max_time=60,
            bulk_file_format="parquet"
        )
        
        assert config.swc_base_url == "https://api.example.com"
        assert config.swc_backoff is False
        assert config.swc_backoff_max_time == 60
        assert config.swc_bulk_file_format == "parquet"

    def test_init_with_defaults(self):
        """Test configuration initialization with default values."""
        config = SWCConfig(base_url="https://api.example.com")
        
        assert config.swc_base_url == "https://api.example.com"
        assert config.swc_backoff is True
        assert config.swc_backoff_max_time == 30
        assert config.swc_bulk_file_format == "csv"

    @patch.dict(os.environ, {'SWC_API_BASE_URL': 'https://env.example.com'})
    def test_init_with_environment_variable(self):
        """Test configuration initialization using environment variable."""
        config = SWCConfig()
        
        assert config.swc_base_url == "https://env.example.com"
        assert config.swc_backoff is True
        assert config.swc_backoff_max_time == 30
        assert config.swc_bulk_file_format == "csv"

    @patch.dict(os.environ, {}, clear=True)
    def test_init_without_base_url_raises_error(self):
        """Test that missing base URL raises ValueError."""
        with pytest.raises(ValueError, match="Base URL is required"):
            SWCConfig()

    def test_str_representation(self):
        """Test string representation of config object."""
        config = SWCConfig(
            base_url="https://api.example.com",
            backoff=True,
            backoff_max_time=45,
            bulk_file_format="parquet"
        )
        
        expected = "https://api.example.com True 45 parquet"
        assert str(config) == expected

    @patch.dict(os.environ, {'SWC_API_BASE_URL': 'https://env.example.com'})
    def test_parameter_overrides_environment(self):
        """Test that explicit parameter overrides environment variable."""
        config = SWCConfig(base_url="https://param.example.com")
        
        assert config.swc_base_url == "https://param.example.com"

    def test_bulk_file_format_case_insensitive(self):
        """Test that bulk file format handling is case insensitive in usage."""
        config_upper = SWCConfig(
            base_url="https://api.example.com",
            bulk_file_format="CSV"
        )
        config_lower = SWCConfig(
            base_url="https://api.example.com",
            bulk_file_format="csv"
        )
        
        assert config_upper.swc_bulk_file_format == "CSV"
        assert config_lower.swc_bulk_file_format == "csv"