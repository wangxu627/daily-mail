import asyncio
import itertools
import time

from aiohttp import TCPConnector
import aiohttp

from cache_tools import CacheCookie
from mail_tools import generate_html

cursor_map = {}


async def post(session, url, query_info):
    async with session.post(url, json=query_info) as response:
        result = await response.json()
        return result


def get_query_info(query, cursor = None):
    return {
        "key_word": query,
        "cursor": (cursor if cursor else "0") 
    }


async def collect_article(session, query):
    results = []
    query_info = get_query_info(query)
    if query_info is None:
        raise Exception("No query info")
    results.append(await get_result(session, query_info))
    query_info = get_query_info(query, cursor_map[query])
    results.append(await get_result(session, query_info))
    return results


async def get_result(session, query_info):
    sleep_time = 0
    url = "https://api.juejin.cn/search_api/v1/search"
    result = await post(session, url, query_info)
    await asyncio.sleep(sleep_time)
    cursor_map[query_info["key_word"]] = result["cursor"]
    return result


async def main():
    t = time.perf_counter()
    async with aiohttp.ClientSession(connector=TCPConnector(ssl=False)) as session:
        cache = CacheCookie(".last_cache_juejin")
        results = []
        results.extend(await collect_article(session, "python"))
        results.extend(await collect_article(session, "javascript"))
        results.extend(await collect_article(session, "css"))
        results.extend(await collect_article(session, "hot"))

        def get_entries(results):
            try:
                return results["data"]
            except Exception:
                return []

        entries = list(map(get_entries, results))

        items = []
        tt = itertools.chain(*entries)
        for entry in itertools.chain(*entries):
            if(entry["result_type"] == 2):
                entry = entry["result_model"]["article_info"]
                title = entry["title"]
                href = "https://juejin.im/post/" + entry["article_id"]
                print(title, href)
                if href not in cache:
                    items.append({"name": title, "href": href})
                    cache.add(href)
                else:
                    print("CCCCCCCCCCCC")

        cache.save()
        generate_html("掘金聚合", items)

    print(time.perf_counter() - t)


def run():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    
if __name__ == "__main__":
    run()

