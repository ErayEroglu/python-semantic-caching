import asyncio
from collections import OrderedDict
from upstash_redis.asyncio import Redis
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

UPSTASH_REDIS_REST_URL = os.getenv('UPSTASH_REDIS_REST_URL')
UPSTASH_REDIS_REST_TOKEN = os.getenv('UPSTASH_REDIS_REST_TOKEN')

redis = Redis(url=UPSTASH_REDIS_REST_URL, token=UPSTASH_REDIS_REST_TOKEN)

class Query:
    def __init__(self, key: str, params: dict, data: any):
        self.key = key
        self.params = params
        self.data = data

class SemanticCache:
    def __init__(self, min_proximity: float = 0.9):
        self.cache = OrderedDict()
        self.min_proximity = min_proximity

    async def get(self, key_or_keys):
        if isinstance(key_or_keys, str):
            return await self.query_key(key_or_keys)
        elif isinstance(key_or_keys, list):
            return await asyncio.gather(*(self.query_key(key) for key in key_or_keys))

    async def query_key(self, key):
        value = await redis.get(key)
        return value

    async def set(self, key_or_keys, value_or_values):
        if isinstance(key_or_keys, str) and isinstance(value_or_values, str):
            await redis.set(key_or_keys, value_or_values)
        elif isinstance(key_or_keys, list) and isinstance(value_or_values, list):
            await asyncio.gather(*(redis.set(key, value) for key, value in zip(key_or_keys, value_or_values)))

    async def delete(self, key):
        result = await redis.delete(key)
        return result

    async def bulk_delete(self, keys):
        result = await asyncio.gather(*(self.delete(key) for key in keys))
        return result

    async def flush(self):
        keys = await redis.keys('*')
        await asyncio.gather(*(self.delete(key) for key in keys))

# Example usage
async def main():
    cache = SemanticCache(min_proximity=0.9)

    query1 = Query(key="q1", params={"param1": "value1"}, data="result1")
    query2 = Query(key="q1", params={"param1": "value2"}, data="result2")

    await cache.set(query1.key, query1.data)
    result = await cache.get("q1")
    print(result)  # Output: the actual result from the Upstash Redis

# Run the example
asyncio.run(main())
