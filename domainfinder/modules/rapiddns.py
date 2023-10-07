from lxml import html
from collections import defaultdict
import httpx
from domainfinder.helpers.helpers import clean_uniq_results
from domainfinder.helpers.display import info, error
import asyncio


async def get_host(target: str, client, verbose: bool):
    results = defaultdict(list)
    limits = httpx.Limits(max_connections=10)
    #client = httpx.AsyncClient(limits=limits)

    response = await client.get(f"https://rapiddns.io/sameip/{target}?full=1")
    #await client.aclose()
    if response.status_code != 200:
        error(f"[RapidDns] Error: status code: {response.status_code}")
        return {}
    tree = html.fromstring(response.content)
    domains = [domain.text_content() for domain in tree.xpath("//table[@id='table']/tbody/tr/td[position() = 1]")]
    # _address = [address.text_content() for address in tree.xpath("//table[@id='table']/tbody/tr/td[position() = 2]")]
    # _record = [record.text_content() for record in tree.xpath("//table[@id='table']/tbody/tr/td[position() = 3]")]

    if verbose:
        info(f"[RapidDNS] {len(domains)} domains found")
    for domain in domains:
        if verbose:
            info(f"[RapidDNS] {domain}")
        if "/" in str(target):
            target = target.split("/")[0]
        results[target].append(domain)
    results = clean_uniq_results(results)
    return results
