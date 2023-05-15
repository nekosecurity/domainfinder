from colorama import Fore, Style

def info(text:str):
    print(f"{Fore.BLUE}[*]{Style.RESET_ALL}{text}")

def ok(text:str):
    print(f"{Fore.GREEN}[+]{Style.RESET_ALL}{text}")

def warn(text:str):
    print(f"{Fore.YELLOW}[+]{Style.RESET_ALL}{text}")

def error(text:str):
    print(f"{Fore.RED}[!]{Style.RESET_ALL}{text}")

def display_domain_in_scope(data: dict, scope: list, outofscope: bool):
    out_of_scope = []
    in_scope = []
    for keys, values in data.items():
        for s in scope:
            for value in values:
                in_scope.append(value) if s in value else out_of_scope.append(value)
    
    print(f"[Scope: {Fore.CYAN}{' '.join(scope)}{Style.RESET_ALL}]")
    [print(value) for value in in_scope]
    if out_of_scope is True:
        print("")
        print(f"[{Fore.YELLOW}Out Of Scope{Style.RESET_ALL}]")
        [print(value) for value in out_of_scope]

def display_results(data: dict):
    for keys, values in data.items():
        for value in values:
            print(value)