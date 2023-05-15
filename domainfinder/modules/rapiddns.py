from lxml import html
from collections import defaultdict
import httpx
from helpers.helpers import clean_uniq_results
from helpers.display import info, error
import asyncio


async def get_host(target: str, verbose: bool):
    results = defaultdict(list)
    client = httpx.AsyncClient()

    response = await client.get(f"https://rapiddns.io/sameip/{target}?full=1")
    await client.aclose()
    if response.status_code != 200:
        error(f"[RapidDns] Error: status code: {response.status_code}")
        return {}
    tree = html.fromstring(response.content)
    domains = [domain.text_content() for domain in tree.xpath("//table[@id='table']/tbody/tr/td[position() = 1]")]
    # _address = [address.text_content() for address in tree.xpath("//table[@id='table']/tbody/tr/td[position() = 2]")]
    # _record = [record.text_content() for record in tree.xpath("//table[@id='table']/tbody/tr/td[position() = 3]")]

    for domain in domains:
        if verbose:
            info(f"[RapidDNS] {domain}")
        if "/" in str(target):
            target = target.split("/")[0]
        results[target].append(domain)
    results = clean_uniq_results(results)
    return results
