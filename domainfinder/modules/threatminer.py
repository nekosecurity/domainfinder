from collections import defaultdict
import httpx
from helpers.helpers import clean_uniq_results
from helpers.display import error


async def get_host(target: str, verbose: bool) -> dict:
    results = defaultdict(list)
    client = httpx.AsyncClient()
    response = await client.get("https://api.threatminer.org/v2/host.php", params={"q": target, "rt": 2})
    if response.status_code != 200:
        error(f"[ThreatMiner] Error: status code: {response.status_code}")
        return {}
    data = response.json()
    if len(data[results]) > 0:
        for items in data["results"]:
            if verbose:
                info(f"[ThreatMiner] {items['domain']}")
            results[target].append(items["domain"])
        results = clean_uniq_results(results)
    return results
