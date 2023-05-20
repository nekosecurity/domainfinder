import argparse
import domainfinder.modules.rapiddns as rapiddns
import domainfinder.modules.alienvault as alienvault
import domainfinder.modules.censys as censys
import domainfinder.modules.urlscan as urlscan
import domainfinder.modules.hackertarget as hackertarget
import domainfinder.modules.shodan as shodan
import domainfinder.modules.threatminer as threatminer
import domainfinder.modules.viewdns as viewdns
from domainfinder.helpers.helpers import (
    clean_uniq_results,
    merge_results,
    analyse_targets,
    is_valid_cidr,
)
from domainfinder.helpers.display import display_domain_in_scope, error, display_results
import asyncio
from pathlib import Path
import yaml


async def get_domains(targets: list, verbose: bool, config: dict) -> dict:
    tasks = []
    if config["rapiddns"]["enable"]:
        rapiddns_target = []
        tmp_targets = targets.copy()

        for target in tmp_targets:
            if is_valid_cidr(target):
                rapiddns_target.append(target)
                tmp_targets.remove(target)

        rapiddns_target.extend(analyse_targets(tmp_targets))
        for target in rapiddns_target:
            tasks.append(asyncio.create_task(rapiddns.get_host(target, verbose)))

    targets = analyse_targets(targets)

    counter = 0
    for target in targets:
        if counter >= 10:
            await asyncio.sleep(1)
            counter = 0
        if config["censys"]["enable"]:
            tasks.append(asyncio.create_task(censys.get_host(target, verbose, config["censys"])))
        if config["alienvault"]["enable"]:
            tasks.append(asyncio.create_task(alienvault.get_host(target, verbose)))
        if config["hackertarget"]["enable"]:
            tasks.append(asyncio.create_task(hackertarget.get_host(target, verbose, config["hackertarget"]["apikey"])))
        if config["shodan"]["enable"]:
            tasks.append(asyncio.create_task(shodan.get_host(target, verbose, config["shodan"]["apikey"])))
            tasks.append(asyncio.create_task(shodan.get_internetdb_info(target, verbose)))
        if config["threatminer"]["enable"]:
            tasks.append(asyncio.create_task(threatminer.get_host(target, verbose)))
        if config["urlscan"]["enable"]:
            tasks.append(asyncio.create_task(urlscan.get_host(target, verbose, config["urlscan"]["apikey"])))
        # if config["viewdns"]["enable"]:
        #     tasks.append(asyncio.create_task(viewdns.get_host(target, verbose, config["viewdns"]["apikey"])))
        counter += 1
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    return responses


def load_config(configfile: str):
    try:
        path = Path(configfile)
        config = yaml.safe_load(open(configfile, "r").read())
        return config
    except Exception as e:
        error(f"[load_config]{e}")
        error("[load_config] Loading default config file")


def select_modules(modules: list, config: dict):
    """
    Select module by disable unwanted
    """
    for keys, values in config.items():
        if keys not in modules and config[keys]["enable"]:
            config[keys]["enable"] = False
        if keys in modules and not config[keys]["enable"]:
            config[keys]["enable"] = True
    return config


def main():
    desc = "Passive domain recovery from IP"
    example = "python domainfinder.py 8.8.8.8"
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=desc,
        epilog=example,
    )

    # Options
    options = parser.add_argument_group("Options")
    options.add_argument("-v", "--verbose", action="store_true")
    options.add_argument("-s", "--scope", help="Highlight domain in scope", nargs="+")
    options.add_argument(
        "--show-outofscope",
        help="Display domain not in scope",
        action="store_true",
        default=None,
    )
    options.add_argument("-o", "--output", help="Save domain in file")
    options.add_argument("--output-append", help="Append domains to file", action="store_true")
    options.add_argument("--silent", help="Display silent output", action="store_true", default=True)
    options.add_argument(
        "-m",
        "--modules",
        help=f"Space separated list of API module. Allowed values are {','.join(list(load_config('domainfinder/configs/domainfinder.yml')['api']))}",
        choices=list(load_config("domainfinder/configs/domainfinder.yml")["api"]),
        nargs="*",
        metavar="",
    )
    options.add_argument("-c", "--config", help="Select config file", default="domainfinder/configs/domainfinder.yml")

    # Core
    parser.add_argument(
        "targets",
        help="the target IP(s), range(s), CIDR(s), file(s) containing a list of targets",
        nargs="+",
    )

    args = parser.parse_args()
    config = load_config(args.config)

    if args.modules:
        config = select_modules(args.modules, config["api"])
    else:
        config = config['api']
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(get_domains(args.targets, args.verbose, config))

    if args.show_outofscope and not args.scope:
        error("--show-outofscope cannot be used without --scope option")
        exit()

    final_results = {}
    for result in results:
        final_results = merge_results(final_results, result)

    final_results = clean_uniq_results(final_results)

    if args.silent and not args.scope:
        display_results(final_results)
    if args.scope:
        args.scope = set(args.scope)
        display_domain_in_scope(final_results, args.scope, args.show_outofscope)
    if args.output_append and not args.output:
        error("--output-append cannot be used without --output option")
        exit()
    if args.output:
        if args.output_append:
            mode = "a"
        else:
            mode = "w"
        with open(args.output, mode) as f:
            for key, values in final_results.items():
                for domain in values:
                    f.write(f"{domain}\n")
