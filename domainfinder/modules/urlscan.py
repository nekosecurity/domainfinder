from collections import defaultdict
import httpx
from helpers.helpers import clean_uniq_results
from helpers.display import info, error


async def get_host(target, verbose: bool, apikey: str) -> dict:
    results = defaultdict(list)
    results = defaultdict(list)
    client = httpx.AsyncClient()

    headers = {}
    if apikey is not None:
        headers["API-Key"] = apikey
    response = await client.get(
        "https://urlscan.io/api/v1/search/",
        params={"q": f"ip:{target}"},
        headers=headers,
    )
    await client.aclose()
    if response.status_code != 200:
        error(
            f"[UrlScan] Error: status code: {response.status_code}\tReason {response.reason_phrase}\t {response.json()['message']}"
        )
        return {}
    data = response.json()
    if verbose:
        info(f"[UrlScan] {len(data['results'])} domains found")
    for infos in data["results"]:
        if verbose:
            info(f"[UrlScan] {infos['page']['ptr']}")
            info(f"[UrlScan] {infos['page']['apexDomain']}")
            print("")
        if "apexDomain" in infos["page"].keys():
            results[target].append(infos["page"]["apexDomain"])
        if "ptr" in infos["page"].keys():
            results[target].append(infos["page"]["ptr"])
    results = clean_uniq_results(results)
    return results
