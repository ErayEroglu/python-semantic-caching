import json
from time import sleep
from typing import List
from upstash_vector import Index
from dotenv import load_dotenv
import os
from langchain.globals import set_llm_cache
from langchain_openai import OpenAI
from langchain_core.outputs.generation import Generation
import time

class SemanticCache:
    id = 0
    is_cached = False
    
    def __init__(self, url, token, min_proximity: float = 0.9):
        self.min_proximity = min_proximity
        self.index = Index(url=url, token=token)

    def get(self, key):
        response = self.query_key(key)
        if response is None or response.score <= self.min_proximity:
            return None
        self.is_cached = True
        return self._loads_generations(response.metadata['data'])
         
    def lookup(self, prompt, llm_string : str = None):
        return self.get(prompt)
    
    def update(self, prompt,  llm_string : str = None, result : str = None):
        self.set(prompt, self._dumps_generations(result))

    def query_key(self, key):
        response = self.index.query(
            data=key,
            top_k=1,
            include_metadata=True
        )
        return response[0] if response else None

    def set(self, key, data):
        if (type(key) == list) and (type(data) == list):
            for i in range(len(key)):
                self.index.upsert([(str(self.id), key[i], {'data': data[i]})])
                self.id += 1
        else:
            self.index.upsert([(str(self.id), key, {'data' : data})])
            self.id += 1

    def delete(self, key):
        id = self.find_id(key)
        if id:
            self.index.delete(id)
        else:
            return False
        
    def bulk_delete(self, keys: List[str]):
        for key in keys:
            self.delete(key)
        
    def flush(self):
        self.index.reset()

    def is_2d_list(self, lst):
        return isinstance(lst, list) and all(isinstance(sublist, list) for sublist in lst)

    def find_id(self, key):
        response = self.query_key(key)
        if response:
            return response.id
        return None
    
    def _dumps_generations(self, generations):
        def generation_to_dict(generation):
            if isinstance(generation, Generation):
                return {
                    "text": generation.text,
                    "generation_info": generation.generation_info
                }
            else:
                raise TypeError(f"Object of type {generation.__class__.__name__} is not JSON serializable")
        return json.dumps([generation_to_dict(g) for g in generations])

    def _loads_generations(self, json_str):
        def dict_to_generation(d):
            if isinstance(d, dict):
                return Generation(text=d["text"], generation_info=d["generation_info"])
            else:
                raise TypeError(f"Object of type {d.__class__.__name__} is not a valid Generation dict")

        return [dict_to_generation(d) for d in json.loads(json_str)]

        

def main():
    # set environment variables
    load_dotenv()
    UPSTASH_VECTOR_REST_URL = os.getenv('UPSTASH_VECTOR_REST_URL')
    UPSTASH_VECTOR_REST_TOKEN = os.getenv('UPSTASH_VECTOR_REST_TOKEN')

    # initialize Upstash database
    cache = SemanticCache(url=UPSTASH_VECTOR_REST_URL, token=UPSTASH_VECTOR_REST_TOKEN, min_proximity=0.7)
    cache.flush()
    sleep(1)
    
    llm = OpenAI(model_name="gpt-3.5-turbo-instruct", n=2, best_of=2)
    set_llm_cache(cache)
    
    prompt1 = "Why is the Moon always showing the same side?"
    prompt2 = "How come we always see one face of the moon?"

    start_time = time.time()
    response1 = llm.invoke(prompt1)
    print(response1)
    end_time = time.time()
    print("Time difference 1:", end_time - start_time, "seconds")
    sleep(1)
    
    start_time = time.time()
    response2 = llm.invoke(prompt2)
    print(response2)
    end_time = time.time()
    time_difference = end_time - start_time
    print("Time difference 2:", time_difference, "seconds")

if __name__ == '__main__':
    main()

