import asyncio
import itertools
import time

from aiohttp import TCPConnector
import aiohttp

from cache_tools import CacheCookie
from mail_tools import generate_html


async def get(session, url, query_info):
    common_headers = {
        "Host": "www.csdn.net",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "X-Requested-With": "XMLHttpRequest",
        "X-Tingyun-Id": "im-pGljNfnc;r=77175301",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "Trailers",
    }
    headers = {}
    headers.update(common_headers)
    params = query_info
    async with session.get(url, headers=headers, params=params) as response:
        result = await response.json()
        return result


async def collect_article(session, query):
    page = 3
    results = []
    query_info = {"category": query}
    result = await get_result(session, query_info)
    results.append(result)
    try:
        while page > 0:
            query_info["shown_offset"] = result["articles"][-1]["shown_offset"]
            result = await get_result(session, query_info)
            results.append(result)
            page -= 1
    except Exception as e:
        print(str(e))
    return results


async def get_result(session, query_info):
    sleep_time = 0
    url = "https://www.csdn.net/api/articles"
    result = await get(session, url, query_info)
    await asyncio.sleep(sleep_time)
    return result


async def main():
    t = time.perf_counter()
    async with aiohttp.ClientSession(connector=TCPConnector(ssl=False)) as session:
        cache = CacheCookie(".last_cache_csdn")
        results = []
        results.extend(await collect_article(session, "python"))
        results.extend(await collect_article(session, "web"))
        results.extend(await collect_article(session, "game"))
        # results.extend(await collect_article(session, "career"))
        results.extend(await collect_article(session, "home"))

        def get_entries(results):
            try:
                return results["articles"]
            except Exception:
                return []

        entries = list(map(get_entries, results))

        items = []
        for entry in itertools.chain(*entries):
            title = entry["title"]
            href = entry["url"]
            print(title)
            if href not in cache:
                items.append({"name": title, "href": href})
                cache.add(href)
        cache.save()
        generate_html("CSDN聚合", items)

    print(time.perf_counter() - t)


def run():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


if __name__ == "__main__":
    run()
