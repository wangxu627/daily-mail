import asyncio
import itertools
import time

import aiohttp

from cache_tools import CacheCookie
from mail_tools import generate_html


async def post(session, url):
    common_headers = {
        "Host": "www.jianshu.com",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0",
        "Accept": "application/json",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Origin": "https://www.jianshu.com",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "Trailers",
    }
    headers = {
        "Cookie": "UM_distinctid=1842eccd9601f-0535b7b9197c3a-26021e51-384000-1842eccd961939; _ga=GA1.2.1597607952.1667232488; __bid_n=1842eccda7aa7129134207; FPTOKEN=30$BJXnD14IsJvdRZD3ebdaF4k+Va+JND7nVK1IrBO/dynz3CFnu3CZ2E3sY/jXFlLNnsda+4uVOdajdmEuRSUpeFRfYrNBVJv+oRiHdBEbp1ky1BM8LvXov/dKLCp052HPVKyoF+TX/55AoeHSKD2ocbECjtKCG0X46RSDuT/zJ0VM/hf1QMIBEFFbvGZDGc9MWRtunCLWeTk7rnxf/poUfhtDcSf5pxJmjRSKbcSlYa/zmEC7c9/UbfHFLDWtWwrGVQHlY7DQ6jsUF8+VipImV1CK+mTt7cCq3vZdBaK7pZeHTZ27lNyWQHKyKnMeqCmuz1Nyb+yDpDawApqZ5F6qc/1m3fMNzG41XCVw/IJC23/6YbZT7NobEo1SBwPMX789IRAoqQhkCUS05DFDfjo1A6OfqT4DRAMplrgGiv+/AuU=|df6DcyAivm9Fq74KnZZuNYgjZTthaz2Zr8D/x0s6/lw=|10|5cab6e6c24c6355bedbe2e2e8feffe46; Hm_lvt_1c6cd6a9fd5f687d8040b44bebe5d395=1667232489,1668733290; CNZZDATA1279807957=1005973712-1667229157-https%3A%2F%2Fwww.baidu.com%2F|1668740900; read_mode=day; default_font=font2; locale=zh-CN; sensorsdata2015jssdkcross={\"distinct_id\":\"1842eccd7183dc-0aad9397603947-26021e51-3686400-1842eccd719b3d\",\"first_id\":\"\",\"props\":{\"$latest_traffic_source_type\":\"直接流量\",\"$latest_search_keyword\":\"未取到值_直接打开\",\"$latest_referrer\":\"\"},\"$device_id\":\"1842eccd7183dc-0aad9397603947-26021e51-3686400-1842eccd719b3d\"}; Hm_lvt_0c0e9d9b1e7d617b3e6842e85b9fb068=1670128528,1670374695,1671412614,1671593756; FEID=v10-2b47f214b4ca624670d16604781c54de23a822d6; __xaf_fpstarttimer__=1671593757033; __xaf_ths__={\"data\":{\"0\":1,\"1\":43200,\"2\":60},\"id\":\"1b531314-6cd5-4e23-a0d3-fac8bededb54\"}; __xaf_thstime__=1671593757184; FPTOKEN=w3HYfAQ9hS8IFh8s0guNsrfXd1NO563FW4B249g3PokHls1AMQ3LoS9P0Z5+G35AqnPwfkzJa7BpJHVrCzHajnETfFVzCijn0RSNquPq9+ooRFlZTPdY8k+wwHjCNp+K3bqTpZLjKn2t37WB9+7neo2SCfzO/ZscRaro/lO767Psl1BZUg/xn4+kZqR56GkznVZd+qH7etCgcX5/pIj6EaL/+VcW4iYBayH/BEAplYOarAfNdSwoVZR6lyw+knZEFBsuBxIBRGT6f2sWw/RVpmbMr/qsQ6nR0LA9oxzJQBR314DFIZKKW5SwxuY/QcgcaYF1Tn4e7mt0INZ7jonC5r8Zr0pCuL+5NxwUSq/R86ZFRBEXwrQHv1jDhE9wPXD7ZEVfb2IJqYLV25IT+3xNYw==|eZrmR8tqPy1wg7/pdWjqnOepFziQgH9oqe67/PG/LXw=|10|a13dde2fe6896201942a0da3635dc476; __xaf_fptokentimer__=1671593757348; _m7e_session_core=316bcf504bdc7fb87ab938fa36c2282e; Hm_lpvt_0c0e9d9b1e7d617b3e6842e85b9fb068=1671593765; signin_redirect=https://www.jianshu.com/search?q=python&page=1&type=note",
        "X-CSRF-Token": "Z+A4UVURKfhxUeJVRWMk5EqK7mLzF281HBZbR3dA2ocvkH8iEtA9hADZz40sCSxGVA4TcWILEVgcsxlhUUQ0NA==",
    }
    headers.update(common_headers)
    async with session.post(url, headers=headers) as response:
        result = await response.json()
        return result


async def collect_article(session, query, page):
    results = []
    for i in range(page):
        results.append(await get_result(session, query, i + 1))
    for i in range(page):
        results.append(await get_result(session, query, i + 1, "published_at"))
    return results


async def get_result(session, query, page, order_by="default"):
    sleep_time = 2
    url = f"https://www.jianshu.com/search/do?q={query}&type=note&page={page}&order_by={order_by}"
    result = await post(session, url)
    await asyncio.sleep(sleep_time)
    return result

# https://www.jianshu.com/search/do?q=python&type=note&page=1&order_by=default
# https://www.jianshu.com/search/do?q=python&type=note&page=1&order_by=default
async def main():
    t = time.perf_counter()
    async with aiohttp.ClientSession() as session:
        cache = CacheCookie(".last_cache_jianshu")
        results = []
        results.extend(await collect_article(session, "python", 3))
        results.extend(await collect_article(session, "javascript", 3))
        results.extend(await collect_article(session, "css", 3))
        results.extend(await collect_article(session, "html", 3))

        get_entries = lambda content: content.get("entries", [])
        entries = list(map(get_entries, results))

        items = []
        for entry in itertools.chain(*entries):
            href = f'https://www.jianshu.com/p/{entry["slug"]}'
            if href not in cache:
                items.append({"name": entry["title"], "href": href})
                cache.add(href)

        cache.save()
        generate_html("简书聚合", items)
    print(time.perf_counter() - t)


def run():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


if __name__ == "__main__":
    run()
