import requests
from pathlib import Path

UPSTREAM_README = "https://raw.githubusercontent.com/TopChina/proxy-list/main/README.md"
UPSTREAM_CONFIG = "https://raw.githubusercontent.com/TopChina/proxy-list/main/clash_sub.yaml"
OUT_PROXIES = Path("proxies.yaml")
OUT_README = Path("README.md")


def fetch(url):
    response = requests.get(url, headers={"Cache-Control": "no-cache"}, timeout=30)
    response.raise_for_status()
    return response.text


def main():
    config = fetch(UPSTREAM_CONFIG)
    if "proxies:" not in config:
        raise ValueError("upstream Clash config does not contain proxies")

    readme = fetch(UPSTREAM_README)
    readme = readme.replace(
        "https://raw.githubusercontent.com/TopChina/proxy-list/refs/heads/main/clash_sub.yaml",
        "https://raw.githubusercontent.com/XM-Chen/proxy-list/refs/heads/main/proxies.yaml",
    )

    OUT_PROXIES.write_text(config, encoding="utf-8")
    OUT_README.write_text(readme, encoding="utf-8")
    print(f"Synced upstream Clash config to {OUT_PROXIES} and README.md")


if __name__ == "__main__":
    main()
