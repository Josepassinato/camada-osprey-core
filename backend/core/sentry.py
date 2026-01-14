import logging
import os

import sentry_sdk
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

logger = logging.getLogger(__name__)


def init_sentry() -> bool:
    dsn = os.environ.get("SENTRY_DSN")
    if not dsn:
        logger.info("Sentry disabled (SENTRY_DSN not set)")
        return False

    environment = os.environ.get("SENTRY_ENVIRONMENT", "development")

    traces_env = os.environ.get("SENTRY_TRACES_SAMPLE_RATE")
    profiles_env = os.environ.get("SENTRY_PROFILES_SAMPLE_RATE")

    if traces_env is None:
        traces_sample_rate = 0.1 if environment == "production" else 0.0
    else:
        traces_sample_rate = float(traces_env)

    if profiles_env is None:
        profiles_sample_rate = 0.0 if environment != "production" else 0.05
    else:
        profiles_sample_rate = float(profiles_env)

    debug = os.environ.get("SENTRY_DEBUG", "false").lower() == "true"
    send_pii = os.environ.get("SENTRY_SEND_PII", "false").lower() == "true"

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=os.environ.get("SENTRY_RELEASE"),
        server_name=os.environ.get("SENTRY_SERVER_NAME"),
        traces_sample_rate=traces_sample_rate,
        profiles_sample_rate=profiles_sample_rate,
        send_default_pii=send_pii,
        debug=debug,
        integrations=[
            FastApiIntegration(),
            StarletteIntegration(),
            AioHttpIntegration(),
            AsyncioIntegration(),
            HttpxIntegration(),
            LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
        ],
    )

    service_name = os.environ.get("SENTRY_SERVICE_NAME", "backend")
    sentry_sdk.set_tag("service", service_name)
    sentry_sdk.set_tag("environment", environment)

    raw_tags = os.environ.get("SENTRY_TAGS", "")
    if raw_tags:
        for pair in raw_tags.split(","):
            if "=" not in pair:
                continue
            key, value = pair.split("=", 1)
            sentry_sdk.set_tag(key.strip(), value.strip())

    logger.info("Sentry initialized")
    return True
