from logging import getLogger
from src.config.database import sessionmanager
from src.config.cache import redis_manager
from src.utils.logging import setup_logging

logger = getLogger(__name__)

async def start_up() -> None:
    """Run on application startup"""
    logger.info("application_starting")
    setup_logging()
    sessionmanager.connect()
    await redis_manager.connect()

async def shut_down() -> None:
    """Run on application shutdown"""
    logger.info("application_shutting_down")
    if sessionmanager._engine is not None:
        await sessionmanager.close()
    await redis_manager.close()