from collections import defaultdict
import httpx
from lxml import html
from helpers.helpers import clean_uniq_results
from helpers.display import info, error


async def get_host(target: str, verbose: bool, apikey: str) -> dict:
    results = defaultdict(list)
    client = httpx.AsyncClient()
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0"}

    if apikey is not None:
        response = await client.get(
            "https://api.viewdns.info/reverseip/",
            params={"host": target, "output": "json", "apikey": apikey},
            headers=headers,
        )
        await client.aclose()
        if response.status_code != 200:
            error(f"[ViewDNS] Error: status code: {response.status_code}")
            return {}

        data = response.json()
        if data["response"]["domain_count"] != "0":
            for domains in data["response"]["domains"]:
                if verbose:
                    info(f"[ViewDNS] {domains['name']}")
                results[target].append(domains["name"])
            results = clean_uniq_results(results)
    else:
        response = await client.get("https://viewdns.info/reverseip/", params={"host": target, "t": 1}, headers=headers)
        await client.aclose()
        if response.status_code != 200:
            error(f"[ViewDNS] Error: status code: {response.status_code}")
            return {}
        tree = html.fromstring(response.content)

        domains = tree.xpath("//table[position() = 1]/tr[position() >= 2]/td[position() = 1]")
        for domain in domains:
            if verbose:
                info(f"[ViewDNS] {domain.text_content()}")
            results[target].append(domain.text_content())
        results = clean_uniq_results(results)
    return results
