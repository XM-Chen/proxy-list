import re
import requests
from pathlib import Path

RAW_README = "https://raw.githubusercontent.com/TopChina/proxy-list/main/README.md"
OUT_FILE = Path("proxies.yaml")

def parse_proxies(md: str):
    proxies = []
    ip_port_re = re.compile(r"^\|\s*(\d{1,3}(?:\.\d{1,3}){3}:\d+)\s*\|")
    for line in md.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        if not ip_port_re.search(line):
            continue
        cols = [c.strip() for c in line.split("|")]
        if len(cols) < 4:
            continue
        ip_port = cols[1]
        username = cols[3]
        if not re.match(r"^\d{1,3}(?:\.\d{1,3}){3}:\d+$", ip_port):
            continue
        if not username:
            continue
        server, port = ip_port.split(":", 1)
        try:
            port = int(port)
        except ValueError:
            continue
        proxies.append({
            "name": ip_port,
            "type": "http",
            "server": server,
            "port": port,
            "username": username,
            "password": "1",
        })
    return proxies

def build_yaml(proxies):
    lines = ["proxies:"]
    for p in proxies:
        lines.append(f'  - name: "{p["name"]}"')
        lines.append(f'    type: {p["type"]}')
        lines.append(f'    server: {p["server"]}')
        lines.append(f'    port: {p["port"]}')
        lines.append(f'    username: "{p["username"]}"')
        lines.append(f'    password: "{p["password"]}"')
    return "\n".join(lines) + "\n"

def main():
    resp = requests.get(RAW_README, headers={"Cache-Control": "no-cache"}, timeout=30)
    resp.raise_for_status()
    proxies = parse_proxies(resp.text)
    yaml_text = build_yaml(proxies)
    OUT_FILE.write_text(yaml_text, encoding="utf-8")
    print(f"Wrote {len(proxies)} proxies to {OUT_FILE}")

if __name__ == "__main__":
    main()
