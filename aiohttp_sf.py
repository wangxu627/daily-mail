import asyncio
import itertools
import time

from aiohttp import TCPConnector
import aiohttp
from bs4 import BeautifulSoup

from cache_tools import CacheCookie
from mail_tools import generate_html

cursor_map = {}


async def get(session, url):
    # async with session.get(url) as response:
    #     result = await response.text()
    #     return result
    async with session.get(url) as response:
        result = await response.json()
        return result


async def collect_article(session, query):
    # global cursor_map
    results = []
    if query is None:
        raise Exception("No query info")
    results.append(await get_result(session, query))
    results.append(await get_result(session, query, cursor_map.get(query)))
    return results


async def get_result(session, query, cursor=0):
    sleep_time = 0
    # url = f"https://segmentfault.com/t/{query}"
    url = f"https://segmentfault.com/gateway/tag/{query}/stream?loadMoreType=scroll&initData=false&page=1&sort=newest&offset={cursor}"
    result = await get(session, url)
    await asyncio.sleep(sleep_time)
    if(isinstance(result, dict)):
        cursor_map[query] = result["offset"]
    else:
        print(url)
        print(result)
    return result


async def main():
    t = time.perf_counter()
    async with aiohttp.ClientSession(connector=TCPConnector(ssl=False)) as session:
        cache = CacheCookie(".last_cache_segment_fault")
        results = []
        results.extend(await collect_article(session, "python"))
        results.extend(await collect_article(session, "frontend"))
        results.extend(await collect_article(session, "backend"))
        results.extend(await collect_article(session, "game"))

        def get_entries(results):
            try:
                # soup = BeautifulSoup(results, "html.parser")
                # li_list = soup.select("ul.list-group.list-group-flush > li")
                # data = []
                # for li in li_list:
                #     a = li.select("div.content > h3 > a")
                #     data.append({
                #         "url": a[0]["href"],
                #         "title": a[0].string
                #     })
                # return data
                return results["rows"]
            except Exception:
                return []

        entries = list(map(get_entries, results))

        items = []
        for entry in itertools.chain(*entries):
            if (entry["type"] == "article"):
                title = entry["title"]
                href = entry["url"]
                if href not in cache:
                    items.append(
                        {"name": title, "href": f"https://segmentfault.com{href}"}
                    )
                    cache.add(href)

        cache.save()
        generate_html("Segment Fault聚合", items)

    print(time.perf_counter() - t)


def run():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

if __name__ == "__main__":
    run()
