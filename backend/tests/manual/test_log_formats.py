#!/usr/bin/env python3
"""Test all logging formats: plain, json, and cef"""

import os


def test_format(log_format: str, pretty: bool):
    """Test a specific logging format"""
    os.environ["LOG_LEVEL"] = "INFO"
    os.environ["LOG_FORMAT"] = log_format
    os.environ["LOG_PRETTY"] = str(pretty).lower()
    os.environ["SENTRY_SERVICE_NAME"] = "osprey-backend"
    os.environ["SENTRY_ENVIRONMENT"] = "production"
    os.environ["SENTRY_RELEASE"] = "2.0.0"

    # Clear any existing logging configuration
    import logging

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Import and setup logging
    from backend.core.logging import setup_logging

    logger = setup_logging()

    format_name = f"{log_format} + {'pretty' if pretty else 'not-pretty'}"
    print(f"\n{'='*80}")
    print(f"FORMAT: {format_name}")
    print(f"{'='*80}\n")

    # Test different log levels and scenarios
    logger.info("Service initialized successfully")
    logger.info("Especialista registrado: H-1B")
    logger.info("Loaded USCIS requirements knowledge base (14160 chars)")
    logger.info("Google Document AI initialized with service account for project osprey-484321")
    logger.info("Credentials file: /Users/dm/.config/google_cloud/osprey.json")
    logger.info("Service account credentials loaded successfully")
    logger.info("Service account credentials verified")

    logger.warning("Translation service degraded - using fallback")
    logger.error("Database connection failed - retrying")

    # Test with context
    logger.info(
        "Case created successfully",
        extra={
            "user_id": "user_123",
            "case_id": "case_456",
            "request_id": "req_789",
            "duration_ms": 234,
        },
    )

    # Test exception logging
    try:
        raise ValueError("Invalid visa type: XYZ")
    except Exception:
        logger.error("Validation failed", exc_info=True)


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("OSPREY LOGGING FORMAT COMPARISON")
    print("=" * 80)

    # Test 1: Plain format (development)
    test_format("plain", True)

    # Test 2: JSON format (production - Datadog/ELK/Splunk)
    test_format("json", False)

    # Test 3: CEF format (security - Azure Sentinel/ArcSight)
    test_format("cef", False)

    print(f"\n{'='*80}")
    print("✅ All logging format tests completed!")
    print(f"{'='*80}\n")
