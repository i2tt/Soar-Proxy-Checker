import os
import sys
import time
import asyncio
import aiohttp
import ctypes
import platform
from threading import Lock
from colorama import Fore, Style, init
from pystyle import Write, Colors

init(autoreset=True)

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

APP_TITLE = "Soar Proxy Checker - Made By i2tt"
print_lock = Lock()

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

def set_console_title(text):
    try:
        if platform.system() == "Windows":
            ctypes.windll.kernel32.SetConsoleTitleW(text)
        else:
            sys.stdout.write(f"\033]0;{text}\007")
            sys.stdout.flush()
    except Exception:
        pass

set_console_title(APP_TITLE)

ascii_art = """
                            ███████╗  ██████╗   █████╗  ██████╗ 
                            ██╔════╝ ██╔═══██╗ ██╔══██╗ ██╔══██╗
                            ███████╗ ██║   ██║ ███████║ ██████╔╝
                            ╚════██║ ██║   ██║ ██╔══██║ ██╔══██╗
                            ███████║ ╚██████╔╝ ██║  ██║ ██║  ██║
                            ╚══════╝  ╚═════╝  ╚═╝  ╚═╝ ╚═╝  ╚═╝


                
                                            Soar Team - Proxy Checker 
                
"""

def parse_proxy(line):
    p = line.strip()
    if not p or p.startswith('#'):
        return None
    proto = 'http'
    if '://' in p:
        proto, p = p.split('://', 1)
    if '@' in p:
        auth, host_port = p.split('@', 1)
        formatted = f"{auth}@{host_port}"
        display = host_port
    else:
        parts = p.split(':')
        if len(parts) == 4:
            formatted = f"{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
            display = f"{parts[0]}:{parts[1]}"
        else:
            formatted = p
            display = p
    return line.strip(), f"{proto}://{formatted}", display

def load_proxies(filepath="proxies.txt"):
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.read().splitlines()
    parsed = []
    seen = set()
    for line in lines:
        item = parse_proxy(line)
        if item and item[1] not in seen:
            seen.add(item[1])
            parsed.append(item)
    return parsed

class Stats:
    def __init__(self, total):
        self.total = total
        self.checked = 0
        self.working = 0
        self.rate_limited = 0
        self.dead = 0
        self.latencies = []

async def check_proxy(session, sem, proxy, target_type, custom_url, timeout, stats, working, rate_limited, dead):
    raw, url, display = proxy
    if target_type == 'discord':
        target = 'https://discord.com/api/v9/unique-username/username-attempt-unauthed'
        req_fn = session.post
        kwargs = {'json': {'username': 'alex'}}
    elif target_type == 'cloudflare':
        target = 'https://www.cloudflare.com/cdn-cgi/trace'
        req_fn = session.get
        kwargs = {}
    else:
        target = custom_url
        req_fn = session.get
        kwargs = {}

    client_timeout = aiohttp.ClientTimeout(total=timeout)
    async with sem:
        t0 = time.perf_counter()
        try:
            async with req_fn(target, proxy=url, timeout=client_timeout, **kwargs) as resp:
                latency = round((time.perf_counter() - t0) * 1000)
                if resp.status == 200:
                    with print_lock:
                        print(f"  {Fore.LIGHTBLACK_EX}~{Fore.RESET} {Fore.GREEN}Active  {Fore.LIGHTBLACK_EX}[{display:<21}] {Fore.GREEN}200 OK  {Fore.LIGHTBLACK_EX}({latency}ms){Style.RESET_ALL}")
                    stats.working += 1
                    stats.latencies.append(latency)
                    working.append(raw)
                elif resp.status == 429:
                    with print_lock:
                        print(f"  {Fore.LIGHTBLACK_EX}~{Fore.RESET} {Fore.YELLOW}RateLtd {Fore.LIGHTBLACK_EX}[{display:<21}] {Fore.YELLOW}429 Blocked{Style.RESET_ALL}")
                    stats.rate_limited += 1
                    rate_limited.append(raw)
                else:
                    with print_lock:
                        print(f"  {Fore.LIGHTBLACK_EX}~{Fore.RESET} {Fore.RED}Dead    {Fore.LIGHTBLACK_EX}[{display:<21}] {Fore.RED}HTTP {resp.status}{Style.RESET_ALL}")
                    stats.dead += 1
                    dead.append(raw)
        except (asyncio.TimeoutError, aiohttp.ServerTimeoutError):
            with print_lock:
                print(f"  {Fore.LIGHTBLACK_EX}~{Fore.RESET} {Fore.RED}Dead    {Fore.LIGHTBLACK_EX}[{display:<21}] {Fore.RED}Timeout{Style.RESET_ALL}")
            stats.dead += 1
            dead.append(raw)
        except (aiohttp.ClientError, OSError):
            with print_lock:
                print(f"  {Fore.LIGHTBLACK_EX}~{Fore.RESET} {Fore.RED}Dead    {Fore.LIGHTBLACK_EX}[{display:<21}] {Fore.RED}Connection Failed{Style.RESET_ALL}")
            stats.dead += 1
            dead.append(raw)
        finally:
            stats.checked += 1
            pct = int((stats.checked / stats.total) * 100) if stats.total else 0
            avg = round(sum(stats.latencies) / len(stats.latencies)) if stats.latencies else 0
            set_console_title(f"Soar Checker | Checked: {stats.checked}/{stats.total} ({pct}%) | Active: {stats.working} | RateLtd: {stats.rate_limited} | Dead: {stats.dead} | Ping: {avg}ms")

