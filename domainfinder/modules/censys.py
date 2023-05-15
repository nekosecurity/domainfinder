from collections import defaultdict
import httpx
from lxml import html
import re
from helpers.helpers import clean_uniq_results
from helpers.display import info, error


async def get_host(target: str, verbose: bool, censys_config: dict) -> dict:
    results = defaultdict(list)
    client = httpx.AsyncClient()

    if censys_config["censys_uid"] is not None and censys_config["censys_secret"] is not None:
        response = await client.get(
            f"https://search.censys.io/api/v2/hosts/{target}",
            auth=(censys_config["censys_uid"], censys_config["censys_secret"]),
        )
        await client.aclose()
        if response.status_code != 200:
            error(f"[Censys] Error: status code: {response.status_code}")
            return {}
        data = response.json()
        results[target].extend(data["result"]["dns"]["names"])
        results[target].extend(data["result"]["dns"]["reverse_dns"]["names"])
        results = clean_uniq_results(results)
        if verbose:
            for values in results.values():
                for value in values:
                    info(f"[Censys API] {value}")
    else:
        response = await client.get(f"https://search.censys.io/hosts/{target}")
        await client.aclose()
        if response.status_code != 200:
            error(f"[Censys] Error: status code: {response.status_code}")
            return {}
        tree = html.fromstring(response.content)
        certificate = tree.xpath("//div[@class='certificate host-detail-chain-cert']")
        if len(certificate) > 0:
            certificate = certificate[0].text_content()
            try:
                common_name = re.search("CN=(.+)\n", certificate).group(1)
            except:
                common_name = None
        else:
            common_name = None
        if tree.xpath("//dl[@class='dl dl-horizontal']/dt[position() = 1]")[0].text_content() == "Reverse DNS":
            rev_dns = tree.xpath("//dl[@class='dl dl-horizontal']/dd[position() = 1]")[0].text_content()
            if common_name is not None:
                results[target].append(common_name)
            if rev_dns is not None:
                results[target].append(rev_dns)
        results = clean_uniq_results(results)
        if verbose:
            for values in results.values():
                for value in values:
                    info(f"[Censys] {value}")
    return results
