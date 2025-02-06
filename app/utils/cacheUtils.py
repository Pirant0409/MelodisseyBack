import diskcache
cache = diskcache.Cache('cache_dir')
access_counter = diskcache.Cache('access_counter')

def get_from_cache(query):
    if (query in cache):
        access_counter[query] = access_counter.get(query,0) +1
        return cache[query]
    else:
        return False
    
def save_on_cache(query,result):
    cache[query] = result
    access_counter[query] = 1
    print("Cache created for", query)