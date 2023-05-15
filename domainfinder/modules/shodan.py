from collections import defaultdict
import httpx
from lxml import html
from helpers.helpers import clean_uniq_results
from helpers.display import error


async def get_internetdb_info(target: str, verbose: bool) -> dict:
    results = defaultdict(list)
    client = httpx.AsyncClient()
    response = await client.get(f"https://internetdb.shodan.io/{target}")
    if response.status_code != 200:
        await client.aclose()
        error(f"[Shodan InternetDB] Error: status code: {response.status_code}")
        return {}
    results[target].extend(response.json()["hostnames"])
    results = clean_uniq_results(results)
    if verbose:
        for values in results.values():
            for value in values:
                info(f"[Shodan InternetDB] {value}")
    return results


async def get_host(target: str, verbose: bool, apikey: str) -> dict:
    results = defaultdict(list)
    client = httpx.AsyncClient(timeout=5)

    if apikey is not None:
        response = await client.get(
            f"https://api.shodan.io/shodan/host/{target}",
            params={"key": apikey, "minify": "true"},
        )
        await client.aclose()
        if response.status_code != 200:
            error(f"[Shodan] Error: status code: {response.status_code}")
            return {}
        data = response.json()
        results[target].extend(data["hostnames"])
        results[target].extend(data["domains"])
        results = clean_uniq_results(results)
        if verbose:
            for values in results.values():
                for value in values:
                    info(f"[Shodan API] {value}")
    else:
        response = await client.get(f"https://www.shodan.io/host/{target}")
        await client.aclose()
        if response.status_code != 200:
            error(f"[Shodan] Error: status code: {response.status_code}")
            return {}
        tree = html.fromstring(response.content)
        domains = tree.xpath("//td/strong[position() = 1]")[0].text_content().split(", ")
        results[target].extends(domains)
        results = clean_uniq_results(results)
        for values in results.values():
            for value in values:
                info(f"[Shodan] {value}")
    return results
