import asyncio
from typing import List, Optional, Union
from upstash_vector import Index
from dotenv import load_dotenv
import os


class SemanticCache:
    def __init__(self, index: Index, min_proximity: float = 0.9):
        self.min_proximity = min_proximity
        self.index = index

    async def get(self, key_or_keys: Union[str, List[str]]) -> Optional[Union[str, List[Optional[str]]]]:
        if isinstance(key_or_keys, str):
            return await self.query_key(key_or_keys)
        elif isinstance(key_or_keys, list):
            results = await asyncio.gather(*(self.query_key(key) for key in key_or_keys))
            return results

    async def query_key(self, key: str) -> Optional[str]:
        response = await self.index.query(
            vector=key, 
            top_k=1,
            include_metadata=True
        )
        if response and response[0]['score'] > self.min_proximity:
            return response[0]['metadata'].get('value')
        return None

    async def set(self, key_or_keys: Union[str, List[str]], vector_or_vectors: Union[list, List[list]], value_or_values: Optional[Union[str, List[str]]] = None) -> None:
        if isinstance(key_or_keys, str) and isinstance(vector_or_vectors, list):
            await self.index.upsert(
                vectors=[(key_or_keys, vector_or_vectors, {'value': value_or_values})]
            )
        elif isinstance(key_or_keys, list) and isinstance(vector_or_vectors, list) and isinstance(value_or_values, list):
            upserts = [
                (key, vector, {'value': value})
                for key, vector, value in zip(key_or_keys, vector_or_vectors, value_or_values)
            ]
            for upsert in upserts:
                await self.index.upsert(vectors=[upsert])

    async def delete(self, key: str) -> int:
        response = await self.index.delete(ids=[key])
        return response['deleted']

    async def bulk_delete(self, keys: List[str]) -> int:
        response = await self.index.delete(ids=keys)
        return response['deleted']

    async def flush(self) -> None:
        await self.index.reset()

async def main():
    # Load environment variables from .env file
    load_dotenv()

    UPSTASH_VECTOR_REST_URL = os.getenv('UPSTASH_VECTOR_REST_URL')
    UPSTASH_VECTOR_REST_TOKEN = os.getenv('UPSTASH_VECTOR_REST_TOKEN')

    # Initialize Upstash Vector Index
    index = Index(url=UPSTASH_VECTOR_REST_URL, token=UPSTASH_VECTOR_REST_TOKEN)
    
    cache = SemanticCache(index, min_proximity=0.9)

    # Sample vectors (replace with actual vectors)
    vector1 = [0.1, 0.2, 0.3]
    vector2 = [0.4, 0.5, 0.6]

    key1 = "key1"
    key2 = "key2"

    data1 = "value1"
    data2 = "value2"

    # Set the vectors in the cache
    await cache.set(key1, vector1, data1)
    await cache.set(key2, vector2, data2)

    # Query a single key
    result = await cache.get(key1)
    print(f"Query result for {key1}: {result}")

    # Query multiple keys
    results = await cache.get([key1, key2])
    print(f"Query results for {key1} and {key2}: {results}")

    # Delete a key
    deleted_count = await cache.delete(key1)
    print(f"Deleted count for {key1}: {deleted_count}")

    # Flush the cache
    await cache.flush()
    print("Cache flushed")

# Run the example
asyncio.run(main())
