from netaddr import IPAddress, INET_PTON, IPRange, IPNetwork, AddrFormatError
import netaddr
from domainfinder.helpers.display import error
from pathlib import Path

def get_ip_version(ip:str) -> str: 
    try:
        ip = IPAddress(ip)
        ip_version = "IPv4" if ip.version == 4 else "IPv6"
        return ip_version
    except:
        return None

def clean_uniq_results(results: dict) -> dict:
    for key, values in results.items():
        results[key] = set(values)
    return results

def _clean_dict(data:dict) -> dict:
    domains_uniq = defaultdict(list)

    for key, value in data.items():
            domains_uniq[key] = [dict(t) for t in {tuple(v.items()) for v in data[key]}]
    return domains_uniq
    
def merge_results(results: dict, new_dict: dict) -> dict:
    try:
        for key, values in new_dict.items():
            if not key in results.keys():
                results[key] = set()
            results[key].update(values) # results[key] == set()
    except:
        return results
    return results

def is_valid_ip(target, display=True):
    if netaddr.valid_ipv4(target) or netaddr.valid_ipv6(target):
        return True
    if display:
        error(f"Not valid ip {target}")

def is_valid_cidr(target):
    if not "/" in target:
        return False
    target = target.split("/")[1]
    if int(target) > 0  and int(target) < 33:
        return True
    error(f"Not valid cidr: {target}")

def analyse_targets(targets):
    final = []
    for target in targets:
        is_valid_ip(target, display=False)
    for target in targets:
        try: path = Path(target)
        except: continue
        if path.is_file():
            '''
            If target is a file, take each values inside and recall analyse_targets
            '''
            targets.extend(open(target, 'r').read().splitlines())
            targets.remove(target)
            return analyse_targets(targets)    
        elif '-' in target:
            start_ip, end_ip = target.split('-')
            try:
                end_ip = IPAddress(end_ip, flags=INET_PTON)
            except:
                first_three_octets = start_ip.split('.')[:-1]
                first_three_octets.append(end_ip)
                end_ip = IPAddress(".".join(first_three_octets))
            if is_valid_ip(start_ip):
                if IPAddress(start_ip) > IPAddress(end_ip):
                    start_ip, end_ip = end_ip, start_ip
                [final.append(ip) for ip in IPRange(start_ip, end_ip)]
        elif "/" in target:
           if is_valid_cidr(target):
                [final.append(ip) for ip in IPNetwork(target)]
        else:
            if target not in final:
                if is_valid_ip(target):
                    final.append(IPAddress(target))
    return final
