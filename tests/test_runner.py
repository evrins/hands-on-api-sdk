#!/usr/bin/env python3
"""Test runner script for swcpy tests."""

import sys
import pytest


def run_tests():
    """Run all tests with appropriate configuration."""
    args = [
        "tests/",
        "-v",
        "--tb=short",
        "--disable-warnings"
    ]
    
    # Add any command line arguments passed to this script
    if len(sys.argv) > 1:
        args.extend(sys.argv[1:])
    
    return pytest.main(args)


if __name__ == "__main__":
    sys.exit(run_tests())