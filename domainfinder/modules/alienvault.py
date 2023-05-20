from collections import defaultdict
import httpx
import netaddr
from domainfinder.helpers.helpers import get_ip_version, clean_uniq_results
from domainfinder.helpers.display import info, error


async def get_host(target: netaddr.IPAddress, verbose: bool) -> dict:
    results = defaultdict(list)
    client = httpx.AsyncClient()
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0"}
    ip_version = get_ip_version(target)
    if ip_version is None:
        return None
    response = await client.get(
        f"https://otx.alienvault.com/api/v1/indicators/{ip_version}/{target}/passive_dns",
        headers=headers,
    )
    await client.aclose()
    if response.status_code != 200:
        error(f"[AlienVault] Error: status code: {response.status_code}")
        return {}

    if verbose:
        info(f"[AlienVault] {response.json()['count']} domains found")
    for d in response.json()["passive_dns"]:
        if verbose:
            info(f"[AlienVault] {d['hostname']}")
        results[target].append(d["hostname"])
    results = clean_uniq_results(results)
    return results
