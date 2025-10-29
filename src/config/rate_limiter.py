from fastapi import Request, HTTPException, status
from src.config.cache import RedisConnectionManager
from src.config.cache import get_redis_client
from src.config.settings import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)

class RateLimiter :
    def __init__ (self, redis_client: RedisConnectionManager) -> None:
        self._redis = redis_client
        self.max_requests = settings.RATE_LIMIT_REQUESTS_PER_MINUTE
        self.window = 60

    async def check_rate_limit (self, client_id: str) -> bool:
        """ Check if the client has exceeded the rate limit."""
        if not self._redis._redis_client:
            return True
        key = f"rate_limit:{client_id}"
        current = await self._redis.get(key)

        if current is None:
            await self._redis.set(key, self.window, 1)
            return True
        
        if int(current) >= self.max_requests:
            return False
        
        await self._redis.incr(key)
        return True
    

async def rate_limit_dependency(request: Request):
    """FastAPI dependency for rate limiting"""
    cache_client = await get_redis_client()
    rate_limiter = RateLimiter(cache_client)
    client_id = request.client.host if request.client else "unknown"
    
    if not await rate_limiter.check_rate_limit(client_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )