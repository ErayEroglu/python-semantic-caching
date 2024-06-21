from time import sleep
import spacy
from typing import List
from upstash_vector import Index, Vector
from dotenv import load_dotenv
import os


class SemanticCache:
    id = 0
    def __init__(self, index, min_proximity: float = 0.9):
        self.min_proximity = min_proximity
        self.index = index

    def get(self, key):
        vector = self.text_to_vector(key)
        response = self.query_key(vector)
        if response == None:
            return None
        if response.score > self.min_proximity:
            return next(iter(response.metadata.items()))[1]

    def query_key(self, input_vector):
        response = self.index.query(
            vector=input_vector,
            top_k=1,
            include_metadata=True
        )
        return response[0] if response else None

    def set(self, key, data):
        if (type(key) == list) and (type(data) == list):
            for i in range(len(key)):
                self.index.upsert(
                    vectors=[Vector(id=str(self.id), vector=self.text_to_vector(key[i]), metadata={key[i]: data[i]})])
                self.id += 1
        elif (type(key) == str) and (type(data) == str):
            self.index.upsert(vectors=[Vector(id=str(self.id), vector=self.text_to_vector(key), metadata={key: data})])
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
        vector = self.text_to_vector(key)
        response = self.query_key(vector)
        if response:
            return response.id
        return None
    
    def text_to_vector(self,text):
        nlp = spacy.load("en_core_web_sm") 
        doc = nlp(text)
        return doc.vector.tolist()

def main():
    
    load_dotenv()
    UPSTASH_VECTOR_REST_URL = os.getenv('UPSTASH_VECTOR_REST_URL')
    UPSTASH_VECTOR_REST_TOKEN = os.getenv('UPSTASH_VECTOR_REST_TOKEN')

    # Initialize Upstash Vector Index
    index = Index(url=UPSTASH_VECTOR_REST_URL, token=UPSTASH_VECTOR_REST_TOKEN)
    cache = SemanticCache(index=index, min_proximity=0.7)
    cache.set('The most crowded city in Turkiye', 'Istanbul')
    sleep(1)
    result = cache.get('Which city has the most population in Turkiye?')
    sleep(1)
    #print(result)
    
    
if __name__ == '__main__':
    main()