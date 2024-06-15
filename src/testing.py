import os
import time
import langchain
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_openai import OpenAI
from langchain.cache import UpstashRedisCache
from upstash_redis import Redis


load_dotenv()
URL = os.getenv("UPSTASH_REDIS_REST_URL")
TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")

llm = OpenAI(model_name="gpt-3.5-turbo-instruct", n=2, best_of=2)
embedding = OpenAIEmbeddings()
langchain.llm_cache = UpstashRedisCache(redis_=Redis(url=URL, token=TOKEN))

current_time = time.time()
print(llm.invoke("Tell me a joke"))
print("Time taken:", time.time() - current_time)

current_time = time.time()
print(llm.invoke("Tell me a joke"))
print("Time taken:", time.time() - current_time)
