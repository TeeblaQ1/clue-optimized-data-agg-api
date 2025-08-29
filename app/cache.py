import os
from cachetools import TTLCache, cached
from dotenv import load_dotenv

load_dotenv()

CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", 300))

report_cache = TTLCache(maxsize=128, ttl=CACHE_TTL)

def cached_report(func):
    def cache_key(*args, **kwargs):
        # Extract sql and params from kwargs to create a unique cache key
        sql = kwargs.get("sql")
        params = kwargs.get("params", {})
        # Create a hashable key from the SQL and sorted params
        return (sql, tuple(sorted(params.items())))
    
    return cached(
        cache=report_cache,
        key=cache_key
    )(func)

# def clear_cache():
#     report_cache.clear()
