import concurrent.futures
import json
from functools import partial
from typing import List


def flatten_list(l: List) -> List:
    return [el for sublist in l for el in sublist]


def split_list_sublists(ids: List, chunksize: int = 100) -> List[List]:
    """Return a list of lists such that the max len of the inner lists is chunksize"""
    ids_chunks = [ids[i*chunksize:i*chunksize+chunksize] for i in range(int(len(ids)/chunksize) + 1)]
    return ids_chunks


def parallel_map(function, iterable, max_workers: int = 100, *args, **kwargs, ):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        result = pool.map(partial(function, *args, **kwargs), iterable)
        return list(result)


def jprint(data):
    """Prints JSON-like string (data) nicely"""
    print(json.dumps(data, indent=4, ensure_ascii=False))


def delete_duplicates_by_key(l: List[dict], key: str, elements_in_result: set = None) -> List[dict]:
    if not elements_in_result:
        elements_in_result = set()
    result = []
    for el in l:
        attr = el.get(key)
        if attr not in elements_in_result:
            result.append(el)
            elements_in_result.add(attr)
    return result
