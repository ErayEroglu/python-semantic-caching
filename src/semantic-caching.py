from typing import List
from upstash_vector import Index
from dotenv import load_dotenv
import os

class SemanticCache:
    def __init__(self, index, min_proximity: float = 0.9):
        self.min_proximity = min_proximity
        self.index = index

    def get(self, key, vector):
        return self.query_key(key,vector)

    def query_key(self, key, input_vector):
        response = self.index.query(
            vector=input_vector,  # Assuming key represents vector data
            top_k=1,
            include_metadata=True
        )
        if response and response[0].score > self.min_proximity:
            return response[0].metadata.get(key)
        return None

    def set(self, key, vector, data):
        self.index.upsert(vectors=[(key, vector, {"value": data})])

    def delete(self, key: str) -> int:
        response = self.index.delete(ids=[key])
        return response['deleted']

    def bulk_delete(self, keys: List[str]) -> int:
        response = self.index.delete(ids=keys)
        return response['deleted']

    def flush(self) -> None:
        self.index.reset()

# Example usage
def main():
    # Load environment variables from .env file
    load_dotenv()

    UPSTASH_VECTOR_REST_URL = os.getenv('UPSTASH_VECTOR_REST_URL')
    UPSTASH_VECTOR_REST_TOKEN = os.getenv('UPSTASH_VECTOR_REST_TOKEN')

    # Initialize Upstash Vector Index
    index = Index(url=UPSTASH_VECTOR_REST_URL, token=UPSTASH_VECTOR_REST_TOKEN)
    
    cache = SemanticCache(index, min_proximity=0.9)

    # Sample vectors (replace with actual vectors)
    vector1 = [0.1, 0.2, 0.3] + [0.0] * 253
    vector2 = [0.4, 0.5, 0.6] + [0.0] * 253

    key1 = "key1"
    key2 = "key2"

    data1 = "value1"
    data2 = "value2"

    # Set the vectors in the cache
    cache.set(key1, vector1, data1)
    cache.set(key2, vector2, data2)

    # Query a single key
    result = cache.get(key1,vector1)
    print(f"Query result for {key1}: {result}")

    # # Query multiple keys
    # results = cache.get([vector1, vector2])
    # print(f"Query results for {key1} and {key2}: {results}")

    # # Delete a key
    # deleted_count = cache.delete(key1)
    # print(f"Deleted count for {key1}: {deleted_count}")

    # # Flush the cache
    # cache.flush()
    # print("Cache flushed")

if __name__ == "__main__":
    main()