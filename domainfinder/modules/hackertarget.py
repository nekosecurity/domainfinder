from collections import defaultdict
import httpx
from domainfinder.helpers.helpers import clean_uniq_results
from domainfinder.helpers.display import info, error


async def get_host(target: str, verbose: bool, apikey: str) -> dict:
    results = defaultdict(list)
    client = httpx.AsyncClient()

    params = {"q": target}
    if apikey is not None:
        params["apikey"] = apikey

    response = await client.get("https://api.hackertarget.com/reverseiplookup/", params=params)
    await client.aclose()
    if response.status_code != 200:
        error(f"[HackerTarget] Error: status code: {response.status_code}")
        return {}
    if b"API count exceeded" in response.content:
        error(f"[HackerTarget] Error: {response.content}")
        return {}
    domains = response.text.split("\n")
    if verbose:
        into(f"[HackerTarget] {len(domains)} domains found")
    for domain in domains:
        if verbose:
            info(f"[HackerTarget] {domain}")
        results[target].append(domain)
    results = clean_uniq_results(results)
    return results
