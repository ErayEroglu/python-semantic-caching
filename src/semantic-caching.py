from time import sleep
from typing import List
from upstash_vector import Index, Vector
from dotenv import load_dotenv
import os

load_dotenv()

UPSTASH_VECTOR_REST_URL = os.getenv('UPSTASH_VECTOR_REST_URL')
UPSTASH_VECTOR_REST_TOKEN = os.getenv('UPSTASH_VECTOR_REST_TOKEN')

# Initialize Upstash Vector Index
index = Index(url=UPSTASH_VECTOR_REST_URL, token=UPSTASH_VECTOR_REST_TOKEN)

class SemanticCache:
    id = 0
    def __init__(self, index, min_proximity: float = 0.9):
        self.min_proximity = min_proximity
        self.index = index

    def get(self, key, vector):
        response = self.query_key(vector)
        print(response)
        if response == None:
            return None
        if response.score > self.min_proximity:
            return response.metadata[key]

    def query_key(self, input_vector):
        response = self.index.query(
            vector=input_vector,
            top_k=1,
            include_metadata=True
        )
        return response[0] if response else None

    def set(self, key, vector, data):
        if (type(key) == list) and (type(data) == list) and self.is_2d_list(vector):
            for i in range(len(key)):
                self.index.upsert(
                    vectors=[Vector(id=str(self.id), vector=vector[i], metadata={key[i]: data[i]})])
                self.id += 1
        elif (type(key) == str) and (type(data) == str) and type(vector) == list:
            self.index.upsert(vectors=[Vector(id=str(self.id), vector=vector, metadata={key: data})])
            self.id += 1

    def delete(self, vector):
        id = self.find_id(vector)
        if id:
            response = self.index.delete(id)
            return response.deleted
        return None
        
    def bulk_delete(self, keys: List[str]) -> int:
        response = self.index.delete(ids=keys)
        
    def flush(self):
        self.index.reset()

    def is_2d_list(self, lst):
        return isinstance(lst, list) and all(isinstance(sublist, list) for sublist in lst)

    def find_id(self, vector):
        response = self.query_key(vector)
        if response:
            return response.id
        return None
    
def main():
    # Load environment variables from .env file
    
    cache = SemanticCache(index, min_proximity=0.9) 
    # Sample vectors (replace with actual vectors)
    vector1 = [0.1, 0.2, 0.3] + [0.0] * 253
    vector2 = [0.4, 0.5, 0.6] + [0.0] * 253

    key1 = "key1"
    data1 = "value1"
    key2 = "key2"
    data2 = "value2"

    # Set the vectors in the cache 
    cache.set(key1, vector1, data1)
    sleep(1)
    cache.set(key2, vector2, data2)
    sleep(1)
    # Query a single key
    result1 = cache.get(key1,vector1)
    sleep(1)
    result2 = cache.get(key2,vector2)
    sleep(1)
    print(f"Query result for {key1}: {result1}")
    print(f"Query result for {key2}: {result2}")

    # Delete a key
    print(cache.delete(vector1))
    sleep(1)
    print(cache.delete(vector2))
    sleep(1)
    result = cache.get(key1,vector1)
    sleep(1)
    print(f"Query result for {key1}: {result}")
    cache.flush()
    sleep(1)

    
    # # Set multiple keys in the cache
    # lst = [key1, key2]
    # data = [value1, value2]
    # vectors = [vector1, vector2]
    # cache.set(lst, vectors, data)
    


if __name__ == "__main__":
    main()