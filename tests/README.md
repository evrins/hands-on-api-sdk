# SWCPy Tests

This directory contains comprehensive test suites for the SWCPy library.

## Test Structure

- `test_swc_client.py` - Unit tests for the main SWCClient class
- `test_swc_config.py` - Unit tests for the SWCConfig configuration class  
- `test_integration.py` - Integration tests for component interactions
- `conftest.py` - Shared pytest fixtures and configuration
- `test_runner.py` - Standalone test runner script

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/test_swc_client.py
```

### Run with verbose output
```bash
pytest -v
```

### Run specific test method
```bash
pytest tests/test_swc_client.py::TestSWCClient::test_init_with_backoff_disabled
```

### Run tests with coverage
```bash
pytest --cov=swcpy --cov-report=html
```

### Run only unit tests
```bash
pytest -m unit
```

### Run only integration tests
```bash
pytest -m integration
```

## Test Categories

- **Unit Tests**: Test individual methods and functions in isolation
- **Integration Tests**: Test interactions between components
- **Mock Tests**: Use mocked dependencies to test behavior without external calls

## Test Coverage

The test suite covers:

- ✅ Client initialization with different configurations
- ✅ API endpoint methods (health check, list operations, get by ID)
- ✅ Bulk file download functionality
- ✅ Error handling and exception scenarios
- ✅ Parameter filtering and validation
- ✅ Configuration management
- ✅ HTTP client behavior with and without retries

## Dependencies

Tests require the following packages (already included in pyproject.toml):
- `pytest` - Testing framework
- `unittest.mock` - Mocking capabilities (built-in)

## Environment Setup

For tests that use environment variables, you may need to set:
```bash
export SWC_API_BASE_URL="https://your-test-api.com"
```

Or the tests will use mocked configurations by default.