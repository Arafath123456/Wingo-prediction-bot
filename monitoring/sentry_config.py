import sentry_sdk
import os
from sentry_sdk.integrations.loguru import LoguruIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from loguru import logger

def init_sentry():
    if dsn := os.getenv("SENTRY_DSN"):
        sentry_sdk.init(
            dsn=dsn,
            integrations=[
                LoguruIntegration(),
                SqlalchemyIntegration(),
                RedisIntegration()
            ],
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
            environment=os.getenv("ENVIRONMENT", "development"),
            release=os.getenv("RELEASE_VERSION", "1.0.0")
        )
        logger.info("Sentry error tracking initialized")
    else:
        logger.warning("Sentry DSN not set - error tracking disabled")
