# Soar Team - Proxy Checker

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/AsyncIO-Supported-5865F2?style=for-the-badge&logo=fastapi&logoColor=white" alt="AsyncIO" />
  <img src="https://img.shields.io/badge/Discord-Compatible-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord" />
  <img src="https://img.shields.io/badge/Windows-Supported-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows" />
  <img src="https://img.shields.io/badge/Linux-Supported-FCC624?style=for-the-badge&logo=linux&logoColor=black" alt="Linux" />
  <img src="https://img.shields.io/badge/macOS-Supported-000000?style=for-the-badge&logo=apple&logoColor=white" alt="macOS" />
</p>

An asynchronous Python CLI tool to test HTTP and HTTPS proxies against Discord, Cloudflare, or custom endpoints.

---

## Features

- Supports `ip:port`, `ip:port:user:pass`, and `user:pass@ip:port` formats
- Asynchronous scanning with adjustable concurrency and timeouts
- Discord check: detects working proxies, 429 rate limits, and dead connections
- Cloudflare check: tests latency and general connectivity
- Custom endpoint check: test against any target URL
- Real-time latency measurement per proxy
- Automatic export to `working.txt`, `rate_limited.txt`, and `dead.txt`
- Proxy list deduplicator and formatter.

---

## Prerequisites

- Python 3.8 or newer
- Windows, Linux, or macOS

---

## Installation

Clone the repository and install requirements:

```bash
git clone https://github.com/i2tt/Soar-Proxy-Checker.git
cd Soar-Proxy-Checker
pip install -r requirements.txt
```

---

## Usage

Place your proxies inside `proxies.txt`, then run the tool:

### Windows

```bash
run.bat
```

### Linux / macOS

```bash
python main.py
```

### Steps

1. Add proxies to `proxies.txt`
2. Start the tool with `run.bat` or `python main.py`
3. Choose a check target (Discord, Cloudflare, or custom URL)
4. Set concurrency and timeout, or press Enter for defaults
5. Working proxies are saved automatically to `working.txt`

---

## Available Options

- `1`: Check Proxies (Discord API)
- `2`: Check Proxies (Cloudflare)
- `3`: Check Proxies (Custom URL)
- `4`: Format Proxy List
- `5`: View Credits
- `6`: Exit

---

## Developers

<p align="center">
  <a href="https://github.com/i2tt">
    <img src="https://img.shields.io/badge/i2tt-GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="i2tt" />
  </a>
  <a href="https://github.com/K2CV">
    <img src="https://img.shields.io/badge/K2CV-GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="K2CV" />
  </a>
</p>

Co-Authored-By: [K2CV](https://github.com/K2CV)

---

## Disclaimer

This software is for educational and network testing purposes only.
Use entirely at your own risk.
