import re
import requests
from pathlib import Path

UPSTREAM_RAW = "https://raw.githubusercontent.com/TopChina/proxy-list/main/README.md"
OUT_PROXIES = Path("proxies.yaml")
OUT_README = Path("README.md")

def parse_proxies(md: str):
    proxies = []
    # 表格行形如：| IP:PORT | 国家/地区 | 用户名 |
    row_re = re.compile(r"^\|\s*\d{1,3}(?:\.\d{1,3}){3}:\d+\s*\|")
    for line in md.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        if not row_re.search(line):
            continue
        cols = [c.strip() for c in line.split("|")]
        # 预期：cols[1]=IP:PORT, cols[2]=国家/地区, cols[3]=用户名
        if len(cols) < 4:
            continue
        ip_port = cols[1]
        country = cols[2] or "未知地区"
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

        # 节点显示名：加入国家/地区
        display_name = f"[{country}] {ip_port}"

        proxies.append({
            "name": display_name,
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
    resp = requests.get(UPSTREAM_RAW, headers={"Cache-Control": "no-cache"}, timeout=30)
    resp.raise_for_status()
    md = resp.text

    # 1) 同步上游 README.md 到本仓库
    OUT_README.write_text(md, encoding="utf-8")

    # 2) 解析并生成 proxies.yaml
    proxies = parse_proxies(md)
    yaml_text = build_yaml(proxies)
    OUT_PROXIES.write_text(yaml_text, encoding="utf-8")
    print(f"Wrote {len(proxies)} proxies to {OUT_PROXIES} and synced README.md")

if __name__ == "__main__":
    main()