async def run_checker(target_type='discord', custom_url=''):
    cls()
    set_console_title("Soar Checker | Scanning...")
    Write.Print(ascii_art, Colors.light_gray, interval=0.001)
    Write.Print("\n                                            [ Powered by Soar Services ]\n", Colors.dark_gray, interval=0.001)
    Write.Print("                                            [ Developed by i2tt & K2CV ]\n\n", Colors.dark_gray, interval=0.001)

    proxies = load_proxies("proxies.txt")
    if not proxies:
        print(f"  {Fore.LIGHTBLACK_EX}~{Fore.RESET} {Fore.RED}No proxies in proxies.txt{Style.RESET_ALL}\n")
        input(Fore.LIGHTBLACK_EX + f"  {Fore.LIGHTBLUE_EX}~{Fore.RESET} Press Enter to return..." + Fore.RESET)
        return

    print(Fore.LIGHTBLACK_EX + "  " + "─" * 86 + Style.RESET_ALL)
    try:
        threads = int(input(f"  {Fore.LIGHTBLUE_EX}~{Fore.RESET}$ Threads (default 100): ").strip() or 100)
    except ValueError:
        threads = 100

    try:
        timeout = float(input(f"  {Fore.LIGHTBLUE_EX}~{Fore.RESET}$ Timeout in seconds (default 4): ").strip() or 4)
    except ValueError:
        timeout = 4.0

    target_name = "Discord" if target_type == 'discord' else ("Cloudflare" if target_type == 'cloudflare' else custom_url)
    print(f"\n  {Fore.CYAN}Checking {len(proxies)} proxies against {target_name} ({threads} threads)...\n{Style.RESET_ALL}")
    time.sleep(0.4)

    stats = Stats(total=len(proxies))
    working, rate_limited, dead = [], [], []

    sem = asyncio.Semaphore(threads)
    connector = aiohttp.TCPConnector(limit=threads, ttl_dns_cache=300)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    t0 = time.time()
    async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
        tasks = [
            check_proxy(session, sem, p, target_type, custom_url, timeout, stats, working, rate_limited, dead)
            for p in proxies
        ]
        await asyncio.gather(*tasks)

    elapsed = round(time.time() - t0, 2)

    with open("working.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(working) + ("\n" if working else ""))

    with open("rate_limited.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(rate_limited) + ("\n" if rate_limited else ""))

    with open("dead.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(dead) + ("\n" if dead else ""))

    set_console_title(f"Soar Checker | Done | Active: {stats.working} | RateLtd: {stats.rate_limited} | Dead: {stats.dead}")

    inner = 76
    top = f"\n  {Fore.LIGHTBLACK_EX}╔" + "═" * inner + f"╗{Style.RESET_ALL}"
    mid = f"  {Fore.LIGHTBLACK_EX}╠" + "═" * inner + f"╣{Style.RESET_ALL}"
    bot = f"  {Fore.LIGHTBLACK_EX}╚" + "═" * inner + f"╝\n{Style.RESET_ALL}"

    title_text = "SCAN RESULTS"
    header = f"  {Fore.LIGHTBLACK_EX}║{Style.RESET_ALL}" + f"{Fore.GREEN}" + title_text.center(inner) + f"{Style.RESET_ALL}" + f"{Fore.LIGHTBLACK_EX}║{Style.RESET_ALL}"

    def row(label, val, col):
        val_str = f"{str(val):<52}"[:52]
        return f"  {Fore.LIGHTBLACK_EX}║{Style.RESET_ALL}  {Fore.CYAN}{label:<18}{Style.RESET_ALL} : {col}{val_str}{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}║{Style.RESET_ALL}"

    pct = f"{(stats.working / stats.total * 100):.1f}%" if stats.total else "0%"
    avg = f"{round(sum(stats.latencies) / len(stats.latencies))}ms" if stats.latencies else "0ms"

    print(top)
    print(header)
    print(mid)
    print(row("Target", target_name, Fore.WHITE))
    print(row("Total", f"{stats.total} proxies", Fore.LIGHTBLACK_EX))
    print(row("Active", f"{stats.working} ({pct})", Fore.GREEN))
    print(row("Rate-Limited", f"{stats.rate_limited}", Fore.YELLOW))
    print(row("Dead", f"{stats.dead}", Fore.RED))
    print(row("Average Ping", avg, Fore.WHITE))
    print(row("Time", f"{elapsed}s", Fore.WHITE))
    print(row("Saved To", "working.txt", Fore.GREEN))
    print(bot)

    input(Fore.LIGHTBLACK_EX + f"  {Fore.LIGHTBLUE_EX}~{Fore.RESET} Press Enter to return..." + Fore.RESET)

def format_proxies_tool():
    cls()
    set_console_title("Soar Checker | Formatter")
    Write.Print(ascii_art, Colors.light_gray, interval=0.001)
    Write.Print("\n                                            [ Powered by Soar Services ]\n\n", Colors.dark_gray, interval=0.001)

    proxies = load_proxies("proxies.txt")
    if not proxies:
        print(f"  {Fore.LIGHTBLACK_EX}~{Fore.RESET} {Fore.RED}No proxies in proxies.txt{Style.RESET_ALL}\n")
        input(Fore.LIGHTBLACK_EX + f"  {Fore.LIGHTBLUE_EX}~{Fore.RESET} Press Enter to return..." + Fore.RESET)
        return

    formatted_list = [p[1].replace('http://', '').replace('https://', '') for p in proxies]

    with open("formatted_proxies.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(formatted_list) + "\n")

    print(f"  {Fore.LIGHTBLACK_EX}~{Fore.RESET} {Fore.GREEN}Saved {len(formatted_list)} proxies to formatted_proxies.txt{Style.RESET_ALL}\n")
    input(Fore.LIGHTBLACK_EX + f"  {Fore.LIGHTBLUE_EX}~{Fore.RESET} Press Enter to return..." + Fore.RESET)

def credits_view():
    cls()
    set_console_title("Soar Checker | Credits")
    Write.Print(ascii_art, Colors.light_gray, interval=0.001)
    print(f"\n  {Fore.LIGHTBLACK_EX} Soar Proxy Checker {Fore.RESET}")
    print(f"  {Fore.LIGHTBLACK_EX} Developer : i2tt {Fore.RESET}")
    print(f"  {Fore.LIGHTBLACK_EX} Developer : K2CV {Fore.RESET}")
    print(f"  {Fore.LIGHTBLACK_EX} Team      : Soar Team {Fore.RESET}")
    print(f"  {Fore.LIGHTBLACK_EX} GitHub    : https://github.com/i2tt/Soar-Proxy-Checker {Fore.RESET}\n")
    input(Fore.LIGHTBLACK_EX + f"  {Fore.LIGHTBLUE_EX}~{Fore.RESET} Press Enter to return..." + Fore.RESET)

def main_menu():
    while True:
        cls()
        set_console_title(APP_TITLE)
        Write.Print(ascii_art, Colors.light_gray, interval=0.001)
        Write.Print("\n                                            [ Powered by Soar Services ]\n", Colors.dark_gray, interval=0.001)
        Write.Print("                                            [ Version : 3.5 ]\n\n", Colors.dark_gray, interval=0.01)
        print(f"  {Fore.LIGHTBLACK_EX}[1]{Fore.RESET} Check Proxies (Discord API)")
        print(f"  {Fore.LIGHTBLACK_EX}[2]{Fore.RESET} Check Proxies (Cloudflare)")
        print(f"  {Fore.LIGHTBLACK_EX}[3]{Fore.RESET} Check Proxies (Custom URL)")
        print(f"  {Fore.LIGHTBLACK_EX}[4]{Fore.RESET} Format Proxy List")
        print(f"  {Fore.LIGHTBLACK_EX}[5]{Fore.RESET} Credits")
        print(f"  {Fore.LIGHTBLACK_EX}[6]{Fore.RESET} Exit\n")

        choice = input("  > ").strip()
        if choice == "1":
            asyncio.run(run_checker('discord'))
        elif choice == "2":
            asyncio.run(run_checker('cloudflare'))
        elif choice == "3":
            cls()
            url = input(f"  {Fore.LIGHTBLUE_EX}~{Fore.RESET}$ URL: ").strip()
            if url and not url.startswith('http'):
                url = 'https://' + url
            if url:
                asyncio.run(run_checker('custom', url))
        elif choice == "4":
            format_proxies_tool()
        elif choice == "5":
            credits_view()
        elif choice == "6":
            cls()
            sys.exit(0)

if __name__ == "__main__":
    main_menu()
