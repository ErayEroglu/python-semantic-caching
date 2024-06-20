from time import sleep
import unittest
from semantic_caching import SemanticCache
from upstash_vector import Index, Vector
from dotenv import load_dotenv
import os

load_dotenv()

UPSTASH_VECTOR_REST_URL = os.getenv('UPSTASH_VECTOR_REST_URL')
UPSTASH_VECTOR_REST_TOKEN = os.getenv('UPSTASH_VECTOR_REST_TOKEN')

# Initialize Upstash Vector Index
index = Index(url=UPSTASH_VECTOR_REST_URL, token=UPSTASH_VECTOR_REST_TOKEN)

class TestSemanticCache(unittest.TestCase):
    vector1 = [0.1, 0.2, 0.3] + [0.0] * 253
    vector2 = [0.4, 0.5, 0.6] + [0.0] * 253
    key1 = "key1"
    key2 = "key2"
    data1 = "value1"
    data2 = "value2"
    
    def setUp(self):
        # Initialize the SemanticCache instance
        self.cache = SemanticCache(index=index, min_proximity=0.9)
        self.refresh()
        
    def test_get_existing_key(self):
        # Set up a key-value pair in the cache

        self.cache.set(self.key1, self.vector1, self.data1)
        sleep(1)
        # Retrieve the value using the key
        result = self.cache.get(self.key1, self.vector1)
        sleep(1)
        # Assert that the retrieved value is correct
        self.assertEqual(result, self.data1)
        self.refresh()

    def test_get_nonexistent_key(self):
        
        # Retrieve a non-existent key
        result = self.cache.get("nonexistent_key",  self.vector1)

        # Assert that the result is None
        self.assertIsNone(result)
        self.refresh()
        
    def test_set_multiple_key_values(self):
        # Set up multiple key-value pairs in the cache
        keys = [self.key1, self.key2]
        vectors = [self.vector1,  self.vector2]
        data = [self.data1, self.data2]
        self.cache.set(keys, vectors, data)
        sleep(1)
        # Retrieve the values using the keys
        result1 = self.cache.get(keys[0], vectors[0])
        sleep(1)
        result2 = self.cache.get(keys[1], vectors[1])
        sleep(1)
        # Assert that the retrieved values are correct
        self.assertEqual(result1, data[0])
        self.assertEqual(result2, data[1])
        self.refresh()
        
    def test_delete_existing_key(self):
        self.cache.set(self.key1, self.vector1, self.data1)

        # Delete the key
        self.cache.delete(self.vector1)

        # Retrieve the value using the key
        result = self.cache.get(self.key1, self.vector1)

        # Assert that the result is None
        self.assertIsNone(result)
        self.refresh()
        
    def test_delete_nonexistent_key(self):
        # Set up a key-value pair in the cache
        key = self.key1
        vector = self.vector1
        data = self.data1
        self.cache.set(key, vector, data)

        # Delete a non-existent key
        result = self.cache.delete([0.4, 0.5, 0.6] + [0.0] * 253)

        # Assert that the result is False
        self.assertFalse(result)
        self.refresh()
        
    def test_bulk_delete(self):
        # Set up multiple key-value pairs in the cache
        keys = [self.key1, self.key2, "key3"]
        vectors = [self.vector1, self.vector2, [0.7, 0.8, 0.9] + [0.0] * 253]
        data = [self.data1, self.data2, "value3"]
        self.cache.set(keys, vectors, data)

        # Delete multiple keys
        self.cache.bulk_delete(keys)

        # Retrieve the values using the keys
        result1 = self.cache.get(keys[0], vectors[0])
        result2 = self.cache.get(keys[1], vectors[1])
        result3 = self.cache.get(keys[2], vectors[2])

        # Assert that the results are None
        self.assertIsNone(result1)
        self.assertIsNone(result2)
        self.assertIsNone(result3)
        self.refresh()

    def test_flush(self):
        # Set up a key-value pair in the cache
        key = self.key1
        vector = self.vector1
        data = self.data1
        self.cache.set(key, vector, data)

        # Flush the cache
        self.cache.flush()

        # Retrieve the value using the key
        result = self.cache.get(key, vector)

        # Assert that the result is None
        self.assertIsNone(result)
        self.refresh()
        
    def refresh(self):
        self.cache.flush()
        sleep(1)

if __name__ == "__main__":
    unittest.main()