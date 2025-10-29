import json
from redis import asyncio as aioredis
from redis.asyncio import Redis
from typing import Any, Optional
from src.config.settings import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)


class RedisConnectionManager:
    """
    Redis connection manager for handling the Redis connection pool.
    """

    _redis_client: Optional[Redis] = None

    def __init__(self, host: str):
        self._host = host
        self._redis_client: Optional[Redis] = None

    async def connect(self) -> None:
        """
        Connect to Redis and initialize the client.
        This should be called at application startup.
        """
        logger.info("Connecting to Redis...")
        self._redis_client = aioredis.from_url(
            self._host, encoding="utf-8", decode_responses=True
        )
        try:
            # Ping Redis to test the connection
            await self._redis_client.ping()
            logger.info("Connection to Redis successful.")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._redis_client = None  # Ensure client is None if connection fails
            raise e

    async def close(self) -> None:
        """
        Close the Redis connection pool gracefully.
        This should be called at application shutdown.
        """
        if self._redis_client is None:
            logger.warning("Redis client is not initialized, nothing to close.")
            return

        logger.info("Closing connection to Redis...")
        await self._redis_client.close()
        self._redis_client = None
        logger.info("Connection to Redis closed.")
    
    async def get(self, key: str) -> Optional[Any]:
        """ Get value from Cache"""
        if self._redis_client is None:
            logger.warning("Redis client is not initialized, nothing to get.")
            return
        value = await self._redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set(self, key: str, value: Any, expire: int = 300) -> None:
        """ Set value in Cache"""
        if self._redis_client is None:
            logger.warning("Redis client is not initialized, nothing to set.")
            return
        await self._redis_client.set(key, json.dumps(value), ex=expire)
    
    async def delete(self, key: str) -> None:
        """ Delete value from Cache"""
        if self._redis_client is None:
            logger.warning("Redis client is not initialized, nothing to delete.")
            return
        await self._redis_client.delete(key)

    async def exists (self, key: str) -> bool:
        """ Check if key exists in Cache"""
        if self._redis_client is None:
            logger.warning("Redis client is not initialized, nothing to check.")
            return False
        return await self._redis_client.exists(key)

    def get_client(self) -> Redis:
        """
        Returns the Redis client instance.
        """
        if self._redis_client is None:
            raise Exception("Redis client is not initialized.")
        return self._redis_client


redis_manager = RedisConnectionManager(settings.get_redis_url)


async def get_redis_client() -> Redis:
    """
    Get the Redis client instance.
    This function should be used to access the Redis client in the application.
    """
    if redis_manager._redis_client is None:
        await redis_manager.connect()
    return redis_manager.get_client()
