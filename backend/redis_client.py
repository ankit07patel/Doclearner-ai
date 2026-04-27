import redis.asyncio as redis
from config import REDIS_URL

client = redis.from_url(REDIS_URL)

async def cache_message(session_id: str, role: str, content: str):
    message = f"{role}:{content}"
    await client.rpush(f"chat:{session_id}", message)
    await client.ltrim(f"chat:{session_id}", -10, -1)  # keep last 10 messages
    await client.expire(f"chat:{session_id}", 3600)  # expire in 1 hour

async def get_cached_messages(session_id: str):
    messages = await client.lrange(f"chat:{session_id}", 0, -1)
    result = []
    for msg in messages:
        role, content = msg.decode().split(":", 1)
        result.append({"role": role, "content": content})
    return result
async def check_rate_limit(user_id: str) -> bool:
    key = f"ratelimit:{user_id}"
    count = await client.incr(key)
    if count == 1:
        await client.expire(key, 60)  # 60 second window
    return count <= 10  # 10 requests per minute