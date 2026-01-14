#!/usr/bin/env python3
"""Test all logging format combinations"""

import os


def test_logging_format(log_format: str, pretty: bool):
    """Test a specific logging configuration"""
    os.environ['LOG_LEVEL'] = 'INFO'
    os.environ['LOG_FORMAT'] = log_format
    os.environ['LOG_PRETTY'] = str(pretty).lower()
    
    # Clear any existing logging configuration
    import logging
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Import and setup logging
    from core.logging import setup_logging
    logger = setup_logging()
    
    print(f"\n{'='*60}")
    print(f"TEST: {log_format} + {'pretty' if pretty else 'not-pretty'}")
    print(f"{'='*60}")
    
    logger.info('✅ Test message with emoji')
    logger.warning('⚠️ Warning message')
    logger.error('❌ Error message')
    
    # Test with extra context
    logger.info(
        '📊 Message with context',
        extra={
            'user_id': 'user_123',
            'case_id': 'case_456',
            'request_id': 'req_789'
        }
    )

if __name__ == '__main__':
    # Test all 4 combinations
    test_logging_format('plain', True)
    test_logging_format('plain', False)
    test_logging_format('json', True)
    test_logging_format('json', False)
    
    print(f"\n{'='*60}")
    print("✅ All logging format tests completed!")
    print(f"{'='*60}\n")
